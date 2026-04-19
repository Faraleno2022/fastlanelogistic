"""
Génération automatique des factures mensuelles.

Usage :
    python manage.py generer_factures                 # mois précédent (défaut)
    python manage.py generer_factures --mois 3 --annee 2026
    python manage.py generer_factures --force         # recalcule même BROUILLON existants
    python manage.py generer_factures --emettre       # passe automatiquement BROUILLON → EMISE

À planifier le 1er de chaque mois (cron / Tâches planifiées Windows) :
    0 2 1 * * cd /app && python manage.py generer_factures --emettre
"""
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.facturation.models import Facture


def _mois_precedent(d: date):
    """Retourne (mois, annee) du mois précédant d."""
    if d.month == 1:
        return 12, d.year - 1
    return d.month - 1, d.year


class Command(BaseCommand):
    help = "Génère automatiquement les factures mensuelles pour tous les contrats actifs."

    def add_arguments(self, parser):
        parser.add_argument("--mois", type=int, help="Mois (1-12). Défaut : mois précédent.")
        parser.add_argument("--annee", type=int, help="Année. Défaut : année courante ou précédente selon le mois.")
        parser.add_argument("--force", action="store_true",
                            help="Recalcule les factures existantes (même BROUILLON).")
        parser.add_argument("--emettre", action="store_true",
                            help="Passe les factures BROUILLON en EMISE après génération.")
        parser.add_argument("--dry-run", action="store_true",
                            help="Simulation : affiche ce qui serait fait sans écrire en base.")

    @transaction.atomic
    def handle(self, *args, **opts):
        mois = opts.get("mois")
        annee = opts.get("annee")

        if not mois or not annee:
            mois, annee = _mois_precedent(date.today())

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n=== Génération des factures pour {mois:02d}/{annee} ==="
        ))

        if opts.get("dry_run"):
            self.stdout.write(self.style.WARNING("Mode DRY-RUN : aucune écriture en base."))
            # Rollback à la fin
            sid = transaction.savepoint()

        resultats = Facture.generer_pour_periode(mois, annee, force=opts.get("force"))

        if not resultats:
            self.stdout.write(self.style.WARNING(
                "Aucun contrat actif éligible pour cette période."
            ))
            return

        nb_crees = 0
        nb_maj = 0
        total_ttc = 0
        for facture, created in resultats:
            verb = "Créée" if created else "Mise à jour"
            if created:
                nb_crees += 1
            else:
                nb_maj += 1
            total_ttc += float(facture.montant_ttc)

            style = self.style.SUCCESS if created else self.style.HTTP_INFO
            self.stdout.write(style(
                f"  {verb:12s} {facture.numero} — {facture.contrat.client[:30]:30s} "
                f"| {facture.nb_rotations:3d} voyages | {facture.tonnage_total:>8.1f} T "
                f"| TTC = {facture.montant_ttc:>15,.0f} GNF"
            ))

            if opts.get("emettre") and facture.statut == Facture.Statut.BROUILLON:
                facture.statut = Facture.Statut.EMISE
                facture.save(update_fields=["statut"])
                self.stdout.write(f"                → Statut mis à EMISE")

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n--- Bilan : {nb_crees} créée(s), {nb_maj} mise(s) à jour — "
            f"Total TTC = {total_ttc:,.0f} GNF ---"
        ))

        if opts.get("dry_run"):
            transaction.savepoint_rollback(sid)
            self.stdout.write(self.style.WARNING("DRY-RUN : rollback effectué."))
