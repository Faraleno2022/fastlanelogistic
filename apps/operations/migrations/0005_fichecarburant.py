from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("flotte", "0001_initial"),
        ("operations", "0004_make_bontransport_contact_fields_optional"),
        ("rh", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FicheCarburant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Modifié le")),
                ("date", models.DateField(verbose_name="Date")),
                ("numero", models.PositiveIntegerField(default=0, verbose_name="N°")),
                ("chauffeur_nom", models.CharField(max_length=160, verbose_name="Nom et prénom")),
                ("plaque", models.CharField(max_length=40, verbose_name="Plaque")),
                ("niveau_carburant", models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name="Niveau carburant (%)")),
                ("quantite", models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Quantité")),
                ("heure", models.TimeField(blank=True, null=True, verbose_name="Heure")),
                ("rotation", models.PositiveIntegerField(default=0, verbose_name="Rotation")),
                ("observation", models.CharField(blank=True, max_length=200, verbose_name="Observation")),
                ("camion", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="fiches_carburant", to="flotte.camion")),
                ("chauffeur", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="fiches_carburant", to="rh.employe")),
            ],
            options={
                "verbose_name": "Fiche de gestion carburant",
                "verbose_name_plural": "Fiches de gestion carburant",
                "ordering": ["-date", "numero"],
                "indexes": [models.Index(fields=["date", "plaque"], name="operations__date_5d105e_idx")],
                "unique_together": {("date", "numero")},
            },
        ),
    ]
