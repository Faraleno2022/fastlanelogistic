"""
Modèle de simulation fiscale - historique des simulations multi-barèmes
"""
from django.db import models
from django.utils import timezone
from core.models import Utilisateur, Entreprise


class SimulationFiscale(models.Model):
    """Historique des simulations fiscales comparatives multi-barèmes"""

    entreprise = models.ForeignKey(
        Entreprise, on_delete=models.CASCADE,
        related_name='simulations_fiscales', null=True, blank=True,
    )
    utilisateur = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='simulations_fiscales',
    )
    date_simulation = models.DateTimeField(default=timezone.now)

    # Paramètres d'entrée
    salaire_brut = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_indemnites = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Label libre (ex: "M. Diallo – vérification barème 2026")
    label = models.CharField(max_length=200, blank=True)

    # Barèmes comparés (ex: ["Barème 2026 — Officiel", "Barème CGI référence"])
    baremes_compares = models.JSONField(
        default=list,
        help_text='Labels lisibles des barèmes comparés',
    )

    # Snapshot complet pour rejeu/audit
    parametres_json = models.JSONField(
        default=dict,
        help_text='Snapshot barèmes + constantes utilisés',
    )
    resultats_json = models.JSONField(
        default=list,
        help_text='Résultats comparatifs par barème (cnss, rts, net, détail tranches)',
    )

    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'simulations_fiscales'
        verbose_name = 'Simulation fiscale'
        verbose_name_plural = 'Simulations fiscales'
        ordering = ['-date_simulation']
        indexes = [
            models.Index(fields=['entreprise', 'date_simulation'], name='idx_sim_entrep_date'),
        ]

    def __str__(self):
        ts = self.date_simulation.strftime('%d/%m/%Y %H:%M')
        label = self.label or f'Brut {int(self.salaire_brut):,} GNF'.replace(',', ' ')
        return f"Simulation {ts} — {label}"

    @property
    def nb_baremes(self):
        return len(self.baremes_compares)
