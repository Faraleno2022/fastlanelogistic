import calendar
from datetime import date, timedelta
from decimal import Decimal
from django.db import models
from apps.core.models import TimeStampedModel, Parametres
from apps.flotte.models import Camion


class Contrat(TimeStampedModel):
    class TypeFacturation(models.TextChoices):
        TONNE = "TONNE", "À la tonne"
        TONNE_KM = "TONNE_KM", "Tonne × km"
        VOYAGE = "VOYAGE", "Au voyage"
        FORFAIT = "FORFAIT", "Forfait mensuel"

    code = models.CharField("N° contrat", max_length=40, unique=True)
    client = models.CharField("Client (société minière)", max_length=120)
    type_facturation = models.CharField("Type de facturation", max_length=10, choices=TypeFacturation.choices, default=TypeFacturation.TONNE)
    tarif = models.DecimalField("Tarif unitaire", max_digits=14, decimal_places=2, default=0)
    date_debut = models.DateField("Date début")
    date_fin = models.DateField("Date fin", null=True, blank=True)
    actif = models.BooleanField("Actif", default=True)
    observations = models.TextField("Observations", blank=True)

    class Meta:
        verbose_name = "Contrat client"
        verbose_name_plural = "Contrats clients"
        ordering = ["-actif", "-date_debut"]

    def __str__(self):
        return f"{self.code} — {self.client}"


