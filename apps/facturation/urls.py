from django.urls import path
from . import views

app_name = "facturation"

urlpatterns = [
    # Factures
    path("", views.liste_factures, name="liste"),
    path("nouveau/", views.facture_create, name="create"),

    # Contrats
    path("contrats/", views.liste_contrats, name="contrats"),
    path("contrats/nouveau/", views.contrat_create, name="contrat_create"),
    path("contrats/<int:pk>/modifier/", views.contrat_edit, name="contrat_edit"),
    path("contrats/<int:pk>/supprimer/", views.contrat_delete, name="contrat_delete"),

    # Facture (détail / edit / delete par numéro)
    path("<str:numero>/modifier/", views.facture_edit, name="edit"),
    path("<str:numero>/supprimer/", views.facture_delete, name="delete"),
    path("<str:numero>/", views.detail_facture, name="detail"),
]
