"""
URLs pour le module Déclarations Fiscales Avancées
"""

from django.urls import path
from django.views.generic import TemplateView

from .views_fiscalite import (
    DossierFiscalListView,
    DossierFiscalDetailView,
    DossierFiscalCreateView,
    DossierFiscalUpdateView,
    DeclarationISListView,
    DeclarationISDetailView,
    DeclarationISCreateView,
    DeclarationISUpdateView,
    DeclarationCATListView,
    DeclarationCATDetailView,
    DeclarationCATCreateView,
    DeclarationCATUpdateView,
    DeclarationCVAEListView,
    DeclarationCVAEDetailView,
    DeclarationCVAECreateView,
    DeclarationCVAEUpdateView,
    LiasseFiscaleListView,
    LiasseFiscaleDetailView,
    LiasseFiscaleCreateView,
    LiasseFiscaleUpdateView,
    DocumentationFiscaleListView,
    DocumentationFiscaleCreateView,
)

# Vue temporaire pour le dashboard
class FiscaliteDashboardView(TemplateView):
    template_name = 'comptabilite/fiscalite/dashboard.html'

urlpatterns = [
    path('', FiscaliteDashboardView.as_view(), name='fiscalite_dashboard'),
    # Dossiers fiscaux
    path('dossiers/', DossierFiscalListView.as_view(), name='fiscalite_dossiers'),
    path('dossiers/nouveau/', DossierFiscalCreateView.as_view(), name='fiscalite_dossier_create'),
    path('dossiers/<uuid:pk>/', DossierFiscalDetailView.as_view(), name='fiscalite_dossier_detail'),
    path('dossiers/<uuid:pk>/modifier/', DossierFiscalUpdateView.as_view(), name='fiscalite_dossier_update'),
    # Déclarations IS
    path('declarations-is/', DeclarationISListView.as_view(), name='fiscalite_declarations_is'),
    path('declarations-is/nouvelle/', DeclarationISCreateView.as_view(), name='fiscalite_declaration_is_create'),
    path('declarations-is/<uuid:pk>/', DeclarationISDetailView.as_view(), name='fiscalite_declaration_is_detail'),
    path('declarations-is/<uuid:pk>/modifier/', DeclarationISUpdateView.as_view(), name='fiscalite_declaration_is_update'),
    # Déclarations CAT
    path('declarations-cat/', DeclarationCATListView.as_view(), name='fiscalite_declarations_cat'),
    path('declarations-cat/nouvelle/', DeclarationCATCreateView.as_view(), name='fiscalite_declaration_cat_create'),
    path('declarations-cat/<uuid:pk>/', DeclarationCATDetailView.as_view(), name='fiscalite_declaration_cat_detail'),
    path('declarations-cat/<uuid:pk>/modifier/', DeclarationCATUpdateView.as_view(), name='fiscalite_declaration_cat_update'),
    # Déclarations CVAE
    path('declarations-cvae/', DeclarationCVAEListView.as_view(), name='fiscalite_declarations_cvae'),
    path('declarations-cvae/nouvelle/', DeclarationCVAECreateView.as_view(), name='fiscalite_declaration_cvae_create'),
    path('declarations-cvae/<uuid:pk>/', DeclarationCVAEDetailView.as_view(), name='fiscalite_declaration_cvae_detail'),
    path('declarations-cvae/<uuid:pk>/modifier/', DeclarationCVAEUpdateView.as_view(), name='fiscalite_declaration_cvae_update'),
    # Liasses fiscales
    path('liasses/', LiasseFiscaleListView.as_view(), name='fiscalite_liasses'),
    path('liasses/nouvelle/', LiasseFiscaleCreateView.as_view(), name='fiscalite_liasse_create'),
    path('liasses/<uuid:pk>/', LiasseFiscaleDetailView.as_view(), name='fiscalite_liasse_detail'),
    path('liasses/<uuid:pk>/modifier/', LiasseFiscaleUpdateView.as_view(), name='fiscalite_liasse_update'),
    # Documentation fiscale
    path('documentation/', DocumentationFiscaleListView.as_view(), name='fiscalite_documentation'),
    path('documentation/ajouter/', DocumentationFiscaleCreateView.as_view(), name='fiscalite_documentation_create'),
]
