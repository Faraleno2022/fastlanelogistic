from decimal import Decimal
from django.db import models
from apps.core.models import TimeStampedModel, Parametres


class Camion(TimeStampedModel):
    class Statut(models.TextChoices):
        EN_SERVICE = "SERVICE", "En service"
        ATELIER = "ATELIER", "En atelier"
        HORS_SERVICE = "HS", "Hors service"
        VENDU = "VENDU", "Vendu"

    code = models.CharField("Code camion", max_length=20, unique=True)
    immatriculation = models.CharField("Immatriculation", max_length=30, unique=True)
    marque_modele = models.CharField("Marque / Modèle", max_length=120)
    capacite_tonnes = models.DecimalField("Capacité (T)", max_digits=6, decimal_places=2)
    date_acquisition = models.DateField("Date d'acquisition")
    prix_achat = models.DecimalField("Prix d'achat (GNF)", max_digits=16, decimal_places=2)
    duree_amortissement = models.PositiveIntegerField("Durée amortissement (années)", default=5)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.EN_SERVICE)

    class Meta:
        verbose_name = "Camion"
        verbose_name_plural = "Camions"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.immatriculation}"

    @property
    def valeur_residuelle(self):
        params = Parametres.load()
        return (self.prix_achat or Decimal(0)) * params.taux_residuel

    @property
    def amortissement_annuel(self):
        if not self.duree_amortissement:
            return Decimal(0)
        return (self.prix_achat - self.valeur_residuelle) / self.duree_amortissement

    @property
    def amortissement_mensuel(self):
        return self.amortissement_annuel / 12

    def tableau_amortissement(self):
        """Retourne une liste de dicts : année, dotation, cumul, VNC, % amorti."""
        rows = []
        cumul = Decimal(0)
        for y in range(1, self.duree_amortissement + 1):
            dotation = self.amortissement_annuel
            cumul += dotation
            vnc = self.prix_achat - cumul
            rows.append({
                "annee": y,
                "dotation": dotation,
                "cumul": cumul,
                "vnc": vnc,
                "pct": cumul / self.prix_achat if self.prix_achat else 0,
            })
        return rows
