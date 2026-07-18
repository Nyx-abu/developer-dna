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
    Serialise a Pydantic model to JSON and write it to the OutboxEvent table
    in the database. Debezium will tail this table and publish to Kafka.
    """
    from events.models import OutboxEvent

    payload = event_schema.model_dump(mode="json")
    
    OutboxEvent.objects.create(
        aggregate_type=topic,
        aggregate_id=key,
        event_type=event_schema.__class__.__name__,
        payload=payload
    )
    logger.debug(f"Saved {topic} event for {key} to outbox")


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
