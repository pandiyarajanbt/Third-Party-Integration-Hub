from django.db import models
from core.models import TimeStampedModel


class SMSMessage(TimeStampedModel):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
        ("undelivered", "Undelivered"),
    ]

    to_number = models.CharField(max_length=20)
    body = models.TextField()
    twilio_sid = models.CharField(max_length=100, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued", db_index=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"SMS to {self.to_number} [{self.status}]"
