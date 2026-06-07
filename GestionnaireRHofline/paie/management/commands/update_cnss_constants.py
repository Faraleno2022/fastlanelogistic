"""
Commande pour mettre à jour les constantes CNSS selon la réglementation guinéenne.

Règles CNSS Guinée:
- Plancher: SMIG (550 000 GNF) - assiette minimale de cotisation
- Plafond: 2 500 000 GNF - assiette maximale de cotisation
- Taux employé: 5% (retraite 2.5% + assurance maladie 2.5%)
- Taux employeur: 18% (prestations familiales 6% + AT/MP 4% + retraite 4% + maladie 4%)
"""
from decimal import Decimal
from datetime import date
from django.core.management.base import BaseCommand
from paie.models import Constante


class Command(BaseCommand):
    help = 'Met à jour les constantes CNSS selon la réglementation guinéenne'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(self.style.NOTICE('Mise à jour des constantes CNSS - Guinée'))
        self.stdout.write(self.style.NOTICE('=' * 60))
        
        constantes_cnss = [
            {
                'code': 'SMIG',
                'libelle': 'Salaire Minimum Interprofessionnel Garanti',
                'valeur': Decimal('440000'),
                'type_valeur': 'montant',
                'categorie': 'general',
                'unite': 'GNF',
                'description': 'SMIG mensuel en Guinée - Plancher de cotisation CNSS'
            },
            {
                'code': 'PLAFOND_CNSS',
                'libelle': 'Plafond de cotisation CNSS',
                'valeur': Decimal('2500000'),
                'type_valeur': 'montant',
                'categorie': 'cnss',
                'unite': 'GNF',
                'description': 'Plafond mensuel pour le calcul des cotisations CNSS (2 500 000 GNF)'
            },
            {
                'code': 'PLANCHER_CNSS',
                'libelle': 'Plancher de cotisation CNSS',
                'valeur': Decimal('550000'),
                'type_valeur': 'montant',
                'categorie': 'cnss',
                'unite': 'GNF',
                'description': 'Plancher mensuel (550 000 GNF) - assiette minimale de cotisation CNSS'
            },
            {
                'code': 'TAUX_CNSS_EMPLOYE',
                'libelle': 'Taux CNSS part employé',
                'valeur': Decimal('5.00'),
                'type_valeur': 'pourcentage',
                'categorie': 'cnss',
                'unite': '%',
                'description': 'Part employé: Retraite-Décès-Invalidité 2,5% + Assurance maladie 2,5%'
            },
            {
                'code': 'TAUX_CNSS_EMPLOYEUR',
                'libelle': 'Taux CNSS part employeur',
                'valeur': Decimal('18.00'),
                'type_valeur': 'pourcentage',
                'categorie': 'cnss',
                'unite': '%',
                'description': 'Part employeur: PF 6% + AT/MP 4% + Retraite 4% + Maladie 4%'
            },
        ]
        
        for const_data in constantes_cnss:
            const, created = Constante.objects.update_or_create(
                code=const_data['code'],
                defaults={
                    'libelle': const_data['libelle'],
                    'valeur': const_data['valeur'],
                    'type_valeur': const_data['type_valeur'],
                    'categorie': const_data['categorie'],
                    'unite': const_data['unite'],
                    'description': const_data['description'],
                    'date_debut_validite': date(2025, 1, 1),
                    'actif': True
                }
            )
            
            action = 'Créée' if created else 'Mise à jour'
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ {const_data["code"]}: {const_data["valeur"]} {const_data["unite"]} ({action})')
            )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Constantes CNSS mises à jour avec succès!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Afficher le récapitulatif des règles
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('📋 RÈGLES DE CALCUL CNSS GUINÉE:'))
        self.stdout.write('-' * 40)
        self.stdout.write('  Situation du salaire        | Assiette de cotisation')
        self.stdout.write('-' * 40)
        self.stdout.write('  Salaire < 550 000 GNF       | On cotise sur 550 000 GNF (plancher)')
        self.stdout.write('  550 000 ≤ Salaire ≤ 2 500 000 | On cotise sur le salaire réel')
        self.stdout.write('  Salaire > 2 500 000 GNF     | On cotise sur 2 500 000 GNF (plafond)')
        self.stdout.write('-' * 40)
        self.stdout.write('')
        self.stdout.write('  📊 RÉPARTITION DES TAUX:')
        self.stdout.write('  ┌─────────────────────────────────┬───────────┬───────────┐')
        self.stdout.write('  │ Branche                         │ Employeur │ Salarié   │')
        self.stdout.write('  ├─────────────────────────────────┼───────────┼───────────┤')
        self.stdout.write('  │ Prestations familiales          │    6%     │    -      │')
        self.stdout.write('  │ Accidents du travail / MP       │    4%     │    -      │')
        self.stdout.write('  │ Retraite-Décès-Invalidité       │    4%     │   2,5%    │')
        self.stdout.write('  │ Assurance maladie               │    4%     │   2,5%    │')
        self.stdout.write('  ├─────────────────────────────────┼───────────┼───────────┤')
        self.stdout.write('  │ TOTAL                           │   18%     │    5%     │')
        self.stdout.write('  └─────────────────────────────────┴───────────┴───────────┘')
