"""
URLs pour le module Gestion Comptable des Contrats
"""

from django.urls import path

from .views_contrats import (
    ContratsDashboardView,
    ContratFournisseurListView, ContratFournisseurDetailView,
    ContratFournisseurCreateView, ContratFournisseurUpdateView,
    ContratClientListView, ContratClientDetailView,
    ContratClientCreateView, ContratClientUpdateView,
    ConditionsPaiementListView, GarantiesListView, PenalitesListView,
    ReclamationsListView, ReclamationDetailView,
    ReclamationCreateView, ReclamationUpdateView,
    AlertesListView
)

urlpatterns = [
    # Dashboard
    path('', ContratsDashboardView.as_view(), name='contrats_dashboard'),

    # Contrats fournisseurs
    path('fournisseurs/', ContratFournisseurListView.as_view(), name='contrats_fournisseurs'),
    path('fournisseurs/nouveau/', ContratFournisseurCreateView.as_view(), name='contrats_fournisseur_create'),
    path('fournisseurs/<uuid:pk>/', ContratFournisseurDetailView.as_view(), name='contrats_fournisseur_detail'),
    path('fournisseurs/<uuid:pk>/modifier/', ContratFournisseurUpdateView.as_view(), name='contrats_fournisseur_update'),

    # Contrats clients
    path('clients/', ContratClientListView.as_view(), name='contrats_clients'),
    path('clients/nouveau/', ContratClientCreateView.as_view(), name='contrats_client_create'),
    path('clients/<uuid:pk>/', ContratClientDetailView.as_view(), name='contrats_client_detail'),
    path('clients/<uuid:pk>/modifier/', ContratClientUpdateView.as_view(), name='contrats_client_update'),

    # Conditions de paiement
    path('conditions-paiement/', ConditionsPaiementListView.as_view(), name='contrats_conditions_paiement'),

    # Garanties
    path('garanties/', GarantiesListView.as_view(), name='contrats_garanties'),

    # Pénalités
    path('penalites/', PenalitesListView.as_view(), name='contrats_penalites'),

    # Réclamations
    path('reclamations/', ReclamationsListView.as_view(), name='contrats_reclamations'),
    path('reclamations/nouveau/', ReclamationCreateView.as_view(), name='contrats_reclamation_create'),
    path('reclamations/<uuid:pk>/', ReclamationDetailView.as_view(), name='contrats_reclamation_detail'),
    path('reclamations/<uuid:pk>/modifier/', ReclamationUpdateView.as_view(), name='contrats_reclamation_update'),

    # Alertes
    path('alertes/', AlertesListView.as_view(), name='contrats_alertes'),
]
