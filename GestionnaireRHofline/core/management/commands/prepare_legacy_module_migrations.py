"""Prepare empty legacy Stock and Secretariat schemas for replacement.

The production database used older, incompatible initial migrations for these
two modules. This command is deliberately narrow: it only supports MySQL,
requires a completed SQL dump, and refuses to remove a table containing data.
"""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder


MODULES = ("secretariat", "stock")
INITIAL_MIGRATIONS = tuple((app, "0001_initial") for app in MODULES)


class Command(BaseCommand):
    help = (
        "Supprime uniquement les tables vides des anciens modules Stock et "
        "Secretariat, puis demarque leurs migrations initiales."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Execute la preparation. Sans cette option, affiche un apercu.",
        )
        parser.add_argument(
            "--backup-file",
            help="Dump MySQL complet exige avec --apply.",
        )

    @staticmethod
    def _validate_backup(path_value):
        if not path_value:
            raise CommandError("--backup-file est obligatoire avec --apply.")

        path = Path(path_value).expanduser().resolve()
        if not path.is_file() or path.stat().st_size == 0:
            raise CommandError(f"Sauvegarde absente ou vide: {path}")

        with path.open("rb") as backup:
            backup.seek(max(0, path.stat().st_size - 4096))
            tail = backup.read()
        if b"-- Dump completed on " not in tail:
            raise CommandError(f"Dump MySQL incomplet: {path}")
        return path

    def handle(self, *args, **options):
        if connection.vendor != "mysql":
            raise CommandError("Cette commande de maintenance est reservee a MySQL.")

        if options["apply"]:
            backup = self._validate_backup(options["backup_file"])
            self.stdout.write(f"Sauvegarde valide: {backup}")

        recorder = MigrationRecorder(connection)
        applied = recorder.applied_migrations()
        later_migrations = sorted(
            (app, name)
            for app, name in applied
            if app in MODULES and name != "0001_initial"
        )
        if later_migrations:
            details = ", ".join(f"{app}.{name}" for app, name in later_migrations)
            raise CommandError(
                "Des migrations ulterieures sont deja appliquees; refus: " + details
            )

        quote = connection.ops.quote_name
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                  AND table_name REGEXP '^(stock|secretariat)_'
                ORDER BY table_name
                """
            )
            tables = [row[0] for row in cursor.fetchall()]

            nonempty = []
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {quote(table)}")
                count = cursor.fetchone()[0]
                self.stdout.write(f"{table}: {count} ligne(s)")
                if count:
                    nonempty.append((table, count))

            if nonempty:
                details = ", ".join(
                    f"{table} ({count})" for table, count in nonempty
                )
                raise CommandError(
                    "Refus de supprimer des tables contenant des donnees: " + details
                )

            if tables:
                placeholders = ", ".join(["%s"] * len(tables))
                cursor.execute(
                    f"""
                    SELECT table_name, constraint_name, referenced_table_name
                    FROM information_schema.key_column_usage
                    WHERE table_schema = DATABASE()
                      AND referenced_table_schema = DATABASE()
                      AND referenced_table_name IN ({placeholders})
                      AND table_name NOT IN ({placeholders})
                    """,
                    tables + tables,
                )
                external_references = cursor.fetchall()
                if external_references:
                    details = ", ".join(
                        f"{table}.{constraint} -> {referenced}"
                        for table, constraint, referenced in external_references
                    )
                    raise CommandError(
                        "Des tables externes referencent les modules; refus: " + details
                    )

            self.stdout.write(
                f"{len(tables)} table(s) vide(s) des anciens modules sont eligibles."
            )
            if not options["apply"]:
                self.stdout.write(
                    self.style.WARNING(
                        "Apercu uniquement. Relancez avec --apply et --backup-file."
                    )
                )
                return

            if tables:
                try:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                    cursor.execute(
                        "DROP TABLE " + ", ".join(quote(table) for table in tables)
                    )
                finally:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{len(tables)} ancienne(s) table(s) vide(s) supprimee(s)."
                    )
                )

        for app_label, migration_name in INITIAL_MIGRATIONS:
            if (app_label, migration_name) in applied:
                recorder.record_unapplied(app_label, migration_name)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Migration demarquee: {app_label}.{migration_name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Preparation terminee. Executez maintenant: python manage.py migrate"
            )
        )
