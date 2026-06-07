"""
Système de notifications email pour GestionnaireRH.
Gère l'envoi d'emails pour les événements RH importants.
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db import models
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class NotificationEmail:
    """Classe de base pour l'envoi de notifications email"""
    
    @staticmethod
    def envoyer_email(destinataire, sujet, template_html, context, cc=None):
        """
        Envoie un email avec template HTML.
        
        Args:
            destinataire: Email du destinataire (str ou list)
            sujet: Sujet de l'email
            template_html: Chemin du template HTML
            context: Contexte pour le template
            cc: Liste des emails en copie
        """
        try:
            # Rendre le template HTML
            html_content = render_to_string(template_html, context)
            text_content = strip_tags(html_content)
            
            # Préparer les destinataires
            if isinstance(destinataire, str):
                destinataire = [destinataire]
            
            # Créer l'email
            email = EmailMultiAlternatives(
                subject=sujet,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=destinataire,
                cc=cc or []
            )
            email.attach_alternative(html_content, "text/html")
            
            # Envoyer
            email.send(fail_silently=False)
            logger.info(f"Email envoyé à {destinataire}: {sujet}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email à {destinataire}: {str(e)}")
            return False


class NotificationConge:
    """Notifications liées aux congés"""
    
    @staticmethod
    def notifier_demande_conge(conge):
        """Notifie le responsable d'une nouvelle demande de congé"""
        employe = conge.employe
        
        # Trouver le responsable (manager du département)
        responsable_email = None
        if employe.departement and hasattr(employe.departement, 'responsable'):
            resp = employe.departement.responsable
            if resp and resp.email:
                responsable_email = resp.email
        
        if not responsable_email:
            logger.warning(f"Pas de responsable trouvé pour {employe.nom}")
            return False
        
        context = {
            'employe': employe,
            'conge': conge,
            'date_demande': date.today(),
        }
        
        return NotificationEmail.envoyer_email(
            destinataire=responsable_email,
            sujet=f"[RH] Demande de congé - {employe.nom} {employe.prenoms}",
            template_html='emails/demande_conge.html',
            context=context
        )
    
    @staticmethod
    def notifier_reponse_conge(conge):
        """Notifie l'employé de la réponse à sa demande de congé"""
        employe = conge.employe
        
        if not employe.email:
            logger.warning(f"Pas d'email pour {employe.nom}")
            return False
        
        context = {
            'employe': employe,
            'conge': conge,
            'approuve': conge.statut_demande == 'approuve',
        }
        
        statut = "approuvée" if conge.statut_demande == 'approuve' else "refusée"
        
        return NotificationEmail.envoyer_email(
            destinataire=employe.email,
            sujet=f"[RH] Votre demande de congé a été {statut}",
            template_html='emails/reponse_conge.html',
            context=context
        )


class NotificationPret:
    """Notifications liées aux prêts"""
    
    @staticmethod
    def notifier_demande_pret(pret):
        """Notifie la direction d'une nouvelle demande de prêt"""
        from core.models import Entreprise
        
        employe = pret.employe
        entreprise = employe.entreprise
        
        # Email de la direction RH
        destinataire = getattr(settings, 'EMAIL_RH', None)
        if not destinataire and entreprise:
            destinataire = entreprise.email
        
        if not destinataire:
            logger.warning("Pas d'email RH configuré")
            return False
        
        context = {
            'employe': employe,
            'pret': pret,
            'date_demande': date.today(),
        }
        
        return NotificationEmail.envoyer_email(
            destinataire=destinataire,
            sujet=f"[RH] Demande de prêt - {employe.nom} {employe.prenoms} - {pret.montant_pret:,.0f} GNF",
            template_html='emails/demande_pret.html',
            context=context
        )
    
    @staticmethod
    def notifier_reponse_pret(pret):
        """Notifie l'employé de la réponse à sa demande de prêt"""
        employe = pret.employe
        
        if not employe.email:
            return False
        
        context = {
            'employe': employe,
            'pret': pret,
            'approuve': pret.statut == 'approuve' or pret.statut == 'en_cours',
        }
        
        statut = "approuvée" if pret.statut in ['approuve', 'en_cours'] else "refusée"
        
        return NotificationEmail.envoyer_email(
            destinataire=employe.email,
            sujet=f"[RH] Votre demande de prêt a été {statut}",
            template_html='emails/reponse_pret.html',
            context=context
        )


