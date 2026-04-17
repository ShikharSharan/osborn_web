# Osborn Healthcare Django Site

This project is now structured as a Django website for Osborn Healthcare.

## Features

- **Appointment Booking**: Patients can book appointments online with form validation
- **Contact Form**: Visitors can send messages through the contact page
- **Admin Panel**: Manage appointments and contact messages
- **Responsive Design**: Mobile-friendly interface
- **SEO Optimized**: Meta tags and proper HTML structure

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
```
