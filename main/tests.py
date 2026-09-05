import json
from datetime import date, time
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .integrations import build_fhir_transaction
from .models import Appointment, Clinic
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


class ClinicalIntegrationTests(TestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name="Integration Clinic",
            slug="integration-clinic",
            address="Gorakhpur",
            phone="+91 9760901297",
            offers_consultation=True,
        )

    def test_availability_endpoint_reports_unconfigured_pms(self):
        response = self.client.get(reverse("appointment_availability"), {
            "clinic": self.clinic.slug,
            "date": "2026-09-14",
            "service": "consultation",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"configured": False, "slots": []})

    @override_settings(PMS_API_BASE_URL="https://pms.example.test", PMS_API_TOKEN="test-token")
    @patch("main.views.get_available_slots", return_value=[{"id": "slot-1", "time": "10:30"}])
    def test_availability_endpoint_returns_pms_slots(self, get_slots):
        response = self.client.get(reverse("appointment_availability"), {
            "clinic": self.clinic.slug,
            "date": "2026-09-14",
            "service": "consultation",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["slots"][0]["id"], "slot-1")
        get_slots.assert_called_once()

    def test_fhir_transaction_contains_patient_and_appointment(self):
        appointment = Appointment.objects.create(
            name="Test Patient",
            phone="+919760901297",
            email="patient@example.com",
            clinic=self.clinic,
            preferred_date=date(2026, 9, 14),
            preferred_time=time(10, 30),
            service="consultation",
        )

        bundle = build_fhir_transaction(appointment)

        self.assertEqual(bundle["resourceType"], "Bundle")
        self.assertEqual(bundle["type"], "transaction")
        self.assertEqual(bundle["entry"][0]["resource"]["resourceType"], "Patient")
        self.assertEqual(bundle["entry"][1]["resource"]["resourceType"], "Appointment")
