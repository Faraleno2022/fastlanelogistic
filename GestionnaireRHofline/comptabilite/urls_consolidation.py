"""
URLs pour le module Consolidation & Reporting
"""

from django.urls import path
from . import views_consolidation as views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_consolidation, name='consolidation_dashboard'),
    
    # Matrice de consolidation
    path('matrice/', views.matrice_list, name='matrice_list'),
    path('matrice/nouvelle/', views.matrice_create, name='matrice_create'),
    path('matrice/<uuid:pk>/', views.matrice_detail, name='matrice_detail'),
    path('matrice/<uuid:pk>/modifier/', views.matrice_update, name='matrice_update'),
    
    # Consolidations
    path('consolidations/', views.consolidation_list, name='consolidation_list'),
    path('consolidations/nouvelle/', views.consolidation_create, name='consolidation_create'),
    path('consolidations/<uuid:pk>/', views.consolidation_detail, name='consolidation_detail'),
    path('consolidations/<uuid:pk>/valider/', views.consolidation_valider, name='consolidation_valider'),
    
    # Éliminations IGF
    path('consolidations/<uuid:consolidation_pk>/eliminations/', views.elimination_list, name='elimination_list'),
    path('consolidations/<uuid:consolidation_pk>/eliminations/nouvelle/', views.elimination_create, name='elimination_create'),
    
    # Ajustements
    path('consolidations/<uuid:consolidation_pk>/ajustements/', views.ajustement_list, name='ajustement_list'),
    path('consolidations/<uuid:consolidation_pk>/ajustements/nouveau/', views.ajustement_create, name='ajustement_create'),
    
    # Affectation du résultat
    path('affectations/', views.affectation_list, name='affectation_list'),
    path('affectations/nouvelle/', views.affectation_create, name='affectation_create'),
    
    # Variation des capitaux
    path('variations-capitaux/', views.variation_capitaux_list, name='variation_capitaux_list'),
    path('variations-capitaux/nouvelle/', views.variation_capitaux_create, name='variation_capitaux_create'),
    
    # Notes explicatives
    path('notes/', views.notes_list, name='notes_list'),
    path('notes/nouvelle/', views.note_create, name='note_create'),
    path('notes/<uuid:pk>/', views.note_detail, name='note_detail'),
    path('notes/<uuid:pk>/modifier/', views.note_update, name='note_update'),
    
    # États financiers consolidés
    path('consolidations/<uuid:consolidation_pk>/bilan/', views.bilan_consolide, name='bilan_consolide'),
    path('consolidations/<uuid:consolidation_pk>/compte-resultat/', views.compte_resultat_consolide, name='compte_resultat_consolide'),
    path('consolidations/<uuid:consolidation_pk>/flux-tresorerie/', views.flux_tresorerie_consolide, name='flux_tresorerie_consolide'),
    path('consolidations/<uuid:consolidation_pk>/tableau-capitaux/', views.tableau_capitaux_consolide, name='tableau_capitaux_consolide'),
    path('consolidations/<uuid:consolidation_pk>/annexes/', views.annexes_consolidees, name='annexes_consolidees'),
    
    # Documentation
    path('consolidations/<uuid:consolidation_pk>/documentation/', views.documentation_list, name='documentation_list'),
    path('consolidations/<uuid:consolidation_pk>/documentation/upload/', views.documentation_upload, name='documentation_upload'),
    
    # API JSON
    path('api/consolidations/<uuid:consolidation_pk>/perimetre/', views.api_perimetre_consolidation, name='api_perimetre_consolidation'),
    path('api/consolidations/<uuid:consolidation_pk>/synthese/', views.api_synthese_consolidation, name='api_synthese_consolidation'),
]
