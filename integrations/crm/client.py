import logging
import requests
from django.conf import settings
from core.oauth import get_valid_token

logger = logging.getLogger(__name__)


class CRMClient:
    def _headers(self) -> dict:
        token = get_valid_token("crm")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def get_contacts(self, page: int = 1) -> list:
        response = requests.get(
            f"{settings.CRM_BASE_URL}/contacts",
            headers=self._headers(),
            params={"page": page, "limit": 100},
            timeout=15,
        )
        response.raise_for_status()
        return response.json().get("contacts", [])

    def upsert_contact(self, data: dict) -> dict:
        response = requests.post(
            f"{settings.CRM_BASE_URL}/contacts",
            headers=self._headers(),
            json=data,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
