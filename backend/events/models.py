from django.db import models
from django.utils import timezone
import uuid

class OutboxEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aggregate_type = models.CharField(max_length=255)
    aggregate_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    processed = models.BooleanField(default=False)

    class Meta:
        db_table = 'outbox_events'
        indexes = [
            models.Index(fields=['processed', 'created_at']),
        ]

    def __str__(self):
        return f"{self.event_type} on {self.aggregate_type} ({self.aggregate_id})"
