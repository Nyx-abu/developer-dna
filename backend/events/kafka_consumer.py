"""
Kafka consumer with at-least-once delivery, dead-letter queue, and
graceful signal-based shutdown.

Design:
 - Manual offset commits after the handler succeeds.
 - On handler failure the message is re-published to a dead-letter topic
   (`dlq-{original_topic}`) so it can be inspected / retried later.
 - SIGTERM and SIGINT flip a threading.Event to break the poll loop.
"""

from __future__ import annotations

import json
import logging
import signal
import threading
from typing import Any, Callable, Optional

from confluent_kafka import Consumer, KafkaError, KafkaException, Producer
from django.conf import settings

logger = logging.getLogger(__name__)

# Type alias for topic handlers: fn(topic, key, payload_dict) -> None
TopicHandler = Callable[[str, str, dict[str, Any]], None]


class EventConsumer:
    """
    Long-running Kafka consumer that dispatches messages to registered
    topic handlers.
    """

    def __init__(
        self,
        handler_map: dict[str, TopicHandler],
        *,
        consumer_config: Optional[dict[str, Any]] = None,
    ) -> None:
        config = consumer_config or dict(settings.KAFKA_CONSUMER_CONFIG)
        self._consumer = Consumer(config)
        self._handler_map = handler_map
        self._shutdown = threading.Event()

        # DLQ producer shares the same broker list but a distinct client.id
        self._dlq_producer = Producer({
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "client.id": "devdna-dlq-producer",
        })

        # Register signal handlers so `manage.py run_consumer` stops cleanly
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    # ── Signal handling ──────────────────────────────────────────────────

    def _signal_handler(self, signum: int, _frame: Any) -> None:
        sig_name = signal.Signals(signum).name
        logger.info("Received %s — initiating graceful shutdown", sig_name)
        self._shutdown.set()

    # ── Dead letter queue ────────────────────────────────────────────────

    def _send_to_dlq(
        self,
        topic: str,
        key: bytes,
        value: bytes,
        error_msg: str,
    ) -> None:
        """Re-publish a failed message to dlq-{topic} with error headers."""
        dlq_topic = f"dlq-{topic}"
        headers = [
            ("original_topic", topic.encode("utf-8")),
            ("error", error_msg.encode("utf-8")),
        ]
        try:
            self._dlq_producer.produce(
                topic=dlq_topic,
                key=key,
                value=value,
                headers=headers,
            )
            self._dlq_producer.poll(0)
            logger.warning(
                "Message sent to DLQ %s — error: %s",
                dlq_topic,
                error_msg,
            )
        except Exception:
            logger.exception("Failed to publish to DLQ %s", dlq_topic)

    # ── Main poll loop ───────────────────────────────────────────────────

    def run(self) -> None:
        """
        Subscribe to configured topics and poll until a shutdown signal
        is received.  Each successfully handled message is committed
        synchronously so we never skip events.
        """
        topics = list(self._handler_map.keys())
        self._consumer.subscribe(topics)
        logger.info("Consumer subscribed to topics: %s", topics)

        try:
            while not self._shutdown.is_set():
                msg = self._consumer.poll(timeout=1.0)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition — not an error, just no more data
                        continue
                    raise KafkaException(msg.error())

                topic: str = msg.topic()
                key: str = (msg.key() or b"").decode("utf-8")
                raw_value: bytes = msg.value() or b"{}"

                try:
                    payload: dict[str, Any] = json.loads(raw_value)
                except json.JSONDecodeError as exc:
                    self._send_to_dlq(
                        topic,
                        msg.key() or b"",
                        raw_value,
                        f"JSON decode error: {exc}",
                    )
                    # Commit so we don't re-process the bad message forever
                    self._consumer.commit(msg)
                    continue

                handler = self._handler_map.get(topic)
                if handler is None:
                    logger.warning("No handler for topic %s — skipping", topic)
                    self._consumer.commit(msg)
                    continue

                try:
                    handler(topic, key, payload)
                except Exception as exc:
                    logger.exception(
                        "Handler for topic %s raised: %s", topic, exc,
                    )
                    self._send_to_dlq(
                        topic,
                        msg.key() or b"",
                        raw_value,
                        str(exc),
                    )

                # Manual commit — at-least-once delivery
                self._consumer.commit(msg)

        except KafkaException as exc:
            logger.exception("Fatal Kafka error: %s", exc)
        finally:
            self._shutdown_consumer()

    # ── Cleanup ──────────────────────────────────────────────────────────

    def _shutdown_consumer(self) -> None:
        """Close consumer and flush DLQ producer."""
        logger.info("Closing Kafka consumer…")
        try:
            self._consumer.close()
        except Exception:
            logger.exception("Error closing consumer")

        remaining = self._dlq_producer.flush(timeout=5.0)
        if remaining > 0:
            logger.warning("DLQ producer flush: %d messages still queued", remaining)
        logger.info("Consumer shutdown complete")
