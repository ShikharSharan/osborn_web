from django.db import models

# Create your models here.

class Appointment(models.Model):
    SERVICE_CHOICES = [
        ('consultation', 'Consultation'),
        ('dialysis_cat', 'Dialysis Catheter Placement'),
        ('central_line', 'Central Line Insertion'),
        ('renal_biopsy', 'Renal Biopsy'),
        ('lumbar_punct', 'Lumbar Puncture'),
        ('bone_marrow', 'Bone Marrow Biopsy'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    preferred_date = models.DateField()
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='consultation')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending',
                            choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')])

    def __str__(self):
        return f"{self.name} - {self.service} on {self.preferred_date}"

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
