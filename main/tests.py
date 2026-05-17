import json

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Clinic
from .saathi import get_saathi_reply


class SaathiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.clinic = Clinic.objects.create(
            name="Osborn Clinic - Bargadwa",
            slug="osborn-bargadwa-test",
            address="Nehru Complex, Bargadwa, Gorakhpur",
            phone="+91 9760901297",
            email="clinic@example.com",
            operating_hours="8:00 AM - 10:00 AM and 3:00 PM - 8:00 PM",
            services_offered="Internal Medicine, Kidney Disease & Nephrology Care, Hypertension Treatment, Diabetes Management, Preventive Health Checkups",
            offers_consultation=True,
            offers_pharmacy=True,
            offers_pathology=True,
        )

    def test_saathi_answers_common_intents_without_ai_fallback(self):
        self.assertIn("8:00 AM", get_saathi_reply("What are the clinic timings?"))
        self.assertIn("Internal Medicine", get_saathi_reply("What services are available?"))
        self.assertIn("Available pharmacy branches", get_saathi_reply("How do I order medicines from the pharmacy?"))
        self.assertIn("Available lab branches", get_saathi_reply("How do I book pathology tests?"))

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "saathi-rate-limit-test",
            }
        }
    )
    def test_saathi_chat_rate_limits_repeated_requests(self):
        cache.clear()
        url = reverse("saathi_chat")
        statuses = [
            self.client.post(
                url,
                data=json.dumps({"message": "hi"}),
                content_type="application/json",
            ).status_code
            for _ in range(22)
        ]

        self.assertEqual(statuses[:20], [200] * 20)
        self.assertEqual(statuses[20:], [429, 429])
