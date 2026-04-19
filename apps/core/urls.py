from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("parametres/", views.parametres_edit, name="parametres"),
    path("contrat-actif/set/", views.set_contrat_actif_view, name="set_contrat_actif"),
    path("contrat-actif/clear/", views.clear_contrat_actif_view, name="clear_contrat_actif"),
]
