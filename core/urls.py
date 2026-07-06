from django.urls import path
from .import views
urlpatterns = [
    path("",views.home),
    path("add-patient/",views.add_patient,name="add_patient"),
    path("view-patients/",views.view_patient,name="view_patient"),
    path("edit-patient/<int:id>/",views.edit_patient,name="edit_patient"),
    path("delete-patient/<int:id>/",views.delete_patient,name="delete_patient"),
]