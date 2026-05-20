import os
import re
import logging
from typing import Optional

from groq import APIConnectionError, APIStatusError


logger = logging.getLogger(__name__)

DEFAULT_CLINIC_INFO = {
    "doctor_name": "Dr. Deepak Chandra Srivastava",
    "qualifications": "MBBS, MD (Medicine), Fellowship in Nephrology",
    "phone": "+91 9760901297",
    "email": "drdeepakchandrasrivastava@gmail.com",
    "address": (
        "Osborn Clinic, Nehru Complex, Shop No. 50, Near SBI Bank, "
        "Bargadwa Nakaha Road, Vikas Nagar, Gorakhpur 273007"
    ),
    "timings": "8:00 AM - 10:00 AM and 3:00 PM - 8:00 PM. Thursday closed.",
    "services": [
        "Internal Medicine",
        "Kidney Disease & Nephrology Care",
        "Hypertension Treatment",
        "Diabetes Management",
        "Fever & Infection Treatment",
        "Thyroid & Lifestyle Disorders",
        "Chronic Disease Care",
        "Preventive Health Checkups",
        "Pharmacy Order",
        "Pathology Booking",
        "Home Collection",
    ],
    "map_url": "https://maps.app.goo.gl/rtrWqpUd5y4uEi2h8",
}


MAX_USER_MESSAGE_CHARS = 500
MAX_AI_REPLY_CHARS = 700
PAYLOAD_TOO_LARGE_REPLY = (
    "This chat has become a bit long. Please ask a shorter question or refresh the page to start a new chat."
)
STABLE_GROQ_MODEL = "llama-3.3-70b-versatile"


def _normalize(message: str) -> str:
    return " ".join(message.lower().split())


def _contains_phrase(text: str, phrase: str) -> bool:
    pattern = r"\b" + re.escape(phrase.lower()) + r"\b"
    return re.search(pattern, text) is not None


def _is_greeting(text: str) -> bool:
    compact = text.strip(" .,!?\n\t")
    greetings = {
        "hi",
        "hello",
        "hey",
        "namaste",
        "hi saathi",
        "hello saathi",
        "hey saathi",
    }
    return compact in greetings


def _services_text() -> str:
    clinic_services = []
    for clinic in _active_clinics():
        if clinic.services_offered:
            clinic_services.append(clinic.services_offered)
    if clinic_services:
        return "; ".join(clinic_services)
    return ", ".join(DEFAULT_CLINIC_INFO["services"])


def _active_clinics():
    try:
        from .models import Clinic

        return list(Clinic.objects.filter(is_active=True).order_by("sort_order", "name"))
    except Exception:
        return []


def _clinic_context_text() -> str:
    clinics = _active_clinics()
    if not clinics:
        return (
            f"Location: {DEFAULT_CLINIC_INFO['address']}. "
            f"Phone: {DEFAULT_CLINIC_INFO['phone']}. Email: {DEFAULT_CLINIC_INFO['email']}. "
            f"Timings: {DEFAULT_CLINIC_INFO['timings']}. Map: {DEFAULT_CLINIC_INFO['map_url']}. "
            f"Services: {', '.join(DEFAULT_CLINIC_INFO['services'])}."
        )

    details = []
    for clinic in clinics:
        services = _clinic_services_label(clinic)

        details.append(
            f"{clinic.name}: address {clinic.address}; phone {clinic.phone}; "
            f"alternate phone {clinic.alternate_phone or 'not listed'}; "
            f"email {clinic.email or 'not listed'}; hours {clinic.operating_hours or 'not listed'}; "
            f"services {services}; map {clinic.google_maps_url or 'not listed'}"
        )
    return "Locations: " + " | ".join(details)


def _system_prompt() -> str:
    return (
        "You are Osborn Saathi for Osborn Healthcare, Gorakhpur. "
        "You can answer two kinds of questions: "
        "1) clinic questions about Osborn Healthcare, and "
        "2) general educational health questions in simple language. "
        f"Doctor: {DEFAULT_CLINIC_INFO['doctor_name']} ({DEFAULT_CLINIC_INFO['qualifications']}). "
        "Core care areas: Internal Medicine, Kidney Care, Hypertension, Diabetes, chronic disease management, and Preventive Healthcare. "
        f"{_clinic_context_text()} "
        "For clinic facts, stay accurate and do not invent new facilities, timings, fees, equipment, or claims. "
        "For general health questions, give short educational information only. "
        "Do not diagnose, prescribe, interpret reports, or claim certainty about a user's condition. "
        "This is a single-turn assistant; answer only the current message and do not imply saved chat memory. "
        "For urgent symptoms, advise immediate medical care. "
        "Keep replies under 90 words, use plain language, and end with a clinic handoff only when relevant."
    )


def _clinic_services_label(clinic) -> str:
    if clinic.services_offered:
        return clinic.services_offered

    service_flags = []
    if clinic.offers_consultation:
        service_flags.append("Doctor Consultation")
    if clinic.offers_pharmacy:
        service_flags.append("Pharmacy")
    if clinic.offers_pathology:
        service_flags.append("Pathology")
    return ", ".join(service_flags) or "Clinic services"


