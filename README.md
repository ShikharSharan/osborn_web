# Osborn Healthcare Django Site

This project is now structured as a Django website for Osborn Healthcare.

## Features

- **Appointment Booking**: Patients can book appointments online with form validation
- **Contact Form**: Visitors can send messages through the contact page
- **Admin Panel**: Manage appointments and contact messages
- **Responsive Design**: Mobile-friendly interface
- **SEO Optimized**: Meta tags and proper HTML structure
- **Clinical integrations**: Environment-configured PMS availability and booking adapter with FHIR R4 and HL7 v2 payload builders
- **Telemedicine readiness**: Stores secure HTTPS meeting links returned by the PMS for confirmed appointments

## Run locally

1. Install dependencies:
   `python3 -m pip install -r requirements.txt`
2. Run migrations:
   `python3 manage.py migrate`
3. Create superuser (optional, for admin access):
   `python3 manage.py createsuperuser`
4. Start the server:
   `python3 manage.py runserver`

## Admin Access

- URL: `/admin/`
- Default credentials: admin / admin123 (change in production!)

## Environment Variables

Create a `.env` file in the project root with:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=openai/gpt-oss-120b
PMS_API_BASE_URL=https://pms.example.com
PMS_API_TOKEN=replace-with-a-secret-token
PMS_API_TIMEOUT=8
PMS_AVAILABILITY_PATH=/api/appointments/availability
PMS_BOOKING_PATH=/api/appointments/book
# Production defaults to hashed static files when DEBUG=False.
USE_MANIFEST_STATICFILES=True
```

When `PMS_API_BASE_URL` and `PMS_API_TOKEN` are set, the appointment page requests live slots and submits bookings to the configured PMS adapter. The booking request includes a FHIR R4 transaction Bundle; `build_hl7_orm_message()` provides an HL7 v2 ORM^O01 message for deployments that connect through an interface engine. Without PMS settings, requests remain available through the existing local workflow.

For production static delivery, run `python3 manage.py collectstatic` with `USE_MANIFEST_STATICFILES=True`, then serve `staticfiles/` through a CDN or web server with long-lived caching for hashed files.
