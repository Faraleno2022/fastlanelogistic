"""
Services pour la gestion de l'audit et de la conformité.

Fournissent:
- Gestion des rapports d'audit
- Vérification de conformité
- Suivi des modifications
"""

from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from .base_service import BaseComptaService
from ..models import (
    RapportAudit, AlerteNonConformite, ReglesConformite,
    HistoriqueModification, DeclarationTVA, EcritureComptable
)

logger = logging.getLogger(__name__)


class AuditService(BaseComptaService):
    """Service pour la gestion des rapports d'audit comptable."""
    
    def __init__(self, utilisateur):
        """
        Initialise le service d'audit.
        
        Args:
            utilisateur: Utilisateur actuel (auditeur)
        """
        self.utilisateur = utilisateur
        self.errors = []
        self.warnings = []
    
    @transaction.atomic
    def creer_rapport(self, code, titre, date_debut, date_fin, objectifs, perimetre):
        """
        Crée un nouveau rapport d'audit.
        
        Args:
            code: Code unique du rapport
            titre: Titre du rapport
            date_debut: Date de début de l'audit
            date_fin: Date de fin (optionnelle)
            objectifs: Objectifs de l'audit
            perimetre: Périmètre de l'audit
        
        Returns:
            (rapport, [erreurs]) tuple
        """
        conditions = {
            "Le code ne doit pas être vide": bool(code),
            "Le titre ne doit pas être vide": bool(titre),
            "La date de début est obligatoire": bool(date_debut),
            "Le code doit être unique": not RapportAudit.objects.filter(
                code=code, 
                entreprise=self.utilisateur.entreprise
            ).exists(),
            "Les objectifs doivent être fournis": bool(objectifs),
            "Le périmètre doit être fourni": bool(perimetre),
        }
        
        try:
            self.valider(conditions)
        except Exception as e:
            return None, self.errors
        
        rapport = RapportAudit.objects.create(
            entreprise=self.utilisateur.entreprise,
            code=code,
            titre=titre,
            date_debut=date_debut,
            date_fin=date_fin,
            objectifs=objectifs,
            perimetre=perimetre,
            statut=RapportAudit.STATUT_CHOICES[0][0],  # PLANIFIE
            auditeur=self.utilisateur,
            cree_par=self.utilisateur,
        )
        
        self.enregistrer_audit(
            action='create',
            module='audit',
            type_objet='RapportAudit',
            id_objet=str(rapport.id),
            details=f"Rapport d'audit {code} créé"
        )
        
        return rapport, []
    
    @transaction.atomic
    def demarrer_rapport(self, rapport_id):
        """
        Démarre un rapport d'audit (passage de PLANIFIE à EN_COURS).
        
        Args:
            rapport_id: ID du rapport
        
        Returns:
            (rapport, [erreurs]) tuple
        """
        try:
            rapport = RapportAudit.objects.get(
                id=rapport_id,
                entreprise=self.utilisateur.entreprise
            )
        except RapportAudit.DoesNotExist:
            return None, ["Rapport d'audit non trouvé"]
        
        conditions = {
            "Le rapport doit être en statut PLANIFIE": rapport.statut == 'PLANIFIE',
        }
        
        try:
            self.valider(conditions)
        except Exception as e:
            return None, self.errors
        
        rapport.statut = 'EN_COURS'
        rapport.save()
        
        self.enregistrer_audit(
            action='update',
            module='audit',
            type_objet='RapportAudit',
            id_objet=str(rapport.id),
            details=f"Rapport d'audit {rapport.code} démarré"
        )
        
        return rapport, []
    
    @transaction.atomic
    def terminer_rapport(self, rapport_id, conclusion, recommandations, niveau_risque=None):
        """
        Termine un rapport d'audit (passage à TERMINE).
        
        Args:
            rapport_id: ID du rapport
            conclusion: Conclusion de l'audit
            recommandations: Recommandations
            niveau_risque: Niveau de risque global (optionnel)
        
        Returns:
            (rapport, [erreurs]) tuple
        """
        try:
            rapport = RapportAudit.objects.get(
                id=rapport_id,
                entreprise=self.utilisateur.entreprise
            )
        except RapportAudit.DoesNotExist:
            return None, ["Rapport d'audit non trouvé"]
        
        conditions = {
            "Le rapport doit être en cours ou planifié": rapport.statut in ['EN_COURS', 'PLANIFIE'],
            "La conclusion est obligatoire": bool(conclusion),
            "Les recommandations sont obligatoires": bool(recommandations),
        }
        
        try:
            self.valider(conditions)
        except Exception as e:
            return None, self.errors
        
        rapport.statut = 'TERMINE'
        rapport.conclusion = conclusion
        rapport.recommandations = recommandations
        rapport.date_fin = timezone.now().date()
        if niveau_risque:
            rapport.niveau_risque_global = niveau_risque
        rapport.save()
        
        self.enregistrer_audit(
            action='update',
            module='audit',
            type_objet='RapportAudit',
            id_objet=str(rapport.id),
            details=f"Rapport d'audit {rapport.code} terminé"
        )
        
        return rapport, []
    
    def obtenir_alertes_par_severite(self, rapport_id):
        """
        Obtient les alertes groupées par sévérité.
        
        Args:
            rapport_id: ID du rapport
        
        Returns:
            Dict {severite: [alertes]}
        """
        alertes = AlerteNonConformite.objects.filter(
            rapport_id=rapport_id,
            entreprise=self.utilisateur.entreprise
        )
        
        return {
            'CRITIQUE': list(alertes.filter(severite='CRITIQUE')),
            'MAJEURE': list(alertes.filter(severite='MAJEURE')),
            'MINEURE': list(alertes.filter(severite='MINEURE')),
        }
    
    def obtenir_alertes_non_resolues(self):
        """Obtient les alertes non résolues de l'entreprise."""
        return AlerteNonConformite.objects.filter(
            entreprise=self.utilisateur.entreprise,
            statut__in=['DETECTEE', 'EN_CORRECTION']
        ).order_by('-severite', 'date_correction_prevue')


