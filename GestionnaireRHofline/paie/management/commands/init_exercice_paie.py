"""
Commande pour initialiser les données de l'exercice de paie
Entreprise COMATEX SARL - Employé Diallo Mamadou
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from decimal import Decimal

from core.models import Societe, Etablissement, Service, Poste
from employes.models import Employe
from paie.models import (
    ParametrePaie, Constante, RubriquePaie, Variable,
    PeriodePaie, BulletinPaie
)


class Command(BaseCommand):
    help = 'Initialise les données de l\'exercice de paie COMATEX SARL'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏢 Initialisation exercice de paie COMATEX SARL...'))
        
        # 1. Créer la société
        societe = self.creer_societe()
        
        # 2. Créer l'établissement
        etablissement = self.creer_etablissement(societe)
        
        # 3. Créer le service
        service = self.creer_service(etablissement)
        
        # 4. Créer le poste
        poste = self.creer_poste(service)
        
        # 5. Créer l'employé
        employe = self.creer_employe(etablissement, service, poste)
        
        # 6. Créer les rubriques de paie
        self.creer_rubriques_paie()
        
        # 7. Créer la période octobre 2025
        periode = self.creer_periode_octobre_2025()
        
        # 8. Mettre à jour les constantes si nécessaire
        self.verifier_constantes()
        
        self.stdout.write(self.style.SUCCESS('✅ Initialisation terminée avec succès!'))
        self.stdout.write(self.style.SUCCESS(f'   Société : {societe.raison_sociale}'))
        self.stdout.write(self.style.SUCCESS(f'   Employé : {employe.nom} {employe.prenoms}'))
        self.stdout.write(self.style.SUCCESS(f'   Période : {periode}'))

    def creer_societe(self):
        """Créer la société COMATEX SARL"""
        self.stdout.write('🏢 Création de la société COMATEX SARL...')
        
        societe, created = Societe.objects.get_or_create(
            raison_sociale='COMATEX SARL',
            defaults={
                'forme_juridique': 'SARL',
                'ville': 'Conakry',
                'pays': 'Guinée',
                'actif': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Société COMATEX SARL créée'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Société COMATEX SARL déjà existante'))
        
        return societe

    def creer_etablissement(self, societe):
        """Créer l'établissement principal"""
        self.stdout.write('🏭 Création de l\'établissement...')
        
        etablissement, created = Etablissement.objects.get_or_create(
            societe=societe,
            code_etablissement='COMATEX-001',
            defaults={
                'nom_etablissement': 'Siège COMATEX',
                'type_etablissement': 'Siège',
                'ville': 'Conakry',
                'actif': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Établissement créé'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Établissement déjà existant'))
        
        return etablissement

    def creer_service(self, etablissement):
        """Créer le service Maintenance"""
        self.stdout.write('🔧 Création du service Maintenance...')
        
        service, created = Service.objects.get_or_create(
            etablissement=etablissement,
            code_service='MAINT',
            defaults={
                'nom_service': 'Maintenance',
                'actif': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Service Maintenance créé'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Service Maintenance déjà existant'))
        
        return service

    def creer_poste(self, service):
        """Créer le poste Technicien en maintenance"""
        self.stdout.write('👷 Création du poste...')
        
        poste, created = Poste.objects.get_or_create(
            code_poste='TECH-MAINT',
            defaults={
                'intitule_poste': 'Technicien en maintenance',
                'service': service,
                'categorie_professionnelle': 'Agent de maîtrise',
                'actif': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Poste Technicien en maintenance créé'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Poste déjà existant'))
        
        return poste

    def creer_employe(self, etablissement, service, poste):
        """Créer l'employé Diallo Mamadou"""
        self.stdout.write('👤 Création de l\'employé Diallo Mamadou...')
        
        employe, created = Employe.objects.get_or_create(
            matricule='COMATEX-001',
            defaults={
                'civilite': 'M.',
                'nom': 'Diallo',
                'prenoms': 'Mamadou',
                'sexe': 'M',
                'situation_matrimoniale': 'Marié(e)',
                'nombre_enfants': 2,
                'date_naissance': date(1990, 1, 1),
                'nationalite': 'Guinéenne',
                'num_cnss_individuel': '123456789',
                'etablissement': etablissement,
                'service': service,
                'poste': poste,
                'date_embauche': date(2024, 1, 1),
                'type_contrat': 'CDI',
                'statut_employe': 'Actif',
                'telephone_principal': '+224 620 00 00 00',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Employé Diallo Mamadou créé'))
            self.stdout.write(self.style.SUCCESS(f'     Matricule : {employe.matricule}'))
            self.stdout.write(self.style.SUCCESS(f'     CNSS : {employe.num_cnss_individuel}'))
            self.stdout.write(self.style.SUCCESS(f'     Situation : {employe.situation_matrimoniale}, {employe.nombre_enfants} enfants'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Employé déjà existant'))
        
        return employe

    def creer_rubriques_paie(self):
        """Créer les rubriques de paie nécessaires"""
        self.stdout.write('💰 Création des rubriques de paie...')
        
        rubriques = [
            # GAINS
            {
                'code_rubrique': 'SALBASE',
                'libelle_rubrique': 'Salaire de base',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_irg': True,
                'ordre_calcul': 10,
                'ordre_affichage': 10,
            },
            {
                'code_rubrique': 'PRIME_TRANSP',
                'libelle_rubrique': 'Prime de transport',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_irg': True,
                'ordre_calcul': 20,
                'ordre_affichage': 20,
            },
            {
                'code_rubrique': 'PRIME_RISQUE',
                'libelle_rubrique': 'Prime de risque',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_irg': True,
                'ordre_calcul': 30,
                'ordre_affichage': 30,
            },
            {
                'code_rubrique': 'HEURES_SUP',
                'libelle_rubrique': 'Heures supplémentaires',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_irg': True,
                'ordre_calcul': 40,
                'ordre_affichage': 40,
            },
            {
                'code_rubrique': 'IND_REPAS',
                'libelle_rubrique': 'Indemnité de repas',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_irg': True,
                'ordre_calcul': 50,
                'ordre_affichage': 50,
            },
            
            # RETENUES
            {
                'code_rubrique': 'CNSS_EMP',
                'libelle_rubrique': 'Cotisation CNSS (salarié)',
                'type_rubrique': 'retenue',
                'taux_rubrique': Decimal('5.50'),  # 5.5% selon l'exercice
                'soumis_cnss': False,
                'soumis_irg': False,
                'ordre_calcul': 100,
                'ordre_affichage': 100,
            },
            {
                'code_rubrique': 'RTS',
                'libelle_rubrique': 'Impôt sur le revenu (RTS/IRSA)',
                'type_rubrique': 'retenue',
                'soumis_cnss': False,
                'soumis_irg': False,
                'ordre_calcul': 110,
                'ordre_affichage': 110,
            },
            {
                'code_rubrique': 'AVANCE',
                'libelle_rubrique': 'Avance sur salaire',
                'type_rubrique': 'retenue',
                'soumis_cnss': False,
                'soumis_irg': False,
                'ordre_calcul': 120,
                'ordre_affichage': 120,
            },
            {
                'code_rubrique': 'RET_SYNDICAT',
                'libelle_rubrique': 'Retenue syndicale',
                'type_rubrique': 'retenue',
                'soumis_cnss': False,
                'soumis_irg': False,
                'ordre_calcul': 130,
                'ordre_affichage': 130,
            },
            
            # COTISATIONS PATRONALES
            {
                'code_rubrique': 'CNSS_PAT',
                'libelle_rubrique': 'Cotisation CNSS (employeur)',
                'type_rubrique': 'cotisation',
                'taux_rubrique': Decimal('18.00'),
                'soumis_cnss': False,
                'soumis_irg': False,
                'ordre_calcul': 200,
                'ordre_affichage': 200,
            },
        ]
        
        count_created = 0
        for rub_data in rubriques:
            rub, created = RubriquePaie.objects.get_or_create(
                code_rubrique=rub_data['code_rubrique'],
                defaults=rub_data
            )
            if created:
                count_created += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {rub_data["libelle_rubrique"]}'))
        
        if count_created == 0:
            self.stdout.write(self.style.WARNING('  ⚠ Toutes les rubriques existent déjà'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ✓ {count_created} rubriques créées'))

    def creer_periode_octobre_2025(self):
        """Créer la période de paie Octobre 2025"""
        self.stdout.write('📅 Création de la période Octobre 2025...')
        
        periode, created = PeriodePaie.objects.get_or_create(
            annee=2025,
            mois=10,
            defaults={
                'libelle': 'Octobre 2025',
                'date_debut': date(2025, 10, 1),
                'date_fin': date(2025, 10, 31),
                'statut_periode': 'ouverte',
                'nombre_jours_travailles': 22,
                'nombre_heures_mois': Decimal('173.33'),
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Période Octobre 2025 créée'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Période Octobre 2025 déjà existante'))
        
        return periode

    def verifier_constantes(self):
        """Vérifier et ajouter les constantes manquantes"""
        self.stdout.write('🔍 Vérification des constantes...')
        
        # Ajouter la constante pour la réduction enfants
        const, created = Constante.objects.get_or_create(
            code='REDUC_ENFANT_RTS',
            defaults={
                'libelle': 'Réduction RTS par enfant à charge',
                'valeur': Decimal('5.00'),
                'type_valeur': 'pourcentage',
                'categorie': 'irg',
                'unite': '%',
                'date_debut_validite': date(2025, 1, 1),
                'actif': True,
                'description': 'Réduction d\'impôt de 5% par enfant à charge (plafonné à 2 enfants)'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Constante REDUC_ENFANT_RTS créée'))
        
        # Note sur le taux CNSS
        self.stdout.write(self.style.WARNING('  ⚠ NOTE: L\'exercice utilise CNSS 5.5% au lieu de 5%'))
        self.stdout.write(self.style.WARNING('     La rubrique CNSS_EMP a été créée avec 5.5%'))
