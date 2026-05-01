# Daily Model Offer Email Scheduler

This repository contains a small scheduler that checks which model offers are
available today and emails them to configured recipients.

## Configure offers

Edit `config/offers.json`.

```json
[
  {
    "model": "gpt-5.5-high",
    "offer": "100%",
    "date": "2026-05-01",
    "description": "Launch-day full credit offer"
  },
  {
    "model": "gpt-5.5-high",
    "offer": "50%",
    "date": "2026-05-02",
    "description": "Tomorrow's half-price offer"
  }
]
```

Each offer can use either:

- `date`: send only on that exact day.
- `start_date` and `end_date`: send on every day in that inclusive range.

`offer` is free text, so values like `50%`, `100%`, `Buy 1 get 1`, or any
other campaign label are supported.

## Configure email

The scheduler uses SMTP settings from environment variables:

| Variable | Required | Example |
| --- | --- | --- |
| `SMTP_HOST` | Yes | `smtp.gmail.com` |
| `SMTP_PORT` | No | `587` |
| `SMTP_USERNAME` | Yes | `alerts@example.com` |
| `SMTP_PASSWORD` | Yes | app password / SMTP password |
| `EMAIL_FROM` | No | `Cursor Offers <alerts@example.com>` |
| `EMAIL_TO` | Yes | `user@example.com,team@example.com` |
| `EMAIL_SUBJECT_PREFIX` | No | `[Cursor Offers]` |
| `SCHEDULER_TIMEZONE` | No | `UTC` |

## Run manually

Preview today's email without sending:

```bash
python3 scripts/send_daily_offer_email.py --dry-run
```

Preview a specific date:

```bash
python3 scripts/send_daily_offer_email.py --date 2026-05-02 --dry-run
```

Send email:

```bash
python3 scripts/send_daily_offer_email.py
```

## Run every day

`.github/workflows/daily-offer-email.yml` runs once per day using GitHub
Actions. Add the SMTP values above as repository secrets or environment
variables before enabling the workflow.
