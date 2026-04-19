from decimal import Decimal
from django.db import models
from apps.core.models import TimeStampedModel
from apps.flotte.models import Camion


class Employe(TimeStampedModel):
    class Fonction(models.TextChoices):
        CHAUFFEUR = "CHAUFFEUR", "Chauffeur"
        MECANICIEN = "MECANICIEN", "Mécanicien"
        PNEUMATICIEN = "PNEUMATICIEN", "Pneumaticien"
        ELECTRICIEN = "ELECTRICIEN", "Électricien auto"
        SOUDEUR = "SOUDEUR", "Soudeur"
        SUPERVISEUR = "SUPERVISEUR", "Superviseur"
        AGENT = "AGENT", "Agent logistique"
        AIDE = "AIDE", "Aide mécanicien"
        ADMIN = "ADMIN", "Administratif"
        GARDIEN = "GARDIEN", "Gardien"

    code = models.CharField("Code employé", max_length=12, unique=True)
    prenom = models.CharField("Prénom", max_length=80)
    nom = models.CharField("Nom", max_length=80)
    fonction = models.CharField("Fonction", max_length=20, choices=Fonction.choices)
    telephone = models.CharField("Téléphone", max_length=30, blank=True)
    site_prestation = models.CharField("Site de prestation", max_length=80, blank=True)
    camion = models.ForeignKey(
        Camion, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="chauffeurs", verbose_name="Camion assigné",
    )
    salaire_jour = models.DecimalField("Salaire / jour (GNF)", max_digits=12, decimal_places=2, default=0)
    salaire_base_mensuel = models.DecimalField("Salaire de base mensuel (GNF)", max_digits=14, decimal_places=2, default=0)
    primes = models.DecimalField("Primes mensuelles (GNF)", max_digits=14, decimal_places=2, default=0)
    taux_charges = models.DecimalField("Taux charges sociales", max_digits=5, decimal_places=4, default=Decimal("0.18"))
    date_embauche = models.DateField("Date d'embauche", null=True, blank=True)
    actif = models.BooleanField("Actif", default=True)

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.prenom} {self.nom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def charges_mensuelles(self):
        return (self.salaire_base_mensuel + self.primes) * self.taux_charges

    @property
    def salaire_total_mensuel(self):
        return self.salaire_base_mensuel + self.primes + self.charges_mensuelles


class Attendance(TimeStampedModel):
    """Pointage journalier d'un employé."""
    class Code(models.TextChoices):
        PRESENT = "P", "Présent"
        ABSENT = "A", "Absent"
        CONGE = "C", "Congé"
        MALADIE = "M", "Maladie"
        DIMANCHE = "D", "Dimanche travaillé"
        REPOS = "R", "Repos / Jour férié"

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField("Date")
    code = models.CharField("Code", max_length=2, choices=Code.choices, default=Code.PRESENT)
    commentaire = models.CharField("Commentaire", max_length=200, blank=True)

    class Meta:
        verbose_name = "Pointage (Attendance)"
        verbose_name_plural = "Pointages (Attendance)"
        unique_together = [("employe", "date")]
        ordering = ["-date", "employe__code"]
        indexes = [models.Index(fields=["date", "employe"])]

    def __str__(self):
        return f"{self.employe.code} — {self.date} : {self.code}"


class HeureSup(TimeStampedModel):
    class Type(models.TextChoices):
        OUVRE = "OUVRE", "Jour ouvré"
        NUIT = "NUIT", "Nuit"
        DIMANCHE = "DIMANCHE", "Dimanche"
        FERIE = "FERIE", "Jour férié"

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name="heures_sup")
    date = models.DateField("Date")
    heure_debut = models.TimeField("Heure début")
    heure_fin = models.TimeField("Heure fin")
    type_hs = models.CharField("Type", max_length=10, choices=Type.choices, default=Type.OUVRE)
    majoration = models.DecimalField(
        "Majoration", max_digits=4, decimal_places=2, default=Decimal("0.25"),
        help_text="Ex. 0.25 pour +25%, 1.00 pour +100%",
    )
    motif = models.CharField("Motif / Description", max_length=200, blank=True)
    valide_par = models.CharField("Validé par", max_length=100, blank=True)

    class Meta:
        verbose_name = "Heure supplémentaire"
        verbose_name_plural = "Heures supplémentaires"
        ordering = ["-date"]

    def __str__(self):
        return f"HS {self.employe.code} — {self.date}"

    @property
    def nb_heures(self):
        from datetime import datetime, date
        d = date.today()
        start = datetime.combine(d, self.heure_debut)
        end = datetime.combine(d, self.heure_fin)
        diff = (end - start).total_seconds() / 3600
        return Decimal(str(round(diff, 2))) if diff > 0 else Decimal(0)

    @property
    def taux_horaire(self):
        if self.employe.salaire_jour:
            return self.employe.salaire_jour / 8
        return Decimal(0)

    @property
    def montant(self):
        return self.nb_heures * self.taux_horaire * (Decimal(1) + self.majoration)
