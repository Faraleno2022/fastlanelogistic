"""
Services pour les calculs RH légaux guinéens.
- Calcul des indemnités de licenciement
- Calcul des préavis
- Calcul des allocations familiales
- Calcul des indemnités d'accident du travail
"""
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class ServiceIndemnites:
    """Service de calcul des indemnités de fin de contrat"""
    
    # Taux d'indemnité par tranche d'ancienneté (Convention Collective Guinée)
    TAUX_TRANCHE_1_5 = Decimal('0.33')  # 33% pour 1-5 ans
    TAUX_TRANCHE_6_10 = Decimal('0.35')  # 35% pour 6-10 ans
    TAUX_TRANCHE_PLUS_10 = Decimal('0.40')  # 40% pour >10 ans
    
    # Durées de préavis par catégorie (Code du travail Art. 172)
    PREAVIS_CADRE = 3  # mois
    PREAVIS_MAITRISE = 2  # mois
    PREAVIS_EMPLOYE = 1  # mois
    
    @classmethod
    def calculer_anciennete(cls, date_embauche, date_fin=None):
        """
        Calcule l'ancienneté en années et mois.
        
        Args:
            date_embauche: Date d'embauche
            date_fin: Date de fin (par défaut: aujourd'hui)
            
        Returns:
            dict: {'annees': int, 'mois': int, 'total_annees': float}
        """
        if not date_embauche:
            return {'annees': 0, 'mois': 0, 'total_annees': 0}
        
        date_fin = date_fin or timezone.now().date()
        delta = relativedelta(date_fin, date_embauche)
        
        total_annees = delta.years + (delta.months / 12)
        
        return {
            'annees': delta.years,
            'mois': delta.months,
            'jours': delta.days,
            'total_annees': round(total_annees, 2)
        }
    
    @classmethod
    def calculer_salaire_moyen(cls, employe, nb_mois=12):
        """
        Calcule le salaire moyen des N derniers mois.
        
        Args:
            employe: Instance Employe
            nb_mois: Nombre de mois à considérer (défaut: 12)
            
        Returns:
            Decimal: Salaire moyen
        """
        from paie.models import BulletinPaie
        
        # Récupérer les bulletins des N derniers mois
        date_limite = timezone.now().date() - relativedelta(months=nb_mois)
        
        bulletins = BulletinPaie.objects.filter(
            employe=employe,
            periode__date_debut__gte=date_limite
        ).order_by('-periode__date_debut')[:nb_mois]
        
        if not bulletins.exists():
            # Utiliser le salaire de base si pas de bulletins
            salaire_base = getattr(employe, 'salaire_base', 0)
            if hasattr(employe, 'poste') and employe.poste:
                salaire_base = employe.poste.salaire_base or salaire_base
            return Decimal(str(salaire_base or 0))
        
        total = sum(b.salaire_brut for b in bulletins)
        return (total / len(bulletins)).quantize(Decimal('1'))
    
    @classmethod
    def calculer_indemnite_licenciement(cls, anciennete_annees, salaire_moyen):
        """
        Calcule l'indemnité de licenciement selon la Convention Collective Guinée.
        
        Formule:
        - Ancienneté 1-5 ans: 33% × Salaire moyen × Nb années
        - Ancienneté 6-10 ans: 35% × Salaire moyen × Nb années
        - Ancienneté >10 ans: 40% × Salaire moyen × Nb années
        
        Args:
            anciennete_annees: Nombre d'années d'ancienneté
            salaire_moyen: Salaire moyen mensuel
            
        Returns:
            tuple: (montant_total, detail_calcul)
        """
        anciennete = float(anciennete_annees)
        salaire = Decimal(str(salaire_moyen))
        
        if anciennete < 1 or salaire <= 0:
            return Decimal('0'), {'raison': 'Ancienneté < 1 an ou salaire non renseigné'}
        
        detail = {
            'anciennete_totale': anciennete,
            'salaire_moyen': float(salaire),
            'tranches': []
        }
        
        total = Decimal('0')
        annees_restantes = anciennete
        
        # Tranche 1: 1-5 ans à 33%
        if annees_restantes > 0:
            annees_tranche1 = min(annees_restantes, 5)
            montant_tranche1 = Decimal(str(annees_tranche1)) * cls.TAUX_TRANCHE_1_5 * salaire
            total += montant_tranche1
            detail['tranches'].append({
                'periode': '1-5 ans',
                'annees': annees_tranche1,
                'taux': '33%',
                'montant': float(montant_tranche1.quantize(Decimal('1')))
            })
            annees_restantes -= annees_tranche1
        
        # Tranche 2: 6-10 ans à 35%
        if annees_restantes > 0:
            annees_tranche2 = min(annees_restantes, 5)
            montant_tranche2 = Decimal(str(annees_tranche2)) * cls.TAUX_TRANCHE_6_10 * salaire
            total += montant_tranche2
            detail['tranches'].append({
                'periode': '6-10 ans',
                'annees': annees_tranche2,
                'taux': '35%',
                'montant': float(montant_tranche2.quantize(Decimal('1')))
            })
            annees_restantes -= annees_tranche2
        
        # Tranche 3: >10 ans à 40%
        if annees_restantes > 0:
            montant_tranche3 = Decimal(str(annees_restantes)) * cls.TAUX_TRANCHE_PLUS_10 * salaire
            total += montant_tranche3
            detail['tranches'].append({
                'periode': '>10 ans',
                'annees': annees_restantes,
                'taux': '40%',
                'montant': float(montant_tranche3.quantize(Decimal('1')))
            })
        
        detail['total'] = float(total.quantize(Decimal('1')))
        return total.quantize(Decimal('1')), detail
    
    @classmethod
    def calculer_duree_preavis(cls, employe):
        """
        Calcule la durée du préavis selon la catégorie (Code du travail Art. 172).
        
        - Cadres supérieurs: 3 mois
        - Agents de maîtrise: 2 mois
        - Employés/Ouvriers: 1 mois
        
        Args:
            employe: Instance Employe
            
        Returns:
            dict: {'duree_mois': int, 'categorie': str, 'heures_recherche_emploi': int}
        """
        categorie = ''
        if employe.poste:
            categorie = getattr(employe.poste, 'categorie', '').lower()
            if not categorie:
                categorie = (employe.poste.intitule or '').lower()
        
        # Déterminer la catégorie
        if any(mot in categorie for mot in ['cadre', 'directeur', 'responsable', 'manager', 'drh', 'dg', 'daf']):
            return {
                'duree_mois': cls.PREAVIS_CADRE,
                'categorie': 'Cadre supérieur',
                'heures_recherche_emploi': 8  # 8h/semaine
            }
        elif any(mot in categorie for mot in ['maitrise', 'maîtrise', 'superviseur', 'chef', 'coordinateur']):
            return {
                'duree_mois': cls.PREAVIS_MAITRISE,
                'categorie': 'Agent de maîtrise',
                'heures_recherche_emploi': 8
            }
        else:
            return {
                'duree_mois': cls.PREAVIS_EMPLOYE,
                'categorie': 'Employé/Ouvrier',
                'heures_recherche_emploi': 8
            }
    
    @classmethod
    def calculer_indemnite_preavis(cls, employe, dispense=True):
        """
        Calcule l'indemnité compensatrice de préavis si dispensé.
        
        Args:
            employe: Instance Employe
            dispense: Si l'employé est dispensé de préavis
            
        Returns:
            dict: {'montant': Decimal, 'duree_mois': int, 'salaire_mensuel': Decimal}
        """
        if not dispense:
            return {'montant': Decimal('0'), 'duree_mois': 0, 'salaire_mensuel': Decimal('0')}
        
        preavis = cls.calculer_duree_preavis(employe)
        salaire_moyen = cls.calculer_salaire_moyen(employe)
        
        montant = salaire_moyen * preavis['duree_mois']
        
        return {
            'montant': montant.quantize(Decimal('1')),
            'duree_mois': preavis['duree_mois'],
            'salaire_mensuel': salaire_moyen,
            'categorie': preavis['categorie']
        }


