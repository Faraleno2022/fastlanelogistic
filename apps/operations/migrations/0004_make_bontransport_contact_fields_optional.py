from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("operations", "0003_blankboncounter"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bontransport",
            name="lieu_chargement",
            field=models.CharField(
                "Lieu de chargement / Loading zone",
                blank=True,
                max_length=120,
            ),
        ),
        migrations.AlterField(
            model_name="bontransport",
            name="nom",
            field=models.CharField("Last Name / Nom", blank=True, max_length=80),
        ),
        migrations.AlterField(
            model_name="bontransport",
            name="plaque",
            field=models.CharField("Plate / Plaque", blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="bontransport",
            name="prenom",
            field=models.CharField("First Name / Prénom", blank=True, max_length=80),
        ),
    ]
