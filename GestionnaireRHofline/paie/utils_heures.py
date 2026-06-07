from decimal import Decimal
from datetime import datetime, time, date, timedelta
from temps_travail.models import Pointage, JourFerie


class CalculateurHeures:
    """Calculateur d'heures selon le Code du Travail guinéen"""
    
    # Taux selon le Code du Travail Art. 221
    TAUX_HS_30 = Decimal('1.30')  # +30% pour les 4 premières HS/semaine
    TAUX_HS_60 = Decimal('1.60')  # +60% au-delà de 4 HS/semaine
    TAUX_NUIT = Decimal('1.20')   # +20% pour heures de nuit (20h-6h)
    TAUX_FERIE_JOUR = Decimal('1.60')  # +60% jour férié (jour)
    TAUX_FERIE_NUIT = Decimal('2.00')  # +100% jour férié (nuit)
    
    # Heures de référence
    HEURES_NORMALES_SEMAINE = Decimal('40.0')
    HEURES_NORMALES_JOUR = Decimal('8.0')
    HEURE_DEBUT_NUIT = time(20, 0)  # 20h
    HEURE_FIN_NUIT = time(6, 0)     # 6h
    
    def __init__(self, employe, periode):
        self.employe = employe
        self.periode = periode
        self.jours_feries = self._get_jours_feries()
    
    def _get_jours_feries(self):
        """Récupère les jours fériés de la période"""
        return JourFerie.objects.filter(
            entreprise=self.employe.entreprise,
            date_jour_ferie__gte=self.periode.date_debut,
            date_jour_ferie__lte=self.periode.date_fin
        ).values_list('date_jour_ferie', flat=True)
    
    def calculer_heures_periode(self):
        """Calcule toutes les heures pour la période"""
        pointages = Pointage.objects.filter(
            employe=self.employe,
            date_pointage__gte=self.periode.date_debut,
            date_pointage__lte=self.periode.date_fin,
            valide=True
        ).order_by('date_pointage')
        
        # Initialisation des compteurs
        heures_normales = Decimal('0')
        heures_sup_30 = Decimal('0')
        heures_sup_60 = Decimal('0')
        heures_nuit = Decimal('0')
        heures_feries = Decimal('0')
        
        # Calcul par semaine pour les heures supplémentaires
        semaines = self._grouper_par_semaine(pointages)
        
        for semaine_pointages in semaines:
            heures_semaine = self._calculer_heures_semaine(semaine_pointages)
            
            heures_normales += heures_semaine['normales']
            heures_sup_30 += heures_semaine['sup_30']
            heures_sup_60 += heures_semaine['sup_60']
            heures_nuit += heures_semaine['nuit']
            heures_feries += heures_semaine['feries']
        
        return {
            'heures_normales': heures_normales,
            'heures_supplementaires_30': heures_sup_30,
            'heures_supplementaires_60': heures_sup_60,
            'heures_nuit': heures_nuit,
            'heures_feries': heures_feries,
        }
    
    def _grouper_par_semaine(self, pointages):
        """Groupe les pointages par semaine (lundi-dimanche)"""
        semaines = []
        semaine_courante = []
        
        for pointage in pointages:
            # Début de semaine = lundi (weekday() = 0)
            if pointage.date_pointage.weekday() == 0 and semaine_courante:
                semaines.append(semaine_courante)
                semaine_courante = []
            
            semaine_courante.append(pointage)
        
        if semaine_courante:
            semaines.append(semaine_courante)
        
        return semaines
    
    def _calculer_heures_semaine(self, pointages_semaine):
        """Calcule les heures pour une semaine"""
        heures_totales_semaine = Decimal('0')
        heures_nuit = Decimal('0')
        heures_feries = Decimal('0')
        
        for pointage in pointages_semaine:
            if not pointage.heures_travaillees:
                continue
            
            heures_jour = Decimal(str(pointage.heures_travaillees))
            heures_totales_semaine += heures_jour
            
            # Calcul des heures de nuit
            if pointage.heure_entree and pointage.heure_sortie:
                heures_nuit += self._calculer_heures_nuit(
                    pointage.date_pointage,
                    pointage.heure_entree,
                    pointage.heure_sortie
                )
            
            # Heures en jour férié
            if pointage.date_pointage in self.jours_feries:
                heures_feries += heures_jour
        
        # Répartition heures normales / supplémentaires
        heures_normales = min(heures_totales_semaine, self.HEURES_NORMALES_SEMAINE)
        heures_sup_total = max(Decimal('0'), heures_totales_semaine - self.HEURES_NORMALES_SEMAINE)
        
        # Répartition des heures supplémentaires
        heures_sup_30 = min(heures_sup_total, Decimal('4.0'))  # 4 premières HS à +30%
        heures_sup_60 = max(Decimal('0'), heures_sup_total - Decimal('4.0'))  # Au-delà à +60%
        
        return {
            'normales': heures_normales,
            'sup_30': heures_sup_30,
            'sup_60': heures_sup_60,
            'nuit': heures_nuit,
            'feries': heures_feries,
        }
    
    def _calculer_heures_nuit(self, date_pointage, heure_entree, heure_sortie):
        """Calcule les heures de nuit (20h-6h)"""
        heures_nuit = Decimal('0')
        
        # Conversion en datetime pour faciliter les calculs
        debut = datetime.combine(date_pointage, heure_entree)
        fin = datetime.combine(date_pointage, heure_sortie)
        
        # Si la sortie est le lendemain
        if heure_sortie < heure_entree:
            fin += timedelta(days=1)
        
        # Période de nuit du jour même (20h-24h)
        debut_nuit_jour = datetime.combine(date_pointage, self.HEURE_DEBUT_NUIT)
        fin_nuit_jour = datetime.combine(date_pointage + timedelta(days=1), time(0, 0))
        
        # Intersection avec la période de travail
        intersection_debut = max(debut, debut_nuit_jour)
        intersection_fin = min(fin, fin_nuit_jour)
        
        if intersection_fin > intersection_debut:
            heures_nuit += Decimal(str((intersection_fin - intersection_debut).total_seconds() / 3600))
        
        # Période de nuit du lendemain (0h-6h)
        debut_nuit_lendemain = datetime.combine(date_pointage + timedelta(days=1), time(0, 0))
        fin_nuit_lendemain = datetime.combine(date_pointage + timedelta(days=1), self.HEURE_FIN_NUIT)
        
        # Intersection avec la période de travail
        intersection_debut = max(debut, debut_nuit_lendemain)
        intersection_fin = min(fin, fin_nuit_lendemain)
        
        if intersection_fin > intersection_debut:
            heures_nuit += Decimal(str((intersection_fin - intersection_debut).total_seconds() / 3600))
        
        return heures_nuit
    
    def calculer_primes(self, salaire_horaire):
        """Calcule les primes selon les heures travaillées"""
        heures = self.calculer_heures_periode()
        
        # Prime heures supplémentaires
        prime_hs_30 = heures['heures_supplementaires_30'] * salaire_horaire * (self.TAUX_HS_30 - Decimal('1'))
        prime_hs_60 = heures['heures_supplementaires_60'] * salaire_horaire * (self.TAUX_HS_60 - Decimal('1'))
        prime_heures_sup = prime_hs_30 + prime_hs_60
        
        # Prime de nuit
        prime_nuit = heures['heures_nuit'] * salaire_horaire * (self.TAUX_NUIT - Decimal('1'))
        
        # Prime jours fériés
        # Calcul complexe : jour férié jour vs nuit
        prime_feries = Decimal('0')
        for pointage in Pointage.objects.filter(
            employe=self.employe,
            date_pointage__gte=self.periode.date_debut,
            date_pointage__lte=self.periode.date_fin,
            date_pointage__in=self.jours_feries,
            valide=True
        ):
            if pointage.heures_travaillees:
                heures_jour_ferie = Decimal(str(pointage.heures_travaillees))
                
                # Vérifier si c'est de nuit
                if pointage.heure_entree and pointage.heure_sortie:
                    heures_nuit_ferie = self._calculer_heures_nuit(
                        pointage.date_pointage,
                        pointage.heure_entree,
                        pointage.heure_sortie
                    )
                    heures_jour_ferie_jour = heures_jour_ferie - heures_nuit_ferie
                    
                    # Prime jour férié jour
                    prime_feries += heures_jour_ferie_jour * salaire_horaire * (self.TAUX_FERIE_JOUR - Decimal('1'))
                    # Prime jour férié nuit
                    prime_feries += heures_nuit_ferie * salaire_horaire * (self.TAUX_FERIE_NUIT - Decimal('1'))
                else:
                    # Par défaut, considérer comme jour
                    prime_feries += heures_jour_ferie * salaire_horaire * (self.TAUX_FERIE_JOUR - Decimal('1'))
        
        return {
            'prime_heures_sup': prime_heures_sup,
            'prime_nuit': prime_nuit,
            'prime_feries': prime_feries,
        }