class ServiceAllocationsFamiliales:
    """Service de calcul des allocations familiales CNSS"""
    
    MONTANT_PAR_ENFANT = Decimal('9000')  # GNF/mois
    MAX_ENFANTS = 10
    AGE_LIMITE_NORMAL = 17
    AGE_LIMITE_SCOLARISE = 20
    JOURS_TRAVAIL_MIN = 18
    HEURES_TRAVAIL_MIN = 120
    
    @classmethod
    def compter_enfants_eligibles(cls, employe, date_reference=None):
        """
        Compte le nombre d'enfants éligibles aux allocations familiales.
        
        Conditions:
        - Âge < 17 ans (ou < 20 ans si scolarisé)
        - Maximum 10 enfants
        
        Args:
            employe: Instance Employe
            date_reference: Date de référence (défaut: aujourd'hui)
            
        Returns:
            dict: {'nombre': int, 'enfants': list, 'non_eligibles': list}
        """
        from employes.models import EnfantEmploye
        
        date_reference = date_reference or timezone.now().date()
        
        enfants = EnfantEmploye.objects.filter(employe=employe)
        eligibles = []
        non_eligibles = []
        
        for enfant in enfants:
            age = date_reference.year - enfant.date_naissance.year - (
                (date_reference.month, date_reference.day) < 
                (enfant.date_naissance.month, enfant.date_naissance.day)
            )
            
            age_limite = cls.AGE_LIMITE_SCOLARISE if enfant.scolarise else cls.AGE_LIMITE_NORMAL
            
            if age < age_limite:
                eligibles.append({
                    'nom': f"{enfant.nom} {enfant.prenoms}",
                    'age': age,
                    'scolarise': enfant.scolarise
                })
            else:
                non_eligibles.append({
                    'nom': f"{enfant.nom} {enfant.prenoms}",
                    'age': age,
                    'raison': f"Âge ({age} ans) >= limite ({age_limite} ans)"
                })
        
        return {
            'nombre': min(len(eligibles), cls.MAX_ENFANTS),
            'enfants': eligibles[:cls.MAX_ENFANTS],
            'non_eligibles': non_eligibles
        }
    
    @classmethod
    def verifier_eligibilite_employe(cls, jours_travailles=0, heures_travaillees=0):
        """
        Vérifie si l'employé est éligible aux allocations familiales.
        
        Condition: 18 jours ou 120h travaillées/mois
        
        Returns:
            tuple: (eligible: bool, raison: str)
        """
        if jours_travailles >= cls.JOURS_TRAVAIL_MIN:
            return True, f"{jours_travailles} jours travaillés (>= {cls.JOURS_TRAVAIL_MIN})"
        elif heures_travaillees >= cls.HEURES_TRAVAIL_MIN:
            return True, f"{heures_travaillees}h travaillées (>= {cls.HEURES_TRAVAIL_MIN}h)"
        else:
            return False, f"Conditions non remplies: {jours_travailles} jours et {heures_travaillees}h"
    
    @classmethod
    def calculer_allocation(cls, employe, mois, annee, jours_travailles=22, heures_travaillees=176):
        """
        Calcule l'allocation familiale pour un mois donné.
        
        Args:
            employe: Instance Employe
            mois: Mois (1-12)
            annee: Année
            jours_travailles: Nombre de jours travaillés
            heures_travaillees: Nombre d'heures travaillées
            
        Returns:
            dict: Détail du calcul
        """
        # Vérifier l'éligibilité de l'employé
        eligible, raison_eligibilite = cls.verifier_eligibilite_employe(
            jours_travailles, heures_travaillees
        )
        
        if not eligible:
            return {
                'eligible': False,
                'raison': raison_eligibilite,
                'montant': Decimal('0'),
                'nb_enfants': 0
            }
        
        # Compter les enfants éligibles
        enfants = cls.compter_enfants_eligibles(employe, date(annee, mois, 1))
        
        montant = cls.MONTANT_PAR_ENFANT * enfants['nombre']
        
        return {
            'eligible': True,
            'raison': raison_eligibilite,
            'montant': montant,
            'nb_enfants': enfants['nombre'],
            'montant_par_enfant': cls.MONTANT_PAR_ENFANT,
            'enfants_eligibles': enfants['enfants'],
            'enfants_non_eligibles': enfants['non_eligibles']
        }


