import os
import re
from typing import Optional

from groq import APIConnectionError, APIStatusError


CLINIC_INFO = {
    "doctor_name": "Dr. Deepak Chandra Srivastava",
    "qualifications": "MBBS, MD (Medicine), F.I.N. (Nephrology)",
    "phone": "+91 9760901297",
    "email": "drdeepakchandrasrivastava@gmail.com",
    "address": (
        "Osborn Clinic, Nehru Complex, Shop No. 50, Near SBI Bank, "
        "Bargadwa Nakaha Road, Vikas Nagar, Gorakhpur 273007"
    ),
    "timings": "8:00 AM - 10:00 AM and 3:00 PM - 8:00 PM. Thursday closed.",
    "services": [
        "Consultation",
        "Dialysis Catheter Placement",
        "Central Line Insertion",
        "Renal Biopsy",
        "Lumbar Puncture",
        "Bone Marrow Biopsy",
    ],
    "map_url": "https://maps.app.goo.gl/rtrWqpUd5y4uEi2h8",
}


SYSTEM_PROMPT = (
    f"You are Osborn Saathi for Osborn Healthcare, Gorakhpur. "
    "You can answer two kinds of questions: "
    "1) clinic questions about Osborn Healthcare, and "
    "2) general educational health questions in simple language. "
    f"Doctor: {CLINIC_INFO['doctor_name']} ({CLINIC_INFO['qualifications']}). "
    f"Phone: {CLINIC_INFO['phone']}. Email: {CLINIC_INFO['email']}. "
    f"Address: {CLINIC_INFO['address']}. Timings: {CLINIC_INFO['timings']}. "
    f"Services: {', '.join(CLINIC_INFO['services'])}. "
    "For clinic facts, stay accurate and do not invent new facilities, timings, fees, equipment, or claims. "
    "For general health questions, give short educational information only. "
    "Do not diagnose, prescribe, interpret reports, or claim certainty about a user's condition. "
    "For urgent symptoms, advise immediate medical care. "
    "Keep replies under 90 words, use plain language, and end with a clinic handoff only when relevant."
)

MAX_USER_MESSAGE_CHARS = 500
MAX_HISTORY_ITEMS = 4
MAX_HISTORY_MESSAGE_CHARS = 280
MAX_AI_REPLY_CHARS = 700


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
    return ", ".join(CLINIC_INFO["services"])


def _truncate_text(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _compress_history(history: list[dict]) -> list[dict]:
    safe_history = []
    for item in history[-MAX_HISTORY_ITEMS:]:
        role = item.get("role")
        content = item.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            continue
        safe_history.append({
            "role": role,
            "content": _truncate_text(content, MAX_HISTORY_MESSAGE_CHARS),
        })
    return safe_history


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
            "or contact the clinic at "
            f"{CLINIC_INFO['phone']} right away. Osborn Saathi cannot provide emergency advice."
        )

    if _is_greeting(text):
        return (
            "Namaste, I am Osborn Saathi. I can help with clinic timings, services, doctor details, "
            "location, and booking appointments."
        )

    if any(_contains_phrase(text, keyword) for keyword in ["timing", "time", "open", "hours", "clinic timing"]):
        return f"Clinic timings are {CLINIC_INFO['timings']}"

    if any(_contains_phrase(text, keyword) for keyword in ["address", "location", "where", "map", "clinic address"]):
        return (
            f"The clinic address is {CLINIC_INFO['address']}. "
            f"You can also open the location here: {CLINIC_INFO['map_url']}"
        )

    if any(_contains_phrase(text, keyword) for keyword in ["phone", "call", "contact number", "mobile", "number"]):
        return (
            f"You can contact Osborn Clinic at {CLINIC_INFO['phone']} "
            f"or email {CLINIC_INFO['email']}."
        )

    if any(_contains_phrase(text, keyword) for keyword in ["email", "mail"]):
        return f"You can email the clinic at {CLINIC_INFO['email']}."

    if any(_contains_phrase(text, keyword) for keyword in ["doctor", "deepak", "qualification", "who is", "specialist"]):
        return (
            f"{CLINIC_INFO['doctor_name']} is a physician and kidney specialist in Gorakhpur. "
            f"Qualifications: {CLINIC_INFO['qualifications']}."
        )

    if any(_contains_phrase(text, keyword) for keyword in ["service", "procedure", "treatment", "what do you do"]):
        return f"Available services include: {_services_text()}."

    if any(_contains_phrase(text, keyword) for keyword in ["appointment", "book", "booking", "schedule", "visit"]):
        return (
            "You can book an appointment from the Book Appointment page by entering your name, "
            "email, preferred date, service, and any message. After submission, the clinic can "
            "review the request and contact you."
        )

    if any(_contains_phrase(text, keyword) for keyword in ["fee", "fees", "price", "cost", "charges"]):
        return (
            "Consultation fees are not currently listed on the website. Please contact the clinic at "
            f"{CLINIC_INFO['phone']} for the latest fee details."
        )

    if any(_contains_phrase(text, keyword) for keyword in ["thank you", "thanks"]):
        return "You are welcome. If you want, I can also help with timings, services, or booking steps."

    return None


def _groq_reply(history: list[dict], message: str) -> Optional[str]:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        return None
    from groq import Groq

    client = Groq(api_key=api_key)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(_compress_history(history))
    messages.append({"role": "user", "content": _truncate_text(message, MAX_USER_MESSAGE_CHARS)})

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_completion_tokens=180,
            top_p=1,
        )
    except APIStatusError as exc:
        if exc.status_code == 413:
            return "__PAYLOAD_TOO_LARGE__"
        return None
    except APIConnectionError:
        return None
    except Exception:
        return None

    reply = (completion.choices[0].message.content or "").strip() or None
    if not reply:
        return None
    return _truncate_text(reply, MAX_AI_REPLY_CHARS)


def get_saathi_reply(message: str, history: Optional[list[dict]] = None) -> str:
    history = history or []
    message = _truncate_text(message, MAX_USER_MESSAGE_CHARS)
    rule_reply = _rule_based_reply(message)
    if rule_reply:
        return rule_reply

    ai_reply = _groq_reply(history, message)
    if ai_reply == "__PAYLOAD_TOO_LARGE__":
        return (
            "This chat has become a bit long. Please ask a shorter question or refresh the page to start a new chat."
        )
    if ai_reply:
        return ai_reply

    return (
        "I can help with clinic information and simple general health guidance. "
        "For personal diagnosis or treatment advice, please speak with a doctor directly."
    )
