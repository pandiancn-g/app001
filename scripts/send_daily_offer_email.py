#!/usr/bin/env python3
"""Send a daily email with the model offers available for a given date."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import smtplib
import ssl
import sys
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo


DEFAULT_OFFERS_FILE = Path(__file__).resolve().parents[1] / "config" / "offers.json"


@dataclass(frozen=True)
class Offer:
    model: str
    offer: str
    description: str
    date: dt.date | None = None
    start_date: dt.date | None = None
    end_date: dt.date | None = None

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Offer":
        model = data.get("model", "").strip()
        offer = data.get("offer", "").strip()
        description = data.get("description", "").strip()

        if not model:
            raise ValueError("Offer is missing required field: model")
        if not offer:
            raise ValueError(f"Offer for {model} is missing required field: offer")

        date = parse_date(data["date"]) if data.get("date") else None
        start_date = parse_date(data["start_date"]) if data.get("start_date") else None
        end_date = parse_date(data["end_date"]) if data.get("end_date") else None

        if date and (start_date or end_date):
            raise ValueError(f"Offer for {model} cannot combine date with start_date/end_date")
        if bool(start_date) != bool(end_date):
            raise ValueError(f"Offer for {model} must provide both start_date and end_date")
        if start_date and end_date and start_date > end_date:
            raise ValueError(f"Offer for {model} has start_date after end_date")
        if not date and not start_date:
            raise ValueError(f"Offer for {model} must provide date or start_date/end_date")

        return cls(
            model=model,
            offer=offer,
            description=description,
            date=date,
            start_date=start_date,
            end_date=end_date,
        )

    def is_active_on(self, day: dt.date) -> bool:
        if self.date:
            return self.date == day
        assert self.start_date is not None
        assert self.end_date is not None
        return self.start_date <= day <= self.end_date


def parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def get_today(timezone_name: str) -> dt.date:
    return dt.datetime.now(ZoneInfo(timezone_name)).date()


def load_offers(path: Path) -> list[Offer]:
    with path.open(encoding="utf-8") as file:
        raw_offers = json.load(file)

    if not isinstance(raw_offers, list):
        raise ValueError(f"{path} must contain a JSON array of offers")

    return [Offer.from_dict(offer) for offer in raw_offers]


def active_offers_for_day(offers: list[Offer], day: dt.date) -> list[Offer]:
    return [offer for offer in offers if offer.is_active_on(day)]


def build_email_body(offers: list[Offer], day: dt.date) -> str:
    if not offers:
        return (
            f"No model offers are configured for {day.isoformat()}.\n\n"
            "Update config/offers.json to add today's offer before the scheduler runs."
        )

    lines = [
        f"Model offers available on {day.isoformat()}:",
        "",
    ]

    for offer in offers:
        lines.append(f"- {offer.model}: {offer.offer}")
        if offer.description:
            lines.append(f"  {offer.description}")

    return "\n".join(lines)


def build_message(
    *,
    sender: str,
    recipients: list[str],
    subject_prefix: str,
    offers: list[Offer],
    day: dt.date,
) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(recipients)

    if offers:
        subject_offer = ", ".join(f"{offer.model} {offer.offer}" for offer in offers)
        message["Subject"] = f"{subject_prefix} {day.isoformat()} - {subject_offer}"
    else:
        message["Subject"] = f"{subject_prefix} {day.isoformat()} - no offers configured"

    message.set_content(build_email_body(offers, day))
    return message


def send_message(message: EmailMessage, recipients: list[str]) -> None:
    host = require_env("SMTP_HOST")
    username = require_env("SMTP_USERNAME")
    password = require_env("SMTP_PASSWORD")
    port = int(os.getenv("SMTP_PORT") or "587")

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        server.login(username, password)
        server.send_message(message, to_addrs=recipients)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def parse_recipients(value: str) -> list[str]:
    recipients = [recipient.strip() for recipient in value.split(",") if recipient.strip()]
    if not recipients:
        raise RuntimeError("EMAIL_TO must include at least one recipient")
    return recipients


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="Date to check, in YYYY-MM-DD format")
    parser.add_argument(
        "--offers-file",
        default=str(DEFAULT_OFFERS_FILE),
        help="Path to offers JSON configuration",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the email instead of sending it")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    timezone_name = os.getenv("SCHEDULER_TIMEZONE", "UTC")
    day = parse_date(args.date) if args.date else get_today(timezone_name)
    offers = active_offers_for_day(load_offers(Path(args.offers_file)), day)

    email_to = os.getenv("EMAIL_TO")
    if not email_to and args.dry_run:
        email_to = "dry-run@example.com"
    recipients = parse_recipients(email_to or "")
    sender = os.getenv("EMAIL_FROM") or os.getenv("SMTP_USERNAME") or "offers@example.com"
    subject_prefix = os.getenv("EMAIL_SUBJECT_PREFIX", "[Cursor Offers]")
    message = build_message(
        sender=sender,
        recipients=recipients,
        subject_prefix=subject_prefix,
        offers=offers,
        day=day,
    )

    if args.dry_run:
        print(message)
        return 0

    send_message(message, recipients)
    print(f"Sent {len(offers)} offer(s) for {day.isoformat()} to {', '.join(recipients)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
