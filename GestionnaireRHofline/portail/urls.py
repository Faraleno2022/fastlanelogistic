from django.urls import path
from . import views
from . import views_conges
from . import views_absences

app_name = 'portail'

urlpatterns = [
    # Accueil
    path('', views.portail_accueil, name='accueil'),
    
    # Bulletins de paie
    path('bulletins/', views.mes_bulletins, name='mes_bulletins'),
    path('bulletins/<int:pk>/', views.detail_bulletin, name='detail_bulletin'),
    
    # Congés (vues de base)
    path('conges/', views.mes_conges, name='mes_conges'),
    path('conges/demander/', views.demander_conge, name='demander_conge'),
    path('conges/<int:pk>/annuler/', views.annuler_conge, name='annuler_conge'),
    
    # Congés (vues étendues)
    path('conges/demande/<int:pk>/', views_conges.detail_demande_conge, name='detail_demande_conge'),
    path('conges/demande/<int:pk>/modifier/', views_conges.modifier_demande_conge, name='modifier_demande_conge'),
    path('conges/demande/<int:pk>/soumettre/', views_conges.soumettre_demande_conge, name='soumettre_demande_conge'),
    path('conges/demande/<int:pk>/annuler/', views_conges.annuler_demande_conge, name='annuler_demande_conge'),
    path('conges/historique/', views_conges.historique_conges, name='historique_conges'),
    path('conges/api/calculer-duree/', views_conges.calculer_jours_conges, name='api_calculer_duree'),
    
    # Absences et permissions
    path('absences/', views_absences.mes_absences, name='mes_absences'),
    path('absences/permission/', views_absences.demander_permission, name='demander_permission'),
    path('absences/permission/<int:pk>/', views_absences.detail_permission, name='detail_permission'),
    path('absences/declarer/', views_absences.declarer_absence, name='declarer_absence'),
    path('absences/historique/', views_absences.historique_absences, name='historique_absences'),
    path('absences/api/calculer-duree/', views_absences.calculer_duree_permission, name='api_calculer_duree_permission'),
    
    # Prêts
    path('prets/', views.mes_prets, name='mes_prets'),
    path('prets/<int:pk>/', views.detail_pret, name='detail_pret'),
    path('prets/demander/', views.demander_pret, name='demander_pret'),
    
    # Heures supplémentaires
    path('heures-sup/', views.mes_heures_sup, name='mes_heures_sup'),
    
    # Profil
    path('profil/', views.mon_profil, name='mon_profil'),
]
