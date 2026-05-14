from django.db import models
from core.models import TimeStampedModel


class CRMContact(TimeStampedModel):
    crm_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    raw_data = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.email} ({self.crm_id})"
