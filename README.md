# Third-Party Integration Hub

A centralised Django service connecting **Stripe** (payments), **Twilio** (SMS), and a **CRM platform** — with OAuth token refresh, webhook ingestion, and async task processing via **Celery + Redis**.

## Features

- **Payment Gateway** — Create Stripe payment intents; status updates via signed webhooks
- **SMS API** — Async SMS dispatch via Twilio with delivery status tracking
- **CRM Sync** — OAuth2 token refresh + paginated contact sync via Celery Beat
- **Webhook Ingestion** — Signature-verified inbound webhooks with exponential-backoff retry and dead-letter queue
- **Async Tasks** — Celery workers + Redis broker; persistent results in PostgreSQL

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2 + DRF |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis 7 |
| Task Queue | Celery 5 + django-celery-beat |
| API Docs | drf-spectacular (Swagger) |
| Monitoring | Sentry |
| Container | Docker + Docker Compose |

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your credentials

# 2. Start all services
docker-compose up --build

# 3. Run migrations
docker-compose exec web python manage.py migrate

# 4. Create superuser
docker-compose exec web python manage.py createsuperuser
```

API docs available at: `http://localhost:8000/api/docs/`

## Project Structure

```
├── config/                  # Django project config
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── development.py
│   │   └── production.py
│   ├── celery.py
│   └── urls.py
├── core/                    # Shared models (OAuthToken, TimeStampedModel)
│   └── oauth.py             # Token refresh logic
├── integrations/
│   ├── payments/            # Stripe integration
│   ├── sms/                 # Twilio integration
│   ├── crm/                 # CRM OAuth + sync
│   └── webhooks/            # Ingestion, retry, dead-letter
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
└── docker-compose.yml
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
