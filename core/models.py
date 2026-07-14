from django.db import models
from django.contrib.auth.models import User

# Create your models here.
STATUS_CHOICES = [
             ("W","Waiting"),
             ("IP","In Progress"),
             ("C","Completed"),
             ("X","Cancelled")
]


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length = 100)
    experience_years = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="patient_profile")
    name = models.CharField(max_length=100)
    phone= models.CharField(max_length=10)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    def __str__(self):
        return self.name
    


class Appointment(models.Model):
    doctor = models.ForeignKey(
         Doctor,
         on_delete = models.PROTECT
)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT
    ) 
    appointment_date = models.DateField()  
    token_number = models.PositiveIntegerField()
       
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default="W"
    )

