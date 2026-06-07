"""
Commande de gestion pour envoyer toutes les alertes RH automatiques.
Usage: python manage.py alertes_rh [--type TYPE]

Types d'alertes:
- contrats: Contrats expirant dans les 30 jours
- conges: Demandes de congés en attente
- prets: Prêts en attente d'approbation et échéances
- visites: Visites médicales à planifier
- declarations: Échéances CNSS/DMU
- all: Toutes les alertes
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from datetime import date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Envoie les alertes RH automatiques par email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['contrats', 'conges', 'prets', 'visites', 'declarations', 'all'],
            default='all',
            help='Type d\'alertes à envoyer'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les alertes sans envoyer d\'emails'
        )

    def handle(self, *args, **options):
        type_alerte = options['type']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.NOTICE(f"=== Alertes RH ({date.today()}) ==="))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("Mode dry-run: aucun email ne sera envoyé"))
        
        alertes = []
        
        if type_alerte in ['contrats', 'all']:
            alertes.extend(self.verifier_contrats())
        
        if type_alerte in ['conges', 'all']:
            alertes.extend(self.verifier_conges())
        
        if type_alerte in ['prets', 'all']:
            alertes.extend(self.verifier_prets())
        
        if type_alerte in ['visites', 'all']:
            alertes.extend(self.verifier_visites_medicales())
        
        if type_alerte in ['declarations', 'all']:
            alertes.extend(self.verifier_declarations())
        
        # Résumé
        self.stdout.write(self.style.NOTICE(f"\n=== Résumé: {len(alertes)} alerte(s) ==="))
        
        if alertes and not dry_run:
            self.envoyer_resume_alertes(alertes)
        
        self.stdout.write(self.style.SUCCESS("Terminé"))

    def verifier_contrats(self):
        """Vérifie les contrats expirant"""
        from employes.models import Employe
        
        self.stdout.write("\n[CONTRATS]")
        alertes = []
        
        date_limite = date.today() + timedelta(days=30)
        
        contrats = Employe.objects.filter(
            statut_employe='actif',
            date_fin_contrat__lte=date_limite,
            date_fin_contrat__gte=date.today()
        ).select_related('entreprise').order_by('date_fin_contrat')
        
        for emp in contrats:
            jours = (emp.date_fin_contrat - date.today()).days
            alerte = {
                'type': 'contrat',
                'priorite': 'haute' if jours <= 7 else 'moyenne',
                'message': f"Contrat de {emp.nom} {emp.prenoms} expire dans {jours} jour(s) ({emp.date_fin_contrat})",
                'entreprise': emp.entreprise,
            }
            alertes.append(alerte)
            
            if jours <= 7:
                self.stdout.write(self.style.ERROR(f"  ⚠ {alerte['message']}"))
            else:
                self.stdout.write(self.style.WARNING(f"  • {alerte['message']}"))
        
        if not contrats:
            self.stdout.write(self.style.SUCCESS("  ✓ Aucun contrat expirant"))
        
        return alertes

    def verifier_conges(self):
        """Vérifie les demandes de congés en attente"""
        from temps_travail.models import Conge
        
        self.stdout.write("\n[CONGÉS]")
        alertes = []
        
        conges = Conge.objects.filter(
            statut_demande='en_attente'
        ).select_related('employe', 'employe__entreprise').order_by('date_demande')
        
        for conge in conges:
            jours_attente = (date.today() - conge.date_demande).days
            alerte = {
                'type': 'conge',
                'priorite': 'haute' if jours_attente > 3 else 'normale',
                'message': f"Demande de congé de {conge.employe.nom} en attente depuis {jours_attente} jour(s)",
                'entreprise': conge.employe.entreprise,
            }
            alertes.append(alerte)
            
            if jours_attente > 3:
                self.stdout.write(self.style.WARNING(f"  • {alerte['message']}"))
            else:
                self.stdout.write(f"  • {alerte['message']}")
        
        if not conges:
            self.stdout.write(self.style.SUCCESS("  ✓ Aucune demande en attente"))
        
        return alertes

    def verifier_prets(self):
        """Vérifie les prêts en attente et les échéances"""
        from paie.models_pret import Pret, EcheancePret
        
        self.stdout.write("\n[PRÊTS]")
        alertes = []
        
        # Prêts en attente
        prets_attente = Pret.objects.filter(statut='en_attente').select_related('employe')
        
        for pret in prets_attente:
            alerte = {
                'type': 'pret',
                'priorite': 'moyenne',
                'message': f"Demande de prêt de {pret.employe.nom}: {pret.montant_pret:,.0f} GNF en attente",
                'entreprise': pret.employe.entreprise,
            }
            alertes.append(alerte)
            self.stdout.write(f"  • {alerte['message']}")
        
        # Échéances en retard
        echeances_retard = EcheancePret.objects.filter(
            statut='en_attente',
            date_echeance__lt=date.today()
        ).select_related('pret', 'pret__employe')
        
        for ech in echeances_retard:
            jours_retard = (date.today() - ech.date_echeance).days
            alerte = {
                'type': 'echeance_pret',
                'priorite': 'haute',
                'message': f"Échéance prêt {ech.pret.numero_pret} en retard de {jours_retard} jour(s) ({ech.montant_echeance:,.0f} GNF)",
                'entreprise': ech.pret.employe.entreprise,
            }
            alertes.append(alerte)
            self.stdout.write(self.style.ERROR(f"  ⚠ {alerte['message']}"))
        
        if not prets_attente and not echeances_retard:
            self.stdout.write(self.style.SUCCESS("  ✓ Aucune alerte prêt"))
        
        return alertes

    def verifier_visites_medicales(self):
        """Vérifie les visites médicales à planifier"""
        from employes.models import VisiteMedicale, Employe
        
        self.stdout.write("\n[VISITES MÉDICALES]")
        alertes = []
        
        # Visites à venir dans 30 jours
        date_limite = date.today() + timedelta(days=30)
        
        visites = VisiteMedicale.objects.filter(
            date_prochaine_visite__lte=date_limite,
            date_prochaine_visite__gte=date.today()
        ).select_related('employe')
        
        for visite in visites:
            jours = (visite.date_prochaine_visite - date.today()).days
            alerte = {
                'type': 'visite_medicale',
                'priorite': 'haute' if jours <= 7 else 'moyenne',
                'message': f"Visite médicale de {visite.employe.nom} à planifier dans {jours} jour(s)",
                'entreprise': visite.employe.entreprise,
            }
            alertes.append(alerte)
            self.stdout.write(f"  • {alerte['message']}")
        
        # Visites en attente de résultat
        en_attente = VisiteMedicale.objects.filter(aptitude='en_attente').count()
        if en_attente > 0:
            self.stdout.write(self.style.WARNING(f"  • {en_attente} visite(s) en attente de résultat"))
        
        if not visites and en_attente == 0:
            self.stdout.write(self.style.SUCCESS("  ✓ Aucune alerte visite médicale"))
        
        return alertes

    def verifier_declarations(self):
        """Vérifie les échéances de déclarations"""
        self.stdout.write("\n[DÉCLARATIONS]")
        alertes = []
        
        aujourd_hui = date.today()
        
        # CNSS: 15 du mois suivant
        if aujourd_hui.month == 12:
            date_cnss = date(aujourd_hui.year + 1, 1, 15)
        else:
            date_cnss = date(aujourd_hui.year, aujourd_hui.month + 1, 15)
        
        jours_cnss = (date_cnss - aujourd_hui).days
        if jours_cnss <= 10:
            alerte = {
                'type': 'declaration',
                'priorite': 'haute' if jours_cnss <= 5 else 'moyenne',
                'message': f"Échéance CNSS dans {jours_cnss} jour(s) ({date_cnss})",
                'entreprise': None,
            }
            alertes.append(alerte)
            self.stdout.write(self.style.WARNING(f"  • {alerte['message']}"))
        
        # DMU: Fin du mois
        if aujourd_hui.month == 12:
            date_dmu = date(aujourd_hui.year + 1, 1, 1) - timedelta(days=1)
        else:
            date_dmu = date(aujourd_hui.year, aujourd_hui.month + 1, 1) - timedelta(days=1)
        
        jours_dmu = (date_dmu - aujourd_hui).days
        if jours_dmu <= 5:
            alerte = {
                'type': 'declaration',
                'priorite': 'haute',
                'message': f"Échéance DMU/DNI dans {jours_dmu} jour(s) ({date_dmu})",
                'entreprise': None,
            }
            alertes.append(alerte)
            self.stdout.write(self.style.WARNING(f"  • {alerte['message']}"))
        
        if not alertes:
            self.stdout.write(self.style.SUCCESS("  ✓ Aucune échéance proche"))
        
        return alertes

    def envoyer_resume_alertes(self, alertes):
        """Envoie un email récapitulatif des alertes"""
        from core.models import Entreprise
        
        if not alertes:
            return
        
        # Grouper par entreprise
        par_entreprise = {}
        alertes_globales = []
        
        for alerte in alertes:
            if alerte['entreprise']:
                ent_id = alerte['entreprise'].id
                if ent_id not in par_entreprise:
                    par_entreprise[ent_id] = {
                        'entreprise': alerte['entreprise'],
                        'alertes': []
                    }
                par_entreprise[ent_id]['alertes'].append(alerte)
            else:
                alertes_globales.append(alerte)
        
        # Envoyer par entreprise
        for ent_id, data in par_entreprise.items():
            entreprise = data['entreprise']
            if entreprise and entreprise.email:
                self.envoyer_email_alertes(entreprise.email, data['alertes'] + alertes_globales)
        
        # Email admin global
        admin_email = getattr(settings, 'EMAIL_RH', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if admin_email:
            self.envoyer_email_alertes(admin_email, alertes)

    def envoyer_email_alertes(self, destinataire, alertes):
        """Envoie un email avec la liste des alertes"""
        hautes = [a for a in alertes if a['priorite'] == 'haute']
        moyennes = [a for a in alertes if a['priorite'] == 'moyenne']
        normales = [a for a in alertes if a['priorite'] == 'normale']
        
        message = f"Résumé des alertes RH du {date.today().strftime('%d/%m/%Y')}\n\n"
        
        if hautes:
            message += "=== ALERTES URGENTES ===\n"
            for a in hautes:
                message += f"⚠ {a['message']}\n"
            message += "\n"
        
        if moyennes:
            message += "=== ALERTES MOYENNES ===\n"
            for a in moyennes:
                message += f"• {a['message']}\n"
            message += "\n"
        
        if normales:
            message += "=== INFORMATIONS ===\n"
            for a in normales:
                message += f"• {a['message']}\n"
        
        try:
            send_mail(
                subject=f"[RH] {len(alertes)} alerte(s) - {date.today().strftime('%d/%m/%Y')}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destinataire],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"Email envoyé à {destinataire}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur envoi email: {str(e)}"))
