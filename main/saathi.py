import os
import re
from typing import Optional


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


SYSTEM_PROMPT = f"""
You are Osborn Saathi, the website assistant for Osborn Healthcare in Gorakhpur.
You help visitors with clinic information, doctor details, services, address, timings,
appointments, and website navigation.

Important rules:
- You are not a doctor and must not diagnose diseases.
- You must not prescribe medicines, dosages, or treatment plans.
- For urgent symptoms, chest pain, breathing trouble, heavy bleeding, confusion, seizure,
  or severe weakness, advise the user to seek immediate medical attention or contact the clinic right away.
- Keep replies concise, friendly, and practical.
- Prefer clinic facts over generic medical explanation.

Clinic facts:
- Doctor: {CLINIC_INFO["doctor_name"]}
- Qualifications: {CLINIC_INFO["qualifications"]}
- Phone: {CLINIC_INFO["phone"]}
- Email: {CLINIC_INFO["email"]}
- Address: {CLINIC_INFO["address"]}
- Timings: {CLINIC_INFO["timings"]}
- Services: {", ".join(CLINIC_INFO["services"])}
""".strip()


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


def _rule_based_reply(message: str) -> Optional[str]:
    text = _normalize(message)

    urgent_keywords = [
        "emergency",
        "urgent",
        "chest pain",
        "breathing problem",
        "breathlessness",
        "can't breathe",
        "cant breathe",
        "bleeding",
        "seizure",
        "unconscious",
        "severe pain",
        "stroke",
        "heart attack",
    ]
    if any(_contains_phrase(text, keyword) for keyword in urgent_keywords):
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

    try:
        from groq import Groq
    except Exception:
        return None

    client = Groq(api_key=api_key)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": message})

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_completion_tokens=350,
            top_p=1,
        )
    except Exception:
        return None

    return (completion.choices[0].message.content or "").strip() or None


def get_saathi_reply(message: str, history: Optional[list[dict]] = None) -> str:
    history = history or []
    rule_reply = _rule_based_reply(message)
    if rule_reply:
        return rule_reply

    ai_reply = _groq_reply(history, message)
    if ai_reply:
        return ai_reply

    return (
        "I can help with clinic timings, doctor details, services, location, and appointment guidance. "
        f"For anything specific, please contact Osborn Clinic at {CLINIC_INFO['phone']}."
    )
