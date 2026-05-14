import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from core.models import OAuthToken


def get_valid_token(service: str) -> str:
    """Return a valid access token, refreshing if expired."""
    token = OAuthToken.objects.get(service=service)
    if token.is_expired():
        token = _refresh_token(token)
    return token.access_token


def _refresh_token(token: OAuthToken) -> OAuthToken:
    response = requests.post(
        settings.CRM_TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "client_id": settings.CRM_CLIENT_ID,
            "client_secret": settings.CRM_CLIENT_SECRET,
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    token.access_token = data["access_token"]
    token.refresh_token = data.get("refresh_token", token.refresh_token)
    token.expires_at = timezone.now() + timedelta(seconds=data["expires_in"])
    token.save(update_fields=["access_token", "refresh_token", "expires_at", "updated_at"])
    return token
