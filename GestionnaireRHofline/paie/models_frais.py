"""
Modèles pour la gestion des notes de frais.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class CategoriesFrais(models.Model):
    """Catégories de frais (transport, hébergement, repas, etc.)"""
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    plafond_journalier = models.DecimalField(
        max_digits=15, decimal_places=2, 
        blank=True, null=True,
        help_text="Plafond journalier en GNF (optionnel)"
    )
    justificatif_obligatoire = models.BooleanField(default=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'categories_frais'
        verbose_name = 'Catégorie de frais'
        verbose_name_plural = 'Catégories de frais'
        ordering = ['libelle']
    
    def __str__(self):
        return self.libelle


class NoteFrais(models.Model):
    """Note de frais d'un employé"""
    STATUTS = (
        ('brouillon', 'Brouillon'),
        ('soumise', 'Soumise'),
        ('validee', 'Validée'),
        ('rejetee', 'Rejetée'),
        ('remboursee', 'Remboursée'),
    )
    
    employe = models.ForeignKey(
        'employes.Employe',
        on_delete=models.CASCADE,
        related_name='notes_frais'
    )
    reference = models.CharField(max_length=50, unique=True, blank=True)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_debut = models.DateField(help_text="Début de la période")
    date_fin = models.DateField(help_text="Fin de la période")
    
    # Montants
    montant_total = models.DecimalField(
        max_digits=15, decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    montant_valide = models.DecimalField(
        max_digits=15, decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    montant_rembourse = models.DecimalField(
        max_digits=15, decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Workflow
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    date_soumission = models.DateTimeField(blank=True, null=True)
    date_validation = models.DateTimeField(blank=True, null=True)
    valideur = models.ForeignKey(
        'employes.Employe',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='notes_frais_validees'
    )
    commentaire_validation = models.TextField(blank=True)
    date_remboursement = models.DateTimeField(blank=True, null=True)
    
    # Mission associée (optionnel)
    mission = models.CharField(max_length=200, blank=True, help_text="Mission ou projet associé")
    
    # Traçabilité
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notes_frais'
        verbose_name = 'Note de frais'
        verbose_name_plural = 'Notes de frais'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.reference} - {self.employe.nom} ({self.montant_total} GNF)"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            from datetime import date
            prefix = f"NF{date.today().strftime('%Y%m')}"
            last = NoteFrais.objects.filter(reference__startswith=prefix).order_by('-reference').first()
            if last:
                num = int(last.reference[-4:]) + 1
            else:
                num = 1
            self.reference = f"{prefix}{num:04d}"
        super().save(*args, **kwargs)
    
    def calculer_total(self):
        """Recalculer le montant total depuis les lignes"""
        total = self.lignes.aggregate(total=models.Sum('montant'))['total'] or Decimal('0')
        self.montant_total = total
        return total
    
    def calculer_valide(self):
        """Recalculer le montant validé"""
        total = self.lignes.filter(valide=True).aggregate(
            total=models.Sum('montant_valide')
        )['total'] or Decimal('0')
        self.montant_valide = total
        return total


class LigneFrais(models.Model):
    """Ligne de détail d'une note de frais"""
    note_frais = models.ForeignKey(
        NoteFrais,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    categorie = models.ForeignKey(
        CategoriesFrais,
        on_delete=models.PROTECT,
        related_name='lignes_frais'
    )
    date_depense = models.DateField()
    description = models.CharField(max_length=500)
    montant = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    devise = models.CharField(max_length=3, default='GNF')
    
    # Justificatif
    justificatif = models.FileField(
        upload_to='frais/justificatifs/%Y/%m/',
        blank=True, null=True
    )
    numero_facture = models.CharField(max_length=100, blank=True)
    
    # Validation
    valide = models.BooleanField(default=False)
    montant_valide = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    motif_rejet = models.TextField(blank=True)
    
    class Meta:
        db_table = 'lignes_frais'
        verbose_name = 'Ligne de frais'
        verbose_name_plural = 'Lignes de frais'
        ordering = ['date_depense']
    
    def __str__(self):
        return f"{self.categorie.libelle} - {self.montant} {self.devise}"
    
    def save(self, *args, **kwargs):
        # Par défaut, montant_valide = montant si validé
        if self.valide and self.montant_valide == 0:
            self.montant_valide = self.montant
        super().save(*args, **kwargs)
        # Recalculer le total de la note
        self.note_frais.calculer_total()
        self.note_frais.save()


class BaremeFrais(models.Model):
    """Barèmes de remboursement par catégorie et type d'employé"""
    categorie = models.ForeignKey(
        CategoriesFrais,
        on_delete=models.CASCADE,
        related_name='baremes'
    )
    type_employe = models.CharField(
        max_length=50,
        choices=(
            ('cadre_superieur', 'Cadre supérieur'),
            ('cadre', 'Cadre'),
            ('agent_maitrise', 'Agent de maîtrise'),
            ('employe', 'Employé'),
            ('ouvrier', 'Ouvrier'),
        ),
        blank=True,
        help_text="Laisser vide pour tous"
    )
    plafond_unitaire = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Plafond par dépense en GNF"
    )
    plafond_journalier = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        help_text="Plafond par jour en GNF"
    )
    plafond_mensuel = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        help_text="Plafond mensuel en GNF"
    )
    date_debut = models.DateField()
    date_fin = models.DateField(blank=True, null=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'baremes_frais'
        verbose_name = 'Barème de frais'
        verbose_name_plural = 'Barèmes de frais'
        ordering = ['categorie', 'type_employe']
    
    def __str__(self):
        return f"{self.categorie.libelle} - {self.get_type_employe_display() or 'Tous'}"
