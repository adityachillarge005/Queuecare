# 🏥 QueueCare

QueueCare is a Hospital Queue and Appointment Management System built with Django. The project is aimed at digitizing the workflow of hospitals by managing patients, doctors, appointments, and consultation queues through a single web application.

The idea behind this project is to replace manual patient record management with an organized system that allows hospitals to efficiently manage appointments and reduce waiting time.

---

## Features

### Patient Management
- Add new patients
- View patient records
- Edit patient information
- Delete patient records
- Prevent duplicate patient registration using phone number

### Doctor Management
- Manage doctor information
- Store doctor specialization
- Assign doctors to appointments

### Appointment Management
- Schedule appointments
- Assign patients to doctors
- Track appointment details
- Maintain appointment history

### Queue Management *(In Progress)*
- Queue generation
- Live queue status
- Consultation status
- Completed appointments

### Authentication *(Planned)*
- Admin login
- Doctor login
- Patient login
- Role-based access

### Dashboard *(Planned)*
- Total patients
- Total doctors
- Total appointments
- Today's appointments
- Queue statistics

---

## Tech Stack

- Python
- Django
- SQLite
- HTML
- CSS
- Bootstrap *(In Progress)*
- Django ORM

---

## Database Design

The application currently consists of three main models:

- Patient
- Doctor
- Appointment

Relationships:

- One patient can have multiple appointments.
- One doctor can have multiple appointments.
- Each appointment is associated with one patient and one doctor.

The project uses Django ORM with Foreign Keys to maintain relationships and data integrity.

---

## Concepts Used

- Django MVT Architecture
- CRUD Operations
- Django ORM
- Foreign Keys
- Reverse Relationships
- URL Routing
- Template Rendering
- Form Handling
- CSRF Protection
- QuerySets
- Django Admin

---

## Future Improvements

- Search and filter patients
- Dashboard with analytics
- JWT Authentication
- Django REST Framework APIs
- Email and SMS notifications
- Medical history management
- Responsive UI with Bootstrap
- Docker deployment

---

## Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/QueueCare.git
```

Create a virtual environment

```bash
python -m venv myenv
```

Activate it

**Windows**

```bash
myenv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Apply migrations

```bash
python manage.py migrate
```

Run the server

```bash
python manage.py runserver
```

Open your browser and visit:

```
http://127.0.0.1:8000/
```

---

## Project Status

This project is currently under development. I am continuously adding new features such as authentication, queue management, dashboards, search functionality, and REST APIs while learning more about Django and backend development.
