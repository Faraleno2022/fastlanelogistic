"""
Module Secrétariat - Gestion administrative pour secrétaires.

Entités : Courrier, Rendez-vous, Visiteur, Appel, Document, Tâche,
Contact, Réunion. Toutes rattachées à une entreprise (multi-tenant).
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class SecretariatBase(models.Model):
    """Base commune : rattachement entreprise + traçabilité."""
    entreprise = models.ForeignKey(
        'core.Entreprise', on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ============================================================
# 2. COURRIER
# ============================================================
class Courrier(SecretariatBase):
    TYPES = [('entrant', 'Entrant'), ('sortant', 'Sortant')]
    STATUTS = [
        ('recu', 'Reçu'), ('en_attente', 'En attente'),
        ('traite', 'Traité'), ('archive', 'Archivé'),
    ]
    numero_ordre = models.CharField(max_length=30, blank=True, verbose_name="N° d'ordre")
    type_courrier = models.CharField(max_length=10, choices=TYPES, default='entrant')
    expediteur = models.CharField(max_length=200, blank=True)
    destinataire = models.CharField(max_length=200, blank=True)
    objet = models.CharField(max_length=255)
    date_courrier = models.DateField(default=timezone.now, verbose_name='Date réception/envoi')
    piece_jointe = models.FileField(upload_to='secretariat/courriers/', blank=True, null=True)
    statut = models.CharField(max_length=12, choices=STATUTS, default='recu')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Courrier'
        ordering = ['-date_courrier', '-id']

    def __str__(self):
        return f"{self.numero_ordre or '—'} · {self.objet}"

    def save(self, *args, **kwargs):
        if not self.numero_ordre and self.entreprise_id:
            annee = timezone.now().year
            n = Courrier.objects.filter(
                entreprise=self.entreprise, date_courrier__year=annee
            ).count() + 1
            prefix = 'C-IN' if self.type_courrier == 'entrant' else 'C-OUT'
            self.numero_ordre = f"{prefix}-{annee}-{n:04d}"
        super().save(*args, **kwargs)


# ============================================================
# 3. RENDEZ-VOUS
# ============================================================
class RendezVous(SecretariatBase):
    STATUTS = [
        ('confirme', 'Confirmé'), ('reporte', 'Reporté'),
        ('annule', 'Annulé'), ('termine', 'Terminé'),
    ]
    visiteur_nom = models.CharField(max_length=200, verbose_name='Nom du visiteur')
    motif = models.CharField(max_length=255)
    personne_concernee = models.CharField(max_length=200, blank=True)
    date_heure = models.DateTimeField(verbose_name='Date et heure')
    duree_minutes = models.PositiveIntegerField(default=30, verbose_name='Durée (min)')
    rappel = models.BooleanField(default=True, verbose_name='Rappel automatique')
    statut = models.CharField(max_length=10, choices=STATUTS, default='confirme')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Rendez-vous'
        verbose_name_plural = 'Rendez-vous'
        ordering = ['date_heure']

    def __str__(self):
        return f"{self.visiteur_nom} · {self.date_heure:%d/%m/%Y %H:%M}"


# ============================================================
# 4. VISITEUR
# ============================================================
class Visiteur(SecretariatBase):
    nom = models.CharField(max_length=200)
    telephone = models.CharField(max_length=30, blank=True)
    structure = models.CharField(max_length=200, blank=True)
    motif = models.CharField(max_length=255, blank=True)
    service_visite = models.CharField(max_length=200, blank=True, verbose_name='Service/responsable visité')
    date_visite = models.DateField(default=timezone.now)
    heure_arrivee = models.TimeField(null=True, blank=True, verbose_name="Heure d'arrivée")
    heure_sortie = models.TimeField(null=True, blank=True, verbose_name='Heure de sortie')

    class Meta:
        verbose_name = 'Visiteur'
        ordering = ['-date_visite', '-heure_arrivee']

    def __str__(self):
        return f"{self.nom} · {self.date_visite:%d/%m/%Y}"


# ============================================================
# 5. APPEL
# ============================================================
class Appel(SecretariatBase):
    SENS = [('entrant', 'Entrant'), ('sortant', 'Sortant')]
    sens = models.CharField(max_length=10, choices=SENS, default='entrant')
    appelant_nom = models.CharField(max_length=200, verbose_name="Nom de l'appelant")
    telephone = models.CharField(max_length=30, blank=True)
    objet = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True, verbose_name='Message laissé')
    suivi_requis = models.BooleanField(default=False, verbose_name='Suivi à faire')
    date_heure = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Appel'
        ordering = ['-date_heure']

    def __str__(self):
        return f"{self.appelant_nom} · {self.get_sens_display()}"


# ============================================================
# 6. DOCUMENT
# ============================================================
class DocumentSecretariat(SecretariatBase):
    CATEGORIES = [
        ('lettre', 'Lettre'), ('rapport', 'Rapport'),
        ('note_service', 'Note de service'), ('contrat', 'Contrat'),
        ('facture', 'Facture'), ('decision', 'Décision'),
        ('pv', 'Procès-verbal'), ('autre', 'Autre'),
    ]
    titre = models.CharField(max_length=255)
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default='lettre')
    fichier = models.FileField(upload_to='secretariat/documents/', blank=True, null=True)
    description = models.TextField(blank=True)
    date_document = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = 'Document'
        ordering = ['-date_document', '-id']

    def __str__(self):
        return self.titre


# ============================================================
# 7. TÂCHE
# ============================================================
class Tache(SecretariatBase):
    PRIORITES = [('faible', 'Faible'), ('moyenne', 'Moyenne'), ('urgente', 'Urgente')]
    ETATS = [('a_faire', 'À faire'), ('en_cours', 'En cours'), ('termine', 'Terminé')]
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priorite = models.CharField(max_length=10, choices=PRIORITES, default='moyenne')
    date_limite = models.DateField(null=True, blank=True, verbose_name='Date limite')
    responsable = models.CharField(max_length=200, blank=True)
    etat = models.CharField(max_length=10, choices=ETATS, default='a_faire')

    class Meta:
        verbose_name = 'Tâche'
        ordering = ['etat', 'date_limite']

    def __str__(self):
        return self.titre

    @property
    def est_en_retard(self):
        return (
            self.date_limite and self.etat != 'termine'
            and self.date_limite < timezone.now().date()
        )


# ============================================================
# 8. CONTACT
# ============================================================
class Contact(SecretariatBase):
    TYPES = [
        ('interne', 'Interne'), ('externe', 'Externe'),
        ('client', 'Client'), ('fournisseur', 'Fournisseur'),
        ('partenaire', 'Partenaire'), ('administration', 'Administration'),
    ]
    nom = models.CharField(max_length=200)
    type_contact = models.CharField(max_length=20, choices=TYPES, default='externe')
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    fonction = models.CharField(max_length=150, blank=True)
    organisation = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Contact'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom}{' · ' + self.organisation if self.organisation else ''}"


# ============================================================
# 9. RÉUNION
# ============================================================
class Reunion(SecretariatBase):
    titre = models.CharField(max_length=255)
    date_heure = models.DateTimeField(verbose_name='Date et heure')
    lieu = models.CharField(max_length=200, blank=True)
    participants = models.TextField(blank=True, help_text='Un participant par ligne')
    ordre_du_jour = models.TextField(blank=True)
    compte_rendu = models.TextField(blank=True)
    decisions = models.TextField(blank=True, verbose_name='Décisions prises')

    class Meta:
        verbose_name = 'Réunion'
        ordering = ['-date_heure']

    def __str__(self):
        return f"{self.titre} · {self.date_heure:%d/%m/%Y}"
