from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
    path("providers", views.providers, name="providers"),
    path("appointment", views.appointment, name="appointment"),
    path("faq", views.faq, name="faq"),
    path("resources", views.resources, name="resources"),
    path("blog", views.blog, name="blog"),
    path("blog/<slug:slug>", views.blog_detail, name="blog_detail"),
    path("api/saathi-chat", views.saathi_chat, name="saathi_chat"),
]
