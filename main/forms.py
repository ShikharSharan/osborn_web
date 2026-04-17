from django import forms
from datetime import date
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['name', 'email', 'phone', 'preferred_date', 'service', 'message']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Any additional information or concerns...'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Optional: +91 XXXXX XXXXX'}),
        }
        labels = {
            'preferred_date': 'Preferred Date',
            'phone': 'Phone Number (Optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preferred_date'].widget.attrs['min'] = date.today().isoformat()

from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Please describe your inquiry...'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Optional: +91 XXXXX XXXXX'}),
        }
        labels = {
            'phone': 'Phone Number (Optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
