from django.urls import path
from . import views

app_name = "flotte"

urlpatterns = [
    path("", views.liste_camions, name="liste"),
    path("amortissement/", views.amortissement_global, name="amortissement"),
    path("nouveau/", views.camion_create, name="create"),
    path("<str:code>/modifier/", views.camion_edit, name="edit"),
    path("<str:code>/supprimer/", views.camion_delete, name="delete"),
    path("<str:code>/", views.detail_camion, name="detail"),
]
