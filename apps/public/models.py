from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Evenement(models.Model):
    STATUT_CHOICES = [
        ("brouillon", "Brouillon"),
        ("publie", "Publié"),
    ]
    titre = models.CharField("Titre", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    date_evenement = models.DateField("Date de l'événement")
    lieu = models.CharField("Lieu", max_length=200, blank=True)
    resume = models.CharField("Résumé", max_length=300, blank=True,
                              help_text="Phrase d'accroche affichée dans la liste")
    contenu = models.TextField("Contenu", blank=True)
    image = models.ImageField("Image de couverture", upload_to="evenements/",
                               blank=True, null=True)
    statut = models.CharField("Statut", max_length=10, choices=STATUT_CHOICES,
                               default="brouillon")
    publie_le = models.DateTimeField("Publié le", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_evenement", "-created_at"]
        verbose_name = "Événement"
        verbose_name_plural = "Événements"

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)[:220] or "evenement"
        if self.statut == "publie" and not self.publie_le:
            self.publie_le = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("public:evenement_detail", args=[self.slug])

    @property
    def est_passe(self):
        return self.date_evenement < timezone.localdate()


class AppelOffre(models.Model):
    STATUT_CHOICES = [
        ("brouillon", "Brouillon"),
        ("ouvert", "Ouvert"),
        ("clos", "Clos"),
    ]
    reference = models.CharField("Référence", max_length=50, unique=True,
                                  help_text="ex: AO-2026-001")
    titre = models.CharField("Titre", max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    objet = models.CharField("Objet", max_length=300,
                              help_text="Résumé court affiché dans la liste")
    description = models.TextField("Description détaillée")
    lieu_execution = models.CharField("Lieu d'exécution", max_length=200, blank=True)
    date_publication = models.DateField("Date de publication",
                                         default=timezone.localdate)
    date_limite = models.DateField("Date limite de dépôt")
    contact_email = models.EmailField("E-mail de contact", blank=True)
    contact_telephone = models.CharField("Téléphone de contact",
                                          max_length=30, blank=True)
    document = models.FileField("Dossier d'appel d'offres (PDF)",
                                  upload_to="appels_offres/", blank=True, null=True)
    statut = models.CharField("Statut", max_length=10, choices=STATUT_CHOICES,
                               default="brouillon")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_publication", "-created_at"]
        verbose_name = "Appel d'offres"
        verbose_name_plural = "Appels d'offres"

    def __str__(self):
        return f"{self.reference} — {self.titre}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.reference}-{self.titre}"
            self.slug = slugify(base)[:240] or "appel-offre"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("public:appel_offre_detail", args=[self.slug])

    @property
    def est_ouvert(self):
        return (self.statut == "ouvert"
                and self.date_limite >= timezone.localdate())

    @property
    def jours_restants(self):
        return (self.date_limite - timezone.localdate()).days


class PageAPropos(models.Model):
    """Singleton pour la page 'À propos' (éditable dans l'admin)."""
    titre = models.CharField("Titre", max_length=200,
                              default="À propos de Fastlane Logistic")
    presentation = models.TextField("Présentation",
        default="Fastlane Logistic est un acteur du transport de bauxite "
                "en Guinée, au service des grands opérateurs miniers.")
    mission = models.TextField("Notre mission", blank=True)
    vision = models.TextField("Notre vision", blank=True)
    valeurs = models.TextField("Nos valeurs", blank=True)
    chiffres_cles = models.TextField(
        "Chiffres clés (un par ligne, format 'valeur|libellé')",
        blank=True,
        help_text="Ex.:\n50+|Camions\n200|Collaborateurs\n15|Ans d'expérience",
    )
    adresse = models.CharField("Adresse", max_length=300, blank=True)
    email = models.EmailField("E-mail public", blank=True)
    telephone = models.CharField("Téléphone public", max_length=30, blank=True)

    class Meta:
        verbose_name = "Page « À propos »"
        verbose_name_plural = "Page « À propos »"

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def chiffres(self):
        out = []
        for line in (self.chiffres_cles or "").splitlines():
            line = line.strip()
            if not line or "|" not in line:
                continue
            v, lbl = line.split("|", 1)
            out.append((v.strip(), lbl.strip()))
        return out
