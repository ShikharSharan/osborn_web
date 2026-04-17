from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AppointmentForm, ContactForm


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


def home(request):
    return render(request, "index.html", {"patient_reviews": PATIENT_REVIEWS})


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

    return render(request, 'contact.html', {'form': form})


def providers(request):
    return render(request, "providers.html")


def appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request,
                f"Thank you, {appointment.name}! Your appointment request for {appointment.get_service_display()} "
                f"on {appointment.preferred_date} has been received. We'll contact you soon at {appointment.email}.")
            return redirect('appointment')
    else:
        form = AppointmentForm()

    return render(request, 'appointment.html', {'form': form})


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
