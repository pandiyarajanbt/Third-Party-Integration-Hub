# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- PostgreSQL 16
- Redis 7
- AWS S3 bucket (for static/media files)
- Sentry project DSN

## Environment Variables

Copy `.env.example` to `.env` and fill in all values.  
Never commit `.env` to version control.

## Production Checklist

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` is a long random string (50+ chars)
- [ ] `ALLOWED_HOSTS` set to your domain(s)
- [ ] `STRIPE_WEBHOOK_SECRET` configured and Stripe endpoint registered
- [ ] `SENTRY_DSN` set for error tracking
- [ ] Database backups configured
- [ ] Redis persistence enabled (`appendonly yes`)
- [ ] HTTPS enforced (SSL termination at load balancer or nginx)

## Deploy Steps

```bash
# Build and start
docker-compose -f docker-compose.yml up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files (auto-runs in Dockerfile for production)
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## Celery Workers

The `docker-compose.yml` starts:
- `celery_worker` — processes webhook events, SMS sends
- `celery_beat` — triggers scheduled tasks (CRM sync)

To scale workers:
```bash
docker-compose up -d --scale celery_worker=3
```

## Scheduling CRM Sync

After first deploy, add a periodic task via Django Admin:
1. Go to `/admin/django_celery_beat/periodictask/`
2. Create task: `integrations.crm.tasks.sync_crm_contacts`
3. Set interval (e.g. every 1 hour)

## Monitoring

- **Sentry** — automatic exception capture in production
- **Django Admin** — view `WebhookEvent`, `DeadLetterEvent`, `CeleryTaskResult`
- **Celery Flower** (optional) — add to docker-compose for real-time task monitoring:

```yaml
flower:
  image: mher/flower
  command: celery --broker=redis://redis:6379/0 flower
  ports:
    - "5555:5555"
  depends_on:
    - redis
```

## Rolling Back

```bash
# Roll back last migration
docker-compose exec web python manage.py migrate <app_label> <previous_migration>
```

## Health Check

Add to your load balancer:
```
GET /api/docs/  →  200 OK
```
Or implement a dedicated `/health/` endpoint.
