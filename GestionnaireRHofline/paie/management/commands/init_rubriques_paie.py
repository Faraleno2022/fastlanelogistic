"""
Commande pour initialiser les rubriques de paie selon la législation guinéenne
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from paie.models import RubriquePaie


class Command(BaseCommand):
    help = 'Initialise les rubriques de paie pour la Guinée'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🇬🇳 Initialisation des rubriques de paie...'))
        
        rubriques = [
            # ===== GAINS - Salaires de base =====
            {'code_rubrique': 'SAL_BASE', 'libelle_rubrique': 'Salaire de base', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 10},
            {'code_rubrique': 'SAL_BASE_CAT_A', 'libelle_rubrique': 'Salaire de base Catégorie A', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 11},
            {'code_rubrique': 'SAL_BASE_CADRE_SUP', 'libelle_rubrique': 'Salaire de base Cadre Supérieur', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 12},
            
            # ===== GAINS - Primes =====
            {'code_rubrique': 'PRIME_TRANSPORT', 'libelle_rubrique': 'Prime de transport', 'type_rubrique': 'gain', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 20},
            {'code_rubrique': 'PRIME_RISQUE', 'libelle_rubrique': 'Prime de risque', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 21},
            {'code_rubrique': 'PRIME_ANCIENNETE', 'libelle_rubrique': 'Prime d\'ancienneté', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 22},
            {'code_rubrique': 'PRIME_RESP', 'libelle_rubrique': 'Prime de responsabilité', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 23},
            {'code_rubrique': 'PRIME_PROD', 'libelle_rubrique': 'Prime de production', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 24},
            {'code_rubrique': 'PRIME_PERFORMANCE', 'libelle_rubrique': 'Prime de performance', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 25},
            {'code_rubrique': 'PRIME_CADRE_SUP', 'libelle_rubrique': 'Prime cadre supérieur', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 26},
            
            # ===== GAINS - Indemnités =====
            {'code_rubrique': 'IND_REPAS', 'libelle_rubrique': 'Indemnité de repas', 'type_rubrique': 'gain', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 30},
            {'code_rubrique': 'IND_REPAS_JOUR', 'libelle_rubrique': 'Indemnité de repas journalière', 'type_rubrique': 'gain', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 31},
            {'code_rubrique': 'IND_FONCTION', 'libelle_rubrique': 'Indemnité de fonction', 'type_rubrique': 'gain', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 32},
            {'code_rubrique': 'IND_FONCTION_DIR', 'libelle_rubrique': 'Indemnité de fonction direction', 'type_rubrique': 'gain', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 33},
            {'code_rubrique': 'IND_DEPLACE', 'libelle_rubrique': 'Indemnité de déplacement', 'type_rubrique': 'gain', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 34},
            {'code_rubrique': 'IND_REPRESENTATION', 'libelle_rubrique': 'Indemnité de représentation', 'type_rubrique': 'gain', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 35},
            
            # ===== GAINS - Allocations =====
            {'code_rubrique': 'ALLOC_LOGEMENT', 'libelle_rubrique': 'Allocation logement', 'type_rubrique': 'gain', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 40},
            {'code_rubrique': 'ALLOC_TRANSPORT', 'libelle_rubrique': 'Allocation transport', 'type_rubrique': 'gain', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 41},
            
            # ===== GAINS - Heures supplémentaires =====
            {'code_rubrique': 'HS_25', 'libelle_rubrique': 'Heures supplémentaires 25%', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 50},
            {'code_rubrique': 'HS_50', 'libelle_rubrique': 'Heures supplémentaires 50%', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 51},
            {'code_rubrique': 'HS_50_CADRE', 'libelle_rubrique': 'Heures supplémentaires cadre 50%', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 52},
            {'code_rubrique': 'HS_100', 'libelle_rubrique': 'Heures supplémentaires 100%', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 53},
            
            # ===== GAINS - Commissions et bonus =====
            {'code_rubrique': 'COMMISSION_CA', 'libelle_rubrique': 'Commission sur CA', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 60},
            {'code_rubrique': 'BONUS_SECURITE', 'libelle_rubrique': 'Bonus de sécurité', 'type_rubrique': 'gain', 'soumis_cnss': True, 'soumis_irg': True, 'ordre_calcul': 61},
            
            # ===== RETENUES - Cotisations sociales =====
            {'code_rubrique': 'CNSS_EMP', 'libelle_rubrique': 'CNSS part employé', 'type_rubrique': 'cotisation', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 100, 'taux_rubrique': Decimal('5.00')},
            {'code_rubrique': 'RTS', 'libelle_rubrique': 'Impôt sur le Revenu Global', 'type_rubrique': 'retenue', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 110},
            
            # ===== RETENUES - Autres =====
            {'code_rubrique': 'AVANCE_SAL', 'libelle_rubrique': 'Avance sur salaire', 'type_rubrique': 'retenue', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 120},
            {'code_rubrique': 'RET_SYNDICAT', 'libelle_rubrique': 'Cotisation syndicale', 'type_rubrique': 'retenue', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 130},
            {'code_rubrique': 'PRET_LOGEMENT', 'libelle_rubrique': 'Remboursement prêt logement', 'type_rubrique': 'retenue', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 140},
            {'code_rubrique': 'RET_DISCIPLINAIRE', 'libelle_rubrique': 'Retenue disciplinaire', 'type_rubrique': 'retenue', 'soumis_cnss': False, 'soumis_irg': False, 'ordre_calcul': 150},
        ]
        
        created_count = 0
        updated_count = 0
        
        for rub_data in rubriques:
            code = rub_data.pop('code_rubrique')
            rub, created = RubriquePaie.objects.update_or_create(
                code_rubrique=code,
                defaults={**rub_data, 'actif': True}
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Terminé: {created_count} rubriques créées, {updated_count} mises à jour'
        ))
