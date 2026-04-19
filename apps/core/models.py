from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    """Base abstraite : created_at / updated_at."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        abstract = True


class Parametres(models.Model):
    """Paramètres globaux de l'application (singleton).
    Équivalent de la feuille 'Paramètres' du fichier Excel.
    """
    societe_nom = models.CharField("Société", max_length=120, default="Fastlane Logistic")
    activite = models.CharField("Activité principale", max_length=120, default="Transport de Bauxite")
    devise = models.CharField("Devise", max_length=10, default="GNF")

    duree_amortissement = models.PositiveIntegerField(
        "Durée d'amortissement par défaut (années)",
        default=settings.DEFAULT_DUREE_AMORTISSEMENT,
    )
    taux_residuel = models.DecimalField(
        "Valeur résiduelle (fraction du prix)",
        max_digits=5, decimal_places=4,
        default=settings.DEFAULT_TAUX_RESIDUEL,
    )
    prix_carburant = models.DecimalField(
        "Prix moyen carburant (GNF/litre)",
        max_digits=12, decimal_places=2,
        default=settings.DEFAULT_PRIX_CARBURANT,
    )
    tarif_bauxite = models.DecimalField(
        "Tarif moyen transport bauxite (GNF/tonne)",
        max_digits=14, decimal_places=2,
        default=settings.DEFAULT_TARIF_BAUXITE,
    )
    taux_tva = models.DecimalField(
        "Taux TVA",
        max_digits=5, decimal_places=4,
        default=settings.DEFAULT_TAUX_TVA,
    )
    jours_ouvres_mois = models.PositiveIntegerField(
        "Jours ouvrés par mois", default=26,
    )

    class Meta:
        verbose_name = "Paramètre général"
        verbose_name_plural = "Paramètres généraux"

    def __str__(self):
        return self.societe_nom

    def save(self, *args, **kwargs):
        self.pk = 1  # singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
