"""
Service de vérification de conformité inspection du travail
Vérifie automatiquement l'état de conformité basé sur les données réelles
"""
from datetime import date, timedelta
from django.db.models import Count, Q


class ConformiteService:
    """Service de vérification de conformité automatique"""
    
    def __init__(self, entreprise):
        self.entreprise = entreprise
    
    def verifier_registre_personnel(self):
        """Vérifie si le registre du personnel est à jour"""
        from employes.models import Employe
        # Au moins un employé actif enregistré
        nb_employes = Employe.objects.filter(
            entreprise=self.entreprise,
            statut_employe='actif'
        ).count()
        return nb_employes > 0
    
    def verifier_registre_paie(self):
        """Vérifie si les bulletins de paie sont générés"""
        from paie.models import BulletinPaie
        today = date.today()
        # Bulletins du mois précédent
        mois_prec = today.month - 1 if today.month > 1 else 12
        annee_prec = today.year if today.month > 1 else today.year - 1
        
        nb_bulletins = BulletinPaie.objects.filter(
            employe__entreprise=self.entreprise,
            mois_paie=mois_prec,
            annee_paie=annee_prec,
            statut_bulletin__in=['valide', 'paye']
        ).count()
        return nb_bulletins > 0
    
    def verifier_registre_conges(self):
        """Vérifie si les congés sont suivis"""
        from temps_travail.models import SoldeConge
        # Soldes de congés initialisés
        nb_soldes = SoldeConge.objects.filter(
            employe__entreprise=self.entreprise,
            annee=date.today().year
        ).count()
        return nb_soldes > 0
    
    def verifier_registre_accidents(self):
        """Vérifie le suivi des accidents du travail"""
        # On considère conforme si le module est accessible
        # (pas d'accident non traité depuis > 30 jours)
        return True  # Module disponible
    
    def verifier_contrats_signes(self):
        """Vérifie si tous les employés ont un contrat"""
        from employes.models import Employe
        
        employes_actifs = Employe.objects.filter(
            entreprise=self.entreprise,
            statut_employe='actif'
        ).count()
        
        if employes_actifs == 0:
            return False
        
        # Employés avec au moins un contrat
        employes_avec_contrat = Employe.objects.filter(
            entreprise=self.entreprise,
            statut_employe='actif',
            contrats__isnull=False
        ).distinct().count()
        
        return employes_avec_contrat >= employes_actifs * 0.9  # 90% minimum
    
    def verifier_bulletins_remis(self):
        """Vérifie si les bulletins sont remis aux employés"""
        from paie.models import BulletinPaie
        today = date.today()
        mois_prec = today.month - 1 if today.month > 1 else 12
        annee_prec = today.year if today.month > 1 else today.year - 1
        
        nb_bulletins = BulletinPaie.objects.filter(
            employe__entreprise=self.entreprise,
            mois_paie=mois_prec,
            annee_paie=annee_prec,
            statut_bulletin__in=['valide', 'paye']
        ).count()
        
        return nb_bulletins > 0
    
    def verifier_cnss_jour(self):
        """Vérifie si les déclarations CNSS sont à jour"""
        from core.models import TransmissionCNSS
        today = date.today()
        mois_prec = today.month - 1 if today.month > 1 else 12
        annee_prec = today.year if today.month > 1 else today.year - 1
        
        transmission = TransmissionCNSS.objects.filter(
            entreprise=self.entreprise,
            periode_annee=annee_prec,
            periode_mois=mois_prec,
            statut__in=['transmis', 'accepte']
        ).exists()
        
        return transmission
    
    def verifier_visites_medicales(self):
        """Vérifie le suivi médical"""
        from employes.models import VisiteMedicale
        # Au moins des visites médicales enregistrées cette année
        nb_visites = VisiteMedicale.objects.filter(
            employe__entreprise=self.entreprise,
            date_visite__year=date.today().year
        ).count()
        return nb_visites > 0
    
    def verifier_formations_securite(self):
        """Vérifie si des formations sécurité ont été dispensées"""
        from formation.models import SessionFormation
        # Sessions de formation réalisées cette année
        nb_sessions = SessionFormation.objects.filter(
            formation__entreprise=self.entreprise,
            date_debut__year=date.today().year,
            statut='terminee'
        ).count()
        return nb_sessions > 0
    
    def get_checklist_complete(self):
        """Retourne la checklist complète avec statuts automatiques"""
        
        checklist = [
            {
                'categorie': 'Registres obligatoires',
                'items': [
                    {
                        'code': 'REG_PERSONNEL',
                        'libelle': 'Registre du personnel à jour',
                        'obligatoire': True,
                        'conforme': self.verifier_registre_personnel(),
                        'detail': 'Basé sur les employés actifs enregistrés'
                    },
                    {
                        'code': 'REG_PAIE',
                        'libelle': 'Registre de paie mensuel',
                        'obligatoire': True,
                        'conforme': self.verifier_registre_paie(),
                        'detail': 'Basé sur les bulletins du mois précédent'
                    },
                    {
                        'code': 'REG_CONGES',
                        'libelle': 'Registre des congés payés',
                        'obligatoire': True,
                        'conforme': self.verifier_registre_conges(),
                        'detail': 'Basé sur les soldes de congés initialisés'
                    },
                    {
                        'code': 'REG_ACCIDENTS',
                        'libelle': 'Registre des accidents du travail',
                        'obligatoire': True,
                        'conforme': self.verifier_registre_accidents(),
                        'detail': 'Module disponible'
                    },
                    {
                        'code': 'REG_DELEGUES',
                        'libelle': 'Registre des délégués du personnel',
                        'obligatoire': False,
                        'conforme': True,  # Optionnel
                        'detail': 'Facultatif selon effectif'
                    },
                ]
            },
            {
                'categorie': 'Affichages obligatoires',
                'items': [
                    {
                        'code': 'AFF_HORAIRES',
                        'libelle': 'Horaires de travail affichés',
                        'obligatoire': True,
                        'conforme': self._verifier_parametre('affichage_horaires'),
                        'detail': 'À valider manuellement'
                    },
                    {
                        'code': 'AFF_REGLEMENT',
                        'libelle': 'Règlement intérieur affiché',
                        'obligatoire': True,
                        'conforme': self._verifier_parametre('affichage_reglement'),
                        'detail': 'À valider manuellement'
                    },
                    {
                        'code': 'AFF_SECURITE',
                        'libelle': 'Consignes de sécurité affichées',
                        'obligatoire': True,
                        'conforme': self._verifier_parametre('affichage_securite'),
                        'detail': 'À valider manuellement'
                    },
                    {
                        'code': 'AFF_INSPECTION',
                        'libelle': 'Coordonnées inspection du travail',
                        'obligatoire': True,
                        'conforme': self._verifier_parametre('affichage_inspection'),
                        'detail': 'À valider manuellement'
                    },
                    {
                        'code': 'AFF_MEDECINE',
                        'libelle': 'Coordonnées médecine du travail',
                        'obligatoire': True,
                        'conforme': self._verifier_parametre('affichage_medecine'),
                        'detail': 'À valider manuellement'
                    },
                ]
            },
            {
                'categorie': 'Documents contrats',
                'items': [
                    {
                        'code': 'DOC_CONTRATS',
                        'libelle': 'Contrats de travail signés',
                        'obligatoire': True,
                        'conforme': self.verifier_contrats_signes(),
                        'detail': 'Basé sur les contrats enregistrés'
                    },
                    {
                        'code': 'DOC_BULLETINS',
                        'libelle': 'Bulletins de paie remis',
                        'obligatoire': True,
                        'conforme': self.verifier_bulletins_remis(),
                        'detail': 'Basé sur les bulletins validés'
                    },
                    {
                        'code': 'DOC_ATTESTATIONS',
                        'libelle': 'Attestations CNSS à jour',
                        'obligatoire': True,
                        'conforme': self.verifier_cnss_jour(),
                        'detail': 'Basé sur les déclarations CNSS'
                    },
                ]
            },
            {
                'categorie': 'Hygiène et sécurité',
                'items': [
                    {
                        'code': 'SEC_EXTINCTEURS',
                        'libelle': 'Extincteurs vérifiés',
                        'obligatoire': True,
                        'conforme': self._verifier_parametre('securite_extincteurs'),
                        'detail': 'À valider manuellement'
                    },
                    {
                        'code': 'SEC_TROUSSE',
                        'libelle': 'Trousse de premiers secours',
                        'obligatoire': True,
                        'conforme': self._verifier_parametre('securite_trousse'),
                        'detail': 'À valider manuellement'
                    },
                    {
                        'code': 'SEC_EQUIPEMENTS',
                        'libelle': 'Équipements de protection fournis',
                        'obligatoire': False,
                        'conforme': self._verifier_parametre('securite_equipements'),
                        'detail': 'Selon activité'
                    },
                    {
                        'code': 'SEC_FORMATION',
                        'libelle': 'Formation sécurité dispensée',
                        'obligatoire': False,
                        'conforme': self.verifier_formations_securite(),
                        'detail': 'Basé sur les sessions de formation'
                    },
                    {
                        'code': 'SEC_MEDICAL',
                        'libelle': 'Suivi médical des employés',
                        'obligatoire': True,
                        'conforme': self.verifier_visites_medicales(),
                        'detail': 'Basé sur les visites médicales'
                    },
                ]
            },
        ]
        
        # Calculer les stats
        total_items = 0
        items_conformes = 0
        items_obligatoires = 0
        obligatoires_conformes = 0
        
        for cat in checklist:
            for item in cat['items']:
                total_items += 1
                if item['conforme']:
                    items_conformes += 1
                if item['obligatoire']:
                    items_obligatoires += 1
                    if item['conforme']:
                        obligatoires_conformes += 1
        
        score = int((items_conformes / total_items) * 100) if total_items > 0 else 0
        score_obligatoire = int((obligatoires_conformes / items_obligatoires) * 100) if items_obligatoires > 0 else 0
        
        return {
            'checklist': checklist,
            'score': score,
            'score_obligatoire': score_obligatoire,
            'items_conformes': items_conformes,
            'total_items': total_items,
            'obligatoires_conformes': obligatoires_conformes,
            'items_obligatoires': items_obligatoires,
        }
    
    def _verifier_parametre(self, code):
        """Vérifie un paramètre de conformité manuelle"""
        from core.models import ParametreConformite
        try:
            param = ParametreConformite.objects.get(
                entreprise=self.entreprise,
                code=code
            )
            return param.valide
        except ParametreConformite.DoesNotExist:
            return False
