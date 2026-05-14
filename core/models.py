import uuid
from django.db import models


class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OAuthToken(TimeStampedModel):
    """Stores OAuth tokens for third-party services."""

    SERVICE_CHOICES = [("crm", "CRM"), ("payments", "Payments")]

    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.service} token"
