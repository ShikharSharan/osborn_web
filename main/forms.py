from django import forms
from datetime import date
from .models import Appointment, Clinic, Contact, PathologyBooking, PharmacyOrder

class AppointmentForm(forms.ModelForm):
    clinic = forms.ModelChoiceField(
        queryset=Clinic.objects.none(),
        empty_label="Select Clinic",
        label="Clinic Branch",
    )

    class Meta:
        model = Appointment
        fields = ['name', 'phone', 'email', 'clinic', 'preferred_date', 'service', 'message']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Any additional information or concerns...'}),
            'phone': forms.TextInput(attrs={'placeholder': '+91 XXXXX XXXXX'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Optional: name@example.com'}),
        }
        labels = {
            'preferred_date': 'Preferred Date',
            'phone': 'Phone Number',
            'email': 'Email (Optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['clinic'].queryset = Clinic.objects.filter(
            is_active=True,
            offers_consultation=True,
        )
        self.fields['preferred_date'].widget.attrs['min'] = date.today().isoformat()
        self.fields['phone'].required = True
        self.fields['email'].required = False

class PharmacyOrderForm(forms.ModelForm):
    branch = forms.ModelChoiceField(
        queryset=Clinic.objects.none(),
        empty_label="Select Branch",
        label="Pickup / Delivery Branch",
    )

    class Meta:
        model = PharmacyOrder
        fields = [
            'name',
            'phone',
            'email',
            'delivery_mode',
            'branch',
            'delivery_address',
            'prescription_upload',
            'medicine_list',
            'preferred_date',
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Optional: name@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+91 XXXXX XXXXX'}),
            'delivery_address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'House number, street, landmark, city, and pincode',
                'data-conditional-field': 'pharmacy-address',
            }),
            'medicine_list': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'List medicines, quantities, or any instructions...',
            }),
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'prescription_upload': forms.ClearableFileInput(attrs={'accept': 'image/*,.pdf'}),
        }
        labels = {
            'email': 'Email (Optional)',
            'delivery_mode': 'Delivery Option',
            'branch': 'Pickup / Delivery Branch',
            'delivery_address': 'Delivery Address',
            'prescription_upload': 'Prescription Upload',
            'medicine_list': 'Medicine List / Notes',
            'preferred_date': 'Preferred Date',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preferred_date'].widget.attrs['min'] = date.today().isoformat()
        self.fields['email'].required = False
        self.fields['branch'].queryset = Clinic.objects.filter(
            is_active=True,
            offers_pharmacy=True,
        )
        self.fields['delivery_address'].required = False
        self.fields['prescription_upload'].required = False
        self.fields['medicine_list'].required = False

    def clean(self):
        cleaned_data = super().clean()
        delivery_mode = cleaned_data.get('delivery_mode')
        delivery_address = cleaned_data.get('delivery_address')
        prescription_upload = cleaned_data.get('prescription_upload')
        medicine_list = cleaned_data.get('medicine_list')

        if delivery_mode == 'home_delivery' and not delivery_address:
            self.add_error('delivery_address', 'Delivery address is required for home delivery.')
        if not prescription_upload and not medicine_list:
            self.add_error('medicine_list', 'Add medicine details or upload a prescription.')
        return cleaned_data


class PathologyBookingForm(forms.ModelForm):
    branch = forms.ModelChoiceField(
        queryset=Clinic.objects.none(),
        empty_label="Select Lab Branch",
        label="Lab Branch",
    )

    TEST_CHOICES = [
        ('cbc', 'Complete Blood Count (CBC)'),
        ('kidney_function', 'Kidney Function Test (KFT)'),
        ('liver_function', 'Liver Function Test (LFT)'),
        ('blood_sugar', 'Blood Sugar'),
        ('thyroid_profile', 'Thyroid Profile'),
        ('lipid_profile', 'Lipid Profile'),
        ('urine_routine', 'Urine Routine'),
        ('vitamin_d', 'Vitamin D'),
    ]

    selected_tests = forms.MultipleChoiceField(
        choices=TEST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Select Tests',
    )

    class Meta:
        model = PathologyBooking
        fields = [
            'patient_name',
            'phone',
            'email',
            'selected_tests',
            'collection_mode',
            'branch',
            'collection_address',
            'preferred_date',
            'referral_doctor',
            'notes',
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Optional: name@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+91 XXXXX XXXXX'}),
            'collection_address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'House number, street, landmark, city, and pincode',
                'data-conditional-field': 'pathology-address',
            }),
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'referral_doctor': forms.TextInput(attrs={'placeholder': 'Optional: referring doctor name'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Fasting status, symptoms, or special instructions...'}),
        }
        labels = {
            'patient_name': 'Patient Name',
            'email': 'Email (Optional)',
            'collection_mode': 'Collection Mode',
            'branch': 'Lab Branch',
            'collection_address': 'Home Collection Address',
            'preferred_date': 'Preferred Date',
            'referral_doctor': 'Referral Doctor (Optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preferred_date'].widget.attrs['min'] = date.today().isoformat()
        self.fields['email'].required = False
        self.fields['branch'].queryset = Clinic.objects.filter(
            is_active=True,
            offers_pathology=True,
        )
        self.fields['collection_address'].required = False
        self.fields['notes'].required = False

    def clean(self):
        cleaned_data = super().clean()
        collection_mode = cleaned_data.get('collection_mode')
        collection_address = cleaned_data.get('collection_address')

        if collection_mode == 'home_collection' and not collection_address:
            self.add_error('collection_address', 'Address is required for home collection.')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.selected_tests = ', '.join(self.cleaned_data['selected_tests'])
        if commit:
            instance.save()
        return instance

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
