from django.urls import path
from . import views
from . import views_hs
from . import views_absence
from . import views_portail_conge

app_name = 'temps_travail'

urlpatterns = [
    # Accueil
    path('', views.temps_travail_home, name='home'),
    
    # Pointages
    path('pointages/', views.liste_pointages, name='pointages'),
    path('pointages/creer/', views.creer_pointage, name='creer_pointage'),
    path('pointages/<int:pk>/', views.detail_pointage, name='detail_pointage'),
    path('pointages/<int:pk>/modifier/', views.modifier_pointage, name='modifier_pointage'),
    path('pointages/<int:pk>/supprimer/', views.supprimer_pointage, name='supprimer_pointage'),
    path('pointages/pointer-entree/', views.pointer_entree, name='pointer_entree'),
    path('pointages/pointer-sortie/', views.pointer_sortie, name='pointer_sortie'),
    
    # Congés
    path('conges/', views.liste_conges, name='conges'),
    path('conges/creer/', views.creer_conge, name='creer_conge'),
    path('conges/<int:pk>/approuver/', views.approuver_conge, name='approuver_conge'),
    path('conges/<int:pk>/modifier/', views.modifier_conge, name='modifier_conge'),
    path('conges/<int:pk>/supprimer/', views.supprimer_conge, name='supprimer_conge'),
    
    # Absences
    path('absences/', views.liste_absences, name='absences'),
    path('absences/creer/', views.creer_absence, name='creer_absence'),
    
    # Jours fériés
    path('jours-feries/', views.liste_jours_feries, name='liste_jours_feries'),
    path('jours-feries/creer/', views.creer_jour_ferie, name='creer_jour_ferie'),
    
    # Rapports
    path('rapports/presence/', views.rapport_presence, name='rapport_presence'),
    path('rapports/presence/pdf/', views.rapport_presence_pdf, name='rapport_presence_pdf'),
    path('rapports/heures-supplementaires/', views.rapport_heures_supplementaires, name='rapport_heures_supplementaires'),
    
    # Heures supplémentaires (gestion)
    path('heures-sup/', views_hs.liste_heures_supplementaires, name='liste_heures_supplementaires'),
    path('heures-sup/ajouter/', views_hs.ajouter_heure_supplementaire, name='ajouter_heure_supplementaire'),
    path('heures-sup/<int:pk>/valider/', views_hs.valider_heure_supplementaire, name='valider_heure_supplementaire'),
    path('heures-sup/<int:pk>/rejeter/', views_hs.rejeter_heure_supplementaire, name='rejeter_heure_supplementaire'),
    path('heures-sup/<int:pk>/supprimer/', views_hs.supprimer_heure_supplementaire, name='supprimer_heure_supplementaire'),
    path('heures-sup/recap/', views_hs.recap_heures_supplementaires, name='recap_heures_supplementaires'),
    
    # Gestion des absences (nouveau système)
    path('gestion-absences/', views_absence.liste_absences, name='liste_absences'),
    path('gestion-absences/declarer/', views_absence.declarer_absence, name='declarer_absence'),
    path('gestion-absences/<int:pk>/', views_absence.detail_absence, name='detail_absence'),
    path('gestion-absences/<int:pk>/justifier/', views_absence.justifier_absence, name='justifier_absence'),
    path('gestion-absences/<int:pk>/non-justifiee/', views_absence.marquer_non_justifiee, name='marquer_non_justifiee'),
    path('gestion-absences/<int:pk>/prolonger/', views_absence.prolonger_absence, name='prolonger_absence'),
    path('gestion-absences/<int:pk>/supprimer/', views_absence.supprimer_absence, name='supprimer_absence'),
    path('gestion-absences/recap/', views_absence.recap_absences, name='recap_absences'),
    path('gestion-absences/calendrier/', views_absence.calendrier_absences, name='calendrier_absences'),
    
    # Portail employé - Congés
    path('mes-conges/', views_portail_conge.mes_conges, name='mes_conges'),
    path('mes-conges/demander/', views_portail_conge.demander_conge, name='demander_conge'),
    path('mes-conges/<int:pk>/', views_portail_conge.detail_ma_demande, name='detail_ma_demande'),
    path('mes-conges/<int:pk>/annuler/', views_portail_conge.annuler_ma_demande, name='annuler_ma_demande'),
    path('mes-conges/solde/', views_portail_conge.mon_solde_conges, name='mon_solde_conges'),
]
