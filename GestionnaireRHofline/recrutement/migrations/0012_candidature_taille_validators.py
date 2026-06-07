from django.db import migrations, models

import core.validators
import recrutement.models


class Migration(migrations.Migration):

    dependencies = [
        ('recrutement', '0011_offreemploi_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidature',
            name='cv_fichier',
            field=models.FileField(
                blank=True,
                help_text='CV au format PDF ou Word, max 3 Mo',
                null=True,
                upload_to=recrutement.models.chemin_cv,
                validators=[core.validators.valider_cv, core.validators.valider_taille_3mo],
            ),
        ),
        migrations.AlterField(
            model_name='candidature',
            name='lettre_motivation',
            field=models.FileField(
                blank=True,
                help_text='Lettre de motivation (PDF ou Word), max 2 Mo',
                null=True,
                upload_to=recrutement.models.chemin_lettre,
                validators=[core.validators.valider_cv, core.validators.valider_taille_2mo],
            ),
        ),
        migrations.AlterField(
            model_name='candidature',
            name='autres_documents',
            field=models.FileField(
                blank=True,
                help_text='Autres documents (PDF, Word, JPEG, PNG), max 5 Mo',
                null=True,
                upload_to=recrutement.models.chemin_autre_doc,
                validators=[core.validators.valider_image_document, core.validators.valider_taille_5mo],
            ),
        ),
    ]
