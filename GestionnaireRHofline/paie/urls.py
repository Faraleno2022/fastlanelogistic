from django.urls import path
from . import views
from .views_irpp import bareme_irpp
from . import views_envoi
from . import views_export
from . import views_pret
from . import views_frais
from . import views_parametres
from . import views_rapports
from . import views_simulation
from . import views_etax

app_name = 'paie'

urlpatterns = [
    # Accueil
    path('', views.paie_home, name='home'),
    
    # Périodes de paie
    path('periodes/', views.liste_periodes, name='liste_periodes'),
    path('periodes/creer/', views.creer_periode, name='creer_periode'),
    path('periodes/<int:pk>/', views.detail_periode, name='detail_periode'),
    path('periodes/<int:pk>/calculer/', views.calculer_periode, name='calculer_periode'),
    path('periodes/<int:pk>/valider/', views.valider_periode, name='valider_periode'),
    path('periodes/<int:pk>/cloturer/', views.cloturer_periode, name='cloturer_periode'),
    
    # Bulletins de paie
    path('bulletins/', views.liste_bulletins, name='liste_bulletins'),
    path('bulletins/<int:pk>/', views.detail_bulletin, name='detail_bulletin'),
    path('bulletins/<int:pk>/recalculer-cnss/', views.recalculer_cnss_bulletin, name='recalculer_cnss_bulletin'),
    path('bulletins/<int:pk>/imprimer/', views.imprimer_bulletin, name='imprimer_bulletin'),
    path('bulletins/<int:pk>/telecharger-pdf/', views.telecharger_bulletin_pdf, name='telecharger_bulletin_pdf'),
    path('bulletins/public/<str:token>/', views.telecharger_bulletin_public, name='telecharger_bulletin_public'),
    
    # Envoi des bulletins
    path('bulletins/<int:pk>/envoyer-email/', views_envoi.envoyer_bulletin_email, name='envoyer_email'),
    path('bulletins/<int:pk>/envoyer-whatsapp/', views_envoi.envoyer_bulletin_whatsapp, name='envoyer_whatsapp'),
    path('bulletins/envoyer-masse/', views_envoi.envoyer_bulletins_masse, name='envoyer_masse'),
    path('bulletins/envoyer-masse/email/', views_envoi.envoyer_masse_email, name='envoyer_masse_email'),
    path('bulletins/envoyer-masse/whatsapp/', views_envoi.generer_liens_whatsapp_masse, name='generer_liens_whatsapp'),
    
    # Livre de paie
    path('livre/', views.livre_paie, name='livre_paie'),
    path('livre/telecharger-pdf/', views.telecharger_livre_paie_pdf, name='telecharger_livre_paie_pdf'),
    
    # Déclarations sociales
    path('declarations/', views.declarations_sociales, name='declarations_sociales'),
    path('declarations/pdf/', views.declarations_sociales_pdf, name='declarations_sociales_pdf'),
    path('declarations/etax/', views_etax.declaration_etax, name='declaration_etax'),
    path('declarations/etax/generer/', views_etax.generer_declaration_etax, name='generer_declaration_etax'),
    path('declarations/etax/<int:pk>/suivi/', views_etax.mettre_a_jour_declaration_etax, name='mettre_a_jour_declaration_etax'),
    path('declarations/etax/excel/', views_etax.declaration_etax_excel, name='declaration_etax_excel'),
    path('declarations/etax/pdf/', views_etax.declaration_etax_pdf, name='declaration_etax_pdf'),
    
    # Éléments de salaire
    path('elements-salaire/', views.liste_elements_salaire, name='liste_elements_salaire'),
    path('elements-salaire/employe/<int:employe_id>/', views.elements_salaire_employe, name='elements_salaire_employe'),
    path('elements-salaire/ajouter/<int:employe_id>/', views.ajouter_element_salaire, name='ajouter_element_salaire'),
    path('elements-salaire/<int:pk>/modifier/', views.modifier_element_salaire, name='modifier_element_salaire'),
    path('elements-salaire/<int:pk>/supprimer/', views.supprimer_element_salaire, name='supprimer_element_salaire'),
    
    # Rubriques de paie
    path('rubriques/', views.liste_rubriques, name='liste_rubriques'),
    path('rubriques/creer/', views.creer_rubrique, name='creer_rubrique'),
    path('rubriques/<int:pk>/', views.detail_rubrique, name='detail_rubrique'),
    path('rubriques/<int:pk>/supprimer/', views.supprimer_rubrique, name='supprimer_rubrique'),
    
    # Barème IRPP
    path('bareme-irpp/', bareme_irpp.bareme_irpp_liste, name='bareme_irpp_liste'),
    path('bareme-irpp/ajouter/', bareme_irpp.bareme_irpp_ajouter, name='bareme_irpp_ajouter'),
    path('bareme-irpp/<int:pk>/modifier/', bareme_irpp.bareme_irpp_modifier, name='bareme_irpp_modifier'),
    path('bareme-irpp/<int:pk>/supprimer/', bareme_irpp.bareme_irpp_supprimer, name='bareme_irpp_supprimer'),
    path('bareme-irpp/dupliquer/', bareme_irpp.bareme_irpp_dupliquer, name='bareme_irpp_dupliquer'),
    path('simulateur-irpp/', bareme_irpp.simulateur_irpp, name='simulateur_irpp'),
    path('api/calculer-irpp/', bareme_irpp.api_calculer_irpp, name='api_calculer_irpp'),
    
    # Alertes échéances
    path('echeances/', views.tableau_bord_echeances, name='tableau_bord_echeances'),
    path('echeances/<int:pk>/traiter/', views.marquer_alerte_traitee, name='marquer_alerte_traitee'),
    path('api/alertes-echeances/', views.api_alertes_echeances, name='api_alertes_echeances'),
    
    # Export CNSS
    path('export/cnss/excel/', views_export.export_cnss_excel, name='export_cnss_excel'),
    path('export/cnss/pdf/', views_export.export_cnss_pdf, name='export_cnss_pdf'),
    
    # Export DMU (Déclaration Mensuelle Unique)
    path('export/dmu/excel/', views_export.export_dmu_excel, name='export_dmu_excel'),
    path('export/dmu/pdf/', views_export.export_dmu_pdf, name='export_dmu_pdf'),
    
    # Historique des bulletins
    path('historique/', views.historique_bulletins, name='historique_bulletins'),
    path('historique/telecharger-masse/', views.telecharger_bulletins_masse, name='telecharger_bulletins_masse'),
    path('attestation/<int:employe_id>/', views.attestation_salaire, name='attestation_salaire'),
    
    # Simulation de paie (simple)
    path('simulation/', views.simulation_paie, name='simulation_paie'),

    # Simulation fiscale comparative multi-barèmes
    path('simulation/comparative/', views_simulation.simulation_comparative, name='simulation_comparative'),
    path('simulation/historique/', views_simulation.historique_simulations, name='historique_simulations'),
    path('simulation/historique/<int:pk>/', views_simulation.detail_simulation, name='detail_simulation'),
    path('simulation/historique/<int:pk>/supprimer/', views_simulation.supprimer_simulation, name='supprimer_simulation'),
    path('simulation/historique/<int:pk>/csv/', views_simulation.export_simulation_csv, name='export_simulation_csv'),
    path('api/baremes-disponibles/', views_simulation.api_baremes_disponibles, name='api_baremes_disponibles'),
    path('api/employe-salaire/<int:pk>/', views_simulation.api_employe_salaire, name='api_employe_salaire'),
    path('api/optimiser-net/', views_simulation.api_optimiser_net, name='api_optimiser_net'),
    path('api/scenario-augmentation/', views_simulation.api_scenario_augmentation, name='api_scenario_augmentation'),
    
    # Gestion des prêts
    path('prets/', views_pret.liste_prets, name='liste_prets'),
    path('prets/creer/', views_pret.creer_pret, name='creer_pret'),
    path('prets/<int:pk>/', views_pret.detail_pret, name='detail_pret'),
    path('prets/<int:pk>/approuver/', views_pret.approuver_pret, name='approuver_pret'),
    path('prets/<int:pk>/rejeter/', views_pret.rejeter_pret, name='rejeter_pret'),
    path('prets/<int:pk>/rembourser/', views_pret.enregistrer_remboursement, name='enregistrer_remboursement'),
    path('prets/a-prelever/', views_pret.prets_a_prelever, name='prets_a_prelever'),
    
    # Notes de frais
    path('frais/', views_frais.liste_notes_frais, name='liste_notes_frais'),
    path('frais/creer/', views_frais.creer_note_frais, name='creer_note_frais'),
    path('frais/<int:pk>/', views_frais.detail_note_frais, name='detail_note_frais'),
    path('frais/<int:pk>/ajouter-ligne/', views_frais.ajouter_ligne_frais, name='ajouter_ligne_frais'),
    path('frais/<int:pk>/supprimer-ligne/<int:ligne_pk>/', views_frais.supprimer_ligne_frais, name='supprimer_ligne_frais'),
    path('frais/<int:pk>/soumettre/', views_frais.soumettre_note_frais, name='soumettre_note_frais'),
    path('frais/<int:pk>/valider/', views_frais.valider_note_frais, name='valider_note_frais'),
    path('frais/<int:pk>/rembourser/', views_frais.rembourser_note_frais, name='rembourser_note_frais'),
    path('frais/<int:pk>/supprimer/', views_frais.supprimer_note_frais, name='supprimer_note_frais'),
    path('frais/recap/', views_frais.recap_frais, name='recap_frais'),
    path('frais/categories/', views_frais.gestion_categories_frais, name='gestion_categories_frais'),
    
    # Archives bulletins - Traçabilité
    path('archives/', views.liste_archives, name='liste_archives'),
    path('archives/<int:pk>/telecharger/', views.telecharger_archive, name='telecharger_archive'),
    path('archives/<int:pk>/verifier/', views.verifier_integrite_archive, name='verifier_integrite_archive'),
    
    # Configuration paie entreprise
    path('configuration/', views.config_paie_entreprise, name='config_entreprise'),

    # Paramètres moteur de calcul (formules personnalisées)
    path('parametres/calcul/', views_parametres.parametres_calcul_paie, name='parametres_calcul'),
    path('parametres/calcul/tester-formule/', views_parametres.tester_formule_ajax, name='tester_formule'),
    path('parametres/calcul/valider-formule/', views_parametres.valider_formule_ajax, name='valider_formule'),
    path('parametres/calcul/historique/', views_parametres.historique_parametres_paie, name='historique_parametres'),

    # Constantes de paie
    path('parametres/constantes/', views_parametres.liste_constantes, name='liste_constantes'),
    path('parametres/constantes/<int:pk>/modifier/', views_parametres.modifier_constante, name='modifier_constante'),

    # Barème RTS
    path('parametres/bareme-rts/', views_parametres.liste_tranches_rts, name='liste_tranches_rts'),
    path('parametres/bareme-rts/ajouter/', views_parametres.ajouter_tranche_rts, name='ajouter_tranche_rts'),
    path('parametres/bareme-rts/<int:pk>/modifier/', views_parametres.modifier_tranche_rts, name='modifier_tranche_rts'),
    path('parametres/bareme-rts/dupliquer/', views_parametres.dupliquer_bareme_rts, name='dupliquer_bareme_rts'),

    # Rapports avancés
    path('rapports/masse-salariale/', views_rapports.rapport_masse_salariale, name='rapport_masse_salariale'),
    path('rapports/masse-salariale/excel/', views_rapports.rapport_masse_salariale_excel, name='rapport_masse_salariale_excel'),
    path('rapports/masse-salariale/pdf/', views_rapports.rapport_masse_salariale_pdf, name='rapport_masse_salariale_pdf'),

    # État de paie
    path('rapports/etat-paie/', views_rapports.rapport_etat_paie, name='rapport_etat_paie'),
    path('rapports/etat-paie/excel/', views_rapports.rapport_etat_paie_excel, name='rapport_etat_paie_excel'),
    path('rapports/etat-paie/pdf/', views_rapports.rapport_etat_paie_pdf, name='rapport_etat_paie_pdf'),

    # Feuille de présence
    path('rapports/feuille-presence/', views_rapports.rapport_feuille_presence, name='rapport_feuille_presence'),
    path('rapports/feuille-presence/excel/', views_rapports.rapport_feuille_presence_excel, name='rapport_feuille_presence_excel'),
    path('rapports/feuille-presence/pdf/', views_rapports.rapport_feuille_presence_pdf, name='rapport_feuille_presence_pdf'),

    # Récapitulatif entreprise (synthèse globale + gains optimisation)
    path('rapports/recapitulatif/', views_rapports.recapitulatif_entreprise, name='recapitulatif_entreprise'),
    path('rapports/recapitulatif/pdf/', views_rapports.recapitulatif_entreprise_pdf, name='recapitulatif_entreprise_pdf'),

    # Bulletins groupés (impression multiple)
    path('bulletins/groupe/pdf/', views.bulletins_groupes_pdf, name='bulletins_groupes_pdf'),

    # Rétro-paie : calcul brut depuis net convenu
    path('api/retropaie/', views.api_retropaie, name='api_retropaie'),
    path('api/retropaie/pdf/', views.retropaie_pdf, name='retropaie_pdf'),
    # Coût total employeur → brut + net
    path('api/cout-total/', views.api_cout_total, name='api_cout_total'),

    # Décomposition intelligente du brut
    path('api/decomposer-brut/', views.api_decomposer_brut, name='api_decomposer_brut'),
    path('api/creer-elements-lot/<int:employe_id>/', views.api_creer_elements_lot, name='api_creer_elements_lot'),
    path('api/impact-fiscal/', views.api_impact_fiscal, name='api_impact_fiscal'),
    path('api/optimiser-decomposition/', views.api_optimiser_decomposition, name='api_optimiser_decomposition'),
    path('api/proposition-complete/', views.api_proposition_complete, name='api_proposition_complete'),
    path('api/valider-simulation/', views.api_valider_simulation, name='api_valider_simulation'),
    path('api/historique-simulations/<int:employe_id>/', views.api_historique_simulations_employe, name='api_historique_simulations_employe'),
    path('api/avancer-dates-elements/', views.api_avancer_dates_elements, name='api_avancer_dates_elements'),
    path('api/simulation-pdf/', views.api_simulation_pdf, name='api_simulation_pdf'),
    path('bulletins/<int:bulletin_id>/audit/', views.bulletin_audit_json, name='bulletin_audit_json'),
    path('bulletins/<int:bulletin_id>/audit/pdf/', views.bulletin_audit_pdf, name='bulletin_audit_pdf'),
]
