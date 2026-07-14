from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Max, ProtectedError
from datetime import datetime

from .models import Patient, Doctor, Appointment

# Decorator to restrict view access to clinic staff/admin only
def staff_required(view_func):
    @login_required(login_url="login")
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Access denied. Clinic staff credentials required.")
            return redirect("patient_dashboard")
    return _wrapped_view

# Public landing page
def landing_page(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("dashboard")
        elif hasattr(request.user, "patient_profile"):
            return redirect("patient_dashboard")
    return render(request, "landing_page.html")

# Unified Login View
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("dashboard")
        elif hasattr(request.user, "patient_profile"):
            return redirect("patient_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, "login.html")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if user.is_staff:
                return redirect("dashboard")
            elif hasattr(user, "patient_profile"):
                return redirect("patient_dashboard")
            else:
                return redirect("landing_page")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")

# Logout View
def logout_view(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("landing_page")

# Patient Self-Registration View
def patient_register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("dashboard")
        elif hasattr(request.user, "patient_profile"):
            return redirect("patient_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        name = request.POST.get("name", "").strip().title()
        phone = request.POST.get("phone", "").strip()
        date_of_birth = request.POST.get("date_of_birth", "")
        gender = request.POST.get("gender", "")

        # Validation
        if not (username and password and name and phone and date_of_birth and gender):
            messages.error(request, "All fields are required.")
            return render(request, "register.html")

        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, "Phone number must be exactly 10 digits.")
            return render(request, "register.html")

        # Duplicate Checks
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, "register.html")

        if Patient.objects.filter(phone=phone).exists():
            messages.error(request, "A patient with this phone number already exists.")
            return render(request, "register.html")

        # Create user and profile
        user = User.objects.create_user(username=username, password=password)
        patient = Patient.objects.create(
            user=user,
            name=name,
            phone=phone,
            date_of_birth=date_of_birth,
            gender=gender
        )
        auth_login(request, user)
        messages.success(request, "Registration successful! Welcome to QueueCare.")
        return redirect("patient_dashboard")

    return render(request, "register.html")

# Clinic Staff Dashboard View
@staff_required
def dashboard_view(request):
    today = timezone.localdate()
    
    # Statistics queries
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.filter(is_active=True).count()
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    waiting_today = Appointment.objects.filter(appointment_date=today, status="W").count()
    in_progress_today = Appointment.objects.filter(appointment_date=today, status="IP").count()
    completed_today = Appointment.objects.filter(appointment_date=today, status="C").count()

    # Get recent appointments
    recent_appointments = Appointment.objects.all().order_by('-appointment_date', '-token_number')[:5]

    context = {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "today_appointments": today_appointments,
        "waiting_today": waiting_today,
        "in_progress_today": in_progress_today,
        "completed_today": completed_today,
        "recent_appointments": recent_appointments,
        "today": today
    }
    return render(request, "dashboard.html", context)

# Patient Dashboard View
@login_required(login_url="login")
def patient_dashboard_view(request):
    if request.user.is_staff:
        return redirect("dashboard")
        
    try:
        patient = request.user.patient_profile
    except Patient.DoesNotExist:
        messages.error(request, "No patient profile associated with this account.")
        return redirect("landing_page")

    # Find active appointment (Waiting or In Progress)
    active_appointment = Appointment.objects.filter(
        patient=patient,
        status__in=["W", "IP"]
    ).order_by('appointment_date', 'token_number').first()

    now_serving_token = None
    people_ahead = 0

    if active_appointment:
        # Get currently serving token for this doctor on the appointment date
        serving = Appointment.objects.filter(
            doctor=active_appointment.doctor,
            appointment_date=active_appointment.appointment_date,
            status="IP"
        ).first()
        if serving:
            now_serving_token = serving.token_number
            
        # Count patients ahead
        people_ahead = Appointment.objects.filter(
            doctor=active_appointment.doctor,
            appointment_date=active_appointment.appointment_date,
            status="W",
            token_number__lt=active_appointment.token_number
        ).count()

    # Fetch previous history
    history = Appointment.objects.filter(patient=patient).order_by('-appointment_date', '-token_number')
    if active_appointment:
        history = history.exclude(id=active_appointment.id)

    context = {
        "patient": patient,
        "active_appointment": active_appointment,
        "now_serving_token": now_serving_token,
        "people_ahead": people_ahead,
        "history": history
    }
    return render(request, "patient_dashboard.html", context)

# Patient Management: Add Patient
@staff_required
def add_patient(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip().title()
        phone = request.POST.get("phone", "").strip()   
        date_of_birth = request.POST.get("date_of_birth", "")
        gender = request.POST.get("gender", "")
        
        if not (name and phone and date_of_birth and gender):
            messages.error(request, "All fields are required.")
            return render(request, "add_patient.html")

        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, "Phone number must be exactly 10 digits.")
            return render(request, "add_patient.html")

        existing_patient = Patient.objects.filter(phone=phone)
        if existing_patient.exists():
            messages.error(request, "Patient with this phone number already exists.")
        else:
            patient = Patient(  
                name=name,
                phone=phone,
                date_of_birth=date_of_birth,
                gender=gender
            )
            patient.save()
            messages.success(request, f"Patient {name} added successfully.")
            return redirect("view_patient")

    return render(request, "add_patient.html")

# Patient Management: View Patients
@staff_required
def view_patient(request):
    patients = Patient.objects.all().order_by('name')
    return render(request, "view_patient.html", {"patients": patients})

# Patient Management: Edit Patient
@staff_required
def edit_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if request.method == "POST":
        name = request.POST.get("name", "").strip().title()
        phone = request.POST.get("phone", "").strip()   
        date_of_birth = request.POST.get("date_of_birth", "")
        gender = request.POST.get("gender", "")

        if not (name and phone and date_of_birth and gender):
            messages.error(request, "All fields are required.")
            return render(request, "edit_patient.html", {"patient": patient})

        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, "Phone number must be exactly 10 digits.")
            return render(request, "edit_patient.html", {"patient": patient})

        # Check if phone belongs to another patient
        if Patient.objects.filter(phone=phone).exclude(id=id).exists():
            messages.error(request, "Another patient with this phone number already exists.")
            return render(request, "edit_patient.html", {"patient": patient})

        patient.name = name
        patient.phone = phone
        patient.date_of_birth = date_of_birth
        patient.gender = gender
        patient.save()
        
        messages.success(request, f"Patient {name} updated successfully.")
        return redirect("view_patient")
        
    return render(request, "edit_patient.html", {"patient": patient})

# Patient Management: Delete Patient
@staff_required
def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if request.method == "POST":
        try:
            user = patient.user
            patient.delete()
            # Only clean up the linked User if Patient deletion succeeds
            if user:
                user.delete()
            messages.success(request, "Patient deleted successfully.")
        except ProtectedError:
            messages.error(request, "This patient cannot be deleted because appointment history is associated with them.")
    return redirect("view_patient")

# Doctor Management: View Doctors
@staff_required
def view_doctors(request):
    doctors = Doctor.objects.filter(is_active=True).order_by('name')
    past_doctors = Doctor.objects.filter(is_active=False).order_by('name')
    return render(request, "view_doctors.html", {"doctors": doctors, "past_doctors": past_doctors})

# Doctor Management: Add Doctor
@staff_required
def add_doctor(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip().title()
        specialization = request.POST.get("specialization", "").strip().title()
        experience_years = request.POST.get("experience_years", "")

        if not (name and specialization and experience_years):
            messages.error(request, "All fields are required.")
            return render(request, "add_doctor.html")

        try:
            exp_yrs = int(experience_years)
            if exp_yrs < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Experience years must be a valid positive number.")
            return render(request, "add_doctor.html")

        doctor = Doctor(
            name=name,
            specialization=specialization,
            experience_years=exp_yrs
        )
        doctor.save()
        messages.success(request, f"Doctor {name} added successfully.")
        return redirect("view_doctors")

    return render(request, "add_doctor.html")

# Doctor Management: Delete Doctor
@staff_required
def delete_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    if request.method == "POST":
        # Soft delete: mark as inactive to preserve historical appointment records
        doctor.is_active = False
        doctor.save()
        messages.success(request, f"Doctor {doctor.name} has been archived successfully.")
    return redirect("view_doctors")

# Appointment Booking & Token Generation
@staff_required
def book_appointment(request):
    patients = Patient.objects.all().order_by('name')
    doctors = Doctor.objects.filter(is_active=True).order_by('name')

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        date_str = request.POST.get("appointment_date")

        if not (patient_id and doctor_id and date_str):
            messages.error(request, "Please fill in all booking details.")
            return render(request, "book_appointment.html", {"patients": patients, "doctors": doctors})

        try:
            appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return render(request, "book_appointment.html", {"patients": patients, "doctors": doctors})

        # Ensure appointment is not in the past
        if appointment_date < timezone.localdate():
            messages.error(request, "Cannot book appointments in the past.")
            return render(request, "book_appointment.html", {"patients": patients, "doctors": doctors})

        patient = get_object_or_404(Patient, id=patient_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Duplicate validation: Check if patient has an active appointment with the same doctor on same date
        active_dup = Appointment.objects.filter(
            patient=patient,
            doctor=doctor,
            appointment_date=appointment_date,
            status__in=["W", "IP"]
        ).exists()

        if active_dup:
            messages.error(request, f"Patient {patient.name} already has an active appointment with {doctor.name} on {appointment_date}.")
            return render(request, "book_appointment.html", {"patients": patients, "doctors": doctors})

        # Token generation: Same doctor + Same appointment date
        max_token = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date
        ).aggregate(Max('token_number'))['token_number__max']

        token_number = 1 if max_token is None else max_token + 1

        # Create appointment
        appointment = Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            appointment_date=appointment_date,
            token_number=token_number,
            status="W"
        )
        
        messages.success(request, f"Appointment booked successfully! {patient.name} has been assigned Token #{token_number} for {doctor.name}.")
        return redirect("queue_view")

    return render(request, "book_appointment.html", {"patients": patients, "doctors": doctors})

# Live Queue View
@staff_required
def queue_view(request):
    doctors = Doctor.objects.filter(is_active=True).order_by('name')
    
    # Filter inputs
    doctor_id = request.GET.get("doctor_id")
    date_str = request.GET.get("date")

    selected_doctor = None
    if doctor_id:
        selected_doctor = get_object_or_404(Doctor, id=doctor_id)
    elif doctors.exists():
        selected_doctor = doctors.first()

    selected_date = timezone.localdate()
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    appointments = []
    currently_serving = None
    waiting_patients = []

    if selected_doctor:
        appointments = Appointment.objects.filter(
            doctor=selected_doctor,
            appointment_date=selected_date
        ).order_by('token_number')
        
        currently_serving = appointments.filter(status="IP").first()
        waiting_patients = appointments.filter(status="W")

    context = {
        "doctors": doctors,
        "selected_doctor": selected_doctor,
        "selected_date": selected_date,
        "appointments": appointments,
        "currently_serving": currently_serving,
        "waiting_patients": waiting_patients,
    }
    return render(request, "queue_view.html", context)

# Call Next Logic
@staff_required
def call_next(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    today = timezone.localdate()
    if request.method == "POST":
        # Verify if there is already an appointment In Progress for this doctor today
        active_ip = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=today,
            status="IP"
        ).exists()

        if active_ip:
            messages.warning(request, "Another patient is currently In Progress. Complete or cancel their appointment first.")
            return redirect(f"/queue/?doctor_id={doctor_id}&date={today}")

        # Find the first Waiting patient for today
        next_app = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=today,
            status="W"
        ).order_by('token_number').first()

        if not next_app:
            messages.warning(request, "No waiting patients in this queue.")
        else:
            next_app.status = "IP"
            next_app.save()
            messages.success(request, f"Called Token #{next_app.token_number}: {next_app.patient.name} to Consultation Room.")

    return redirect(f"/queue/?doctor_id={doctor_id}&date={today}")

