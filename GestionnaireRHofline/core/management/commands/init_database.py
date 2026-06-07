"""
Commande Django pour initialiser la base de données avec les données de base
Usage: python manage.py init_database
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from datetime import datetime, date
import os


class Command(BaseCommand):
    help = 'Initialise la base de données avec les données de référence pour la Guinée'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Réinitialiser toutes les données (ATTENTION: supprime les données existantes)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Initialisation de la base de données RH Guinée ===\n'))

        if options['reset']:
            self.stdout.write(self.style.WARNING('Mode RESET activé - Suppression des données existantes...'))
            if input('Êtes-vous sûr? (oui/non): ').lower() != 'oui':
                self.stdout.write(self.style.ERROR('Opération annulée'))
                return

        try:
            # 1. Paramètres de paie Guinée
            self.stdout.write('1. Création des paramètres de paie...')
            self.create_parametres_paie()

            # 2. Tranches RTS Guinée
            self.stdout.write('2. Création des tranches RTS...')
            self.create_tranches_irg()

            # 3. Jours fériés Guinée 2025
            self.stdout.write('3. Création du calendrier des jours fériés...')
            self.create_jours_feries()

            # 4. Rubriques de paie standard
            self.stdout.write('4. Création des rubriques de paie...')
            self.create_rubriques_paie()

            # 5. Types de prêts
            self.stdout.write('5. Création des types de prêts...')
            self.create_types_prets()

            # 6. Types de départ
            self.stdout.write('6. Création des types de départ...')
            self.create_types_depart()

            # 7. Types de sanctions
            self.stdout.write('7. Création des types de sanctions...')
            self.create_types_sanctions()

            # 8. Profils utilisateurs
            self.stdout.write('8. Création des profils utilisateurs...')
            self.create_profils_utilisateurs()

            # 9. Horaires de travail standard
            self.stdout.write('9. Création des horaires de travail...')
            self.create_horaires_travail()

            # 10. Indicateurs RH
            self.stdout.write('10. Création des indicateurs RH...')
            self.create_indicateurs_rh()

            self.stdout.write(self.style.SUCCESS('\n✓ Initialisation terminée avec succès!'))
            self.stdout.write(self.style.SUCCESS('La base de données est prête à être utilisée.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Erreur lors de l\'initialisation: {str(e)}'))
            raise

    def execute_sql(self, sql, params=None):
        """Exécute une requête SQL"""
        with connection.cursor() as cursor:
            cursor.execute(sql, params or [])

    def create_parametres_paie(self):
        """Crée les paramètres de paie pour la Guinée"""
        parametres = [
            # SMIG et salaires
            ('SMIG', 'Salaire Minimum Interprofessionnel Garanti', None, 440000, 'Numérique', 'Général', 'GNF'),
            ('PLAFOND_CNSS', 'Plafond de cotisation CNSS', None, 3000000, 'Numérique', 'CNSS', 'GNF'),
            
            # Taux CNSS
            ('TAUX_CNSS_EMPLOYE', 'Taux de cotisation CNSS employé', None, 5.00, 'Numérique', 'CNSS', '%'),
            ('TAUX_CNSS_EMPLOYEUR', 'Taux de cotisation CNSS employeur', None, 18.00, 'Numérique', 'CNSS', '%'),
            
            # INAM
            ('TAUX_INAM', 'Taux de cotisation INAM', None, 2.50, 'Numérique', 'INAM', '%'),
            ('PLAFOND_INAM', 'Plafond de cotisation INAM', None, 3000000, 'Numérique', 'INAM', 'GNF'),
            
            # RTS
            ('ABATTEMENT_RTS', 'Abattement forfaitaire RTS', None, 20.00, 'Numérique', 'RTS', '%'),
            ('PLAFOND_ABATTEMENT_RTS', 'Plafond abattement RTS', None, 300000, 'Numérique', 'RTS', 'GNF'),
            
            # Temps de travail
            ('HEURES_MOIS_STANDARD', 'Nombre d\'heures standard par mois', None, 173.33, 'Numérique', 'Général', 'Heures'),
            ('JOURS_MOIS_STANDARD', 'Nombre de jours standard par mois', None, 22, 'Numérique', 'Général', 'Jours'),
            ('JOURS_CONGES_ANNUELS', 'Nombre de jours de congés annuels (1,5j/mois)', None, 18, 'Numérique', 'Général', 'Jours'),
            
            # Heures supplémentaires (Code du Travail Art. 221)
            ('TAUX_HS_4PREM', 'Majoration 4 premières HS/semaine', None, 30.00, 'Numérique', 'Général', '%'),
            ('TAUX_HS_AUDELA', 'Majoration au-delà 4 HS/semaine', None, 60.00, 'Numérique', 'Général', '%'),
            ('TAUX_HS_NUIT', 'Majoration heures de nuit (20h-6h)', None, 20.00, 'Numérique', 'Général', '%'),
            ('TAUX_HS_FERIE_JOUR', 'Majoration jour férié (jour)', None, 60.00, 'Numérique', 'Général', '%'),
            ('TAUX_HS_FERIE_NUIT', 'Majoration jour férié (nuit)', None, 100.00, 'Numérique', 'Général', '%'),
        ]

        sql = """
            INSERT INTO parametres_paie 
            (code_parametre, libelle_parametre, valeur_parametre, valeur_numerique, 
             type_parametre, categorie, unite, actif, date_debut_validite)
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, CURRENT_DATE)
            ON CONFLICT (code_parametre) DO NOTHING
        """

        for param in parametres:
            self.execute_sql(sql, param)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(parametres)} paramètres créés'))

    def create_tranches_irg(self):
        """Crée les tranches RTS pour la Guinée (2025)"""
        tranches = [
            (1, 0, 1000000, 0.00, 2025),
            (2, 1000001, 3000000, 5.00, 2025),
            (3, 3000001, 6000000, 10.00, 2025),
            (4, 6000001, 12000000, 15.00, 2025),
            (5, 12000001, 25000000, 20.00, 2025),
            (6, 25000001, None, 25.00, 2025),
        ]

        sql = """
            INSERT INTO tranches_irg 
            (numero_tranche, borne_inferieure, borne_superieure, taux_irg, 
             annee_validite, actif, date_debut_validite)
            VALUES (%s, %s, %s, %s, %s, TRUE, CURRENT_DATE)
            ON CONFLICT DO NOTHING
        """

        for tranche in tranches:
            self.execute_sql(sql, tranche)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(tranches)} tranches RTS créées'))

    def create_jours_feries(self):
        """Crée le calendrier des jours fériés de Guinée pour 2025"""
        jours_feries = [
            ('Jour de l\'An', '2025-01-01', 2025, 'National', True),
            ('Lundi de Pâques', '2025-04-21', 2025, 'Religieux', False),
            ('Fête du Travail', '2025-05-01', 2025, 'National', True),
            ('Aïd el-Fitr (fin Ramadan)', '2025-03-31', 2025, 'Religieux', False),
            ('Aïd el-Kebir (Tabaski)', '2025-06-07', 2025, 'Religieux', False),
            ('Fête de l\'Indépendance', '2025-10-02', 2025, 'National', True),
            ('Maouloud (Naissance du Prophète)', '2025-09-05', 2025, 'Religieux', False),
            ('Noël', '2025-12-25', 2025, 'Religieux', True),
        ]

        sql = """
            INSERT INTO calendrier_jours_feries 
            (libelle, date_jour_ferie, annee, type_ferie, recurrent)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """

        for jour in jours_feries:
            self.execute_sql(sql, jour)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(jours_feries)} jours fériés créés'))

    def create_rubriques_paie(self):
        """Crée les rubriques de paie standard"""
        rubriques = [
            # GAINS
            ('SAL_BASE', 'Salaire de Base', 'Gain', 'Salaire_base', None, None, 100, True, True, False, 1),
            ('PRIME_ANC', 'Prime d\'Ancienneté', 'Gain', 'Prime', None, None, 110, True, True, False, 2),
            ('PRIME_FONC', 'Prime de Fonction', 'Gain', 'Prime', None, None, 120, True, True, False, 3),
            ('PRIME_REND', 'Prime de Rendement', 'Gain', 'Prime', None, None, 130, True, True, False, 4),
            ('IND_TRANS', 'Indemnité de Transport', 'Gain', 'Indemnité', None, None, 140, True, True, False, 5),
            ('IND_LOG', 'Indemnité de Logement', 'Gain', 'Indemnité', None, None, 150, True, True, False, 6),
            ('IND_NOUR', 'Indemnité de Nourriture', 'Gain', 'Indemnité', None, None, 160, True, True, False, 7),
            ('HS_NORM', 'Heures Supplémentaires Normales', 'Gain', 'Heures_sup', None, None, 170, True, True, False, 8),
            ('HS_NUIT', 'Heures Supplémentaires Nuit', 'Gain', 'Heures_sup', None, None, 180, True, True, False, 9),
            
            # RETENUES SOCIALES
            ('CNSS_EMP', 'Cotisation CNSS Employé', 'Retenue', 'CNSS', None, 5.00, 200, False, False, False, 10),
            ('INAM_EMP', 'Cotisation INAM Employé', 'Retenue', 'INAM', None, 2.50, 210, False, False, False, 11),
            ('RTS', 'Impôt sur Revenu (RTS)', 'Retenue', 'RTS', None, None, 220, False, False, False, 12),
            
            # COTISATIONS PATRONALES
            ('CNSS_PAT', 'Cotisation CNSS Employeur', 'Cotisation', 'CNSS', None, 18.00, 300, False, False, False, 13),
            
            # AUTRES RETENUES
            ('ACOMPTE', 'Acompte sur Salaire', 'Retenue', 'Acompte', None, None, 400, False, False, False, 14),
            ('PRET', 'Remboursement Prêt', 'Retenue', 'Prêt', None, None, 410, False, False, False, 15),
            ('SANCTION', 'Retenue Sanction', 'Retenue', 'Sanction', None, None, 420, False, False, False, 16),
            
            # INFORMATIONS
            ('BRUT', 'Salaire Brut', 'Information', 'Calcul', None, None, 500, False, False, False, 17),
            ('NET', 'Net à Payer', 'Information', 'Calcul', None, None, 600, False, False, False, 18),
        ]

        sql = """
            INSERT INTO rubriques_paie 
            (code_rubrique, libelle_rubrique, type_rubrique, nature_rubrique, 
             base_calcul, taux_rubrique, ordre_calcul, soumis_cnss, soumis_irg, 
             soumis_inam, ordre_affichage, actif, affichage_bulletin)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, TRUE)
            ON CONFLICT (code_rubrique) DO NOTHING
        """

        for rubrique in rubriques:
            self.execute_sql(sql, rubrique)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(rubriques)} rubriques de paie créées'))

    def create_types_prets(self):
        """Crée les types de prêts"""
        types_prets = [
            ('PRET_PERS', 'Prêt Personnel', 5000000, 24, 5.00),
            ('PRET_SCOL', 'Prêt Scolaire', 3000000, 12, 3.00),
            ('PRET_LOG', 'Prêt Logement', 10000000, 36, 4.00),
            ('PRET_SANTE', 'Prêt Santé', 2000000, 12, 2.00),
            ('PRET_URGENCE', 'Prêt d\'Urgence', 1000000, 6, 0.00),
        ]

        sql = """
            INSERT INTO types_prets 
            (code_type_pret, libelle_type_pret, montant_maximum, duree_maximum_mois, 
             taux_interet, actif)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (code_type_pret) DO NOTHING
        """

        for type_pret in types_prets:
            self.execute_sql(sql, type_pret)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(types_prets)} types de prêts créés'))

    def create_types_depart(self):
        """Crée les types de départ"""
        types_depart = [
            ('DEM', 'Démission', 'Volontaire', True, True),
            ('LIC_ECO', 'Licenciement Économique', 'Involontaire', True, True),
            ('LIC_FAUTE', 'Licenciement pour Faute', 'Involontaire', False, False),
            ('FIN_CDD', 'Fin de CDD', 'Naturel', True, False),
            ('RETRAITE', 'Départ à la Retraite', 'Naturel', True, False),
            ('DECES', 'Décès', 'Naturel', False, False),
            ('MUT_CONV', 'Mutation Conventionnelle', 'Volontaire', False, True),
            ('ABANDON', 'Abandon de Poste', 'Involontaire', False, False),
        ]

        sql = """
            INSERT INTO types_depart 
            (code_type_depart, libelle_type_depart, categorie, calcul_indemnites, preavis_requis)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (code_type_depart) DO NOTHING
        """

        for type_depart in types_depart:
            self.execute_sql(sql, type_depart)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(types_depart)} types de départ créés'))

    def create_types_sanctions(self):
        """Crée les types de sanctions disciplinaires"""
        types_sanctions = [
            ('AVERT_ORAL', 'Avertissement Oral', 'Avertissement', 1, False, False),
            ('AVERT_ECRIT', 'Avertissement Écrit', 'Avertissement', 2, False, False),
            ('BLAME', 'Blâme', 'Blâme', 3, False, True),
            ('MAP_1J', 'Mise à Pied 1 Jour', 'Mise_à_pied', 4, True, True),
            ('MAP_3J', 'Mise à Pied 3 Jours', 'Mise_à_pied', 5, True, True),
            ('MAP_8J', 'Mise à Pied 8 Jours', 'Mise_à_pied', 6, True, True),
            ('RETRO', 'Rétrogradation', 'Rétrogradation', 7, True, True),
            ('LIC_FAUTE', 'Licenciement pour Faute', 'Licenciement', 10, True, True),
        ]

        sql = """
            INSERT INTO types_sanctions 
            (code_sanction, libelle_sanction, categorie, niveau_gravite, 
             impact_paie, impact_carriere)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (code_sanction) DO NOTHING
        """

        for sanction in types_sanctions:
            self.execute_sql(sql, sanction)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(types_sanctions)} types de sanctions créés'))

    def create_profils_utilisateurs(self):
        """Crée les profils utilisateurs"""
        profils = [
            ('Consultation', 'Accès en lecture seule', 1),
            ('Opérateur RH', 'Saisie et modification des données RH', 2),
            ('Manager', 'Gestion d\'équipe et validations', 3),
            ('Responsable RH', 'Gestion complète RH et paie', 4),
            ('Administrateur', 'Accès complet au système', 5),
        ]

        sql = """
            INSERT INTO profils_utilisateurs 
            (nom_profil, description, niveau_acces, actif)
            VALUES (%s, %s, %s, TRUE)
            ON CONFLICT (nom_profil) DO NOTHING
        """

        for profil in profils:
            self.execute_sql(sql, profil)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(profils)} profils utilisateurs créés'))

    def create_horaires_travail(self):
        """Crée les horaires de travail standard"""
        horaires = [
            ('NORMAL', 'Horaire Normal (8h-17h)', '08:00:00', '17:00:00', '12:00:00', '13:00:00', 8.00, 'Normal'),
            ('MATIN', 'Équipe Matin (6h-14h)', '06:00:00', '14:00:00', '10:00:00', '10:30:00', 7.50, 'Équipe'),
            ('APREM', 'Équipe Après-midi (14h-22h)', '14:00:00', '22:00:00', '18:00:00', '18:30:00', 7.50, 'Équipe'),
            ('NUIT', 'Équipe Nuit (22h-6h)', '22:00:00', '06:00:00', '02:00:00', '02:30:00', 7.50, 'Nuit'),
            ('CONTINU', 'Horaire Continu (8h-16h)', '08:00:00', '16:00:00', None, None, 8.00, 'Normal'),
        ]

        sql = """
            INSERT INTO horaires_travail 
            (code_horaire, libelle_horaire, heure_debut, heure_fin, 
             heure_pause_debut, heure_pause_fin, heures_jour, type_horaire, actif)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (code_horaire) DO NOTHING
        """

        for horaire in horaires:
            self.execute_sql(sql, horaire)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(horaires)} horaires de travail créés'))

    def create_indicateurs_rh(self):
        """Crée les indicateurs RH"""
        indicateurs = [
            ('EFF_TOTAL', 'Effectif Total', 'Effectif', 'Comptage', 'Nombre'),
            ('EFF_HOMME', 'Effectif Hommes', 'Effectif', 'Comptage', 'Nombre'),
            ('EFF_FEMME', 'Effectif Femmes', 'Effectif', 'Comptage', 'Nombre'),
            ('AGE_MOYEN', 'Âge Moyen', 'Effectif', 'Moyenne', 'Années'),
            ('ANC_MOYENNE', 'Ancienneté Moyenne', 'Effectif', 'Moyenne', 'Années'),
            ('MASSE_SAL', 'Masse Salariale', 'Paie', 'Somme', 'GNF'),
            ('SAL_MOYEN', 'Salaire Moyen', 'Paie', 'Moyenne', 'GNF'),
            ('TAUX_ABS', 'Taux d\'Absentéisme', 'Temps', 'Ratio', '%'),
            ('TAUX_TURN', 'Taux de Turnover', 'Turnover', 'Ratio', '%'),
            ('NB_DEPARTS', 'Nombre de Départs', 'Turnover', 'Comptage', 'Nombre'),
            ('NB_RECRUT', 'Nombre de Recrutements', 'Turnover', 'Comptage', 'Nombre'),
            ('HEURES_FORM', 'Heures de Formation', 'Formation', 'Somme', 'Heures'),
        ]

        sql = """
            INSERT INTO indicateurs_rh 
            (code_indicateur, libelle_indicateur, categorie, type_calcul, 
             unite_mesure, actif, frequence_calcul)
            VALUES (%s, %s, %s, %s, %s, TRUE, 'Mensuel')
            ON CONFLICT (code_indicateur) DO NOTHING
        """

        for indicateur in indicateurs:
            self.execute_sql(sql, indicateur)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(indicateurs)} indicateurs RH créés'))
