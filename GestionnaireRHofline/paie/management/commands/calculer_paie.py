"""
Commande pour calculer automatiquement la paie
Usage: python manage.py calculer_paie --periode 2025-10 [--employe MATRICULE]
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date

from employes.models import Employe
from paie.models import PeriodePaie, BulletinPaie
from paie.services import MoteurCalculPaie


class Command(BaseCommand):
    help = 'Calculer automatiquement la paie pour une période donnée'

    def add_arguments(self, parser):
        parser.add_argument(
            '--periode',
            type=str,
            required=True,
            help='Période au format AAAA-MM (ex: 2025-10)'
        )
        parser.add_argument(
            '--employe',
            type=str,
            help='Matricule de l\'employé (optionnel, sinon tous les employés)'
        )
        parser.add_argument(
            '--recalculer',
            action='store_true',
            help='Recalculer les bulletins existants'
        )

    def handle(self, *args, **options):
        periode_str = options['periode']
        matricule = options.get('employe')
        recalculer = options.get('recalculer', False)
        
        # Parser la période
        try:
            annee, mois = map(int, periode_str.split('-'))
        except ValueError:
            self.stdout.write(self.style.ERROR('Format de période invalide. Utilisez AAAA-MM'))
            return
        
        # Récupérer la période
        try:
            periode = PeriodePaie.objects.get(annee=annee, mois=mois)
        except PeriodePaie.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Période {periode_str} non trouvée'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n🧮 Calcul de la paie pour {periode}\n'))
        
        # Récupérer les employés
        if matricule:
            employes = Employe.objects.filter(matricule=matricule, statut_employe='actif')
            if not employes.exists():
                self.stdout.write(self.style.ERROR(f'Employé {matricule} non trouvé ou inactif'))
                return
        else:
            employes = Employe.objects.filter(statut_employe='actif')
        
        total_employes = employes.count()
        self.stdout.write(f'📊 {total_employes} employé(s) à traiter\n')
        
        # Calculer pour chaque employé
        bulletins_crees = 0
        bulletins_recalcules = 0
        erreurs = 0
        
        for employe in employes:
            try:
                # Vérifier si bulletin existe déjà
                bulletin_existe = BulletinPaie.objects.filter(
                    employe=employe,
                    periode=periode
                ).exists()
                
                if bulletin_existe and not recalculer:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  {employe.matricule} - Bulletin déjà existant (utilisez --recalculer)')
                    )
                    continue
                
                if bulletin_existe and recalculer:
                    # Supprimer l'ancien bulletin
                    BulletinPaie.objects.filter(employe=employe, periode=periode).delete()
                    bulletins_recalcules += 1
                
                # Calculer le bulletin
                moteur = MoteurCalculPaie(employe, periode)
                bulletin = moteur.generer_bulletin()
                
                bulletins_crees += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✅ {employe.matricule} - {employe.nom} {employe.prenoms}\n'
                        f'      Brut: {bulletin.salaire_brut:,.0f} GNF | '
                        f'Net: {bulletin.net_a_payer:,.0f} GNF'
                    )
                )
                
            except Exception as e:
                erreurs += 1
                self.stdout.write(
                    self.style.ERROR(f'  ❌ {employe.matricule} - Erreur: {str(e)}')
                )
        
        # Résumé
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS(f'\n📈 RÉSUMÉ DU CALCUL\n'))
        self.stdout.write(f'  • Bulletins créés: {bulletins_crees}')
        if bulletins_recalcules > 0:
            self.stdout.write(f'  • Bulletins recalculés: {bulletins_recalcules}')
        if erreurs > 0:
            self.stdout.write(self.style.ERROR(f'  • Erreurs: {erreurs}'))
        
        # Statistiques de la période
        bulletins = BulletinPaie.objects.filter(periode=periode)
        if bulletins.exists():
            total_brut = sum(b.salaire_brut for b in bulletins)
            total_net = sum(b.net_a_payer for b in bulletins)
            total_irg = sum(b.irg for b in bulletins)
            
            self.stdout.write(f'\n📊 STATISTIQUES PÉRIODE {periode}')
            self.stdout.write(f'  • Total brut: {total_brut:,.0f} GNF')
            self.stdout.write(f'  • Total net: {total_net:,.0f} GNF')
            self.stdout.write(f'  • Total IRG: {total_irg:,.0f} GNF')
            self.stdout.write(f'  • Nombre de bulletins: {bulletins.count()}')
        
        self.stdout.write('\n' + '='*70 + '\n')
        self.stdout.write(self.style.SUCCESS('✅ Calcul terminé!\n'))
