import logging
from celery import shared_task
from django.utils import timezone
from integrations.crm.client import CRMClient
from integrations.crm.models import CRMContact

logger = logging.getLogger(__name__)


@shared_task
def sync_crm_contacts():
    client = CRMClient()
    page = 1
    synced = 0

    while True:
        contacts = client.get_contacts(page=page)
        if not contacts:
            break

        for contact in contacts:
            CRMContact.objects.update_or_create(
                crm_id=contact["id"],
                defaults={
                    "email": contact.get("email", ""),
                    "first_name": contact.get("firstName", ""),
                    "last_name": contact.get("lastName", ""),
                    "synced_at": timezone.now(),
                    "raw_data": contact,
                },
            )
            synced += 1
        page += 1

    logger.info("CRM sync complete: %d contacts synced", synced)
    return synced
