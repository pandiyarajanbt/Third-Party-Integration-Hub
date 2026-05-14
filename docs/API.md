# API Reference

Interactive docs: `GET /api/docs/`  
OpenAPI schema: `GET /api/schema/`

---

## Payments

### Create Payment Intent
`POST /api/payments/intents/`

**Request**
```json
{ "amount": 2000, "currency": "usd", "email": "user@example.com" }
```
`amount` is in cents (2000 = $20.00).

**Response `201`**
```json
{
  "client_secret": "pi_xxx_secret_xxx",
  "transaction": {
    "id": "uuid",
    "stripe_payment_intent_id": "pi_xxx",
    "amount": "20.00",
    "currency": "usd",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### List Transactions
`GET /api/payments/transactions/`

Returns last 50 transactions ordered by newest first.

---

## SMS

### Send SMS
`POST /api/sms/send/`

**Request**
```json
{ "to": "+14155552671", "body": "Your OTP is 123456" }
```

**Response `202`**
```json
{ "id": "uuid", "status": "queued" }
```

---

## CRM

### List Contacts
`GET /api/crm/contacts/`

Returns last 100 synced contacts.

### Trigger Sync
`POST /api/crm/sync/`

**Response `202`**
```json
{ "task_id": "celery-task-uuid", "status": "sync started" }
```

---

## Webhooks (Inbound)

These endpoints are public (`AllowAny`) and verified by signature.

### Stripe Webhook
`POST /api/webhooks/stripe/`

Header: `Stripe-Signature: t=...,v1=...`

### Twilio Status Callback
`POST /api/webhooks/twilio/`

Standard Twilio status callback POST body.

---

## Dead-Letter Events

Accessible via Django Admin at `/admin/webhooks/deadletterevent/`.  
Set `resolved=True` once manually handled.
