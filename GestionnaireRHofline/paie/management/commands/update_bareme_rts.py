"""
Commande pour mettre à jour le barème RTS (Retenue sur Traitements et Salaires) 
selon la législation guinéenne (CGI 2022).

Barème RTS officiel CGI 2022 (6 tranches):
- 0 - 1 000 000 GNF : 0%
- 1 000 001 - 3 000 000 GNF : 5%
- 3 000 001 - 5 000 000 GNF : 8%
- 5 000 001 - 10 000 000 GNF : 10%
- 10 000 001 - 20 000 000 GNF : 15%
- Au-delà de 20 000 000 GNF : 20%

Usage:
    python manage.py update_bareme_rts
"""
from decimal import Decimal
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from paie.models import TrancheRTS, Constante


class Command(BaseCommand):
    help = 'Met à jour le barème RTS (RTS) selon la législation guinéenne 2022+'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(self.style.NOTICE('MISE À JOUR DU BARÈME RTS (RTS) - Guinée 2022+'))
        self.stdout.write(self.style.NOTICE('=' * 60))
        
        # 1. Mettre à jour le barème RTS
        self._update_bareme_rts()
        
        # 2. Ajouter les charges patronales manquantes
        self._update_charges_patronales()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Mise à jour terminée avec succès!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

    def _update_bareme_rts(self):
        """Met à jour les tranches du barème RTS"""
        self.stdout.write('\n📊 BARÈME RTS (depuis 2022):')
        self.stdout.write('-' * 50)
        
        # Barème RTS officiel CGI 2022 (6 tranches)
        tranches = [
            {
                'numero_tranche': 1,
                'borne_inferieure': Decimal('0'),
                'borne_superieure': Decimal('1000000'),
                'taux_irg': Decimal('0.00'),
            },
            {
                'numero_tranche': 2,
                'borne_inferieure': Decimal('1000001'),
                'borne_superieure': Decimal('3000000'),
                'taux_irg': Decimal('5.00'),
            },
            {
                'numero_tranche': 3,
                'borne_inferieure': Decimal('3000001'),
                'borne_superieure': Decimal('5000000'),
                'taux_irg': Decimal('8.00'),
            },
            {
                'numero_tranche': 4,
                'borne_inferieure': Decimal('5000001'),
                'borne_superieure': Decimal('10000000'),
                'taux_irg': Decimal('10.00'),
            },
            {
                'numero_tranche': 5,
                'borne_inferieure': Decimal('10000001'),
                'borne_superieure': Decimal('20000000'),
                'taux_irg': Decimal('15.00'),
            },
            {
                'numero_tranche': 6,
                'borne_inferieure': Decimal('20000001'),
                'borne_superieure': None,  # Illimité
                'taux_irg': Decimal('20.00'),
            },
        ]
        
        annee = date.today().year
        
        with transaction.atomic():
            # Désactiver les anciennes tranches
            TrancheRTS.objects.filter(annee_validite=annee).update(actif=False)
            
            for tranche_data in tranches:
                tranche, created = TrancheRTS.objects.update_or_create(
                    annee_validite=annee,
                    numero_tranche=tranche_data['numero_tranche'],
                    defaults={
                        'borne_inferieure': tranche_data['borne_inferieure'],
                        'borne_superieure': tranche_data['borne_superieure'],
                        'taux_irg': tranche_data['taux_irg'],
                        'date_debut_validite': date(annee, 1, 1),
                        'actif': True
                    }
                )
                
                borne_sup = f"{tranche_data['borne_superieure']:,.0f}" if tranche_data['borne_superieure'] else "∞"
                action = 'Créée' if created else 'Mise à jour'
                self.stdout.write(
                    f"  Tranche {tranche_data['numero_tranche']}: "
                    f"{tranche_data['borne_inferieure']:>12,.0f} - {borne_sup:>12} GNF → "
                    f"{tranche_data['taux_irg']:>5}% ({action})"
                )

    def _update_charges_patronales(self):
        """Ajoute les charges patronales manquantes"""
        self.stdout.write('\n💼 CHARGES PATRONALES:')
        self.stdout.write('-' * 50)
        
        charges = [
            {
                'code': 'TAUX_VF',
                'libelle': 'Versement Forfaitaire (VF)',
                'valeur': Decimal('6.00'),
                'type_valeur': 'pourcentage',
                'categorie': 'general',
                'unite': '%',
                'description': 'Versement Forfaitaire - impôt sur la masse salariale à charge de l\'employeur (6%)'
            },
            {
                'code': 'TAUX_TA',
                'libelle': 'Taxe d\'Apprentissage',
                'valeur': Decimal('1.50'),
                'type_valeur': 'pourcentage',
                'categorie': 'general',
                'unite': '%',
                'description': 'Taxe d\'apprentissage à charge de l\'employeur (1,5% de la masse salariale)'
            },
        ]
        
        for charge_data in charges:
            charge, created = Constante.objects.update_or_create(
                code=charge_data['code'],
                defaults={
                    'libelle': charge_data['libelle'],
                    'valeur': charge_data['valeur'],
                    'type_valeur': charge_data['type_valeur'],
                    'categorie': charge_data['categorie'],
                    'unite': charge_data['unite'],
                    'description': charge_data['description'],
                    'date_debut_validite': date(date.today().year, 1, 1),
                    'actif': True
                }
            )
            
            action = 'Créée' if created else 'Mise à jour'
            self.stdout.write(f"  {charge_data['code']}: {charge_data['valeur']}% ({action})")
        
        # Afficher le récapitulatif des charges patronales
        self.stdout.write('\n📋 RÉCAPITULATIF CHARGES PATRONALES:')
        self.stdout.write('  ┌────────────────────────────────┬───────────┐')
        self.stdout.write('  │ Charge                         │ Taux      │')
        self.stdout.write('  ├────────────────────────────────┼───────────┤')
        self.stdout.write('  │ CNSS Employeur                 │   18%     │')
        self.stdout.write('  │ Versement Forfaitaire (VF)     │    6%     │')
        self.stdout.write('  │ Taxe d\'Apprentissage (TA)      │  1,5%     │')
        self.stdout.write('  │ Contribution ONFPP              │  1,5%     │')
        self.stdout.write('  ├────────────────────────────────┼───────────┤')
        self.stdout.write('  │ TOTAL CHARGES PATRONALES       │   27%     │')
        self.stdout.write('  └────────────────────────────────┴───────────┘')
