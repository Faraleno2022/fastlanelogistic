"""
URLs pour le module Contrôle Interne & Conformité
"""

from django.urls import path
from django.views.generic import TemplateView

from .views_controle import (
    MatriceRisquesListView,
    MatriceRisquesDetailView,
    MatriceRisquesCreateView,
    MatriceRisquesUpdateView,
    ProcedureControleListView,
    ProcedureControleDetailView,
    ProcedureControleCreateView,
    ProcedureControleUpdateView,
    TestControleListView,
    TestControleDetailView,
    TestControleCreateView,
    TestControleUpdateView,
    NonConformiteListView,
    NonConformiteDetailView,
    NonConformiteCreateView,
    NonConformiteUpdateView,
    DelegationPouvoirsListView,
    DelegationPouvoirsDetailView,
    DelegationPouvoirsCreateView,
    DelegationPouvoirsUpdateView,
    WorkflowListView,
    RapportControleListView,
    RapportControleDetailView,
    RapportControleCreateView,
    RapportControleUpdateView,
)

# Vue temporaire pour le dashboard
class ControleDashboardView(TemplateView):
    template_name = 'comptabilite/controle/dashboard.html'

urlpatterns = [
    path('', ControleDashboardView.as_view(), name='controle_dashboard'),
    # Matrice des risques
    path('risques/', MatriceRisquesListView.as_view(), name='controle_risques'),
    path('risques/nouveau/', MatriceRisquesCreateView.as_view(), name='controle_risque_create'),
    path('risques/<uuid:pk>/', MatriceRisquesDetailView.as_view(), name='controle_risque_detail'),
    path('risques/<uuid:pk>/modifier/', MatriceRisquesUpdateView.as_view(), name='controle_risque_update'),
    # Procédures
    path('procedures/', ProcedureControleListView.as_view(), name='controle_procedures'),
    path('procedures/nouvelle/', ProcedureControleCreateView.as_view(), name='controle_procedure_create'),
    path('procedures/<uuid:pk>/', ProcedureControleDetailView.as_view(), name='controle_procedure_detail'),
    path('procedures/<uuid:pk>/modifier/', ProcedureControleUpdateView.as_view(), name='controle_procedure_update'),
    # Tests
    path('tests/', TestControleListView.as_view(), name='controle_tests'),
    path('tests/nouveau/', TestControleCreateView.as_view(), name='controle_test_create'),
    path('tests/<uuid:pk>/', TestControleDetailView.as_view(), name='controle_test_detail'),
    path('tests/<uuid:pk>/modifier/', TestControleUpdateView.as_view(), name='controle_test_update'),
    # Non-conformités
    path('non-conformites/', NonConformiteListView.as_view(), name='controle_non_conformites'),
    path('non-conformites/nouvelle/', NonConformiteCreateView.as_view(), name='controle_non_conformite_create'),
    path('non-conformites/<uuid:pk>/', NonConformiteDetailView.as_view(), name='controle_non_conformite_detail'),
    path('non-conformites/<uuid:pk>/modifier/', NonConformiteUpdateView.as_view(), name='controle_non_conformite_update'),
    # Délégations
    path('delegations/', DelegationPouvoirsListView.as_view(), name='controle_delegations'),
    path('delegations/nouvelle/', DelegationPouvoirsCreateView.as_view(), name='controle_delegation_create'),
    path('delegations/<uuid:pk>/', DelegationPouvoirsDetailView.as_view(), name='controle_delegation_detail'),
    path('delegations/<uuid:pk>/modifier/', DelegationPouvoirsUpdateView.as_view(), name='controle_delegation_update'),
    # Workflows
    path('workflows/', WorkflowListView.as_view(), name='controle_workflows'),
    # Rapports
    path('rapports/', RapportControleListView.as_view(), name='controle_rapports'),
    path('rapports/nouveau/', RapportControleCreateView.as_view(), name='controle_rapport_create'),
    path('rapports/<uuid:pk>/', RapportControleDetailView.as_view(), name='controle_rapport_detail'),
    path('rapports/<uuid:pk>/modifier/', RapportControleUpdateView.as_view(), name='controle_rapport_update'),
]
