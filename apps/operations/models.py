from decimal import Decimal
from django.db import models
from apps.core.models import TimeStampedModel, Parametres
from apps.flotte.models import Camion
from apps.rh.models import Employe


class Carburant(TimeStampedModel):
    """Une prise de carburant."""
    date = models.DateField("Date")
    heure = models.TimeField("Heure", null=True, blank=True)
    camion = models.ForeignKey(Camion, on_delete=models.PROTECT, related_name="carburants")
    chauffeur = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True, related_name="carburants")
    contrat = models.ForeignKey(
        "facturation.Contrat", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="carburants", verbose_name="Projet / Contrat",
        help_text="Si renseigné, ce carburant sera imputé à ce contrat. Sinon, il sera réparti au prorata entre tous les contrats actifs.",
    )
    km_tableau_bord = models.PositiveIntegerField("Km au tableau de bord", default=0)
    km_avant = models.PositiveIntegerField("Km avant prise", default=0)
    litres_avant = models.DecimalField("Nb L avant", max_digits=8, decimal_places=2, default=0)
    litres_apres = models.DecimalField("Nb L après", max_digits=8, decimal_places=2, default=0)
    prix_unitaire = models.DecimalField("Prix unitaire (GNF/L)", max_digits=10, decimal_places=2, default=0)
    station = models.CharField("Station / Lieu", max_length=120, blank=True)
    observations = models.CharField("Observations", max_length=200, blank=True)

    class Meta:
        verbose_name = "Prise de carburant"
        verbose_name_plural = "Carburant — Suivi des prises"
        ordering = ["-date", "-heure"]
        indexes = [models.Index(fields=["date", "camion"])]

    def __str__(self):
        return f"{self.date} — {self.camion.code}"

    def save(self, *args, **kwargs):
        if not self.prix_unitaire:
            self.prix_unitaire = Parametres.load().prix_carburant
        super().save(*args, **kwargs)

    @property
    def km_parcourus(self):
        return max(self.km_tableau_bord - self.km_avant, 0)

    @property
    def litres_pris(self):
        return max(self.litres_apres - self.litres_avant, Decimal(0))

    @property
    def consommation_100km(self):
        km = self.km_parcourus
        if km == 0:
            return Decimal(0)
        return (self.litres_pris / Decimal(km)) * Decimal(100)

    @property
    def montant_total(self):
        return self.litres_pris * self.prix_unitaire


class Panne(TimeStampedModel):
    class Type(models.TextChoices):
        PNEUS = "PNEUS", "Pneus"
        MOTEUR = "MOTEUR", "Moteur"
        FREINAGE = "FREINAGE", "Freinage"
        TRANSMISSION = "TRANSMISSION", "Transmission"
        SUSPENSION = "SUSPENSION", "Suspension"
        ELECTRICITE = "ELECTRICITE", "Électricité"
        HYDRAULIQUE = "HYDRAULIQUE", "Hydraulique"
        CARROSSERIE = "CARROSSERIE", "Carrosserie"
        AUTRE = "AUTRE", "Autre"

    date = models.DateField("Date")
    camion = models.ForeignKey(Camion, on_delete=models.PROTECT, related_name="pannes")
    contrat = models.ForeignKey(
        "facturation.Contrat", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pannes", verbose_name="Projet / Contrat",
        help_text="Si renseigné, cette panne sera imputée à ce contrat. Sinon, elle sera répartie au prorata entre tous les contrats actifs.",
    )
    type_panne = models.CharField("Type", max_length=20, choices=Type.choices)
    piece_remplacee = models.CharField("Pièce remplacée", max_length=200, blank=True)
    fournisseur = models.CharField("Fournisseur / Garage", max_length=120, blank=True)
    cout_pieces = models.DecimalField("Coût pièces (GNF)", max_digits=14, decimal_places=2, default=0)
    cout_main_oeuvre = models.DecimalField("Coût main d'œuvre (GNF)", max_digits=14, decimal_places=2, default=0)
    duree_immobilisation = models.PositiveIntegerField("Durée immobilisation (jours)", default=0)
    observations = models.CharField("Observations", max_length=200, blank=True)

    class Meta:
        verbose_name = "Panne / Réparation"
        verbose_name_plural = "Pannes & réparations"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} — {self.camion.code} — {self.get_type_panne_display()}"

    @property
    def cout_total(self):
        return self.cout_pieces + self.cout_main_oeuvre


