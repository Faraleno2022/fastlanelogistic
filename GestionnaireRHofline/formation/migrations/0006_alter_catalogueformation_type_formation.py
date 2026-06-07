# Generated migration for type_formation field length increase

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formation', '0005_add_inscription_formation_public'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogueformation',
            name='type_formation',
            field=models.CharField(max_length=500),
        ),
    ]
