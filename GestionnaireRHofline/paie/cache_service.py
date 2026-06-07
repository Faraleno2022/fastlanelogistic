"""
Service de cache pour les données fréquemment utilisées dans la paie.
Optimise les performances en réduisant les requêtes DB répétitives.
"""
from django.core.cache import cache
from django.conf import settings
from decimal import Decimal
from typing import Dict, List, Optional, Any
import hashlib


class PayrollCacheService:
    """
    Service de cache pour les calculs de paie.
    Réduit drastiquement les requêtes DB en cachant les données statiques.
    """
    
    # Durées de cache en secondes
    CACHE_TIMEOUT_CONSTANTES = 3600  # 1 heure
    CACHE_TIMEOUT_RUBRIQUES = 3600   # 1 heure
    CACHE_TIMEOUT_TRANCHES = 3600    # 1 heure
    CACHE_TIMEOUT_DEVISES = 1800     # 30 minutes
    CACHE_TIMEOUT_ELEMENTS = 300     # 5 minutes (plus volatile)
    
    # Préfixes de clés de cache
    PREFIX_CONSTANTES = 'paie:constantes'
    PREFIX_RUBRIQUES = 'paie:rubriques'
    PREFIX_TRANCHES = 'paie:tranches'
    PREFIX_ELEMENTS = 'paie:elements'
    PREFIX_DEVISES = 'paie:devises'
    PREFIX_EMPLOYE = 'paie:employe'
    
    @classmethod
    def get_constantes(cls, force_refresh: bool = False, date_reference=None) -> Dict[str, Decimal]:
        """
        Récupère les constantes de paie avec cache, filtrées par date de validité.

        :param date_reference: Date pour filtrer par validité (date_debut <= ref <= date_fin).
                               Si None, retourne toutes les constantes actives (compatibilité).
        Returns:
            Dict mapping code -> valeur
        """
        suffix = f":{date_reference.isoformat()}" if date_reference else ""
        cache_key = f"{cls.PREFIX_CONSTANTES}{suffix}"

        if not force_refresh:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        from django.db import models as _m
        from .models import Constante

        qs = Constante.objects.filter(actif=True)
        if date_reference:
            qs = qs.filter(date_debut_validite__lte=date_reference).filter(
                _m.Q(date_fin_validite__isnull=True) |
                _m.Q(date_fin_validite__gte=date_reference)
            )

        constantes = {}
        for const in qs.only('code', 'valeur'):
            constantes[const.code] = const.valeur

        cache.set(cache_key, constantes, cls.CACHE_TIMEOUT_CONSTANTES)
        return constantes
    
    @classmethod
    def get_tranches_rts(cls, annee: int, force_refresh: bool = False) -> List[Dict]:
        """
        Récupère les tranches RTS avec cache et fallback année précédente.
        
        Args:
            annee: Année de validité
            
        Returns:
            Liste des tranches ordonnées
        """
        cache_key = f"{cls.PREFIX_TRANCHES}:{annee}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        from .models import TrancheRTS
        tranches = list(
            TrancheRTS.objects.filter(
                annee_validite=annee,
                actif=True,
                type_bareme='officiel',
            ).order_by('numero_tranche').values(
                'numero_tranche', 'borne_inferieure',
                'borne_superieure', 'taux_irg'
            )
        )

        # Fallback: année précédente si pas de tranches pour l'année demandée
        if not tranches:
            tranches = list(
                TrancheRTS.objects.filter(
                    annee_validite=annee - 1,
                    actif=True,
                    type_bareme='officiel',
                ).order_by('numero_tranche').values(
                    'numero_tranche', 'borne_inferieure',
                    'borne_superieure', 'taux_irg'
                )
            )

        # Dernier recours: dernière année disponible
        if not tranches:
            derniere_annee = TrancheRTS.objects.filter(
                actif=True, type_bareme='officiel'
            ).order_by('-annee_validite').values_list('annee_validite', flat=True).first()
            if derniere_annee:
                tranches = list(
                    TrancheRTS.objects.filter(
                        annee_validite=derniere_annee,
                        actif=True,
                        type_bareme='officiel',
                    ).order_by('numero_tranche').values(
                        'numero_tranche', 'borne_inferieure',
                        'borne_superieure', 'taux_irg'
                    )
                )
        
        # Fallback ultime: barème RTS CGI 2022 codé en dur (bornes continues)
        if not tranches:
            tranches = [
                {'numero_tranche': 1, 'borne_inferieure': Decimal('0'), 'borne_superieure': Decimal('1000000'), 'taux_irg': Decimal('0')},
                {'numero_tranche': 2, 'borne_inferieure': Decimal('1000000'), 'borne_superieure': Decimal('3000000'), 'taux_irg': Decimal('5')},
                {'numero_tranche': 3, 'borne_inferieure': Decimal('3000000'), 'borne_superieure': Decimal('5000000'), 'taux_irg': Decimal('8')},
                {'numero_tranche': 4, 'borne_inferieure': Decimal('5000000'), 'borne_superieure': Decimal('10000000'), 'taux_irg': Decimal('10')},
                {'numero_tranche': 5, 'borne_inferieure': Decimal('10000000'), 'borne_superieure': Decimal('20000000'), 'taux_irg': Decimal('15')},
                {'numero_tranche': 6, 'borne_inferieure': Decimal('20000000'), 'borne_superieure': None, 'taux_irg': Decimal('20')},
            ]
        
        cache.set(cache_key, tranches, cls.CACHE_TIMEOUT_TRANCHES)
        return tranches
    
    @classmethod
    def get_rubriques_actives(cls, force_refresh: bool = False) -> Dict[str, Dict]:
        """
        Récupère les rubriques de paie actives avec cache.
        
        Returns:
            Dict mapping code -> rubrique data
        """
        cache_key = cls.PREFIX_RUBRIQUES
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        from .models import RubriquePaie
        rubriques = {}
        for rub in RubriquePaie.objects.filter(actif=True).only(
            'id', 'code_rubrique', 'libelle_rubrique', 'type_rubrique',
            'soumis_cnss', 'soumis_irg', 'ordre_calcul', 'ordre_affichage',
            'taux_rubrique', 'montant_fixe'
        ):
            rubriques[rub.code_rubrique] = {
                'id': rub.id,
                'code': rub.code_rubrique,
                'libelle': rub.libelle_rubrique,
                'type': rub.type_rubrique,
                'soumis_cnss': rub.soumis_cnss,
                'soumis_irg': rub.soumis_irg,
                'ordre_calcul': rub.ordre_calcul,
                'ordre_affichage': rub.ordre_affichage,
                'taux': rub.taux_rubrique,
                'montant_fixe': rub.montant_fixe,
            }
        
        cache.set(cache_key, rubriques, cls.CACHE_TIMEOUT_RUBRIQUES)
        return rubriques
    
    @classmethod
    def get_rubrique_by_code(cls, code: str) -> Optional[Dict]:
        """Récupère une rubrique par son code."""
        rubriques = cls.get_rubriques_actives()
        return rubriques.get(code)
    
    @classmethod
    def get_elements_employe(cls, employe_id: int, annee: int, mois: int, 
                             force_refresh: bool = False) -> List[Dict]:
        """
        Récupère les éléments de salaire d'un employé avec cache.
        """
        from datetime import date
        cache_key = f"{cls.PREFIX_ELEMENTS}:{employe_id}:{annee}:{mois}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        from .models import ElementSalaire
        date_ref = date(annee, mois, 1)
        
        elements = list(
            ElementSalaire.objects.filter(
                employe_id=employe_id,
                actif=True,
                date_debut__lte=date_ref
            ).filter(
                models.Q(date_fin__isnull=True) | 
                models.Q(date_fin__gte=date_ref)
            ).select_related('rubrique').values(
                'id', 'montant', 'taux', 
                'rubrique__code_rubrique', 'rubrique__type_rubrique',
                'rubrique__soumis_cnss', 'rubrique__soumis_irg',
                'rubrique__ordre_affichage'
            )
        )
        
        cache.set(cache_key, elements, cls.CACHE_TIMEOUT_ELEMENTS)
        return elements
    
    @classmethod
    def get_devise_base(cls, force_refresh: bool = False) -> Any:
        """Récupère la devise de base avec cache."""
        cache_key = f"{cls.PREFIX_DEVISES}:base"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        from core.services.devises import DeviseService
        devise = DeviseService.get_devise_base()
        
        cache.set(cache_key, devise, cls.CACHE_TIMEOUT_DEVISES)
        return devise
    
    @classmethod
    def invalidate_constantes(cls):
        """Invalide le cache des constantes."""
        cache.delete(cls.PREFIX_CONSTANTES)
    
    @classmethod
    def invalidate_rubriques(cls):
        """Invalide le cache des rubriques."""
        cache.delete(cls.PREFIX_RUBRIQUES)
    
    @classmethod
    def invalidate_tranches(cls, annee: int = None):
        """Invalide le cache des tranches RTS."""
        if annee:
            cache.delete(f"{cls.PREFIX_TRANCHES}:{annee}")
        else:
            # Invalider toutes les années récentes
            from datetime import datetime
            current_year = datetime.now().year
            for year in range(current_year - 2, current_year + 2):
                cache.delete(f"{cls.PREFIX_TRANCHES}:{year}")
    
    @classmethod
    def invalidate_elements_employe(cls, employe_id: int):
        """Invalide le cache des éléments d'un employé."""
        from datetime import datetime
        current_year = datetime.now().year
        for mois in range(1, 13):
            cache.delete(f"{cls.PREFIX_ELEMENTS}:{employe_id}:{current_year}:{mois}")
    
    @classmethod
    def invalidate_all(cls):
        """Invalide tout le cache de paie."""
        cls.invalidate_constantes()
        cls.invalidate_rubriques()
        cls.invalidate_tranches()
        cache.delete(f"{cls.PREFIX_DEVISES}:base")
    
    @classmethod
    def warmup_cache(cls, annee: int = None):
        """
        Préchauffe le cache avec les données fréquemment utilisées.
        Appeler au démarrage de l'application ou avant un calcul massif.
        """
        from datetime import datetime
        if annee is None:
            annee = datetime.now().year
        
        # Précharger les données statiques
        cls.get_constantes(force_refresh=True)
        cls.get_rubriques_actives(force_refresh=True)
        cls.get_tranches_rts(annee, force_refresh=True)
        cls.get_devise_base(force_refresh=True)


# Import models pour la fonction get_elements_employe
from django.db import models