class NotificationPaie:
    """Notifications liées à la paie"""
    
    @staticmethod
    def notifier_bulletin_disponible(bulletin):
        """Notifie l'employé que son bulletin est disponible"""
        employe = bulletin.employe
        
        if not employe.email:
            return False
        
        context = {
            'employe': employe,
            'bulletin': bulletin,
            'periode': bulletin.periode,
        }
        
        return NotificationEmail.envoyer_email(
            destinataire=employe.email,
            sujet=f"[RH] Votre bulletin de paie {bulletin.periode.get_mois_display()} {bulletin.periode.annee} est disponible",
            template_html='emails/bulletin_disponible.html',
            context=context
        )
    
    @staticmethod
    def notifier_bulletins_masse(bulletins):
        """Envoie les notifications pour plusieurs bulletins"""
        succes = 0
        echecs = 0
        
        for bulletin in bulletins:
            if NotificationPaie.notifier_bulletin_disponible(bulletin):
                succes += 1
            else:
                echecs += 1
        
        return {'succes': succes, 'echecs': echecs}


class NotificationContrat:
    """Notifications liées aux contrats"""
    
    @staticmethod
    def notifier_contrats_expirant(jours_avant=30):
        """Notifie les contrats expirant dans les X jours"""
        from employes.models import Employe
        
        date_limite = date.today() + timedelta(days=jours_avant)
        
        contrats = Employe.objects.filter(
            statut_employe='actif',
            date_fin_contrat__lte=date_limite,
            date_fin_contrat__gte=date.today()
        ).select_related('entreprise', 'service')
        
        if not contrats.exists():
            return {'total': 0}
        
        # Grouper par entreprise
        par_entreprise = {}
        for emp in contrats:
            ent_id = emp.entreprise_id
            if ent_id not in par_entreprise:
                par_entreprise[ent_id] = {
                    'entreprise': emp.entreprise,
                    'employes': []
                }
            par_entreprise[ent_id]['employes'].append(emp)
        
        # Envoyer une notification par entreprise
        envoyes = 0
        for ent_id, data in par_entreprise.items():
            entreprise = data['entreprise']
            if entreprise and entreprise.email:
                context = {
                    'entreprise': entreprise,
                    'employes': data['employes'],
                    'jours_avant': jours_avant,
                }
                
                if NotificationEmail.envoyer_email(
                    destinataire=entreprise.email,
                    sujet=f"[RH] {len(data['employes'])} contrat(s) expirant dans les {jours_avant} jours",
                    template_html='emails/contrats_expirant.html',
                    context=context
                ):
                    envoyes += 1
        
        return {'total': contrats.count(), 'envoyes': envoyes}


class NotificationAlerte:
    """Notifications pour les alertes diverses"""
    
    @staticmethod
    def notifier_echeance_declaration(type_declaration, date_limite, entreprise):
        """Notifie une échéance de déclaration proche"""
        if not entreprise or not entreprise.email:
            return False
        
        context = {
            'entreprise': entreprise,
            'type_declaration': type_declaration,
            'date_limite': date_limite,
            'jours_restants': (date_limite - date.today()).days,
        }
        
        return NotificationEmail.envoyer_email(
            destinataire=entreprise.email,
            sujet=f"[RH] Rappel: Échéance {type_declaration} le {date_limite.strftime('%d/%m/%Y')}",
            template_html='emails/echeance_declaration.html',
            context=context
        )