class ServiceAccidentTravail:
    """Service de calcul des indemnités d'accident du travail"""
    
    TAUX_28_PREMIERS_JOURS = Decimal('0.50')  # 50%
    TAUX_APRES_28_JOURS = Decimal('0.667')  # 66,7%
    TAUX_INCAPACITE_TOTALE = Decimal('0.70')  # 70% du salaire annuel
    
    # Pensions survivants
    TAUX_PENSION_VEUF = Decimal('0.30')  # 30%
    TAUX_PENSION_ORPHELIN = Decimal('0.15')  # 15% par enfant (max 2)
    
    @classmethod
    def calculer_indemnites_temporaires(cls, salaire_base, duree_arret_jours):
        """
        Calcule les indemnités temporaires d'accident du travail.
        
        - 50% du salaire les 28 premiers jours
        - 66,7% ensuite
        
        Args:
            salaire_base: Salaire mensuel de base
            duree_arret_jours: Durée de l'arrêt en jours
            
        Returns:
            dict: Détail du calcul
        """
        salaire_journalier = Decimal(str(salaire_base)) / Decimal('30')
        
        total = Decimal('0')
        detail = {
            'salaire_journalier': float(salaire_journalier.quantize(Decimal('1'))),
            'duree_totale': duree_arret_jours,
            'tranches': []
        }
        
        jours_restants = duree_arret_jours
        
        # 28 premiers jours à 50%
        jours_50 = min(jours_restants, 28)
        montant_50 = jours_50 * salaire_journalier * cls.TAUX_28_PREMIERS_JOURS
        total += montant_50
        detail['tranches'].append({
            'periode': '28 premiers jours',
            'jours': jours_50,
            'taux': '50%',
            'montant': float(montant_50.quantize(Decimal('1')))
        })
        jours_restants -= jours_50
        
        # Jours suivants à 66,7%
        if jours_restants > 0:
            montant_667 = jours_restants * salaire_journalier * cls.TAUX_APRES_28_JOURS
            total += montant_667
            detail['tranches'].append({
                'periode': 'Jours suivants',
                'jours': jours_restants,
                'taux': '66,7%',
                'montant': float(montant_667.quantize(Decimal('1')))
            })
        
        detail['total'] = float(total.quantize(Decimal('1')))
        return detail
    
    @classmethod
    def calculer_rente_incapacite(cls, salaire_annuel, taux_incapacite):
        """
        Calcule la rente d'incapacité permanente.
        
        - Incapacité totale (100%): 70% du salaire annuel
        - Incapacité partielle: Prorata
        
        Args:
            salaire_annuel: Salaire annuel de référence
            taux_incapacite: Taux d'incapacité (0-100)
            
        Returns:
            dict: Détail du calcul
        """
        salaire = Decimal(str(salaire_annuel))
        taux = Decimal(str(taux_incapacite)) / Decimal('100')
        
        # Rente = 70% × salaire annuel × taux d'incapacité
        rente_annuelle = salaire * cls.TAUX_INCAPACITE_TOTALE * taux
        rente_mensuelle = rente_annuelle / Decimal('12')
        
        return {
            'salaire_annuel': float(salaire),
            'taux_incapacite': float(taux_incapacite),
            'rente_annuelle': float(rente_annuelle.quantize(Decimal('1'))),
            'rente_mensuelle': float(rente_mensuelle.quantize(Decimal('1')))
        }
    
    @classmethod
    def verifier_delais_declaration(cls, date_accident, date_declaration_victime=None, 
                                     date_declaration_employeur=None):
        """
        Vérifie si les délais de déclaration sont respectés.
        
        - Victime: 24h
        - Employeur: 48h
        
        Returns:
            list: Liste des alertes
        """
        alertes = []
        
        if date_declaration_victime:
            delai = (date_declaration_victime - date_accident).days
            if delai > 1:
                alertes.append({
                    'type': 'warning',
                    'message': f"Déclaration victime hors délai ({delai} jours > 24h)"
                })
        
        if date_declaration_employeur:
            delai = (date_declaration_employeur - date_accident).days
            if delai > 2:
                alertes.append({
                    'type': 'warning',
                    'message': f"Déclaration employeur hors délai ({delai} jours > 48h)"
                })
        
        return alertes


