from django.urls import path
from . import views

app_name = "rh"

urlpatterns = [
    # Employés
    path("employes/", views.liste_employes, name="liste_employes"),
    path("employes/nouveau/", views.employe_create, name="employe_create"),
    path("employes/<int:pk>/modifier/", views.employe_edit, name="employe_edit"),
    path("employes/<int:pk>/supprimer/", views.employe_delete, name="employe_delete"),

    # Attendance
    path("attendance/", views.attendance_mensuel, name="attendance"),
    path("attendance/nouveau/", views.attendance_create, name="attendance_create"),
    path("attendance/<int:pk>/modifier/", views.attendance_edit, name="attendance_edit"),
    path("attendance/<int:pk>/supprimer/", views.attendance_delete, name="attendance_delete"),

    # Heures sup
    path("heures-sup/", views.liste_heures_sup, name="heures_sup"),
    path("heures-sup/nouveau/", views.hs_create, name="hs_create"),
    path("heures-sup/<int:pk>/modifier/", views.hs_edit, name="hs_edit"),
    path("heures-sup/<int:pk>/supprimer/", views.hs_delete, name="hs_delete"),
]
