"""
Thread-safe Kafka producer singleton using confluent-kafka.

The singleton pattern avoids the overhead of creating a new producer per
request (librdkafka's internal thread pool is heavyweight).  `atexit`
ensures we flush unsent messages on interpreter shutdown.
"""

from __future__ import annotations

import atexit
import json
import logging
import threading
from typing import Optional

from confluent_kafka import KafkaError, Producer
from django.conf import settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)

_producer: Optional[Producer] = None
_lock = threading.Lock()


# ──────────────────────────────────────────────────────────────────────────────
# Factory
# ──────────────────────────────────────────────────────────────────────────────

def get_producer() -> Producer:
    """
    Return the global Kafka producer, creating it lazily on first call.
    Thread-safe via a double-checked lock.
    """
    global _producer  # noqa: PLW0603
    if _producer is not None:
        return _producer

    with _lock:
        # Re-check after acquiring the lock (another thread may have
        # created the producer while we waited).
        if _producer is not None:
            return _producer

        _producer = Producer(settings.KAFKA_PRODUCER_CONFIG)
        # Register a shutdown hook so we don't lose in-flight messages
        atexit.register(flush)
        logger.info(
            "Kafka producer initialised — brokers=%s",
            settings.KAFKA_BOOTSTRAP_SERVERS,
        )
        return _producer


# ──────────────────────────────────────────────────────────────────────────────
# Delivery callback
# ──────────────────────────────────────────────────────────────────────────────

def _delivery_callback(err: Optional[KafkaError], msg: object) -> None:
    """Invoked once per message when the broker acknowledges (or rejects)."""
    if err is not None:
        logger.error("Kafka delivery failed: %s", err)
    else:
        # msg is confluent_kafka.Message
        logger.debug(
            "Delivered to %s [%s] @ offset %s",
            msg.topic(),  # type: ignore[union-attr]
            msg.partition(),  # type: ignore[union-attr]
            msg.offset(),  # type: ignore[union-attr]
        )


# ──────────────────────────────────────────────────────────────────────────────
# Generic publish
# ──────────────────────────────────────────────────────────────────────────────

def publish_event(
    topic: str,
    key: str,
    event_schema: BaseModel,
) -> None:
    """
    Serialise a Pydantic model to JSON and publish to the given Kafka
    topic.  Uses the key for partitioning (usually user_id).
    """
    producer = get_producer()
    payload = json.dumps(
        event_schema.model_dump(mode="json"),
        default=str,
    ).encode("utf-8")

    producer.produce(
        topic=topic,
        key=key.encode("utf-8"),
        value=payload,
        callback=_delivery_callback,
    )
    # Trigger any queued delivery callbacks without blocking.
    producer.poll(0)


# ──────────────────────────────────────────────────────────────────────────────
# Typed convenience wrappers
# ──────────────────────────────────────────────────────────────────────────────

def publish_code_event(key: str, event: BaseModel) -> None:
    """Publish a code event to the code-events topic."""
    publish_event("code-events", key, event)


def publish_git_event(key: str, event: BaseModel) -> None:
    """Publish a git event to the git-events topic."""
    publish_event("git-events", key, event)


def publish_terminal_event(key: str, event: BaseModel) -> None:
    """Publish a terminal event to the terminal-events topic."""
    publish_event("terminal-events", key, event)


def publish_error_event(key: str, event: BaseModel) -> None:
    """Publish an error event to the error-events topic."""
    publish_event("error-events", key, event)


def publish_session_event(key: str, event: BaseModel) -> None:
    """Publish a session lifecycle event."""
    publish_event("session-events", key, event)


def publish_analysis_request(key: str, event: BaseModel) -> None:
    """Publish an analysis request."""
    publish_event("analysis-requests", key, event)


# ──────────────────────────────────────────────────────────────────────────────
# Shutdown
# ──────────────────────────────────────────────────────────────────────────────

def flush(timeout: float = 5.0) -> None:
    """
    Flush all buffered messages.  Called automatically at interpreter
    shutdown via `atexit`.
    """
    global _producer  # noqa: PLW0603
    if _producer is not None:
        remaining = _producer.flush(timeout)
        if remaining > 0:
            logger.warning(
                "Kafka producer flush timed out — %d messages still in queue",
                remaining,
            )
        logger.info("Kafka producer flushed and shut down")
