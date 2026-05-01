import importlib.util
import datetime as dt
import pathlib
import sys
import unittest


SCRIPT_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "send_daily_offer_email.py"
SPEC = importlib.util.spec_from_file_location("send_daily_offer_email", SCRIPT_PATH)
send_daily_offer_email = importlib.util.module_from_spec(SPEC)
sys.modules["send_daily_offer_email"] = send_daily_offer_email
assert SPEC.loader is not None
SPEC.loader.exec_module(send_daily_offer_email)


class DailyOfferEmailTests(unittest.TestCase):
    def test_filters_exact_date_and_date_range(self):
        offers = list(
            map(
                send_daily_offer_email.Offer.from_dict,
                [
                    {"model": "gpt-5.5-high", "offer": "100%", "date": "2026-05-01"},
                    {"model": "gpt-5.5-high", "offer": "50%", "date": "2026-05-02"},
                    {
                        "model": "gpt-5.5-pro",
                        "offer": "25%",
                        "start_date": "2026-05-01",
                        "end_date": "2026-05-03",
                    },
                ],
            )
        )

        result = send_daily_offer_email.active_offers_for_day(offers, dt.date(2026, 5, 2))

        self.assertEqual(
            [offer.offer for offer in result],
            ["50%", "25%"],
        )

    def test_build_email_includes_available_offers(self):
        offers = [
            send_daily_offer_email.Offer.from_dict(
                {
                    "model": "gpt-5.5-high",
                    "offer": "50%",
                    "date": "2026-05-02",
                    "description": "Tomorrow half-price offer",
                }
            )
        ]

        message = send_daily_offer_email.build_message(
            sender="offers@example.com",
            recipients=["user@example.com"],
            subject_prefix="[Cursor Offers]",
            offers=offers,
            day=dt.date(2026, 5, 2),
        )

        body = message.get_content()
        self.assertEqual(
            message["Subject"],
            "[Cursor Offers] 2026-05-02 - gpt-5.5-high 50%",
        )
        self.assertIn("gpt-5.5-high: 50%", body)
        self.assertIn("Tomorrow half-price offer", body)

    def test_build_email_handles_no_offers(self):
        message = send_daily_offer_email.build_message(
            sender="offers@example.com",
            recipients=["user@example.com"],
            subject_prefix="[Cursor Offers]",
            offers=[],
            day=dt.date(2026, 5, 3),
        )

        self.assertEqual(message["Subject"], "[Cursor Offers] 2026-05-03 - no offers configured")
        self.assertIn("No model offers are configured", message.get_content())

    def test_rejects_invalid_schedule_shape(self):
        with self.assertRaisesRegex(ValueError, "must provide both start_date and end_date"):
            send_daily_offer_email.Offer.from_dict(
                {
                    "model": "gpt-5.5-high",
                    "offer": "50%",
                    "start_date": "2026-05-01",
                }
            )


if __name__ == "__main__":
    unittest.main()
