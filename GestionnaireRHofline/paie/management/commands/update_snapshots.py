from django.core.management.base import BaseCommand
from django.db import transaction
from paie.models import BulletinPaie
from paie.services import MoteurCalculPaie


class Command(BaseCommand):
    help = "Migre les snapshots bulletins v1.0 → v2.0 (audit JSON complet)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recalculer même les bulletins déjà en v2.0'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limiter le nombre de bulletins à traiter'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler sans écrire en base'
        )

    def handle(self, *args, **options):
        force   = options['force']
        limit   = options['limit']
        dry_run = options['dry_run']

        # Sélection des bulletins à migrer
        qs = BulletinPaie.objects.select_related(
            'employe', 'periode'
        ).order_by('id')

        if not force:
            # Uniquement les bulletins sans audit (v1.0 ou snapshot vide)
            qs = [
                b for b in qs
                if not (b.snapshot_parametres or {}).get('audit_calcul')
            ]
        else:
            qs = list(qs)

        if limit:
            qs = qs[:limit]

        total = len(qs)
        self.stdout.write(f"📋 {total} bulletin(s) à traiter"
                          + (" [DRY RUN]" if dry_run else ""))

        success = errors = skipped = 0

        for bulletin in qs:
            try:
                moteur = MoteurCalculPaie(bulletin.employe, bulletin.periode)
                moteur.calculer_bulletin()
                nouveau_snapshot = moteur._construire_snapshot()

                if dry_run:
                    skipped += 1
                    self.stdout.write(
                        f"  [DRY] {bulletin.id} — {bulletin.employe} "
                        f"{bulletin.mois_paie:02d}/{bulletin.annee_paie} → OK"
                    )
                    continue

                with transaction.atomic():
                    bulletin.snapshot_parametres = nouveau_snapshot
                    bulletin.save(update_fields=['snapshot_parametres'])

                success += 1
                if success % 10 == 0:
                    self.stdout.write(f"  ✅ {success}/{total} traités...")

            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"  ❌ Bulletin {bulletin.id} "
                        f"({bulletin.employe} {bulletin.mois_paie:02d}/"
                        f"{bulletin.annee_paie}): {e}"
                    )
                )

        # Résumé final
        self.stdout.write("")
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"DRY RUN terminé — {total} bulletins analysés, rien écrit."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"✅ Migration terminée : {success} OK / "
                f"{errors} erreurs / {total} total"
            ))
