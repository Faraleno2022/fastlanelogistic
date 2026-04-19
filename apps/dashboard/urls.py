from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("rapport-mensuel/", views.rapport_mensuel, name="rapport"),
    path("rapport-mensuel/generer-factures/", views.generer_factures_mois, name="generer_factures"),
    path("projets/", views.projets_liste, name="projets"),
    path("projets/<str:code>/", views.projet_detail, name="projet_detail"),
    path("bilan-entreprise/", views.bilan_entreprise_vue, name="bilan_entreprise"),
]
