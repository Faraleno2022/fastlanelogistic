from django.urls import path
from . import views
from . import views_evaluation
from . import views_mission
from . import views_reclamation
from . import views_medical
from . import views_import
from . import views_absences

app_name = 'employes'

urlpatterns = [
    # Liste et CRUD employés
    path('', views.EmployeListView.as_view(), name='list'),
    path('create/', views.EmployeCreateView.as_view(), name='create'),
    path('<int:pk>/', views.EmployeDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EmployeUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.EmployeDeleteView.as_view(), name='delete'),

    # Export
    path('export/excel/', views.employe_export_excel, name='export_excel'),

    # Import employés
    path('import/', views_import.import_employes_page, name='import_page'),
    path('import/template/', views_import.telecharger_template_import, name='telecharger_template'),
    path('import/preview/', views_import.import_employes_preview, name='import_preview'),
    path('import/execute/', views_import.import_employes_execute, name='import_execute'),
    path('import/template-salaires/', views_import.telecharger_template_import_salaires, name='template_salaires'),
    
    # Contrats
    path('<int:employe_id>/contrat/create/', views.employe_contrat_create, name='contrat_create'),
    path('contrats/modele-cdi/', views.telecharger_modele_contrat_cdi, name='telecharger_modele_contrat_cdi'),
    path('contrats/<int:contrat_id>/generer/', views.generer_contrat_employe, name='generer_contrat_employe'),
    
    # Documents
    path('<int:employe_id>/document/upload/', views.employe_document_upload, name='document_upload'),
    path('document/<int:document_id>/delete/', views.employe_document_delete, name='document_delete'),
    
    # Famille (conjoint et enfants)
    path('<int:employe_id>/conjoint/', views.sauvegarder_conjoint, name='sauvegarder_conjoint'),
    path('<int:employe_id>/enfant/', views.sauvegarder_enfant, name='sauvegarder_enfant'),
    path('enfant/<int:enfant_id>/supprimer/', views.supprimer_enfant, name='supprimer_enfant'),

    # Évaluations (performance)
    path('<int:employe_id>/evaluations/', views.evaluation_list, name='evaluation_list'),
    path('<int:employe_id>/evaluations/create/', views.evaluation_create, name='evaluation_create'),
    path('evaluations/<int:pk>/', views.evaluation_detail, name='evaluation_detail'),
    path('evaluations/<int:pk>/delete/', views.evaluation_delete, name='evaluation_delete'),

    # Sanctions disciplinaires
    path('<int:employe_id>/sanctions/', views.sanction_list, name='sanction_list'),
    path('<int:employe_id>/sanctions/create/', views.sanction_create, name='sanction_create'),
    path('sanctions/<int:pk>/', views.sanction_detail, name='sanction_detail'),
    path('sanctions/<int:pk>/delete/', views.sanction_delete, name='sanction_delete'),
    
    # Campagnes d'évaluation de performance
    path('campagnes/', views_evaluation.liste_campagnes, name='liste_campagnes'),
    path('campagnes/creer/', views_evaluation.creer_campagne, name='creer_campagne'),
    path('campagnes/<int:pk>/', views_evaluation.detail_campagne, name='detail_campagne'),
    path('campagnes/<int:pk>/lancer/', views_evaluation.lancer_campagne, name='lancer_campagne'),
    path('campagnes/synthese/', views_evaluation.synthese_evaluations, name='synthese_evaluations'),
    
    # Évaluations de performance (nouveau système)
    path('performance/<int:pk>/', views_evaluation.detail_evaluation, name='detail_evaluation_perf'),
    path('performance/<int:pk>/modifier/', views_evaluation.modifier_evaluation, name='modifier_evaluation'),
    path('performance/<int:evaluation_id>/objectif/', views_evaluation.ajouter_objectif, name='ajouter_objectif'),
    path('performance/objectif/<int:pk>/evaluer/', views_evaluation.evaluer_objectif, name='evaluer_objectif'),
    path('performance/<int:evaluation_id>/competence/', views_evaluation.ajouter_competence, name='ajouter_competence'),
    
    # Missions et déplacements
    path('missions/', views_mission.liste_missions, name='liste_missions'),
    path('missions/creer/', views_mission.creer_mission, name='creer_mission'),
    path('missions/<int:pk>/', views_mission.detail_mission, name='detail_mission'),
    path('missions/<int:pk>/modifier/', views_mission.modifier_mission, name='modifier_mission'),
    path('missions/<int:pk>/demarrer/', views_mission.demarrer_mission, name='demarrer_mission'),
    path('missions/<int:pk>/terminer/', views_mission.terminer_mission, name='terminer_mission'),
    path('missions/<int:pk>/annuler/', views_mission.annuler_mission, name='annuler_mission'),
    path('missions/<int:pk>/supprimer/', views_mission.supprimer_mission, name='supprimer_mission'),
    path('missions/<int:pk>/frais/', views_mission.ajouter_frais_mission, name='ajouter_frais_mission'),
    path('missions/<int:pk>/frais/<int:frais_pk>/supprimer/', views_mission.supprimer_frais_mission, name='supprimer_frais_mission'),
    path('missions/<int:pk>/avance/', views_mission.accorder_avance, name='accorder_avance'),
    path('missions/recap/', views_mission.recap_missions, name='recap_missions'),
    path('missions/baremes/', views_mission.gestion_baremes_indemnites, name='gestion_baremes_indemnites'),
    
    # Réclamations
    path('reclamations/', views_reclamation.liste_reclamations, name='liste_reclamations'),
    path('reclamations/creer/', views_reclamation.creer_reclamation, name='creer_reclamation'),
    path('reclamations/<int:pk>/', views_reclamation.detail_reclamation, name='detail_reclamation'),
    path('reclamations/<int:pk>/prendre-en-charge/', views_reclamation.prendre_en_charge, name='prendre_en_charge'),
    path('reclamations/<int:pk>/assigner/', views_reclamation.assigner_reclamation, name='assigner_reclamation'),
    path('reclamations/<int:pk>/commentaire/', views_reclamation.ajouter_commentaire, name='ajouter_commentaire'),
    path('reclamations/<int:pk>/resoudre/', views_reclamation.resoudre_reclamation, name='resoudre_reclamation'),
    path('reclamations/<int:pk>/rejeter/', views_reclamation.rejeter_reclamation, name='rejeter_reclamation'),
    path('reclamations/<int:pk>/fermer/', views_reclamation.fermer_reclamation, name='fermer_reclamation'),
    path('reclamations/<int:pk>/satisfaction/', views_reclamation.noter_satisfaction, name='noter_satisfaction'),
    path('reclamations/recap/', views_reclamation.recap_reclamations, name='recap_reclamations'),
    path('reclamations/categories/', views_reclamation.gestion_categories_reclamations, name='gestion_categories_reclamations'),
    
    # Vues globales RH
    path('contrats/', views.liste_contrats, name='liste_contrats'),
    path('carrieres/', views.liste_carrieres, name='liste_carrieres'),
    path('documents/', views.liste_documents, name='liste_documents_global'),
    path('sanctions-global/', views.liste_sanctions_global, name='liste_sanctions_global'),
    path('accidents/', views.liste_accidents, name='liste_accidents'),

    # Visites médicales
    path('medical/', views_medical.liste_visites_medicales, name='liste_visites_medicales'),
    path('medical/planifier/', views_medical.planifier_visite, name='planifier_visite'),
    path('medical/<int:pk>/', views_medical.detail_visite, name='detail_visite'),
    path('medical/<int:pk>/resultat/', views_medical.enregistrer_resultat, name='enregistrer_resultat'),
    path('medical/<int:pk>/supprimer/', views_medical.supprimer_visite, name='supprimer_visite'),
    path('medical/tableau-bord/', views_medical.tableau_bord_medical, name='tableau_bord_medical'),
    path('medical/employe/<int:employe_id>/', views_medical.suivi_medical_employe, name='suivi_medical_employe'),

    # Tableau de bord absences
    path('absences/tableau-de-bord/', views_absences.tableau_bord_absences, name='tableau_bord_absences'),
    path('absences/tableau-de-bord/pdf/', views_absences.tableau_bord_absences_pdf, name='tableau_bord_absences_pdf'),
]
