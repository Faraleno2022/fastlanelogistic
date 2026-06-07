"""
URLs pour le module Rapprochements bancaires.
"""

from django.urls import path
from . import views

app_name = 'rapprochements'

urlpatterns = [
    # Comptes bancaires
    path('comptes/', views.CompteBancaireListView.as_view(), name='compte-list'),
    path('comptes/<int:pk>/', views.CompteBancaireDetailView.as_view(), name='compte-detail'),
    path('comptes/create/', views.CompteBancaireCreateView.as_view(), name='compte-create'),
    path('comptes/<int:pk>/update/', views.CompteBancaireUpdateView.as_view(), name='compte-update'),
    path('comptes/<int:pk>/delete/', views.CompteBancaireDeleteView.as_view(), name='compte-delete'),
    
    # Rapprochements
    path('', views.RapprochementListView.as_view(), name='rapprochement-list'),
    path('<int:pk>/', views.RapprochementDetailView.as_view(), name='rapprochement-detail'),
    path('create/', views.RapprochementCreateView.as_view(), name='rapprochement-create'),
    path('<int:pk>/update/', views.RapprochementUpdateView.as_view(), name='rapprochement-update'),
    path('<int:pk>/delete/', views.RapprochementDeleteView.as_view(), name='rapprochement-delete'),
    
    # Import
    path('import/', views.OperationImportView.as_view(), name='import-operations'),
    
    # AJAX
    path('ajax/lettrage/', views.LettrageView.as_view(), name='ajax-lettrage'),
    path('ajax/lettrage-annuler/', views.LettrageAnnulationView.as_view(), name='ajax-lettrage-annuler'),
    path('ajax/finaliser/', views.RapprochementFinalisationView.as_view(), name='ajax-finaliser'),
]
