"""
Service de calcul automatique de l'IRPP selon le barème progressif guinéen
"""
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Q
from core.models import BaremeIRPP, DeductionFiscale


class IRPPService:
    """Service pour le calcul de l'IRPP (Impôt sur le Revenu des Personnes Physiques)"""
    
    def __init__(self, entreprise=None, annee=None):
        self.entreprise = entreprise
        self.annee = annee or self._get_annee_courante()
        self._charger_bareme()
        self._charger_deductions()
    
    def _get_annee_courante(self):
        from datetime import date
        return date.today().year
    
    def _charger_bareme(self):
        """Charge le barème IRPP pour l'année"""
        query = Q(annee=self.annee, actif=True)
        if self.entreprise:
            query &= Q(entreprise=self.entreprise) | Q(entreprise__isnull=True)
        else:
            query &= Q(entreprise__isnull=True)
        
        self.tranches = list(BaremeIRPP.objects.filter(query).order_by('tranche_numero'))
    
    def _charger_deductions(self):
        """Charge les déductions fiscales pour l'année"""
        query = Q(annee=self.annee, actif=True)
        if self.entreprise:
            query &= Q(entreprise=self.entreprise) | Q(entreprise__isnull=True)
        else:
            query &= Q(entreprise__isnull=True)
        
        self.deductions = {d.type_deduction: d for d in DeductionFiscale.objects.filter(query)}
    
    def calculer_deductions_familiales(self, situation_matrimoniale, nombre_enfants=0, 
                                        nombre_ascendants=0, personnes_handicapees=0):
        """
        Calcule les déductions familiales selon la situation
        
        Args:
            situation_matrimoniale: 'celibataire', 'marie', 'divorce', 'veuf'
            nombre_enfants: Nombre d'enfants à charge
            nombre_ascendants: Nombre d'ascendants à charge
            personnes_handicapees: Nombre de personnes handicapées à charge
        
        Returns:
            Decimal: Montant total des déductions
        """
        total_deductions = Decimal('0')
        
        # Déduction conjoint
        if situation_matrimoniale in ['marie', 'Marié(e)', 'Marié']:
            deduction_conjoint = self.deductions.get('conjoint')
            if deduction_conjoint:
                total_deductions += deduction_conjoint.montant_deduction
        
        # Déduction enfants (avec plafond)
        deduction_enfant = self.deductions.get('enfant')
        if deduction_enfant and nombre_enfants > 0:
            max_enfants = deduction_enfant.nombre_max or 4  # Par défaut 4 en Guinée
            nb_enfants_deductibles = min(nombre_enfants, max_enfants)
            total_deductions += deduction_enfant.montant_deduction * nb_enfants_deductibles
        
        # Déduction ascendants
        deduction_ascendant = self.deductions.get('ascendant')
        if deduction_ascendant and nombre_ascendants > 0:
            max_ascendants = deduction_ascendant.nombre_max or 2
            nb_ascendants_deductibles = min(nombre_ascendants, max_ascendants)
            total_deductions += deduction_ascendant.montant_deduction * nb_ascendants_deductibles
        
        # Déduction handicap
        deduction_handicap = self.deductions.get('handicap')
        if deduction_handicap and personnes_handicapees > 0:
            total_deductions += deduction_handicap.montant_deduction * personnes_handicapees
        
        return total_deductions
    
    def calculer_irpp(self, revenu_imposable):
        """
        Calcule l'IRPP selon le barème progressif
        
        Args:
            revenu_imposable: Revenu imposable après déductions
        
        Returns:
            dict: {
                'revenu_imposable': Decimal,
                'irpp': Decimal,
                'taux_moyen': Decimal,
                'taux_marginal': Decimal,
                'detail_tranches': list
            }
        """
        revenu = Decimal(str(revenu_imposable))
        
        if revenu <= 0 or not self.tranches:
            return {
                'revenu_imposable': revenu,
                'irpp': Decimal('0'),
                'taux_moyen': Decimal('0'),
                'taux_marginal': Decimal('0'),
                'detail_tranches': []
            }
        
        irpp_total = Decimal('0')
        detail_tranches = []
        taux_marginal = Decimal('0')
        revenu_restant = revenu
        
        for tranche in self.tranches:
            if revenu_restant <= 0:
                break
            
            # Calculer la base imposable dans cette tranche
            if tranche.revenu_max:
                largeur_tranche = tranche.revenu_max - tranche.revenu_min
            else:
                largeur_tranche = revenu_restant  # Dernière tranche illimitée
            
            # Montant imposable dans cette tranche
            if revenu >= tranche.revenu_min:
                if tranche.revenu_max and revenu > tranche.revenu_max:
                    base_tranche = largeur_tranche
                else:
                    base_tranche = revenu - tranche.revenu_min
                
                # Calculer l'impôt pour cette tranche
                impot_tranche = (base_tranche * tranche.taux / Decimal('100')).quantize(
                    Decimal('1'), rounding=ROUND_HALF_UP
                )
                
                irpp_total += impot_tranche
                taux_marginal = tranche.taux
                
                detail_tranches.append({
                    'tranche': tranche.tranche_numero,
                    'revenu_min': tranche.revenu_min,
                    'revenu_max': tranche.revenu_max,
                    'taux': tranche.taux,
                    'base_imposable': base_tranche,
                    'impot': impot_tranche
                })
                
                revenu_restant = revenu - (tranche.revenu_max or revenu)
        
        # Calculer le taux moyen
        taux_moyen = Decimal('0')
        if revenu > 0:
            taux_moyen = (irpp_total / revenu * Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        
        return {
            'revenu_imposable': revenu,
            'irpp': irpp_total,
            'taux_moyen': taux_moyen,
            'taux_marginal': taux_marginal,
            'detail_tranches': detail_tranches
        }
    
    def calculer_irpp_mensuel(self, salaire_brut, cotisations_sociales,
                               situation_matrimoniale='celibataire', nombre_enfants=0):
        """
        Calcule l'IRPP mensuel pour un salarié
        
        Args:
            salaire_brut: Salaire brut mensuel
            cotisations_sociales: Total des cotisations sociales (CNSS, etc.)
            situation_matrimoniale: Situation familiale
            nombre_enfants: Nombre d'enfants à charge
        
        Returns:
            dict: Détail du calcul IRPP mensuel
        """
        salaire_brut = Decimal(str(salaire_brut))
        cotisations = Decimal(str(cotisations_sociales))
        
        # Base imposable = Brut - Cotisations sociales
        base_imposable = salaire_brut - cotisations
        
        # Déductions familiales mensuelles
        deductions_annuelles = self.calculer_deductions_familiales(
            situation_matrimoniale, nombre_enfants
        )
        deductions_mensuelles = (deductions_annuelles / Decimal('12')).quantize(
            Decimal('1'), rounding=ROUND_HALF_UP
        )
        
        # Revenu imposable mensuel
        revenu_imposable = max(base_imposable - deductions_mensuelles, Decimal('0'))
        
        # Calculer l'IRPP sur base annualisée puis diviser par 12
        revenu_annuel = revenu_imposable * Decimal('12')
        resultat_annuel = self.calculer_irpp(revenu_annuel)
        
        irpp_mensuel = (resultat_annuel['irpp'] / Decimal('12')).quantize(
            Decimal('1'), rounding=ROUND_HALF_UP
        )
        
        return {
            'salaire_brut': salaire_brut,
            'cotisations_sociales': cotisations,
            'base_imposable': base_imposable,
            'deductions_familiales': deductions_mensuelles,
            'revenu_imposable': revenu_imposable,
            'irpp_mensuel': irpp_mensuel,
            'taux_moyen': resultat_annuel['taux_moyen'],
            'taux_marginal': resultat_annuel['taux_marginal']
        }
    
    @staticmethod
    def get_bareme_defaut_guinee(annee=2025):
        """
        Retourne le barème IRPP par défaut pour la Guinée
        
        Barème 2025 (à ajuster selon la législation en vigueur):
        - 0 à 1 000 000 GNF : 0%
        - 1 000 001 à 5 000 000 GNF : 5%
        - 5 000 001 à 10 000 000 GNF : 10%
        - 10 000 001 à 20 000 000 GNF : 15%
        - 20 000 001 à 50 000 000 GNF : 20%
        - Plus de 50 000 000 GNF : 25%
        """
        return [
            {'tranche': 1, 'min': 0, 'max': 1000000, 'taux': 0},
            {'tranche': 2, 'min': 1000000, 'max': 5000000, 'taux': 5},
            {'tranche': 3, 'min': 5000000, 'max': 10000000, 'taux': 10},
            {'tranche': 4, 'min': 10000000, 'max': 20000000, 'taux': 15},
            {'tranche': 5, 'min': 20000000, 'max': 50000000, 'taux': 20},
            {'tranche': 6, 'min': 50000000, 'max': None, 'taux': 25},
        ]
    
    @staticmethod
    def get_deductions_defaut_guinee(annee=2025):
        """
        Retourne les déductions fiscales par défaut pour la Guinée
        """
        return [
            {'type': 'conjoint', 'montant': 100000, 'plafond': None, 'max': 1},
            {'type': 'enfant', 'montant': 50000, 'plafond': 200000, 'max': 4},
            {'type': 'ascendant', 'montant': 50000, 'plafond': 100000, 'max': 2},
            {'type': 'handicap', 'montant': 100000, 'plafond': None, 'max': None},
        ]