def _clinics_for_service(flag_name: str):
    return [clinic for clinic in _active_clinics() if getattr(clinic, flag_name, False)]


def _service_locations_text(flag_name: str, service_label: str) -> str:
    clinics = _clinics_for_service(flag_name)
    if not clinics:
        return f"{service_label} branch details are not listed yet. Please contact {_clinic_contacts_text()}."
    return "; ".join(
        f"{clinic.name}: {clinic.phone}"
        + (f", {clinic.alternate_phone}" if clinic.alternate_phone else "")
        + (f", {clinic.address}" if clinic.address else "")
        for clinic in clinics
    )


def _clinic_contacts_text() -> str:
    clinics = _active_clinics()
    if not clinics:
        return f"{DEFAULT_CLINIC_INFO['phone']} or email {DEFAULT_CLINIC_INFO['email']}"
    return "; ".join(
        f"{clinic.name}: {clinic.phone}"
        + (f", {clinic.alternate_phone}" if clinic.alternate_phone else "")
        + (f", {clinic.email}" if clinic.email else "")
        for clinic in clinics
    )


def _clinic_locations_text() -> str:
    clinics = _active_clinics()
    if not clinics:
        return f"{DEFAULT_CLINIC_INFO['address']}. Map: {DEFAULT_CLINIC_INFO['map_url']}"
    return "; ".join(
        f"{clinic.name}: {clinic.address}"
        + (f". Map: {clinic.google_maps_url}" if clinic.google_maps_url else "")
        for clinic in clinics
    )


def _clinic_timings_text() -> str:
    clinics = _active_clinics()
    if not clinics:
        return DEFAULT_CLINIC_INFO["timings"]
    timing_lines = []
    for clinic in clinics:
        timing_lines.append(f"{clinic.name}: {clinic.operating_hours or 'timings not listed'}")
    return "; ".join(timing_lines)


def _clinic_services_by_location_text() -> str:
    clinics = _active_clinics()
    if not clinics:
        return ", ".join(DEFAULT_CLINIC_INFO["services"])
    return "; ".join(
        f"{clinic.name}: {_clinic_services_label(clinic)}"
        for clinic in clinics
    )


