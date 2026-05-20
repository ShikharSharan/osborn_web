import json

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import AppointmentForm, ContactForm, PathologyBookingForm, PharmacyOrderForm
from .models import Clinic
from .saathi import PAYLOAD_TOO_LARGE_REPLY, get_saathi_reply


BLOG_POSTS = {
    "healthy-eating": {
        "title": "Healthy Eating for a Better Life",
        "summary": "Simple food habits that support energy, immunity, and long-term wellness.",
        "content": [
            "A balanced plate with vegetables, fruits, protein, whole grains, and enough water goes a long way.",
            "Try to keep highly processed foods, extra sugar, and excessive salt to a minimum during the week.",
            "If you have kidney, diabetes, or blood pressure concerns, ask your doctor for a personalized nutrition plan.",
        ],
    },
    "stress-management": {
        "title": "Stress Management Techniques",
        "summary": "Practical ways to reduce daily stress and protect your mental and physical health.",
        "content": [
            "Short daily walks, deep breathing, and better sleep routines can lower stress significantly.",
            "Break large problems into smaller next steps and stay connected with people you trust.",
            "If stress is affecting work, sleep, or relationships, a medical consultation can help identify the right support.",
        ],
    },
    "preventive-care": {
        "title": "Importance of Preventive Care",
        "summary": "Preventive checkups help detect risk early and keep small problems from becoming bigger ones.",
        "content": [
            "Routine blood pressure checks, blood sugar screening, and age-appropriate testing can catch issues early.",
            "Vaccinations, follow-up appointments, and healthy lifestyle habits are part of preventive care too.",
            "Preventive care is most effective when it happens regularly rather than only during illness.",
        ],
    },
}

PATIENT_REVIEWS = [
    {
        "name": "Chandan Mahto",
        "meta": "1 review",
        "time": "4 months ago",
        "text": "Bahut acche doctor hai. mjhe fever ki wajah se kidney ki paresani thi sath me pilia hua tha, abhi thik hai, puri recovery ho gyi. Doctor sahab Gorakhpur ke best doctor hain.",
    },
    {
        "name": "Pankaj Ravan",
        "meta": "1 review",
        "time": "2 months ago",
        "text": "Dr. Deepak Chandra Shrivastava ek bahut hi acche aur humble doctor hain. Meri problems ko dhyan se suna aur clearly samjhaya. Treatment se mujhe thik kiya.",
    },
    {
        "name": "Dheeraj Kumar",
        "meta": "1 review",
        "time": "2 months ago",
        "text": "Dr Deepak ji bahut acche doctor hain. Inhone meri pareshaniyon ko samjha aur ek achha treatment kiya.",
    },
    {
        "name": "Alok Mishra",
        "meta": "1 review",
        "time": "6 months ago",
        "text": "Doctor sahab ki prashansa shabdon se nahi kiya ja sakta hai. Kyunki jo bhi vyakti ek bar unse milega usko swayam anubhav ho jayega.",
    },
    {
        "name": "Anant Ranjan",
        "meta": "2 reviews",
        "time": "2 months ago",
        "text": "This is a very good facility, the patient got cured from here. Patient name - Asha Devi.",
    },
    {
        "name": "Sagar Singh",
        "meta": "15 reviews · 3 photos",
        "time": "A year ago",
        "text": "Best doctor in my knowledge... great behaviour and staff also very good in nature.",
    },
]

SAATHI_RATE_LIMIT = 20
SAATHI_RATE_WINDOW_SECONDS = 60


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _is_saathi_rate_limited(request):
    identifier = request.session.session_key or _client_ip(request)
    cache_key = f"saathi_rate:{identifier}"
    request_count = cache.get(cache_key, 0) + 1
    cache.set(cache_key, request_count, SAATHI_RATE_WINDOW_SECONDS)
    return request_count > SAATHI_RATE_LIMIT


def home(request):
    clinics = Clinic.objects.filter(is_active=True)
    return render(request, "index.html", {"patient_reviews": PATIENT_REVIEWS, "clinics": clinics})


def about(request):
    return render(request, "about.html")


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request,
                f"Thank you, {contact.name}! Your message has been received. We'll get back to you at {contact.email} within 24 hours.")
            return redirect('contact')
    else:
        form = ContactForm()

    clinics = Clinic.objects.filter(is_active=True)
    return render(request, 'contact.html', {'form': form, 'clinics': clinics})


def providers(request):
    return render(request, "providers.html")


def appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request,
                f"Thank you, {appointment.name}! Your appointment request for {appointment.get_service_display()} "
                f"at {appointment.clinic.name} "
                f"on {appointment.preferred_date} has been received. We'll contact you soon at {appointment.phone}.")
            return redirect('appointment')
    else:
        initial = {}
        clinic_slug = request.GET.get('clinic')
        if clinic_slug:
            clinic = Clinic.objects.filter(
                slug=clinic_slug,
                is_active=True,
                offers_consultation=True,
            ).first()
            if clinic:
                initial['clinic'] = clinic
        form = AppointmentForm(initial=initial)

    return render(request, 'appointment.html', {'form': form})


def pharmacy(request):
    clinics = Clinic.objects.filter(is_active=True, offers_pharmacy=True)
    
    if request.method == 'POST':
        form = PharmacyOrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save()
            messages.success(
                request,
                f"Thank you, {order.name}! Your pharmacy request for {order.get_delivery_mode_display()} "
                f"has been received. We'll contact you soon at {order.phone}.",
            )
            return redirect('pharmacy')
    else:
        form = PharmacyOrderForm()
    
    return render(request, "pharmacy.html", {"clinics": clinics, "form": form})


def pharmacy_order(request):
    if request.method == 'POST':
        form = PharmacyOrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save()
            messages.success(
                request,
                f"Thank you, {order.name}! Your pharmacy request for {order.get_delivery_mode_display()} "
                f"has been received. We'll contact you soon at {order.phone}.",
            )
            return redirect('pharmacy_order')
    else:
        form = PharmacyOrderForm()

    return render(request, 'pharmacy_order.html', {'form': form})


def pathology(request):
    clinics = Clinic.objects.filter(is_active=True, offers_pathology=True)
    return render(request, "pathology.html", {"clinics": clinics})


def pathology_booking(request):
    if request.method == 'POST':
        form = PathologyBookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(
                request,
                f"Thank you, {booking.patient_name}! Your pathology booking for "
                f"{booking.get_collection_mode_display()} has been received. "
                f"We'll contact you soon at {booking.phone}.",
            )
            return redirect('pathology_booking')
    else:
        form = PathologyBookingForm()

    return render(request, 'pathology_booking.html', {'form': form})


def faq(request):
    return render(request, "faq.html")


def resources(request):
    return render(request, "resource.html", {"posts": BLOG_POSTS})


def blog(request):
    return render(request, "blog.html", {"posts": BLOG_POSTS})


def blog_detail(request, slug):
    post = BLOG_POSTS.get(slug)
    if not post:
        return render(request, "blog_detail.html", {"post": None, "slug": slug}, status=404)
    return render(request, "blog_detail.html", {"post": post, "slug": slug})


@require_POST
def saathi_chat(request):
    if _is_saathi_rate_limited(request):
        return JsonResponse(
            {
                "error": (
                    "Too many Saathi messages in a short time. "
                    "Please wait a minute and try again."
                )
            },
            status=429,
        )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    reply = get_saathi_reply(message)
    if reply == PAYLOAD_TOO_LARGE_REPLY:
        return JsonResponse({"reply": reply, "reset": True})
    return JsonResponse({"reply": reply})
