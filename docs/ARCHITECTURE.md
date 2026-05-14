# Architecture

## Overview

```
                        ┌─────────────────────────────────────────┐
                        │           Third-Party Integration Hub    │
                        │                                          │
  Stripe ──────────────▶│  /api/webhooks/stripe/   ──▶  Celery    │
  Twilio ──────────────▶│  /api/webhooks/twilio/   ──▶  Worker    │
                        │                                  │       │
  Client ──────────────▶│  /api/payments/intents/          │       │
  Client ──────────────▶│  /api/sms/send/                  ▼       │
  Client ──────────────▶│  /api/crm/sync/          PostgreSQL      │
                        │                                          │
                        │  Celery Beat ──▶ sync_crm_contacts       │
                        └─────────────────────────────────────────┘
                                    │              │
                                 Redis           PostgreSQL
                               (broker)         (results + DB)
```

## Apps

### `core`
- `TimeStampedModel` — UUID PK, created_at, updated_at abstract base
- `OAuthToken` — stores access/refresh tokens per service
- `oauth.py` — `get_valid_token(service)` auto-refreshes expired tokens

### `integrations.payments`
- Creates Stripe PaymentIntents via REST
- `PaymentTransaction` model tracks status
- Stripe webhook updates status via `handle_stripe_event`

### `integrations.sms`
- `send_sms_task` Celery task dispatches via Twilio API
- Twilio status callback webhook updates `SMSMessage.status`

### `integrations.crm`
- `CRMClient` wraps CRM REST API with OAuth bearer token
- `sync_crm_contacts` Celery task paginates and upserts `CRMContact` records
- Scheduled via django-celery-beat

### `integrations.webhooks`
- Inbound webhooks verified by signature (Stripe HMAC-SHA256)
- `WebhookEvent` persisted immediately, then processed async
- Retry with exponential backoff: `delay = backoff * 2^(retry_count - 1)`
- After `WEBHOOK_MAX_RETRIES` failures → `DeadLetterEvent` created

## Webhook Retry Flow

```
Inbound POST
    │
    ▼
Verify Signature ──fail──▶ 400
    │
    ▼
Save WebhookEvent (pending)
    │
    ▼
process_webhook_event.delay()
    │
    ▼
Run Handler
    ├── success ──▶ status=success
    └── failure ──▶ retry_count++
                    ├── retries < max ──▶ retry with backoff
                    └── retries >= max ──▶ DeadLetterEvent
```

## OAuth Token Refresh Flow

```
Request to CRM API
    │
    ▼
get_valid_token("crm")
    │
    ├── not expired ──▶ return access_token
    └── expired ──▶ POST /oauth/token (refresh_token grant)
                       │
                       ▼
                  Update OAuthToken
                       │
                       ▼
                  return new access_token
```