class Facture(TimeStampedModel):
    class Statut(models.TextChoices):
        BROUILLON = "BROUILLON", "Brouillon"
        EMISE = "EMISE", "Émise"
        PAYEE = "PAYEE", "Payée"
        ANNULEE = "ANNULEE", "Annulée"

    numero = models.CharField("N° facture", max_length=40, unique=True)
    contrat = models.ForeignKey(Contrat, on_delete=models.PROTECT, related_name="factures")
    periode_mois = models.PositiveSmallIntegerField("Mois")
    periode_annee = models.PositiveIntegerField("Année")
    date_emission = models.DateField("Date d'émission")
    echeance = models.DateField("Échéance", null=True, blank=True)

    nb_bons = models.PositiveIntegerField("Nombre de bons", default=0)
    nb_rotations = models.PositiveIntegerField("Nombre de rotations", default=0)
    tonnage_total = models.DecimalField("Tonnage total (T)", max_digits=12, decimal_places=2, default=0)
    distance_total = models.DecimalField("Distance totale (km)", max_digits=12, decimal_places=2, default=0)

    montant_brut = models.DecimalField("Montant brut (GNF)", max_digits=18, decimal_places=2, default=0)
    bonus = models.DecimalField("Bonus (GNF)", max_digits=14, decimal_places=2, default=0)
    penalites = models.DecimalField("Pénalités (GNF)", max_digits=14, decimal_places=2, default=0)
    deduction_carburant = models.DecimalField("Déduction avance carburant (GNF)", max_digits=14, decimal_places=2, default=0)

    montant_ht = models.DecimalField("Montant HT (GNF)", max_digits=18, decimal_places=2, default=0)
    taux_tva = models.DecimalField("Taux TVA", max_digits=5, decimal_places=4, default=Decimal("0.18"))
    tva = models.DecimalField("TVA (GNF)", max_digits=16, decimal_places=2, default=0)
    montant_ttc = models.DecimalField("Montant TTC (GNF)", max_digits=18, decimal_places=2, default=0)

    statut = models.CharField("Statut", max_length=10, choices=Statut.choices, default=Statut.BROUILLON)
    observations = models.TextField("Observations", blank=True)

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ["-date_emission"]

    def __str__(self):
        return f"{self.numero} — {self.contrat.client} — {self.periode_mois}/{self.periode_annee}"

    def recalculer(self):
        """Recalcule les montants à partir des opérations du mois.
        Utilise des agrégats SQL (Sum/Count) pour la performance.
        Stratégie : rattachement au contrat via FK (priorité), sinon fallback
        sur le champ `client` du voyage (compat. historique).
        """
        from django.db.models import Sum, Count, Q
        from apps.operations.models import TransportBauxite, BonTransport, Carburant

        voyages_qs = TransportBauxite.objects.filter(
            date__month=self.periode_mois,
            date__year=self.periode_annee,
        ).filter(
            Q(contrat=self.contrat) |
            (Q(contrat__isnull=True) & Q(client__iexact=self.contrat.client))
        )
        voyages_agg = voyages_qs.aggregate(
            nb=Count("id"),
            tonnage=Sum("tonnage"),
            distance=Sum("distance_km"),
        )
        self.nb_rotations = voyages_agg["nb"] or 0
        self.tonnage_total = voyages_agg["tonnage"] or Decimal(0)
        self.distance_total = voyages_agg["distance"] or Decimal(0)

        self.nb_bons = BonTransport.objects.filter(
            date__month=self.periode_mois,
            date__year=self.periode_annee,
        ).filter(
            Q(contrat=self.contrat) | Q(contrat__isnull=True)
        ).count()

        # Calcul du montant brut selon le type de facturation du contrat
        if self.contrat.type_facturation == Contrat.TypeFacturation.TONNE:
            self.montant_brut = self.tonnage_total * self.contrat.tarif
        elif self.contrat.type_facturation == Contrat.TypeFacturation.TONNE_KM:
            self.montant_brut = self.tonnage_total * self.distance_total * self.contrat.tarif
        elif self.contrat.type_facturation == Contrat.TypeFacturation.VOYAGE:
            self.montant_brut = self.nb_rotations * self.contrat.tarif
        else:  # FORFAIT
            self.montant_brut = self.contrat.tarif

        # Déduction automatique du carburant consommé sur la période (si 0 saisi)
        if not self.deduction_carburant:
            car = Carburant.objects.filter(
                date__month=self.periode_mois,
                date__year=self.periode_annee,
            ).aggregate(total=Sum(
                models.F("litres_apres") - models.F("litres_avant"),
                output_field=models.DecimalField(max_digits=14, decimal_places=2),
            ))
            # On ne pré-remplit PAS la déduction automatiquement :
            # la déduction carburant reste un choix client (avance). On garde 0 par défaut.

        self.montant_ht = self.montant_brut + self.bonus - self.penalites - self.deduction_carburant
        self.tva = self.montant_ht * self.taux_tva
        self.montant_ttc = self.montant_ht + self.tva
        return self

    # ---------------------------------------------------------------
    # GÉNÉRATION AUTOMATIQUE INTELLIGENTE
    # ---------------------------------------------------------------
    @classmethod
    def numero_suivant(cls, mois, annee, contrat):
        """Génère un numéro de facture FAC-YYYY-MM-NNN unique."""
        prefix = f"FAC-{annee}-{mois:02d}"
        existing = cls.objects.filter(numero__startswith=prefix).count()
        return f"{prefix}-{existing + 1:03d}"

    @classmethod
    def generer_mensuelle(cls, contrat, mois, annee, force=False):
        """Crée ou met à jour la facture d'un contrat pour une période donnée.

        - Idempotent : si la facture existe déjà, elle est retournée.
        - Si statut=BROUILLON ou force=True → recalcul des montants.
        - Si statut=EMISE/PAYEE/ANNULEE → figée, pas de recalcul.
        """
        last_day = calendar.monthrange(annee, mois)[1]
        date_emission = date(annee, mois, last_day)
        echeance = date_emission + timedelta(days=30)

        facture = cls.objects.filter(
            contrat=contrat, periode_mois=mois, periode_annee=annee
        ).first()

        created = False
        if facture is None:
            facture = cls(
                contrat=contrat,
                periode_mois=mois,
                periode_annee=annee,
                date_emission=date_emission,
                echeance=echeance,
                taux_tva=Parametres.load().taux_tva,
                statut=cls.Statut.BROUILLON,
                numero=cls.numero_suivant(mois, annee, contrat),
            )
            created = True

        modifiable = facture.statut == cls.Statut.BROUILLON
        if created or force or modifiable:
            facture.recalculer()
            facture.save()

        return facture, created

    @classmethod
    def generer_pour_periode(cls, mois, annee, force=False):
        """Génère les factures pour TOUS les contrats actifs sur (mois, annee).
        Retourne la liste (facture, created) pour journalisation.
        """
        resultats = []
        contrats = Contrat.objects.filter(actif=True).filter(
            models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=date(annee, mois, 1))
        )
        for c in contrats:
            # Skip si contrat commence après la fin de la période
            fin_periode = date(annee, mois, calendar.monthrange(annee, mois)[1])
            if c.date_debut > fin_periode:
                continue
            facture, created = cls.generer_mensuelle(c, mois, annee, force=force)
            resultats.append((facture, created))
        return resultats
