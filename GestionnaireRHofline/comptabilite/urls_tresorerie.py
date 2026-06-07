"""
URLs pour le module Trésorerie Avancée
"""

from django.urls import path
from . import views_tresorerie as views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_tresorerie, name='tresorerie_dashboard'),
    
    # Situation de trésorerie
    path('situations/', views.situation_tresorerie_list, name='situation_tresorerie_list'),
    path('situations/<uuid:pk>/', views.situation_tresorerie_detail, name='situation_tresorerie_detail'),
    path('situations/generer/', views.generer_situation_journaliere, name='generer_situation_journaliere'),
    
    # Échéancier
    path('echeancier/', views.echeancier_list, name='echeancier_list'),
    path('echeancier/nouveau/', views.echeancier_create, name='echeancier_create'),
    path('echeancier/<uuid:pk>/', views.echeancier_detail, name='echeancier_detail'),
    path('echeancier/<uuid:pk>/modifier/', views.echeancier_update, name='echeancier_update'),
    path('echeancier/<uuid:pk>/realiser/', views.echeancier_realiser, name='echeancier_realiser'),
    
    # Synchronisation bancaire
    path('synchronisations/', views.synchronisation_list, name='synchronisation_list'),
    path('synchronisations/nouvelle/', views.synchronisation_create, name='synchronisation_create'),
    path('synchronisations/<uuid:pk>/executer/', views.synchronisation_executer, name='synchronisation_executer'),
    
    # Alertes
    path('alertes/', views.alertes_tresorerie_list, name='alertes_tresorerie_list'),
    path('alertes/<uuid:pk>/acquitter/', views.alerte_acquitter, name='alerte_tresorerie_acquitter'),
    
    # Seuils de liquidité
    path('seuils/', views.seuils_liquidite_list, name='seuils_liquidite_list'),
    path('seuils/nouveau/', views.seuil_liquidite_create, name='seuil_liquidite_create'),
    
    # Gestion numéraire
    path('numeraire/', views.numeraire_list, name='numeraire_list'),
    path('numeraire/nouveau/', views.numeraire_create, name='numeraire_create'),
    path('numeraire/<uuid:pk>/valider/', views.numeraire_valider, name='numeraire_valider'),
    
    # Optimisation
    path('optimisation/', views.optimisation_list, name='optimisation_list'),
    path('optimisation/nouvelle/', views.optimisation_create, name='optimisation_create'),
    path('optimisation/<uuid:pk>/', views.optimisation_detail, name='optimisation_detail'),
    
    # Flux journaliers
    path('flux-journaliers/', views.flux_journaliers_list, name='flux_journaliers_list'),
    path('flux-journaliers/<uuid:pk>/', views.flux_journalier_detail, name='flux_journalier_detail'),
    
    # API JSON
    path('api/previsions/', views.api_previsions_tresorerie, name='api_previsions_tresorerie'),
    path('api/echeances-calendrier/', views.api_echeances_calendrier, name='api_echeances_calendrier'),
]