def _truncate_text(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _has_urgent_symptom(text: str) -> bool:
    urgent_phrases = [
        "emergency",
        "urgent",
        "chest pain",
        "pain in chest",
        "pain chest",
        "chest tightness",
        "tightness in chest",
        "breathing problem",
        "breathlessness",
        "shortness of breath",
        "can't breathe",
        "cant breathe",
        "heavy bleeding",
        "bleeding",
        "seizure",
        "unconscious",
        "stroke",
        "heart attack",
    ]
    if any(_contains_phrase(text, phrase) for phrase in urgent_phrases):
        return True

    pain_terms = ["pain", "severe pain"]
    critical_body_terms = ["chest", "breath", "breathing", "heart"]
    return any(_contains_phrase(text, pain) for pain in pain_terms) and any(
        _contains_phrase(text, body) for body in critical_body_terms
    )


def _rule_based_reply(message: str) -> Optional[str]:
    text = _normalize(message)

    if _has_urgent_symptom(text):
        return (
            "If this feels urgent or includes symptoms like chest pain, breathing trouble, "
            "heavy bleeding, seizure, or severe weakness, please seek immediate medical care "
            f"or contact the clinic at {_clinic_contacts_text()} right away. "
            "Osborn Saathi cannot provide emergency advice."
        )

    if _is_greeting(text):
        return (
            "Namaste, I am Osborn Saathi. I can help with clinic timings, services, doctor details, "
            "locations, appointments, pharmacy, pathology, kidney care, hypertension, diabetes, and preventive checkups. "
            "I answer one question at a time."
        )

    if any(_contains_phrase(text, keyword) for keyword in ["timing", "timings", "time", "open", "hours", "clinic timing", "clinic timings"]):
        return f"Clinic timings are: {_clinic_timings_text()}"

    if any(_contains_phrase(text, keyword) for keyword in ["address", "location", "where", "map", "clinic address"]):
        return f"Our clinic locations are: {_clinic_locations_text()}."

    if any(_contains_phrase(text, keyword) for keyword in ["phone", "call", "contact number", "mobile", "number"]):
        return f"You can contact Osborn Healthcare at {_clinic_contacts_text()}."

    if any(_contains_phrase(text, keyword) for keyword in ["email", "mail"]):
        return f"Clinic email details are: {_clinic_contacts_text()}."

    if any(_contains_phrase(text, keyword) for keyword in ["pharmacy", "medicine", "medicines", "prescription"]):
        return (
            "For pharmacy orders, use the Pharmacy Order form and choose a branch. "
            f"Available pharmacy branches: {_service_locations_text('offers_pharmacy', 'Pharmacy')}"
        )

    if any(_contains_phrase(text, keyword) for keyword in ["pathology", "lab", "test", "tests", "blood test", "home collection"]):
        return (
            "For pathology bookings, use the Pathology Booking form and choose home collection or lab visit. "
            f"Available lab branches: {_service_locations_text('offers_pathology', 'Pathology')}"
        )

    if any(
        _contains_phrase(text, keyword)
        for keyword in [
            "kidney",
            "nephrology",
            "hypertension",
            "blood pressure",
            "diabetes",
            "thyroid",
            "preventive",
            "checkup",
            "chronic disease",
            "ckd",
            "creatinine",
            "proteinuria",
        ]
    ):
        return (
            "Osborn Healthcare supports Internal Medicine, Kidney Disease & Nephrology Care, "
            "Hypertension Treatment, Diabetes Management, Thyroid & Lifestyle Disorders, "
            "chronic disease care, and Preventive Health Checkups. Please book an appointment "
            "for personalized evaluation."
        )

    if any(_contains_phrase(text, keyword) for keyword in ["doctor", "deepak", "qualification", "who is", "specialist"]):
        return (
            f"{DEFAULT_CLINIC_INFO['doctor_name']} provides Internal Medicine, Kidney Care, Hypertension, Diabetes, and Preventive Healthcare support in Gorakhpur. "
            f"Qualifications: {DEFAULT_CLINIC_INFO['qualifications']}."
        )

    if any(_contains_phrase(text, keyword) for keyword in ["service", "services", "procedure", "procedures", "treatment", "treatments", "what do you do"]):
        return f"Available services by location: {_clinic_services_by_location_text()}."

    if any(_contains_phrase(text, keyword) for keyword in ["appointment", "book", "booking", "schedule", "visit"]):
        return (
            "Use Book Appointment for doctor visits, Pharmacy for medicine delivery or pickup, "
            "and Pathology for lab tests or home collection. Choose your preferred branch in the form. "
            "Phone is required and email is optional. "
            "The clinic team will review the request and contact you."
        )

    if any(_contains_phrase(text, keyword) for keyword in ["fee", "fees", "price", "cost", "charges"]):
        return (
            "Consultation fees are not currently listed on the website. Please contact the clinic at "
            f"{_clinic_contacts_text()} for the latest fee details."
        )

    if any(_contains_phrase(text, keyword) for keyword in ["thank you", "thanks"]):
        return "You are welcome. If you want, I can also help with timings, services, or booking steps."

    return None


def _call_groq_model(client, model: str, message: str) -> Optional[str]:
    messages = [
        {"role": "system", "content": _system_prompt()},
        {"role": "user", "content": _truncate_text(message, MAX_USER_MESSAGE_CHARS)},
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_completion_tokens=180,
        top_p=1,
    )
    reply = (completion.choices[0].message.content or "").strip() or None
    if not reply:
        return None
    return _truncate_text(reply, MAX_AI_REPLY_CHARS)


def _groq_reply(message: str) -> Optional[str]:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", STABLE_GROQ_MODEL)
    if not api_key:
        logger.info("Groq API key is not configured; using Saathi fallback response.")
        return None
    from groq import Groq

    client = Groq(api_key=api_key)

    try:
        return _call_groq_model(client, model, message)
    except APIStatusError as exc:
        logger.warning(
            "Groq API status error in Saathi.",
            extra={"status_code": exc.status_code, "model": model},
        )
        if exc.status_code == 413:
            try:
                if model != STABLE_GROQ_MODEL:
                    return _call_groq_model(client, STABLE_GROQ_MODEL, message)
            except APIStatusError as fallback_exc:
                logger.warning(
                    "Groq fallback model returned a status error in Saathi.",
                    extra={"status_code": fallback_exc.status_code, "model": STABLE_GROQ_MODEL},
                )
                if fallback_exc.status_code == 413:
                    return "__PAYLOAD_TOO_LARGE__"
                return None
            except APIConnectionError:
                logger.warning(
                    "Groq fallback model connection error in Saathi.",
                    extra={"model": STABLE_GROQ_MODEL},
                )
                return None
            except Exception:
                logger.exception(
                    "Unexpected Groq fallback error in Saathi.",
                    extra={"model": STABLE_GROQ_MODEL},
                )
                return None
            return "__PAYLOAD_TOO_LARGE__"
        return None
    except APIConnectionError:
        logger.warning("Groq API connection error in Saathi.", extra={"model": model})
        return None
    except Exception:
        logger.exception("Unexpected Groq API error in Saathi.", extra={"model": model})
        return None


def get_saathi_reply(message: str) -> str:
    message = _truncate_text(message, MAX_USER_MESSAGE_CHARS)
    rule_reply = _rule_based_reply(message)
    if rule_reply:
        return rule_reply

    ai_reply = _groq_reply(message)
    if ai_reply == "__PAYLOAD_TOO_LARGE__":
        return PAYLOAD_TOO_LARGE_REPLY
    if ai_reply:
        return ai_reply

    return (
        "I can help with clinic information and simple general health guidance. "
        "For personal diagnosis or treatment advice, please speak with a doctor directly."
    )
