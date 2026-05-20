from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = "public"

urlpatterns = [
    path("", RedirectView.as_view(url="/connexion/", permanent=False), name="home"),
    path("a-propos/", RedirectView.as_view(url="/connexion/", permanent=False), name="a_propos"),
    path("gestion/messages/", views.gestion_messages, name="gestion_messages"),
    path("gestion/messages/<int:pk>/", views.gestion_message_detail, name="gestion_message_detail"),
    path("gestion/evenements/", views.gestion_evenements, name="gestion_evenements"),
    path("gestion/evenements/ajouter/", views.evenement_create, name="evenement_create"),
    path("gestion/evenements/<int:pk>/modifier/", views.evenement_edit, name="evenement_edit"),
    path("gestion/evenements/<int:pk>/supprimer/", views.evenement_delete, name="evenement_delete"),
    path("gestion/appels-offres/", views.gestion_appels_offres, name="gestion_appels_offres"),
    path("gestion/appels-offres/ajouter/", views.appel_offre_create, name="appel_offre_create"),
    path("gestion/appels-offres/<int:pk>/modifier/", views.appel_offre_edit, name="appel_offre_edit"),
    path("gestion/appels-offres/<int:pk>/supprimer/", views.appel_offre_delete, name="appel_offre_delete"),
    path("evenements/", RedirectView.as_view(url="/connexion/", permanent=False), name="evenements"),
    path("evenements/<slug:slug>/", RedirectView.as_view(url="/connexion/", permanent=False), name="evenement_detail"),
    path("appels-offres/", RedirectView.as_view(url="/connexion/", permanent=False), name="appels_offres"),
    path("appels-offres/<slug:slug>/", RedirectView.as_view(url="/connexion/", permanent=False), name="appel_offre_detail"),
    path("contact/", RedirectView.as_view(url="/connexion/", permanent=False), name="contact"),
]