def calculer_salaire_horaire(salaire_mensuel, heures_mensuelles=Decimal('173.33')):
    """Calcule le salaire horaire à partir du salaire mensuel"""
    return salaire_mensuel / heures_mensuelles


def integrer_heures_bulletin(bulletin):
    """Intègre automatiquement les heures dans un bulletin de paie"""
    calculateur = CalculateurHeures(bulletin.employe, bulletin.periode)
    
    # Calcul des heures
    heures = calculateur.calculer_heures_periode()
    
    # Mise à jour du bulletin
    bulletin.heures_normales = heures['heures_normales']
    bulletin.heures_supplementaires_30 = heures['heures_supplementaires_30']
    bulletin.heures_supplementaires_60 = heures['heures_supplementaires_60']
    bulletin.heures_nuit = heures['heures_nuit']
    bulletin.heures_feries = heures['heures_feries']
    
    # Calcul du salaire horaire
    salaire_horaire = calculer_salaire_horaire(bulletin.employe.salaire_base)
    
    # Calcul des primes
    primes = calculateur.calculer_primes(salaire_horaire)
    bulletin.prime_heures_sup = primes['prime_heures_sup']
    bulletin.prime_nuit = primes['prime_nuit']
    bulletin.prime_feries = primes['prime_feries']
    
    # Recalcul du salaire brut
    bulletin.salaire_base = bulletin.employe.salaire_base
    bulletin.salaire_brut = (
        bulletin.salaire_base + 
        bulletin.prime_heures_sup + 
        bulletin.prime_nuit + 
        bulletin.prime_feries
    )
    
    bulletin.save()
    
    return bulletin
