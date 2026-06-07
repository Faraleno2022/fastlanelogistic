"""
Commande pour tester l'intégration des pointages et absences dans le calcul de paie
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from datetime import date, timedelta
import calendar

from employes.models import Employe
from temps_travail.models import Pointage, Absence, Conge
from paie.models import PeriodePaie


class Command(BaseCommand):
    help = 'Teste l\'intégration des pointages et absences dans le calcul de paie'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('TEST INTEGRATION POINTAGES/ABSENCES - PAIE'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # 1. Vérifier les pointages existants
        self.verifier_pointages()
        
        # 2. Vérifier les absences
        self.verifier_absences()
        
        # 3. Vérifier les congés
        self.verifier_conges()
        
        # 4. Test de calcul avec un employé
        self.test_calcul_paie()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Test terminé!'))

    def verifier_pointages(self):
        self.stdout.write('\n📊 POINTAGES:')
        
        today = date.today()
        mois = today.month
        annee = today.year
        
        # Compter les pointages du mois
        premier_jour = date(annee, mois, 1)
        dernier_jour = date(annee, mois, calendar.monthrange(annee, mois)[1])
        
        pointages = Pointage.objects.filter(
            date_pointage__gte=premier_jour,
            date_pointage__lte=dernier_jour
        )
        
        total = pointages.count()
        presents = pointages.filter(statut_pointage='present').count()
        absents = pointages.filter(statut_pointage='absent').count()
        retards = pointages.filter(statut_pointage='retard').count()
        
        self.stdout.write(f'  Période: {premier_jour} - {dernier_jour}')
        self.stdout.write(f'  Total pointages: {total}')
        self.stdout.write(f'  - Présents: {presents}')
        self.stdout.write(f'  - Absents: {absents}')
        self.stdout.write(f'  - Retards: {retards}')
        
        # Heures supplémentaires
        from django.db.models import Sum
        heures_sup = pointages.aggregate(total=Sum('heures_supplementaires'))['total'] or 0
        self.stdout.write(f'  Heures supplémentaires totales: {heures_sup}h')

    def verifier_absences(self):
        self.stdout.write('\n📋 ABSENCES:')
        
        today = date.today()
        mois = today.month
        annee = today.year
        
        premier_jour = date(annee, mois, 1)
        dernier_jour = date(annee, mois, calendar.monthrange(annee, mois)[1])
        
        absences = Absence.objects.filter(
            date_absence__gte=premier_jour,
            date_absence__lte=dernier_jour
        )
        
        total = absences.count()
        justifiees = absences.filter(justifie=True).count()
        non_payees = absences.filter(impact_paie='non_paye').count()
        
        self.stdout.write(f'  Total absences: {total}')
        self.stdout.write(f'  - Justifiées: {justifiees}')
        self.stdout.write(f'  - Non payées: {non_payees}')
        
        # Détail par type
        for type_abs in ['maladie', 'accident_travail', 'absence_injustifiee', 'permission']:
            count = absences.filter(type_absence=type_abs).count()
            if count > 0:
                self.stdout.write(f'  - {type_abs}: {count}')

    def verifier_conges(self):
        self.stdout.write('\n🏖️ CONGÉS:')
        
        today = date.today()
        
        # Congés en cours
        conges_en_cours = Conge.objects.filter(
            date_debut__lte=today,
            date_fin__gte=today,
            statut_demande='approuve'
        ).count()
        
        # Congés en attente
        conges_attente = Conge.objects.filter(statut_demande='en_attente').count()
        
        self.stdout.write(f'  Congés en cours: {conges_en_cours}')
        self.stdout.write(f'  Demandes en attente: {conges_attente}')

    def test_calcul_paie(self):
        self.stdout.write('\n💰 TEST CALCUL PAIE:')
        
        # Trouver un employé actif
        employe = Employe.objects.filter(statut_employe='actif').first()
        
        if not employe:
            self.stdout.write(self.style.WARNING('  ⚠ Aucun employé actif trouvé'))
            return
        
        # Trouver une période de paie
        periode = PeriodePaie.objects.filter(statut_periode='ouverte').first()
        
        if not periode:
            self.stdout.write(self.style.WARNING('  ⚠ Aucune période de paie ouverte'))
            return
        
        self.stdout.write(f'  Employé: {employe.nom_complet}')
        self.stdout.write(f'  Période: {periode.mois}/{periode.annee}')
        
        try:
            from paie.services import MoteurCalculPaie
            moteur = MoteurCalculPaie(employe, periode)
            montants = moteur.calculer_bulletin()
            
            self.stdout.write(self.style.SUCCESS('\n  📈 Résultats du calcul:'))
            self.stdout.write(f'    Jours ouvrables: {montants.get("jours_ouvrables", 0)}')
            self.stdout.write(f'    Jours travaillés: {montants.get("jours_travailles", 0)}')
            self.stdout.write(f'    Jours absence: {montants.get("jours_absence", 0)}')
            self.stdout.write(f'    Jours congé: {montants.get("jours_conge", 0)}')
            self.stdout.write(f'    Heures supplémentaires: {montants.get("heures_supplementaires", 0)}h')
            self.stdout.write(f'    Retenue absence: {montants.get("retenue_absence", 0):,.0f} GNF')
            self.stdout.write(f'    Salaire brut: {montants.get("brut", 0):,.0f} GNF')
            self.stdout.write(f'    Salaire net: {montants.get("net", 0):,.0f} GNF')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Erreur: {str(e)}'))
