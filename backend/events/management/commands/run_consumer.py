import json
import logging
import signal
import sys
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaError, KafkaException

from events.topic_router import route_message

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Run Kafka consumer worker for processing events"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.running = True

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--topics", nargs="+", default=settings.KAFKA_TOPICS,
                            help="Kafka topics to consume")

    def handle(self, *args: Any, **options: Any) -> None:
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

        topics = options["topics"]
        
        # Proactively create topics to prevent KafkaError{code=UNKNOWN_TOPIC_OR_PART}
        from confluent_kafka.admin import AdminClient, NewTopic
        admin_client = AdminClient({"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS})
        new_topics = [NewTopic(topic, num_partitions=1, replication_factor=1) for topic in topics]
        fs = admin_client.create_topics(new_topics)
        for topic, f in fs.items():
            try:
                f.result()
            except Exception:
                pass # Ignore if topic already exists
        
        consumer = Consumer(settings.KAFKA_CONSUMER_CONFIG)
        consumer.subscribe(topics)
        self.stdout.write(self.style.SUCCESS(f"Consuming from {topics}..."))

        try:
            while self.running:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error(f"Consumer error: {msg.error()}")
                    raise KafkaException(msg.error())

                try:
                    data = json.loads(msg.value().decode("utf-8"))
                    route_message(msg.topic(), data)
                    consumer.commit(message=msg, asynchronous=False)
                except Exception as e:
                    logger.exception(f"Failed to process message at {msg.topic()}/{msg.partition()}/{msg.offset()}")
                    self._dead_letter(msg, e)
                    consumer.commit(message=msg, asynchronous=False)
        finally:
            self.stdout.write("Shutting down consumer...")
            consumer.close()
            self.stdout.write(self.style.SUCCESS("Consumer closed."))

    def _handle_exit(self, signum: int, frame: Any) -> None:
        self.stdout.write(self.style.WARNING(f"Received signal {signum}, shutting down..."))
        self.running = False

    def _dead_letter(self, original_msg: Any, error: Exception) -> None:
        from events.kafka_producer import get_producer
        producer = get_producer()
        headers = [
            ("x-original-topic", original_msg.topic().encode("utf-8")),
            ("x-error-message", str(error).encode("utf-8")),
        ]
        if original_msg.headers():
            headers.extend(original_msg.headers())

        dlq_topic = f"dlq-{original_msg.topic()}"
        producer.publish_event(
            topic=dlq_topic,
            key=original_msg.key().decode("utf-8") if original_msg.key() else None,
            event_schema=None, # Raw payload
            raw_value=original_msg.value(),
            headers=headers
        )
