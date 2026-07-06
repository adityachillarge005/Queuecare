from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Patient

# Create your views here.
def home(request):
    return render(
        request,
        "home.html"
)

def add_patient(request):
    if request.method == "POST":
        name = request.POST["name"].strip().title()
        phone = request.POST["phone"]   
        date_of_birth = request.POST["date_of_birth"]
        gender = request.POST["gender"]
        
        existing_patient = Patient.objects.filter(phone=phone)
        if existing_patient.exists():
            messages.error(request, "Patient already exists")
        else:
            patient = Patient(  
            name = name,
            phone = phone,
            date_of_birth = date_of_birth,
            gender =gender
            )
            patient.save()
        return redirect("/add-patient/")

    return render(request,"add_patient.html")

def view_patient(request):
    patients = Patient.objects.all()
    return render(request,
                  "view_patient.html",
                  {
                    "patients" : patients
                  }
    )

def edit_patient(request,id):
    patient = Patient.objects.get(id=id)
    if(request.method == "POST"):
        patient.name = request.POST["name"].strip().title()
        patient.phone = request.POST["phone"]   
        patient.date_of_birth = request.POST["date_of_birth"]
        patient.gender = request.POST["gender"]

        patient.save()
        return redirect("/view-patients/")
    return render(request,
                  "edit_patient.html",
                  {
                  "patient" : patient
                  }
    )

def delete_patient(request,id):
    patient = Patient.objects.get(id=id)
    if(request.method == "POST"):
        patient.delete()
        return redirect("view_patient")
    
    return redirect("view_patient")
    