class ConformiteService(BaseComptaService):
    """Service pour la vérification de conformité comptable."""
    
    def __init__(self, utilisateur):
        """
        Initialise le service de conformité.
        
        Args:
            utilisateur: Utilisateur actuel
        """
        self.utilisateur = utilisateur
        self.errors = []
        self.warnings = []
    
    @transaction.atomic
    def creer_alerte(self, rapport_id, numero_alerte, titre, description, severite, domaine):
        """
        Crée une alerte de non-conformité.
        
        Args:
            rapport_id: ID du rapport d'audit
            numero_alerte: Numéro unique
            titre: Titre de l'alerte
            description: Description détaillée
            severite: Niveau de sévérité
            domaine: Domaine affecté
        
        Returns:
            (alerte, [erreurs]) tuple
        """
        try:
            rapport = RapportAudit.objects.get(
                id=rapport_id,
                entreprise=self.utilisateur.entreprise
            )
        except RapportAudit.DoesNotExist:
            return None, ["Rapport d'audit non trouvé"]
        
        conditions = {
            "Le numéro d'alerte ne doit pas être vide": bool(numero_alerte),
            "Le titre ne doit pas être vide": bool(titre),
            "La description ne doit pas être vide": bool(description),
            "La sévérité doit être spécifiée": severite in ['MINEURE', 'MAJEURE', 'CRITIQUE'],
            "Le domaine ne doit pas être vide": bool(domaine),
            "Le numéro d'alerte doit être unique par rapport": not AlerteNonConformite.objects.filter(
                rapport=rapport,
                numero_alerte=numero_alerte
            ).exists(),
        }
        
        try:
            self.valider(conditions)
        except Exception as e:
            return None, self.errors
        
        alerte = AlerteNonConformite.objects.create(
            entreprise=self.utilisateur.entreprise,
            rapport=rapport,
            numero_alerte=numero_alerte,
            titre=titre,
            description=description,
            severite=severite,
            domaine=domaine,
            statut='DETECTEE'
        )
        
        self.enregistrer_audit(
            action='create',
            module='audit',
            type_objet='AlerteNonConformite',
            id_objet=str(alerte.id),
            details=f"Alerte {numero_alerte} créée"
        )
        
        return alerte, []
    
    @transaction.atomic
    def creer_alerte_avec_plan_action(self, rapport_id, numero_alerte, titre, description,
                                      severite, domaine, plan_action, date_correction_prevue):
        """
        Crée une alerte complète avec plan d'action.
        
        Args:
            (voir creer_alerte)
            plan_action: Plan d'action
            date_correction_prevue: Date prévue de correction
        
        Returns:
            (alerte, [erreurs]) tuple
        """
        alerte, errors = self.creer_alerte(
            rapport_id, numero_alerte, titre, description, severite, domaine
        )
        
        if alerte:
            alerte.plan_action = plan_action
            alerte.date_correction_prevue = date_correction_prevue
            alerte.save()
        
        return alerte, errors
    
    @transaction.atomic
    def enregistrer_correction(self, alerte_id, date_correction, observations=None):
        """
        Enregistre la correction d'une alerte.
        
        Args:
            alerte_id: ID de l'alerte
            date_correction: Date de correction
            observations: Observations optionnelles
        
        Returns:
            (alerte, [erreurs]) tuple
        """
        try:
            alerte = AlerteNonConformite.objects.get(
                id=alerte_id,
                entreprise=self.utilisateur.entreprise
            )
        except AlerteNonConformite.DoesNotExist:
            return None, ["Alerte non trouvée"]
        
        conditions = {
            "La date de correction ne doit pas être vide": bool(date_correction),
        }
        
        try:
            self.valider(conditions)
        except Exception as e:
            return None, self.errors
        
        alerte.date_correction_reelle = date_correction
        alerte.statut = 'CORRIGEE'
        if observations:
            alerte.observations = observations
        alerte.save()
        
        self.enregistrer_audit(
            action='update',
            module='audit',
            type_objet='AlerteNonConformite',
            id_objet=str(alerte.id),
            details=f"Alerte {alerte.numero_alerte} corrigée"
        )
        
        return alerte, []
    
    def verifier_regles(self):
        """
        Vérifie toutes les règles de conformité actives.
        
        Returns:
            List d'alertes générées
        """
        alertes_generees = []
        regles = ReglesConformite.objects.filter(
            entreprise=self.utilisateur.entreprise,
            actif=True
        )
        
        for regle in regles:
            # Logique de vérification par module
            if regle.module_concerne == 'TVA':
                resultat = self._verifier_tva(regle)
            elif regle.module_concerne == 'Comptabilité':
                resultat = self._verifier_comptabilite(regle)
            else:
                resultat = True
            
            # Si la vérification échoue, générer une alerte
            if not resultat:
                logger.warning(f"Conformité: Règle {regle.code} non respectée")
                self.avertissement(f"Règle {regle.code}: {regle.nom}")
        
        return alertes_generees
    
    def _verifier_tva(self, regle):
        """Vérifie une règle TVA."""
        # Logique spécifique TVA
        # Exemple: vérifier que toutes les déclarations sont finalisées
        declarations_brouillon = DeclarationTVA.objects.filter(
            entreprise=self.utilisateur.entreprise,
            statut='BROUILLON',
            periode_fin__lt=timezone.now().date()
        )
        return not declarations_brouillon.exists()
    
    def _verifier_comptabilite(self, regle):
        """Vérifie une règle de comptabilité."""
        # Logique spécifique comptabilité
        return True
    
    def obtenir_conformite_globale(self):
        """
        Calcule un score de conformité global.
        
        Returns:
            Dict avec score et détails
        """
        total_regles = ReglesConformite.objects.filter(
            entreprise=self.utilisateur.entreprise,
            actif=True
        ).count()
        
        alertes = AlerteNonConformite.objects.filter(
            entreprise=self.utilisateur.entreprise,
            statut__in=['DETECTEE', 'EN_CORRECTION']
        )
        
        if total_regles == 0:
            score = 100
        else:
            # Score = 100 - (nombre_alertes_critiques * 20 + majeure * 10 + mineure * 5)
            critiques = alerts.filter(severite='CRITIQUE').count()
            majeures = alertes.filter(severite='MAJEURE').count()
            mineures = alertes.filter(severite='MINEURE').count()
            
            deductions = (critiques * 20) + (majeures * 10) + (mineures * 5)
            score = max(0, 100 - deductions)
        
        return {
            'score': score,
            'total_regles': total_regles,
            'alertes_non_resolues': alertes.count(),
            'alertes_critiques': alertes.filter(severite='CRITIQUE').count(),
        }


