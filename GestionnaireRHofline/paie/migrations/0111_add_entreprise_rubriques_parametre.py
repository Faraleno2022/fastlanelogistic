"""
Migration: Isolation multi-tenant pour RubriquePaie et ParametrePaie.
Chaque entreprise gère désormais ses propres rubriques et paramètres de paie.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('paie', '0110_bulletinpaie_abattement_forfaitaire_and_more'),
    ]

    operations = [
        # Ajouter le champ entreprise à RubriquePaie
        migrations.AddField(
            model_name='rubriquepaie',
            name='entreprise',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rubriques_paie',
                to='core.entreprise',
            ),
        ),
        # Supprimer l'ancienne contrainte unique sur code_rubrique
        migrations.AlterField(
            model_name='rubriquepaie',
            name='code_rubrique',
            field=models.CharField(max_length=20),
        ),
        # Ajouter la contrainte unique_together (entreprise, code_rubrique)
        migrations.AlterUniqueTogether(
            name='rubriquepaie',
            unique_together={('entreprise', 'code_rubrique')},
        ),
        # Ajouter le champ entreprise à ParametrePaie
        migrations.AddField(
            model_name='parametrepaie',
            name='entreprise',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='parametres_paie',
                to='core.entreprise',
            ),
        ),
    ]
