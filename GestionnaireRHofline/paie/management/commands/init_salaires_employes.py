"""
Commande pour initialiser les éléments de salaire de base pour tous les employés existants
"""
from django.core.management.base import BaseCommand
from datetime import date
from decimal import Decimal

from employes.models import Employe
from paie.models import RubriquePaie, ElementSalaire


class Command(BaseCommand):
    help = 'Initialise les éléments de salaire de base pour tous les employés sans élément'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la création même si des éléments existent déjà',
        )
        parser.add_argument(
            '--montant',
            type=int,
            default=550000,
            help='Montant du salaire de base par défaut (SMIG: 550000)',
        )

    def handle(self, *args, **options):
        force = options['force']
        montant_defaut = Decimal(str(options['montant']))
        
        self.stdout.write(self.style.SUCCESS('💰 Initialisation des salaires de base...\n'))
        
        # Récupérer ou créer la rubrique salaire de base
        rubrique_base = RubriquePaie.objects.filter(
            code_rubrique__icontains='SAL_BASE',
            type_rubrique='gain',
            actif=True
        ).first()
        
        if not rubrique_base:
            rubrique_base, created = RubriquePaie.objects.get_or_create(
                code_rubrique='SAL_BASE',
                defaults={
                    'libelle_rubrique': 'Salaire de base',
                    'type_rubrique': 'gain',
                    'soumis_cnss': True,
                    'soumis_irg': True,
                    'ordre_calcul': 10,
                    'ordre_affichage': 10,
                    'actif': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('  ✅ Rubrique SAL_BASE créée'))
        
        # Récupérer tous les employés actifs
        employes = Employe.objects.filter(statut_employe='actif')
        
        created_count = 0
        skipped_count = 0
        
        for employe in employes:
            # Vérifier si un élément de salaire de base existe déjà
            existe = ElementSalaire.objects.filter(
                employe=employe,
                rubrique=rubrique_base,
                actif=True
            ).exists()
            
            if existe and not force:
                skipped_count += 1
                continue
            
            # Déterminer le montant
            montant = montant_defaut
            if hasattr(employe, 'salaire_base') and employe.salaire_base:
                montant = employe.salaire_base
            
            # Créer ou mettre à jour l'élément
            ElementSalaire.objects.update_or_create(
                employe=employe,
                rubrique=rubrique_base,
                defaults={
                    'montant': montant,
                    'date_debut': employe.date_embauche or date.today(),
                    'actif': True,
                    'recurrent': True
                }
            )
            created_count += 1
            self.stdout.write(f'  ✅ {employe.nom_complet}: {montant:,.0f} GNF')
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Terminé: {created_count} éléments créés, {skipped_count} ignorés'
        ))
        self.stdout.write(self.style.WARNING(
            '\n💡 Conseil: Modifiez les montants individuellement dans Paie > Éléments de salaire'
        ))
