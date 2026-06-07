"""
Migration anti-IDOR : ajout d'un champ UUID aux offres d'emploi.
Les URLs utiliseront ce UUID au lieu de l'ID séquentiel.
"""
import uuid
from django.db import migrations, models


def generer_uuids(apps, schema_editor):
    """Attribue un UUID unique à chaque offre existante."""
    OffreEmploi = apps.get_model('recrutement', 'OffreEmploi')
    for offre in OffreEmploi.objects.all():
        offre.uuid = uuid.uuid4()
        offre.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('recrutement', '0010_candidature_idx_cand_offre_statut_and_more'),
    ]

    operations = [
        # 1. Ajouter le champ UUID (nullable temporairement)
        migrations.AddField(
            model_name='offreemploi',
            name='uuid',
            field=models.UUIDField(null=True),
        ),
        # 2. Remplir les UUIDs pour les enregistrements existants
        migrations.RunPython(generer_uuids, reverse_code=migrations.RunPython.noop),
        # 3. Rendre non-nullable, unique et indexé
        migrations.AlterField(
            model_name='offreemploi',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True),
        ),
    ]