class ServiceCongeMaternite:
    """Service de gestion du congé maternité"""
    
    SEMAINES_PRENATAL = 6  # 6 semaines avant
    SEMAINES_POSTNATAL = 8  # 8 semaines après
    JOURS_PROLONGATION_MAX = 21  # Max 21 jours de prolongation maladie
    MOIS_CONGE_NON_PAYE_MAX = 9  # Max 9 mois de congé non payé
    
    @classmethod
    def calculer_dates_conge(cls, date_accouchement_prevue, date_accouchement_reelle=None,
                              prolongation_maladie=False, conge_non_paye_mois=0):
        """
        Calcule les dates du congé maternité.
        
        - 6 semaines avant accouchement (prénatal)
        - 8 semaines après accouchement (postnatal)
        - +21 jours max si prolongation maladie
        - +9 mois max si congé non payé
        
        Args:
            date_accouchement_prevue: Date prévue d'accouchement
            date_accouchement_reelle: Date réelle d'accouchement (optionnel)
            prolongation_maladie: Si prolongation pour maladie
            conge_non_paye_mois: Nombre de mois de congé non payé (0-9)
            
        Returns:
            dict: Détail des dates et durées
        """
        date_accouchement = date_accouchement_reelle or date_accouchement_prevue
        
        # Dates de base
        date_debut_prenatal = date_accouchement_prevue - timedelta(weeks=cls.SEMAINES_PRENATAL)
        date_fin_postnatal = date_accouchement + timedelta(weeks=cls.SEMAINES_POSTNATAL)
        
        result = {
            'date_accouchement_prevue': date_accouchement_prevue,
            'date_accouchement_reelle': date_accouchement_reelle,
            'date_debut_prenatal': date_debut_prenatal,
            'date_fin_postnatal': date_fin_postnatal,
            'duree_legale_jours': (date_fin_postnatal - date_debut_prenatal).days,
            'duree_legale_semaines': cls.SEMAINES_PRENATAL + cls.SEMAINES_POSTNATAL,
        }
        
        date_fin_effective = date_fin_postnatal
        
        # Prolongation maladie
        if prolongation_maladie:
            date_fin_prolongation = date_fin_postnatal + timedelta(days=cls.JOURS_PROLONGATION_MAX)
            result['prolongation_maladie'] = True
            result['date_fin_prolongation'] = date_fin_prolongation
            result['jours_prolongation'] = cls.JOURS_PROLONGATION_MAX
            date_fin_effective = date_fin_prolongation
        
        # Congé non payé
        if conge_non_paye_mois > 0:
            mois = min(conge_non_paye_mois, cls.MOIS_CONGE_NON_PAYE_MAX)
            date_fin_non_paye = date_fin_effective + relativedelta(months=mois)
            result['conge_non_paye'] = True
            result['mois_non_paye'] = mois
            result['date_fin_conge_non_paye'] = date_fin_non_paye
            date_fin_effective = date_fin_non_paye
        
        result['date_fin_effective'] = date_fin_effective
        result['duree_totale_jours'] = (date_fin_effective - date_debut_prenatal).days
        
        return result
    
    @classmethod
    def calculer_indemnites_cnss(cls, salaire_journalier, duree_jours):
        """
        Calcule les indemnités CNSS pour le congé maternité.
        
        Indemnité = 100% du salaire pendant la durée légale
        
        Args:
            salaire_journalier: Salaire journalier de référence
            duree_jours: Durée en jours (max 98 jours = 14 semaines)
            
        Returns:
            dict: Détail du calcul
        """
        salaire = Decimal(str(salaire_journalier))
        jours = min(duree_jours, 98)  # Max 14 semaines = 98 jours
        
        total = salaire * jours
        
        return {
            'salaire_journalier': float(salaire),
            'jours_indemnises': jours,
            'taux': '100%',
            'total_indemnites': float(total.quantize(Decimal('1')))
        }
