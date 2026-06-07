"""
Commande pour initialiser les éléments de salaire des employés de test
"""
from django.core.management.base import BaseCommand
from datetime import date
from decimal import Decimal

from employes.models import Employe
from paie.models import RubriquePaie, ElementSalaire


class Command(BaseCommand):
    help = 'Initialise les éléments de salaire pour les employés de test'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('💰 Initialisation des éléments de salaire...\n'))
        
        # 1. COMATEX - Diallo Mamadou
        self.init_comatex()
        
        # 2. MINÉRAUX GUINÉE - Diallo Abdoulaye
        self.init_mineraux()
        
        # 3. SGT - Camara Moussa
        self.init_sgt()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Initialisation terminée!'))
    
    def init_comatex(self):
        """Initialiser éléments pour COMATEX"""
        self.stdout.write('📋 COMATEX SARL - Diallo Mamadou...')
        
        try:
            employe = Employe.objects.get(matricule='COMATEX-001')
        except Employe.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠️  Employé non trouvé'))
            return
        
        # Supprimer les anciens éléments
        ElementSalaire.objects.filter(employe=employe).delete()
        
        elements = [
            # Salaire de base
            {
                'code': 'SAL_BASE',
                'montant': Decimal('2500000'),
            },
            # Prime de transport
            {
                'code': 'PRIME_TRANSPORT',
                'montant': Decimal('300000'),
            },
            # Prime de risque
            {
                'code': 'PRIME_RISQUE',
                'montant': Decimal('200000'),
            },
            # Heures supplémentaires (10h × 5000)
            {
                'code': 'HS_25',
                'montant': Decimal('50000'),
            },
            # Indemnité de repas
            {
                'code': 'IND_REPAS',
                'montant': Decimal('150000'),
            },
            # Avance sur salaire
            {
                'code': 'AVANCE_SAL',
                'montant': Decimal('200000'),
            },
            # Retenue syndicale
            {
                'code': 'RET_SYNDICAT',
                'montant': Decimal('50000'),
            },
        ]
        
        count = 0
        for elem_data in elements:
            try:
                rubrique = RubriquePaie.objects.get(code_rubrique=elem_data['code'])
                ElementSalaire.objects.create(
                    employe=employe,
                    rubrique=rubrique,
                    montant=elem_data['montant'],
                    date_debut=date(2024, 1, 1),
                    actif=True,
                    recurrent=True
                )
                count += 1
            except RubriquePaie.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Rubrique {elem_data["code"]} non trouvée'))
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count} éléments créés'))
    
    def init_mineraux(self):
        """Initialiser éléments pour MINÉRAUX GUINÉE"""
        self.stdout.write('⛏️  MINÉRAUX GUINÉE SA - Diallo Abdoulaye...')
        
        try:
            employe = Employe.objects.get(matricule='MG-2021-847')
        except Employe.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠️  Employé non trouvé'))
            return
        
        # Supprimer les anciens éléments
        ElementSalaire.objects.filter(employe=employe).delete()
        
        elements = [
            # Salaire de base
            {
                'code': 'SAL_BASE_CAT_A',
                'montant': Decimal('4500000'),
            },
            # Indemnité de fonction
            {
                'code': 'IND_FONCTION',
                'montant': Decimal('800000'),
            },
            # Prime d'ancienneté (5%)
            {
                'code': 'PRIME_ANCIENNETE',
                'montant': Decimal('225000'),
            },
            # Prime de responsabilité
            {
                'code': 'PRIME_RESP',
                'montant': Decimal('600000'),
            },
            # Prime de production
            {
                'code': 'PRIME_PROD',
                'montant': Decimal('750000'),
            },
            # Bonus de sécurité
            {
                'code': 'BONUS_SECURITE',
                'montant': Decimal('300000'),
            },
            # Commission sur CA
            {
                'code': 'COMMISSION_CA',
                'montant': Decimal('625000'),
            },
            # Indemnité déplacement
            {
                'code': 'IND_DEPLACE',
                'montant': Decimal('800000'),
            },
            # Indemnité repas
            {
                'code': 'IND_REPAS_JOUR',
                'montant': Decimal('1100000'),
            },
            # Allocation logement
            {
                'code': 'ALLOC_LOGEMENT',
                'montant': Decimal('400000'),
            },
            # Allocation transport
            {
                'code': 'ALLOC_TRANSPORT',
                'montant': Decimal('250000'),
            },
            # Heures supplémentaires
            {
                'code': 'HS_25',
                'montant': Decimal('487717'),
            },
            # Avance
            {
                'code': 'AVANCE_SAL',
                'montant': Decimal('300000'),
            },
            # Syndicat
            {
                'code': 'RET_SYNDICAT',
                'montant': Decimal('100000'),
            },
            # Prêt logement
            {
                'code': 'PRET_LOGEMENT',
                'montant': Decimal('400000'),
            },
            # Retenue disciplinaire
            {
                'code': 'RET_DISCIPLINAIRE',
                'montant': Decimal('150000'),
            },
        ]
        
        count = 0
        for elem_data in elements:
            try:
                rubrique = RubriquePaie.objects.get(code_rubrique=elem_data['code'])
                ElementSalaire.objects.create(
                    employe=employe,
                    rubrique=rubrique,
                    montant=elem_data['montant'],
                    date_debut=date(2020, 3, 15),
                    actif=True,
                    recurrent=True
                )
                count += 1
            except RubriquePaie.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Rubrique {elem_data["code"]} non trouvée'))
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count} éléments créés'))
    
    def init_sgt(self):
        """Initialiser éléments pour SGT (simplifié pour test)"""
        self.stdout.write('📡 SGT SA - Camara Moussa...')
        
        try:
            employe = Employe.objects.get(matricule='SGT-EXP-2019-512')
        except Employe.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠️  Employé non trouvé'))
            return
        
        # Supprimer les anciens éléments
        ElementSalaire.objects.filter(employe=employe).delete()
        
        # Version simplifiée pour test initial
        elements = [
            # Salaire de base
            {
                'code': 'SAL_BASE_CADRE_SUP',
                'montant': Decimal('8000000'),
            },
            # Indemnité de fonction (exonérée)
            {
                'code': 'IND_FONCTION_DIR',
                'montant': Decimal('2000000'),
            },
            # Prime de cadre
            {
                'code': 'PRIME_CADRE_SUP',
                'montant': Decimal('1500000'),
            },
            # Indemnité de représentation
            {
                'code': 'IND_REPRESENTATION',
                'montant': Decimal('1200000'),
            },
            # Prime de performance
            {
                'code': 'PRIME_PERFORMANCE',
                'montant': Decimal('1200000'),
            },
            # Commission bonus groupe
            {
                'code': 'COMMISSION_BONUS_GRP',
                'montant': Decimal('750000'),
            },
            # Intéressement
            {
                'code': 'INTERESSEMENT',
                'montant': Decimal('448000'),
            },
            # Indemnité siège
            {
                'code': 'IND_SIEGE_CONAKRY',
                'montant': Decimal('800000'),
            },
            # Allocation antenne
            {
                'code': 'ALLOC_ANTENNE_KINDIA',
                'montant': Decimal('750000'),
            },
            # Indemnité risque
            {
                'code': 'IND_RISQUE_TELECOM',
                'montant': Decimal('240000'),
            },
            # Formation continue
            {
                'code': 'IND_FORMATION_CONT',
                'montant': Decimal('1000000'),
            },
            # Allocation éducation
            {
                'code': 'ALLOC_EDUC_ENFANTS',
                'montant': Decimal('400000'),
            },
            # Vêtements/équipement
            {
                'code': 'IND_VETEMENTS_EQUIP',
                'montant': Decimal('300000'),
            },
            # Heures supplémentaires
            {
                'code': 'HS_50_CADRE',
                'montant': Decimal('762007'),
            },
            # Prêt logement
            {
                'code': 'PRET_LOGEMENT_REMBOURS',
                'montant': Decimal('1200000'),
            },
            # Avance
            {
                'code': 'AVANCE_SAL_REGUL',
                'montant': Decimal('500000'),
            },
            # Retenue disciplinaire
            {
                'code': 'RET_DISCIPL_LEGER',
                'montant': Decimal('100000'),
            },
            # Ordre professionnel
            {
                'code': 'COTIS_ORDRE_PROF',
                'montant': Decimal('75000'),
            },
            # Épargne retraite volontaire
            {
                'code': 'EPARGNE_RETRAITE_VOL',
                'montant': Decimal('500000'),
            },
            # Plan épargne salarié
            {
                'code': 'PLAN_EPARGNE_SAL',
                'montant': Decimal('800000'),
            },
            # Mutuelle supplémentaire
            {
                'code': 'MUTUELLE_SUPP_VOL',
                'montant': Decimal('200000'),
            },
        ]
        
        count = 0
        for elem_data in elements:
            try:
                rubrique = RubriquePaie.objects.get(code_rubrique=elem_data['code'])
                ElementSalaire.objects.create(
                    employe=employe,
                    rubrique=rubrique,
                    montant=elem_data['montant'],
                    date_debut=date(2019, 6, 1),
                    actif=True,
                    recurrent=True
                )
                count += 1
            except RubriquePaie.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Rubrique {elem_data["code"]} non trouvée'))
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count} éléments créés'))
