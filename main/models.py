from django.db import models
from django.utils.text import slugify

# Create your models here.


class Clinic(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    operating_hours = models.CharField(max_length=160, blank=True)
    services_offered = models.TextField(blank=True)
    offers_consultation = models.BooleanField(default=True)
    offers_pharmacy = models.BooleanField(default=False)
    offers_pathology = models.BooleanField(default=False)
    map_embed_url = models.URLField(max_length=1000, blank=True)
    google_maps_url = models.URLField(max_length=1000, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "clinic"
            slug = base_slug
            counter = 2
            while Clinic.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    SERVICE_CHOICES = [
        ('consultation', 'General Physician Consultation'),
        ('internal_medicine', 'Internal Medicine Consultation'),
        ('kidney_care', 'Kidney Disease & Nephrology Care'),
        ('hypertension', 'High Blood Pressure Treatment'),
        ('diabetes', 'Diabetes Management'),
        ('fever_infection', 'Fever & Infection Treatment'),
        ('thyroid_lifestyle', 'Thyroid & Lifestyle Disorders'),
        ('preventive_checkup', 'Preventive Health Checkup'),
        ('dialysis_counselling', 'Dialysis Counselling & Kidney Protection'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15)
    clinic = models.ForeignKey(Clinic, on_delete=models.PROTECT, related_name='appointments')
    preferred_date = models.DateField()
    service = models.CharField(max_length=32, choices=SERVICE_CHOICES, default='consultation')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending',
                            choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')])

    def __str__(self):
        return f"{self.name} - {self.service} on {self.preferred_date}"


class PharmacyOrder(models.Model):
    DELIVERY_CHOICES = [
        ('home_delivery', 'Home Delivery'),
        ('store_pickup', 'Store Pickup'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    delivery_mode = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='home_delivery')
    branch = models.ForeignKey(Clinic, on_delete=models.PROTECT, related_name='pharmacy_orders')
    delivery_address = models.TextField(blank=True)
    prescription_upload = models.FileField(upload_to='prescriptions/', blank=True)
    medicine_list = models.TextField(blank=True)
    preferred_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.get_delivery_mode_display()} on {self.preferred_date}"


class PathologyBooking(models.Model):
    COLLECTION_CHOICES = [
        ('home_collection', 'Home Collection'),
        ('lab_visit', 'Lab Visit'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('collected', 'Sample Collected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    selected_tests = models.TextField()
    collection_mode = models.CharField(max_length=20, choices=COLLECTION_CHOICES, default='home_collection')
    branch = models.ForeignKey(Clinic, on_delete=models.PROTECT, related_name='pathology_bookings')
    collection_address = models.TextField(blank=True)
    preferred_date = models.DateField()
    referral_doctor = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.get_collection_mode_display()} on {self.preferred_date}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']


class SaathiSettings(models.Model):
    name = models.CharField(max_length=80, default="Default", unique=True)
    ai_enabled = models.BooleanField(
        default=True,
        help_text="If enabled, unmatched questions can be sent to the configured AI provider.",
    )
    fallback_reply = models.TextField(
        default=(
            "I can help with clinic information and simple general health guidance. "
            "For personal diagnosis or treatment advice, please speak with a doctor directly."
        )
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Saathi Setting"
        verbose_name_plural = "Saathi Settings"

    def __str__(self):
        return self.name


class SaathiChatLog(models.Model):
    SOURCE_RULE = "rule"
    SOURCE_AI = "ai"
    SOURCE_FALLBACK = "fallback"
    SOURCE_AI_DISABLED = "ai_disabled"
    SOURCE_AI_NOT_CONFIGURED = "ai_not_configured"
    SOURCE_AI_ERROR = "ai_error"
    SOURCE_RATE_LIMIT = "rate_limit"
    SOURCE_CHOICES = [
        (SOURCE_RULE, "Internal rule"),
        (SOURCE_AI, "AI provider"),
        (SOURCE_FALLBACK, "Fallback"),
        (SOURCE_AI_DISABLED, "AI disabled fallback"),
        (SOURCE_AI_NOT_CONFIGURED, "AI not configured fallback"),
        (SOURCE_AI_ERROR, "AI error fallback"),
        (SOURCE_RATE_LIMIT, "Rate limited"),
    ]

    message = models.TextField()
    reply = models.TextField(blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    ai_model = models.CharField(max_length=80, blank=True)
    error_detail = models.TextField(blank=True)
    ip_address = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_source_display()} - {self.created_at:%Y-%m-%d %H:%M}"


class SiteErrorLog(models.Model):
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=12, blank=True)
    status_code = models.PositiveIntegerField(default=500)
    exception_type = models.CharField(max_length=160)
    message = models.TextField(blank=True)
    traceback = models.TextField(blank=True)
    user_label = models.CharField(max_length=160, blank=True)
    ip_address = models.CharField(max_length=64, blank=True)
    user_agent = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.exception_type} on {self.path}"
