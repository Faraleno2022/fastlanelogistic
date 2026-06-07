"""
Modèles pour les évaluations de performance des employés.
Gère les campagnes d'évaluation, les objectifs et les entretiens annuels.
"""
from django.db import models
from decimal import Decimal
from datetime import date


class CampagneEvaluation(models.Model):
    """Campagne d'évaluation annuelle"""
    STATUTS = (
        ('preparation', 'En préparation'),
        ('en_cours', 'En cours'),
        ('cloturee', 'Clôturée'),
        ('annulee', 'Annulée'),
    )
    
    entreprise = models.ForeignKey(
        'core.Entreprise',
        on_delete=models.CASCADE,
        related_name='campagnes_evaluation'
    )
    annee = models.IntegerField()
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUTS, default='preparation')
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'campagnes_evaluation'
        verbose_name = 'Campagne d\'évaluation'
        verbose_name_plural = 'Campagnes d\'évaluation'
        unique_together = ['entreprise', 'annee']
        ordering = ['-annee']
    
    def __str__(self):
        return f"Campagne {self.annee} - {self.titre}"
    
    @property
    def nb_evaluations(self):
        return self.evaluations.count()
    
    @property
    def nb_terminees(self):
        return self.evaluations.filter(statut='validee').count()
    
    @property
    def taux_completion(self):
        total = self.nb_evaluations
        if total > 0:
            return round((self.nb_terminees / total) * 100, 1)
        return 0


class Evaluation(models.Model):
    """Évaluation individuelle d'un employé"""
    STATUTS = (
        ('brouillon', 'Brouillon'),
        ('auto_evaluation', 'Auto-évaluation'),
        ('evaluation_manager', 'Évaluation manager'),
        ('entretien', 'Entretien planifié'),
        ('validee', 'Validée'),
        ('annulee', 'Annulée'),
    )
    
    NOTES = (
        (1, '1 - Insuffisant'),
        (2, '2 - À améliorer'),
        (3, '3 - Satisfaisant'),
        (4, '4 - Bon'),
        (5, '5 - Excellent'),
    )
    
    campagne = models.ForeignKey(
        CampagneEvaluation,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    employe = models.ForeignKey(
        'employes.Employe',
        on_delete=models.CASCADE,
        related_name='evaluations_performance'
    )
    evaluateur = models.ForeignKey(
        'employes.Employe',
        on_delete=models.SET_NULL,
        null=True,
        related_name='evaluations_realisees'
    )
    
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    date_entretien = models.DateField(null=True, blank=True)
    
    # Notes globales
    note_objectifs = models.IntegerField(choices=NOTES, null=True, blank=True)
    note_competences = models.IntegerField(choices=NOTES, null=True, blank=True)
    note_comportement = models.IntegerField(choices=NOTES, null=True, blank=True)
    note_globale = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    
    # Commentaires
    points_forts = models.TextField(blank=True)
    axes_amelioration = models.TextField(blank=True)
    commentaire_employe = models.TextField(blank=True)
    commentaire_evaluateur = models.TextField(blank=True)
    
    # Plan de développement
    plan_developpement = models.TextField(blank=True)
    besoins_formation = models.TextField(blank=True)
    
    # Évolution
    souhait_evolution = models.TextField(blank=True)
    proposition_augmentation = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Pourcentage d'augmentation proposé"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'evaluations_performance'
        verbose_name = 'Évaluation de performance'
        verbose_name_plural = 'Évaluations de performance'
        unique_together = ['campagne', 'employe']
        ordering = ['-campagne__annee', 'employe__nom']
    
    def __str__(self):
        return f"Évaluation {self.campagne.annee} - {self.employe}"
    
    def calculer_note_globale(self):
        """Calcule la note globale moyenne"""
        notes = [n for n in [self.note_objectifs, self.note_competences, self.note_comportement] if n]
        if notes:
            self.note_globale = Decimal(sum(notes)) / len(notes)
        return self.note_globale
    
    @property
    def appreciation(self):
        """Retourne l'appréciation basée sur la note globale"""
        if not self.note_globale:
            return None
        note = float(self.note_globale)
        if note >= 4.5:
            return 'Excellent'
        elif note >= 3.5:
            return 'Bon'
        elif note >= 2.5:
            return 'Satisfaisant'
        elif note >= 1.5:
            return 'À améliorer'
        else:
            return 'Insuffisant'


class ObjectifEvaluation(models.Model):
    """Objectifs individuels pour une évaluation"""
    STATUTS = (
        ('en_cours', 'En cours'),
        ('atteint', 'Atteint'),
        ('partiellement', 'Partiellement atteint'),
        ('non_atteint', 'Non atteint'),
        ('abandonne', 'Abandonné'),
    )
    
    PRIORITES = (
        ('haute', 'Haute'),
        ('moyenne', 'Moyenne'),
        ('basse', 'Basse'),
    )
    
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name='objectifs'
    )
    intitule = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    indicateurs = models.TextField(blank=True, help_text="Indicateurs de mesure")
    priorite = models.CharField(max_length=10, choices=PRIORITES, default='moyenne')
    poids = models.IntegerField(default=100, help_text="Poids en pourcentage")
    date_echeance = models.DateField(null=True, blank=True)
    
    # Résultats
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_cours')
    taux_realisation = models.IntegerField(default=0, help_text="Pourcentage de réalisation")
    commentaire_employe = models.TextField(blank=True)
    commentaire_evaluateur = models.TextField(blank=True)
    
    class Meta:
        db_table = 'objectifs_evaluation'
        verbose_name = 'Objectif'
        verbose_name_plural = 'Objectifs'
        ordering = ['-priorite', 'intitule']
    
    def __str__(self):
        return self.intitule


class CompetenceEvaluation(models.Model):
    """Évaluation des compétences"""
    NIVEAUX = (
        (1, '1 - Non maîtrisé'),
        (2, '2 - En cours d\'acquisition'),
        (3, '3 - Maîtrisé'),
        (4, '4 - Expert'),
    )
    
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name='competences'
    )
    competence = models.CharField(max_length=200)
    categorie = models.CharField(max_length=100, blank=True)
    niveau_requis = models.IntegerField(choices=NIVEAUX, default=3)
    niveau_actuel = models.IntegerField(choices=NIVEAUX, null=True, blank=True)
    commentaire = models.TextField(blank=True)
    
    class Meta:
        db_table = 'competences_evaluation'
        verbose_name = 'Compétence évaluée'
        verbose_name_plural = 'Compétences évaluées'
        ordering = ['categorie', 'competence']
    
    def __str__(self):
        return self.competence
    
    @property
    def ecart(self):
        """Calcule l'écart entre niveau requis et actuel"""
        if self.niveau_actuel:
            return self.niveau_actuel - self.niveau_requis
        return None
