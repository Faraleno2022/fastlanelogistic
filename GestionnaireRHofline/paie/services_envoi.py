"""
Service d'envoi des bulletins de paie par email et WhatsApp
"""
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from urllib.parse import quote


class BulletinEnvoiService:
    """Service pour l'envoi des bulletins de paie"""
    
    def __init__(self, entreprise):
        self.entreprise = entreprise
    
    def envoyer_email(self, bulletin, destinataire_email, params=None, message_personnalise=None):
        if not destinataire_email:
            return False, "Adresse email non renseignée"
        
        try:
            # Préparer l'email
            sujet = f"Bulletin de paie - {bulletin.periode}"
            
            corps = message_personnalise or render_to_string('paie/emails/bulletin_email.html', {
                'bulletin': bulletin,
                'employe': bulletin.employe,
                'entreprise': self.entreprise,
            })
            
            email = EmailMessage(
                subject=sujet,
                body=corps,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                to=[destinataire_email],
            )
            email.content_subtype = 'html'
            email.send()
            
            return True, "Email envoyé avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de l'envoi: {str(e)}"
    
    def generer_lien_whatsapp(self, bulletin, numero_telephone, message=None):
        """Génère un lien WhatsApp pour envoyer le bulletin avec lien PDF public"""
        if not numero_telephone:
            return None, "Numéro de téléphone non renseigné"
        
        # Nettoyer le numéro (enlever espaces, tirets, etc.)
        numero = ''.join(filter(str.isdigit, numero_telephone))
        
        # Ajouter l'indicatif Guinée si nécessaire
        if not numero.startswith('224'):
            numero = '224' + numero
        
        # Générer le token public pour le PDF si pas encore fait
        token = bulletin.generer_token_public()
        
        # Construire le lien public du PDF
        lien_pdf = f"https://www.guineerh.space/paie/bulletins/public/{token}/"
        
        # Message par défaut avec lien PDF
        if not message:
            message = f"""Bonjour {bulletin.employe.prenoms},

Veuillez trouver votre bulletin de paie pour la période {bulletin.periode}.

📄 *Télécharger votre bulletin PDF:*
{lien_pdf}

💰 *Détails:*
- Salaire brut: {bulletin.salaire_brut:,.0f} GNF
- Net à payer: {bulletin.net_a_payer:,.0f} GNF

Cordialement,
{self.entreprise.nom if self.entreprise else 'Service RH'}"""
        else:
            # Ajouter le lien PDF au message personnalisé
            message = f"{message}\n\n📄 Télécharger le bulletin PDF:\n{lien_pdf}"
        
        # Encoder le message pour l'URL
        message_encode = quote(message)
        
        # Générer le lien WhatsApp
        lien = f"https://wa.me/{numero}?text={message_encode}"
        
        return lien, "Lien WhatsApp généré"
    
    def envoyer_bulletin_whatsapp_api(self, bulletin, numero_telephone, params=None):
        """
        Envoie le bulletin via l'API WhatsApp Business (si configurée)
        Note: Nécessite une configuration API WhatsApp Business
        """
        # Cette méthode nécessite l'intégration avec l'API WhatsApp Business
        # Pour l'instant, on retourne le lien web WhatsApp
        return self.generer_lien_whatsapp(bulletin, numero_telephone)
    
    def envoyer_masse_email(self, bulletins, params=None, message_personnalise=None):
        """Envoie les bulletins à plusieurs employés par email"""
        resultats = {
            'succes': [],
            'echecs': [],
        }
        
        for bulletin in bulletins:
            email = bulletin.employe.email_professionnel
            if email:
                success, message = self.envoyer_email(
                    bulletin, email, params, message_personnalise
                )
                if success:
                    resultats['succes'].append({
                        'employe': bulletin.employe.nom_complet,
                        'email': email,
                    })
                else:
                    resultats['echecs'].append({
                        'employe': bulletin.employe.nom_complet,
                        'email': email,
                        'erreur': message,
                    })
            else:
                resultats['echecs'].append({
                    'employe': bulletin.employe.nom_complet,
                    'email': None,
                    'erreur': 'Email non renseigné',
                })
        
        return resultats
    
    def generer_liens_whatsapp_masse(self, bulletins):
        """Génère les liens WhatsApp pour plusieurs bulletins"""
        liens = []
        
        for bulletin in bulletins:
            telephone = bulletin.employe.telephone_principal
            if telephone:
                lien, _ = self.generer_lien_whatsapp(bulletin, telephone)
                liens.append({
                    'employe': bulletin.employe.nom_complet,
                    'telephone': telephone,
                    'lien': lien,
                    'bulletin': bulletin,
                })
            else:
                liens.append({
                    'employe': bulletin.employe.nom_complet,
                    'telephone': None,
                    'lien': None,
                    'bulletin': bulletin,
                    'erreur': 'Téléphone non renseigné',
                })
        
        return liens