class HistoriqueModificationService(BaseComptaService):
    """Service pour le suivi de l'historique des modifications."""
    
    def __init__(self, utilisateur):
        """
        Initialise le service d'historique.
        
        Args:
            utilisateur: Utilisateur actuel
        """
        self.utilisateur = utilisateur
        self.errors = []
        self.warnings = []
    
    @transaction.atomic
    def enregistrer_modification(self, type_objet, id_objet, nom_objet, action,
                                 champ_modifie=None, valeur_ancienne=None, valeur_nouvelle=None,
                                 motif=None, reference=None, ip_adresse=None):
        """
        Enregistre une modification dans l'historique.
        
        Args:
            type_objet: Type d'objet modifié
            id_objet: ID de l'objet
            nom_objet: Nom/libellé de l'objet
            action: Type d'action (CREATE, UPDATE, DELETE, etc.)
            champ_modifie: Champ spécifiquement modifié (optionnel)
            valeur_ancienne: Valeur avant (optionnel)
            valeur_nouvelle: Valeur après (optionnel)
            motif: Motif de la modification (optionnel)
            reference: Référence externe (optionnel)
            ip_adresse: Adresse IP du client (optionnel)
        
        Returns:
            historique ou None
        """
        try:
            historique = HistoriqueModification.objects.create(
                entreprise=self.utilisateur.entreprise,
                type_objet=type_objet,
                id_objet=str(id_objet),
                nom_objet=nom_objet,
                action=action,
                champ_modifie=champ_modifie or '',
                valeur_ancienne=str(valeur_ancienne) if valeur_ancienne else '',
                valeur_nouvelle=str(valeur_nouvelle) if valeur_nouvelle else '',
                motif=motif or '',
                reference=reference or '',
                utilisateur=self.utilisateur,
                ip_adresse=ip_adresse,
            )
            return historique
        except Exception as e:
            logger.error(f"Erreur enregistrement historique: {e}")
            return None
    
    def obtenir_historique_objet(self, type_objet, id_objet, limite=50):
        """
        Obtient l'historique d'un objet spécifique.
        
        Args:
            type_objet: Type d'objet
            id_objet: ID de l'objet
            limite: Nombre maximum d'entrées (défaut: 50)
        
        Returns:
            QuerySet d'HistoriqueModification
        """
        return HistoriqueModification.objects.filter(
            entreprise=self.utilisateur.entreprise,
            type_objet=type_objet,
            id_objet=str(id_objet)
        ).order_by('-date_modification')[:limite]
    
    def obtenir_modifications_utilisateur(self, utilisateur, depuis=None, limite=100):
        """
        Obtient l'historique des modifications d'un utilisateur.
        
        Args:
            utilisateur: Utilisateur concerné
            depuis: Date depuis (optionnel)
            limite: Nombre maximum (défaut: 100)
        
        Returns:
            QuerySet d'HistoriqueModification
        """
        qs = HistoriqueModification.objects.filter(
            entreprise=self.utilisateur.entreprise,
            utilisateur=utilisateur
        )
        
        if depuis:
            qs = qs.filter(date_modification__gte=depuis)
        
        return qs.order_by('-date_modification')[:limite]
    
    def obtenir_modifications_recentes(self, heures=24):
        """
        Obtient les modifications récentes de l'entreprise.
        
        Args:
            heures: Nombre d'heures à considérer
        
        Returns:
            QuerySet d'HistoriqueModification
        """
        depuis = timezone.now() - timedelta(hours=heures)
        return HistoriqueModification.objects.filter(
            entreprise=self.utilisateur.entreprise,
            date_modification__gte=depuis
        ).order_by('-date_modification')
    
    def obtenir_modifications_par_type(self, type_objet):
        """Obtient toutes les modifications d'un type d'objet."""
        return HistoriqueModification.objects.filter(
            entreprise=self.utilisateur.entreprise,
            type_objet=type_objet
        ).order_by('-date_modification')
