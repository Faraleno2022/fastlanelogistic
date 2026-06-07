"""
URLs pour le module Comptabilité Analytique Avancée
"""

from django.urls import path
from django.views.generic import TemplateView

from .views_analytique import (
    SectionAnalytiqueListView,
    SectionAnalytiqueDetailView,
    SectionAnalytiqueCreateView,
    SectionAnalytiqueUpdateView,
    ImputationAnalytiqueListView,
    ImputationAnalytiqueDetailView,
    ImputationAnalytiqueCreateView,
    ImputationAnalytiqueUpdateView,
    BudgetAnalytiqueListView,
    BudgetAnalytiqueDetailView,
    BudgetAnalytiqueCreateView,
    BudgetAnalytiqueUpdateView,
    AnalyseVarianceListView,
    AnalyseVarianceDetailView,
    AnalyseVarianceCreateView,
    AnalyseVarianceUpdateView,
)

# Vues temporaires - à remplacer par les vraies vues
class AnalytiqueDashboardView(TemplateView):
    template_name = 'comptabilite/analytique/dashboard.html'

class CentreCoutsListView(TemplateView):
    template_name = 'comptabilite/analytique/centres_couts.html'

class CentreCoutCreateView(TemplateView):
    template_name = 'comptabilite/analytique/centre_cout_form.html'

class CentreCoutDetailView(TemplateView):
    template_name = 'comptabilite/analytique/centre_cout_detail.html'

class CentreCoutUpdateView(TemplateView):
    template_name = 'comptabilite/analytique/centre_cout_form.html'

class CommandesListView(TemplateView):
    template_name = 'comptabilite/analytique/commandes.html'

class RapportsListView(TemplateView):
    template_name = 'comptabilite/analytique/rapports.html'

urlpatterns = [
    path('', AnalytiqueDashboardView.as_view(), name='analytique_dashboard'),
    path('centres-couts/', CentreCoutsListView.as_view(), name='analytique_centres_couts'),
    path('centres-couts/nouveau/', CentreCoutCreateView.as_view(), name='analytique_centre_cout_create'),
    path('centres-couts/<uuid:pk>/', CentreCoutDetailView.as_view(), name='analytique_centre_cout_detail'),
    path('centres-couts/<uuid:pk>/modifier/', CentreCoutUpdateView.as_view(), name='analytique_centre_cout_update'),
    path('sections/', SectionAnalytiqueListView.as_view(), name='analytique_sections'),
    path('sections/nouvelle/', SectionAnalytiqueCreateView.as_view(), name='analytique_section_create'),
    path('sections/<uuid:pk>/', SectionAnalytiqueDetailView.as_view(), name='analytique_section_detail'),
    path('sections/<uuid:pk>/modifier/', SectionAnalytiqueUpdateView.as_view(), name='analytique_section_update'),
    path('commandes/', CommandesListView.as_view(), name='analytique_commandes'),
    path('imputations/', ImputationAnalytiqueListView.as_view(), name='analytique_imputations'),
    path('imputations/nouvelle/', ImputationAnalytiqueCreateView.as_view(), name='analytique_imputation_create'),
    path('imputations/<uuid:pk>/', ImputationAnalytiqueDetailView.as_view(), name='analytique_imputation_detail'),
    path('imputations/<uuid:pk>/modifier/', ImputationAnalytiqueUpdateView.as_view(), name='analytique_imputation_update'),
    path('budgets/', BudgetAnalytiqueListView.as_view(), name='analytique_budgets'),
    path('budgets/nouveau/', BudgetAnalytiqueCreateView.as_view(), name='analytique_budget_create'),
    path('budgets/<uuid:pk>/', BudgetAnalytiqueDetailView.as_view(), name='analytique_budget_detail'),
    path('budgets/<uuid:pk>/modifier/', BudgetAnalytiqueUpdateView.as_view(), name='analytique_budget_update'),
    path('variances/', AnalyseVarianceListView.as_view(), name='analytique_variances'),
    path('variances/nouvelle/', AnalyseVarianceCreateView.as_view(), name='analytique_variance_create'),
    path('variances/<uuid:pk>/', AnalyseVarianceDetailView.as_view(), name='analytique_variance_detail'),
    path('variances/<uuid:pk>/modifier/', AnalyseVarianceUpdateView.as_view(), name='analytique_variance_update'),
    path('rapports/', RapportsListView.as_view(), name='analytique_rapports'),
]
