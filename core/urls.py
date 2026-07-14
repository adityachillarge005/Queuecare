from django.urls import path
from . import views

urlpatterns = [
    # Landing & Authentication
    path("", views.landing_page, name="landing_page"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.patient_register_view, name="register"),

    # Dashboards
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("patient/dashboard/", views.patient_dashboard_view, name="patient_dashboard"),

    # Patient CRUD (Preserved paths and names)
    path("add-patient/", views.add_patient, name="add_patient"),
    path("view-patients/", views.view_patient, name="view_patient"),
    path("edit-patient/<int:id>/", views.edit_patient, name="edit_patient"),
    path("delete-patient/<int:id>/", views.delete_patient, name="delete_patient"),

    # Doctor Management
    path("doctors/", views.view_doctors, name="view_doctors"),
    path("doctors/add/", views.add_doctor, name="add_doctor"),
    path("doctors/delete/<int:id>/", views.delete_doctor, name="delete_doctor"),

    # Appointment Booking
    path("appointments/book/", views.book_appointment, name="book_appointment"),

    # Live Queue View and Controls
    path("queue/", views.queue_view, name="queue_view"),
    path("queue/call-next/<int:doctor_id>/", views.call_next, name="call_next"),
    path("queue/complete/<int:appointment_id>/", views.complete_appointment, name="complete_appointment"),
    path("queue/cancel/<int:appointment_id>/", views.cancel_appointment, name="cancel_appointment"),
]