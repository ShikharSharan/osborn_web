import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

from django.conf import settings


class IntegrationError(Exception):
    """Raised when a configured clinical integration cannot be reached."""


def _headers(content_type="application/json"):
    headers = {"Accept": "application/json", "Content-Type": content_type}
    if settings.PMS_API_TOKEN:
        headers["Authorization"] = f"Bearer {settings.PMS_API_TOKEN}"
    return headers


def _request(url, method="GET", payload=None, content_type="application/json"):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=_headers(content_type), method=method)
    try:
        with urllib.request.urlopen(request, timeout=settings.PMS_API_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as error:
        raise IntegrationError("The clinical system is unavailable.") from error


def _endpoint(path):
    return f"{settings.PMS_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"


def pms_is_configured():
    return bool(settings.PMS_API_BASE_URL and settings.PMS_API_TOKEN)


def get_available_slots(clinic, appointment_date, service):
    if not pms_is_configured():
        return None

    query = urllib.parse.urlencode({
        "clinic": clinic.slug,
        "date": appointment_date.isoformat(),
        "service": service,
    })
    response = _request(f"{_endpoint(settings.PMS_AVAILABILITY_PATH)}?{query}")
    return response.get("slots", [])


def build_fhir_transaction(appointment):
    patient = {
        "resourceType": "Patient",
        "identifier": [{"system": "https://osbornhealthcare.in/patient", "value": str(appointment.pk)}],
        "name": [{"text": appointment.name}],
        "telecom": [{"system": "phone", "value": appointment.phone, "use": "mobile"}],
    }
    if appointment.email:
        patient["telecom"].append({"system": "email", "value": appointment.email})

    appointment_resource = {
        "resourceType": "Appointment",
        "status": "proposed",
        "description": appointment.message or appointment.get_service_display(),
        "serviceType": [{"text": appointment.get_service_display()}],
        "start": f"{appointment.preferred_date.isoformat()}T{appointment.preferred_time}:00+05:30",
        "participant": [
            {"actor": {"reference": f"Location/{appointment.clinic.slug}", "display": appointment.clinic.name}, "status": "accepted"},
            {"actor": {"reference": f"Patient/{appointment.pk}", "display": appointment.name}, "status": "accepted"},
        ],
    }
    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": f"urn:uuid:patient-{appointment.pk}",
                "resource": patient,
                "request": {"method": "POST", "url": "Patient"},
            },
            {
                "fullUrl": f"urn:uuid:appointment-{appointment.pk}",
                "resource": appointment_resource,
                "request": {"method": "POST", "url": "Appointment"},
            },
        ],
    }


def build_hl7_orm_message(appointment, control_id=None):
    """Build an HL7 v2 ORM^O01 message for a downstream interface engine."""
    control_id = control_id or f"OSB-{appointment.pk}"
    timestamp = appointment.created_at.strftime("%Y%m%d%H%M%S%z")
    segments = [
        f"MSH|^~\\&|OSBORN|OSBORN|PMS|PMS|{timestamp}||ORM^O01|{control_id}|P|2.5",
        f"PID|||{appointment.pk}||{appointment.name}||{appointment.preferred_date.strftime('%Y%m%d')}|",
        f"ORC|NW|{control_id}||||||||{timestamp}",
        f"OBR|1|{control_id}||{appointment.get_service_display()}|||{appointment.preferred_date.strftime('%Y%m%d')}"
        f"{appointment.preferred_time.strftime('%H%M%S')}||||||||||||||||||||||||||",
    ]
    return "\r".join(segments) + "\r"


def book_with_pms(appointment):
    if not pms_is_configured():
        return None

    response = _request(
        _endpoint(settings.PMS_BOOKING_PATH),
        method="POST",
        payload={
            "appointment": {
                "clinic": appointment.clinic.slug,
                "date": appointment.preferred_date.isoformat(),
                "time": appointment.preferred_time,
                "service": appointment.service,
                "name": appointment.name,
                "phone": appointment.phone,
                "email": appointment.email,
                "slot_id": appointment.slot_id,
            },
            "fhir_bundle": build_fhir_transaction(appointment),
        },
    )
    return {
        "external_id": response.get("id") or response.get("appointment_id", ""),
        "meeting_url": response.get("meeting_url", ""),
    }
