from django.urls import path
from django.views.generic import RedirectView
from . import views
from . import views_io

app_name = "operations"

urlpatterns = [
    # Export / Import / Fiches
    path("export/xlsx/<str:module>/", views_io.export_excel, name="export_xlsx"),
    path("export/pdf/<str:module>/", views_io.export_pdf, name="export_pdf"),
    path("import/<str:module>/template/", views_io.import_template, name="import_template"),
    path("import/<str:module>/", views_io.import_upload, name="import_upload"),
    path("fiche-vierge/<str:fiche_type>/", views_io.fiche_vierge, name="fiche_vierge"),


    # Fiche carburant
    path("fiche-carburant/", views.fiche_carburant, name="fiche_carburant"),
    path("fiche-carburant/nouveau/", views.fiche_carburant_create, name="fiche_carburant_create"),
    path("fiche-carburant/<int:pk>/modifier/", views.fiche_carburant_edit, name="fiche_carburant_edit"),
    path("fiche-carburant/<int:pk>/supprimer/", views.fiche_carburant_delete, name="fiche_carburant_delete"),

    # Pannes
    path("pannes/", views.pannes_list, name="pannes"),
    path("pannes/nouveau/", views.panne_create, name="panne_create"),
    path("pannes/<int:pk>/modifier/", views.panne_edit, name="panne_edit"),
    path("pannes/<int:pk>/supprimer/", views.panne_delete, name="panne_delete"),

    # Dépenses administratives
    path("depenses-admin/", views.depenses_admin, name="depenses_admin"),
    path("depenses-admin/nouveau/", views.depense_create, name="depense_create"),
    path("depenses-admin/<int:pk>/modifier/", views.depense_edit, name="depense_edit"),
    path("depenses-admin/<int:pk>/supprimer/", views.depense_delete, name="depense_delete"),

    # Bons de transport
    path("bons-transport/", views.bons_transport, name="bons_transport"),
    path("bons-transport/modele-vierge/", views.bon_modele_vierge, name="bon_modele_vierge"),
    path("bons-transport/nouveau/", views.bon_create, name="bon_create"),
    path("bons-transport/<int:pk>/modifier/", views.bon_edit, name="bon_edit"),
    path("bons-transport/<int:pk>/supprimer/", views.bon_delete, name="bon_delete"),
    path("bons-transport/<int:pk>/imprimer/", views.bon_imprimer, name="bon_imprimer"),

    # Anciennes URLs Transport bauxite : redirection vers Bons de transport.
    path(
        "transport-bauxite/",
        RedirectView.as_view(pattern_name="operations:bons_transport", permanent=False),
        name="transport_bauxite",
    ),
    path(
        "transport-bauxite/nouveau/",
        RedirectView.as_view(pattern_name="operations:bon_create", permanent=False),
        name="transport_create",
    ),
    path(
        "transport-bauxite/<int:pk>/modifier/",
        RedirectView.as_view(pattern_name="operations:bons_transport", permanent=False),
        name="transport_edit",
    ),
    path(
        "transport-bauxite/<int:pk>/supprimer/",
        RedirectView.as_view(pattern_name="operations:bons_transport", permanent=False),
        name="transport_delete",
    ),
]