# Complete Appointment
@staff_required
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == "POST":
        if appointment.status != "IP":
            messages.error(request, "Only appointments currently In Progress can be completed.")
        else:
            appointment.status = "C"
            appointment.save()
            messages.success(request, f"Appointment for {appointment.patient.name} completed successfully.")
    return redirect(f"/queue/?doctor_id={appointment.doctor.id}&date={appointment.appointment_date}")

# Cancel Appointment (Supports Staff cancelling or Patient cancelling their own active appointments)
@login_required(login_url="login")
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Authorization checks
    is_staff = request.user.is_staff
    is_owner = hasattr(request.user, "patient_profile") and appointment.patient == request.user.patient_profile
    
    if not (is_staff or is_owner):
        messages.error(request, "You are not authorized to cancel this appointment.")
        return redirect("landing_page")

    if request.method == "POST":
        # Business rule validation
        if appointment.status == "C":
            messages.error(request, "Cannot cancel an already completed appointment.")
        elif appointment.status == "X":
            messages.error(request, "This appointment is already cancelled.")
        else:
            appointment.status = "X"
            appointment.save()
            messages.success(request, "Appointment cancelled successfully.")

    if is_staff:
        return redirect(f"/queue/?doctor_id={appointment.doctor.id}&date={appointment.appointment_date}")
    else:
        return redirect("patient_dashboard")