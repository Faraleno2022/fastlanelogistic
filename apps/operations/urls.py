from django.urls import path
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


    # Carburant
    path("carburant/", views.carburant_list, name="carburant"),
    path("carburant/nouveau/", views.carburant_create, name="carburant_create"),
    path("carburant/<int:pk>/modifier/", views.carburant_edit, name="carburant_edit"),
    path("carburant/<int:pk>/supprimer/", views.carburant_delete, name="carburant_delete"),

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

    # Transport bauxite
    path("transport-bauxite/", views.transport_bauxite, name="transport_bauxite"),
    path("transport-bauxite/nouveau/", views.transport_create, name="transport_create"),
    path("transport-bauxite/<int:pk>/modifier/", views.transport_edit, name="transport_edit"),
    path("transport-bauxite/<int:pk>/supprimer/", views.transport_delete, name="transport_delete"),

    # Bons de transport
    path("bons-transport/", views.bons_transport, name="bons_transport"),
    path("bons-transport/nouveau/", views.bon_create, name="bon_create"),
    path("bons-transport/<int:pk>/modifier/", views.bon_edit, name="bon_edit"),
    path("bons-transport/<int:pk>/supprimer/", views.bon_delete, name="bon_delete"),
]
