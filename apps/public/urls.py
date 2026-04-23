from django.urls import path
from . import views

app_name = "public"

urlpatterns = [
    path("", views.home, name="home"),
    path("a-propos/", views.a_propos, name="a_propos"),
    path("evenements/", views.evenements_liste, name="evenements"),
    path("evenements/<slug:slug>/", views.evenement_detail, name="evenement_detail"),
    path("appels-offres/", views.appels_offres_liste, name="appels_offres"),
    path("appels-offres/<slug:slug>/", views.appel_offre_detail, name="appel_offre_detail"),
    path("contact/", views.contact, name="contact"),
]
