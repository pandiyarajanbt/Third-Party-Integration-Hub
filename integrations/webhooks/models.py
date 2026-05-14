from django.db import models
from core.models import TimeStampedModel


class WebhookEvent(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_DEAD = "dead"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
        (STATUS_DEAD, "Dead Letter"),
    ]

    source = models.CharField(max_length=50)          # e.g. "stripe", "twilio"
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    headers = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source}:{self.event_type} [{self.status}]"


class DeadLetterEvent(TimeStampedModel):
    """Events that exhausted all retries."""
    webhook_event = models.OneToOneField(WebhookEvent, on_delete=models.CASCADE, related_name="dead_letter")
    failure_reason = models.TextField()
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Dead: {self.webhook_event}"
