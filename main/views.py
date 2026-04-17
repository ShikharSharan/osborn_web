from django.shortcuts import render


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


def home(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def providers(request):
    return render(request, "providers.html")


def appointment(request):
    submitted = request.method == "POST"
    appointment_data = {
        "name": request.POST.get("name", "").strip(),
        "email": request.POST.get("email", "").strip(),
        "date": request.POST.get("date", "").strip(),
        "service": request.POST.get("service", "").strip(),
    }
    return render(
        request,
        "appointment.html",
        {
            "submitted": submitted,
            "appointment_data": appointment_data,
        },
    )


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
