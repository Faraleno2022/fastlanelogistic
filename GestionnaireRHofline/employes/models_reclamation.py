"""
Modèles pour la gestion des réclamations employés.
"""
from django.db import models


class CategorieReclamation(models.Model):
    """Catégories de réclamations"""
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    delai_traitement_jours = models.IntegerField(
        default=5,
        help_text="Délai de traitement en jours ouvrables"
    )
    responsable_defaut = models.ForeignKey(
        'employes.Employe',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='categories_reclamations_responsable',
        help_text="Responsable par défaut pour cette catégorie"
    )
    actif = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'categories_reclamations'
        verbose_name = 'Catégorie de réclamation'
        verbose_name_plural = 'Catégories de réclamations'
        ordering = ['libelle']
    
    def __str__(self):
        return self.libelle


class Reclamation(models.Model):
    """Réclamation d'un employé"""
    PRIORITES = (
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    )
    
    STATUTS = (
        ('ouverte', 'Ouverte'),
        ('en_cours', 'En cours de traitement'),
        ('en_attente', 'En attente d\'information'),
        ('resolue', 'Résolue'),
        ('rejetee', 'Rejetée'),
        ('fermee', 'Fermée'),
    )
    
    # Référence
    reference = models.CharField(max_length=50, unique=True, blank=True)
    
    # Demandeur
    employe = models.ForeignKey(
        'employes.Employe',
        on_delete=models.CASCADE,
        related_name='reclamations'
    )
    
    # Classification
    categorie = models.ForeignKey(
        CategorieReclamation,
        on_delete=models.PROTECT,
        related_name='reclamations'
    )
    priorite = models.CharField(max_length=20, choices=PRIORITES, default='normale')
    
    # Contenu
    objet = models.CharField(max_length=300)
    description = models.TextField()
    pieces_jointes = models.FileField(
        upload_to='reclamations/%Y/%m/',
        blank=True, null=True
    )
    
    # Workflow
    statut = models.CharField(max_length=20, choices=STATUTS, default='ouverte')
    date_ouverture = models.DateTimeField(auto_now_add=True)
    date_prise_en_charge = models.DateTimeField(blank=True, null=True)
    date_resolution = models.DateTimeField(blank=True, null=True)
    date_fermeture = models.DateTimeField(blank=True, null=True)
    
    # Traitement
    responsable = models.ForeignKey(
        'employes.Employe',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='reclamations_assignees'
    )
    reponse = models.TextField(blank=True, help_text="Réponse/résolution")
    motif_rejet = models.TextField(blank=True)
    
    # Satisfaction
    satisfaction = models.IntegerField(
        blank=True, null=True,
        help_text="Note de satisfaction (1-5)"
    )
    commentaire_satisfaction = models.TextField(blank=True)
    
    # Confidentialité
    confidentiel = models.BooleanField(
        default=False,
        help_text="Réclamation confidentielle (visible uniquement par RH)"
    )
    
    # Traçabilité
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reclamations'
        verbose_name = 'Réclamation'
        verbose_name_plural = 'Réclamations'
        ordering = ['-date_ouverture']
    
    def __str__(self):
        return f"{self.reference} - {self.objet}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            from datetime import date
            prefix = f"REC{date.today().strftime('%Y%m')}"
            last = Reclamation.objects.filter(reference__startswith=prefix).order_by('-reference').first()
            if last:
                num = int(last.reference[-4:]) + 1
            else:
                num = 1
            self.reference = f"{prefix}{num:04d}"
        super().save(*args, **kwargs)
    
    @property
    def delai_depasse(self):
        """Vérifier si le délai de traitement est dépassé"""
        if self.statut in ['resolue', 'rejetee', 'fermee']:
            return False
        from datetime import timedelta
        from django.utils import timezone
        delai = self.categorie.delai_traitement_jours
        date_limite = self.date_ouverture + timedelta(days=delai)
        return timezone.now() > date_limite
    
    @property
    def jours_ouverts(self):
        """Nombre de jours depuis l'ouverture"""
        from django.utils import timezone
        delta = timezone.now() - self.date_ouverture
        return delta.days


class CommentaireReclamation(models.Model):
    """Commentaires/suivi d'une réclamation"""
    reclamation = models.ForeignKey(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='commentaires'
    )
    auteur = models.ForeignKey(
        'employes.Employe',
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    contenu = models.TextField()
    piece_jointe = models.FileField(
        upload_to='reclamations/commentaires/%Y/%m/',
        blank=True, null=True
    )
    interne = models.BooleanField(
        default=False,
        help_text="Commentaire interne (non visible par l'employé)"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'commentaires_reclamations'
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['date_creation']
    
    def __str__(self):
        return f"Commentaire sur {self.reclamation.reference}"
