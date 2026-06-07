"""
Commande pour calculer les droits aux congés payés selon le Code du Travail guinéen.

Usage:
    python manage.py calculer_droits_conges
    python manage.py calculer_droits_conges --annee 2025
    python manage.py calculer_droits_conges --employe EMP001
"""
from django.core.management.base import BaseCommand
from datetime import date
from decimal import Decimal

from temps_travail.services import GestionCongesService, ProvisionCongesService
from employes.models import Employe
from core.models import Entreprise


class Command(BaseCommand):
    help = 'Calcule les droits aux congés payés selon le Code du Travail guinéen'

    def add_arguments(self, parser):
        parser.add_argument(
            '--annee',
            type=int,
            default=date.today().year,
            help='Année de référence (défaut: année en cours)'
        )
        parser.add_argument(
            '--employe',
            type=str,
            help='Matricule d\'un employé spécifique'
        )
        parser.add_argument(
            '--entreprise',
            type=str,
            help='ID de l\'entreprise'
        )
        parser.add_argument(
            '--provision',
            action='store_true',
            help='Calculer aussi les provisions comptables'
        )

    def handle(self, *args, **options):
        annee = options['annee']
        matricule = options.get('employe')
        provision = options.get('provision', False)
        
        self.stdout.write(self.style.NOTICE('=' * 70))
        self.stdout.write(self.style.NOTICE(f'CALCUL DES DROITS AUX CONGÉS PAYÉS - ANNÉE {annee}'))
        self.stdout.write(self.style.NOTICE('=' * 70))
        
        # Afficher les règles
        self.stdout.write('')
        self.stdout.write('📋 RÈGLES CODE DU TRAVAIL GUINÉEN:')
        self.stdout.write('   - Acquisition: 2,5 jours ouvrables par mois')
        self.stdout.write('   - Majoration ancienneté:')
        self.stdout.write('     • +1 jour après 5 ans')
        self.stdout.write('     • +2 jours après 10 ans')
        self.stdout.write('     • +3 jours après 15 ans')
        self.stdout.write('     • +4 jours après 20 ans')
        self.stdout.write('')
        
        # Récupérer les employés
        if matricule:
            employes = Employe.objects.filter(matricule=matricule)
            if not employes.exists():
                self.stdout.write(self.style.ERROR(f'Employé {matricule} non trouvé'))
                return
        else:
            employes = Employe.objects.filter(statut_employe='actif')
        
        if not employes.exists():
            self.stdout.write(self.style.WARNING('Aucun employé actif trouvé'))
            return
        
        self.stdout.write(f'📊 Calcul pour {employes.count()} employé(s)...')
        self.stdout.write('-' * 70)
        
        total_jours_acquis = Decimal('0')
        total_jours_pris = Decimal('0')
        total_solde = Decimal('0')
        
        for employe in employes:
            service = GestionCongesService(employe)
            droits = service.calculer_droits_annuels(annee)
            
            # Mettre à jour en base
            service.mettre_a_jour_droits(annee)
            
            # Afficher le résultat
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(
                f'👤 {employe.matricule} - {employe.nom} {employe.prenoms}'
            ))
            self.stdout.write(f'   Ancienneté: {droits["anciennete_annees"]} ans')
            self.stdout.write(f'   Jours base (2,5j/mois): {droits["jours_base"]:.1f} jours')
            
            if droits['jours_anciennete'] > 0:
                self.stdout.write(self.style.WARNING(
                    f'   Majoration ancienneté: +{droits["jours_anciennete"]:.0f} jour(s)'
                ))
            
            if droits['jours_reportes'] > 0:
                self.stdout.write(f'   Jours reportés: {droits["jours_reportes"]:.1f} jours')
            
            self.stdout.write(f'   Total acquis: {droits["total_acquis"]:.1f} jours')
            self.stdout.write(f'   Jours pris: {droits["jours_pris"]:.1f} jours')
            self.stdout.write(self.style.SUCCESS(
                f'   ➜ SOLDE DISPONIBLE: {droits["solde_disponible"]:.1f} jours'
            ))
            
            total_jours_acquis += droits['total_acquis']
            total_jours_pris += droits['jours_pris']
            total_solde += droits['solde_disponible']
        
        # Résumé
        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('📊 RÉCAPITULATIF'))
        self.stdout.write(f'   Nombre d\'employés: {employes.count()}')
        self.stdout.write(f'   Total jours acquis: {total_jours_acquis:.1f} jours')
        self.stdout.write(f'   Total jours pris: {total_jours_pris:.1f} jours')
        self.stdout.write(f'   Total solde disponible: {total_solde:.1f} jours')
        
        # Calcul des provisions si demandé
        if provision and employes.first():
            entreprise = employes.first().entreprise
            if entreprise:
                self.stdout.write('')
                self.stdout.write('=' * 70)
                self.stdout.write(self.style.NOTICE('💰 PROVISIONS COMPTABLES CONGÉS PAYÉS'))
                self.stdout.write('-' * 70)
                
                prov_service = ProvisionCongesService(entreprise)
                prov_annuelle = prov_service.calculer_provision_annuelle(annee)
                
                self.stdout.write(f'   Taux de provision: {prov_service.TAUX_PROVISION}% (1/12)')
                self.stdout.write('')
                
                for prov in prov_annuelle['provisions_mensuelles']:
                    if prov['masse_salariale'] > 0:
                        self.stdout.write(
                            f'   {prov["mois"]:02d}/{prov["annee"]}: '
                            f'Masse salariale {prov["masse_salariale"]:>12,.0f} GNF → '
                            f'Provision {prov["provision"]:>10,.0f} GNF'
                        )
                
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS(
                    f'   TOTAL PROVISION ANNUELLE: {prov_annuelle["total_provision"]:,.0f} GNF'
                ))
        
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ Calcul terminé'))