class DepenseAdmin(TimeStampedModel):
    class Type(models.TextChoices):
        IMMATRICULATION = "IMMAT", "Immatriculation"
        ASSURANCE = "ASSU", "Assurance"
        VISITE_TECHNIQUE = "VT", "Visite technique"
        TAXE = "TAXE", "Taxe de transport"
        LICENCE = "LICENCE", "Licence"
        BANQUE = "BANQUE", "Frais bancaires"
        AUTRE = "AUTRE", "Autre"

    class Statut(models.TextChoices):
        PAYE = "PAYE", "Payé"
        EN_ATTENTE = "ATTENTE", "En attente"
        EN_RETARD = "RETARD", "En retard"

    date = models.DateField("Date")
    camion = models.ForeignKey(Camion, on_delete=models.SET_NULL, null=True, blank=True, related_name="depenses_admin")
    contrat = models.ForeignKey(
        "facturation.Contrat", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="depenses_admin", verbose_name="Projet / Contrat",
        help_text="Si renseigné, cette dépense sera imputée à ce contrat. Sinon, elle sera répartie au prorata entre tous les contrats actifs.",
    )
    type_depense = models.CharField("Type de dépense", max_length=10, choices=Type.choices)
    description = models.CharField("Description", max_length=200)
    reference = models.CharField("Référence / N° document", max_length=80, blank=True)
    montant = models.DecimalField("Montant (GNF)", max_digits=14, decimal_places=2, default=0)
    echeance = models.DateField("Échéance", null=True, blank=True)
    statut = models.CharField("Statut", max_length=10, choices=Statut.choices, default=Statut.PAYE)

    class Meta:
        verbose_name = "Dépense administrative"
        verbose_name_plural = "Dépenses administratives"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} — {self.get_type_depense_display()} — {self.montant}"


class TransportBauxite(TimeStampedModel):
    """Voyage / rotation de bauxite."""
    date = models.DateField("Date")
    camion = models.ForeignKey(Camion, on_delete=models.PROTECT, related_name="transports")
    chauffeur = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True, related_name="transports")
    contrat = models.ForeignKey(
        "facturation.Contrat", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="transports", verbose_name="Projet / Contrat",
        help_text="Contrat client auquel ce voyage est rattaché. Détermine la facturation.",
    )
    trajet = models.CharField("Trajet (départ → arrivée)", max_length=200)
    distance_km = models.DecimalField("Distance (km)", max_digits=8, decimal_places=2, default=0)
    tonnage = models.DecimalField("Tonnage transporté (T)", max_digits=8, decimal_places=2, default=0)
    tarif_unitaire = models.DecimalField("Tarif (GNF/T)", max_digits=14, decimal_places=2, default=0)
    client = models.CharField("Client (société minière)", max_length=80, default="CBG")
    num_bon = models.CharField("N° Bon de livraison", max_length=40, blank=True, unique=False)
    observations = models.CharField("Observations", max_length=200, blank=True)

    class Meta:
        verbose_name = "Voyage bauxite"
        verbose_name_plural = "Transport bauxite"
        ordering = ["-date"]
        indexes = [models.Index(fields=["date", "camion"]), models.Index(fields=["client"])]

    def __str__(self):
        return f"{self.date} — {self.camion.code} — {self.tonnage} T"

    def save(self, *args, **kwargs):
        if not self.tarif_unitaire:
            self.tarif_unitaire = Parametres.load().tarif_bauxite
        super().save(*args, **kwargs)

    @property
    def chiffre_affaires(self):
        return self.tonnage * self.tarif_unitaire


class BonTransport(TimeStampedModel):
    """Bon de transport — registre chargement/pesée (feuille Bon Transport)."""
    date = models.DateField("Date")
    prenom = models.CharField("First Name / Prénom", max_length=80)
    nom = models.CharField("Last Name / Nom", max_length=80)
    telephone = models.CharField("Phone Number", max_length=30, blank=True)
    plaque = models.CharField("Plate / Plaque", max_length=30)
    carte_entree = models.CharField("Carte d'entrée / Entry car N°", max_length=40, blank=True)
    lieu_chargement = models.CharField("Lieu de chargement / Loading zone", max_length=120)
    heure_depart = models.TimeField("Heure de départ / Departure Time", null=True, blank=True)
    heure_pesee_start = models.TimeField("Heure pesée Start", null=True, blank=True)
    heure_pesee_end = models.TimeField("Heure pesée End", null=True, blank=True)
    observation = models.CharField("Observation", max_length=200, blank=True)
    quantite = models.DecimalField("Quantité / Quantity (T)", max_digits=8, decimal_places=2, default=0)
    num_bon = models.CharField("N° Bon", max_length=40, unique=True)
    camion = models.ForeignKey(Camion, on_delete=models.SET_NULL, null=True, blank=True, related_name="bons")
    chauffeur = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True, related_name="bons")
    contrat = models.ForeignKey(
        "facturation.Contrat", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="bons", verbose_name="Projet / Contrat",
        help_text="Contrat client auquel ce bon de transport est rattaché.",
    )

    class Meta:
        verbose_name = "Bon de transport"
        verbose_name_plural = "Bons de transport"
        ordering = ["-date"]
        indexes = [models.Index(fields=["date", "plaque"])]

    def __str__(self):
        return f"{self.num_bon} — {self.date}"

    def save(self, *args, **kwargs):
        if not self.num_bon:
            self.num_bon = f"BT-{self.date.strftime('%Y-%m')}-{BonTransport.objects.filter(date__year=self.date.year, date__month=self.date.month).count()+1:03d}"
        super().save(*args, **kwargs)
