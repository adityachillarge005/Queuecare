# 🏥 QueueCare - Clinic Queue & Appointment Management System

QueueCare is a digital appointment and queue management system designed for clinics and hospitals. It digitizes the patient consultation flow, manages doctor specialty queues, schedules visits, and provides live status updates to patients via automated daily token numbering.

---

## 🚀 Key Features

### 1. Administration & Clinic Staff Console
* **Protected Dashboard**: Displays real-time operational metrics: total registered patients, active doctors, today's appointments, waiting counts, serving numbers, and completed consults.
* **Patient Directory (CRUD)**: Register new patients, edit medical profiles, search patient details, and safely delete records (with database deletion protection).
* **Doctor Registry**: Add new doctors, specialty departments, and experience logs.
* **Smart Appointment Booking**: Dropdown-based interface to select patient and doctor, select date, and automatically calculate wait tokens.
* **Live Queue Console**: Allows staff to call the next waiting patient, transition consultations to "In Progress", complete visits, or cancel appointments.

### 2. Patient Self-Service Portal
* **Account Registration & Login**: Unified login portal. Patients can self-register a user profile.
* **Live Token Status Card**: Displays their token number, the token currently being called, and the count of patients ahead in the queue.
* **Consultation History**: Lists all past completed and cancelled visits, including department specializations.
* **Patient Cancellations**: Permits patients to cancel their own active appointments directly from the dashboard.

### 3. Smart Token Generation
* **Per-Doctor, Per-Day Scope**: Tokens are completely independent for each doctor. Each doctor has a separate queue starting from Token #1 every new calendar day.
* **Automatic Incrementing**: System calculates the maximum existing token for the doctor on that day and assigns `max_token + 1`.

---

## 🛠️ Technology Stack

* **Backend**: Django (Python 3.13)
* **Database**: SQLite3
* **Frontend**: Django Templates, HTML5, CSS3, Bootstrap 5, Bootstrap Icons
* **Authentication**: Django Built-in Auth System (Sessions, Password Hashing, Decorators)

---

## 📂 Project Structure

```text
Queuecare/
│
├── core/                       # Django App Directory
│   ├── migrations/             # Database Migrations
│   ├── templates/              # HTML Templates (MVT Views)
│   │   ├── add_doctor.html
│   │   ├── add_patient.html
│   │   ├── base.html           # Baseline styling & layout
│   │   ├── book_appointment.html
│   │   ├── dashboard.html      # Staff control dashboard
│   │   ├── edit_patient.html
│   │   ├── landing_page.html   # SaaS hero landing page
│   │   ├── login.html          # Portal login
│   │   ├── patient_dashboard.html
│   │   ├── queue_view.html     # Live queue management console
│   │   ├── register.html       # Patient registration
│   │   ├── view_doctors.html
│   │   └── view_patient.html   # Patient directory
│   │
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Doctor, Patient, Appointment Models
│   ├── urls.py                 # Core routing patterns
│   └── views.py                # Business logic views
│
├── queuecare/                  # Project Settings Directory
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL patterns
│   └── wsgi.py / asgi.py
│
├── manage.py                   # Django management utility
└── db.sqlite3                  # Local SQLite database
```

---

## 💻 Local Setup & Execution

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/adityachillarge005/Queuecare.git
cd Queuecare
```

### 3. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install django
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Admin / Clinic Staff User
To create an administrative account to log in to the Clinic Console:
```bash
python manage.py createsuperuser
```
Follow the prompts to enter a username, email, and password.

### 7. Run the Server
```bash
python manage.py runserver
```

Open your browser and visit: `http://127.0.0.1:8000/`

---

## 🔒 Security Features Implemented

* **CSRF Protection**: All state-changing forms include Django's CSRF token check to prevent cross-site request forgery.
* **Password Hashing**: User passwords are saved securely using Django's PBKDF2 algorithm.
* **Access Control**: Administrative views are protected with the custom `@staff_required` decorator, ensuring only authorized staff can manage queues.
* **ORM Safety**: Queries are made via Django ORM QuerySets, protecting the application against SQL Injection.
* **Cascade Deletion Prevention**: ForeignKeys use `on_delete=models.PROTECT` to prevent accidental loss of patient historical data. Deletion attempts show friendly error alerts instead of server crashes.

---

## 🔮 Future Improvements

1. **Concurrency Control**: Use database-level locks (e.g., PostgreSQL `select_for_update`) or transactions to handle high-frequency bookings.
2. **Real-time Notifications**: Integrate WebSockets (Django Channels) or server-sent events to update queues instantly without refreshing.
3. **SMS Alerts**: Notify patients when they are next in line (e.g. 2 patients ahead).
