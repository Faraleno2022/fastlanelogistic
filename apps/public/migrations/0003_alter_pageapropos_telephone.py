# Generated manually because Python is not available in the current shell.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0002_contactmessage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pageapropos",
            name="telephone",
            field=models.CharField(
                blank=True,
                max_length=60,
                verbose_name="Téléphone public",
            ),
        ),
    ]
