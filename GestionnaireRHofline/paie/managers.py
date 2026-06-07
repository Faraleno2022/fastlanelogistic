"""
Managers personnalisés pour les modèles de paie.
Optimisent les requêtes courantes avec select_related/prefetch_related.
"""
from django.db import models
from django.db.models import Prefetch, Sum, Count, Q


class BulletinPaieQuerySet(models.QuerySet):
    """QuerySet optimisé pour les bulletins de paie."""
    
    def avec_employe(self):
        """Précharge les données de l'employé."""
        return self.select_related(
            'employe',
            'employe__etablissement',
            'employe__service',
            'employe__poste',
        )
    
    def avec_periode(self):
        """Précharge les données de la période."""
        return self.select_related('periode')
    
    def avec_lignes(self):
        """Précharge les lignes du bulletin."""
        from .models import LigneBulletin
        return self.prefetch_related(
            Prefetch(
                'lignes',
                queryset=LigneBulletin.objects.select_related('rubrique').order_by('ordre')
            )
        )
    
    def complet(self):
        """Précharge toutes les relations courantes."""
        return self.avec_employe().avec_periode().avec_lignes()
    
    def pour_entreprise(self, entreprise):
        """Filtre par entreprise."""
        return self.filter(employe__entreprise=entreprise)
    
    def pour_periode(self, periode):
        """Filtre par période."""
        return self.filter(periode=periode)
    
    def valides(self):
        """Bulletins validés uniquement."""
        return self.filter(statut_bulletin='valide')
    
    def calcules(self):
        """Bulletins calculés (non validés)."""
        return self.filter(statut_bulletin='calcule')
    
    def stats_agregees(self):
        """Calcule les statistiques agrégées."""
        return self.aggregate(
            total_brut=Sum('salaire_brut'),
            total_net=Sum('net_a_payer'),
            total_cnss_employe=Sum('cnss_employe'),
            total_cnss_employeur=Sum('cnss_employeur'),
            total_irg=Sum('irg'),
            count=Count('id'),
        )


class BulletinPaieManager(models.Manager):
    """Manager pour BulletinPaie avec méthodes optimisées."""
    
    def get_queryset(self):
        return BulletinPaieQuerySet(self.model, using=self._db)
    
    def avec_employe(self):
        return self.get_queryset().avec_employe()
    
    def avec_periode(self):
        return self.get_queryset().avec_periode()
    
    def complet(self):
        return self.get_queryset().complet()
    
    def pour_entreprise(self, entreprise):
        return self.get_queryset().pour_entreprise(entreprise)


class ElementSalaireQuerySet(models.QuerySet):
    """QuerySet optimisé pour les éléments de salaire."""
    
    def actifs(self):
        """Éléments actifs uniquement."""
        return self.filter(actif=True)
    
    def avec_rubrique(self):
        """Précharge la rubrique."""
        return self.select_related('rubrique')
    
    def pour_employe(self, employe):
        """Filtre par employé."""
        return self.filter(employe=employe)
    
    def valides_pour_date(self, date_ref):
        """Éléments valides à une date donnée."""
        return self.filter(
            date_debut__lte=date_ref
        ).filter(
            Q(date_fin__isnull=True) | Q(date_fin__gte=date_ref)
        )
    
    def gains(self):
        """Gains uniquement."""
        return self.filter(rubrique__type_rubrique='gain')
    
    def retenues(self):
        """Retenues uniquement."""
        return self.filter(rubrique__type_rubrique__in=['retenue', 'cotisation'])


class ElementSalaireManager(models.Manager):
    """Manager pour ElementSalaire."""
    
    def get_queryset(self):
        return ElementSalaireQuerySet(self.model, using=self._db)
    
    def actifs(self):
        return self.get_queryset().actifs()
    
    def avec_rubrique(self):
        return self.get_queryset().avec_rubrique()
    
    def pour_employe(self, employe):
        return self.get_queryset().pour_employe(employe)


class PeriodePaieQuerySet(models.QuerySet):
    """QuerySet optimisé pour les périodes de paie."""
    
    def ouvertes(self):
        """Périodes ouvertes."""
        return self.filter(statut_periode='ouverte')
    
    def calculees(self):
        """Périodes calculées."""
        return self.filter(statut_periode='calculee')
    
    def validees(self):
        """Périodes validées."""
        return self.filter(statut_periode='validee')
    
    def cloturees(self):
        """Périodes clôturées."""
        return self.filter(statut_periode='cloturee')
    
    def pour_entreprise(self, entreprise):
        """Filtre par entreprise."""
        return self.filter(entreprise=entreprise)
    
    def annee(self, annee):
        """Filtre par année."""
        return self.filter(annee=annee)
    
    def avec_stats_bulletins(self):
        """Ajoute les statistiques des bulletins."""
        return self.annotate(
            nb_bulletins=Count('bulletins'),
            total_brut=Sum('bulletins__salaire_brut'),
            total_net=Sum('bulletins__net_a_payer'),
        )


class PeriodePaieManager(models.Manager):
    """Manager pour PeriodePaie."""
    
    def get_queryset(self):
        return PeriodePaieQuerySet(self.model, using=self._db)
    
    def ouvertes(self):
        return self.get_queryset().ouvertes()
    
    def pour_entreprise(self, entreprise):
        return self.get_queryset().pour_entreprise(entreprise)
