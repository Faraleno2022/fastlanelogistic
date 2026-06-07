# Migration : isolation Service et Poste par entreprise
# Chaque entreprise peut créer ses propres services/postes avec les mêmes codes

import django.db.models.deletion
from django.db import migrations, models


def peupler_entreprise(apps, schema_editor):
    """Remplir le champ entreprise depuis la chaîne etablissement→societe→entreprise"""
    Service = apps.get_model('core', 'Service')
    Poste = apps.get_model('core', 'Poste')

    # Services : entreprise via etablissement.societe.entreprise
    for service in Service.objects.filter(entreprise__isnull=True):
        if service.etablissement_id:
            etab = service.etablissement
            if etab and hasattr(etab, 'societe') and etab.societe and etab.societe.entreprise_id:
                service.entreprise_id = etab.societe.entreprise_id
                service.save(update_fields=['entreprise'])

    # Postes : entreprise via service.etablissement.societe.entreprise
    for poste in Poste.objects.filter(entreprise__isnull=True):
        if poste.service_id and poste.service and poste.service.entreprise_id:
            poste.entreprise_id = poste.service.entreprise_id
            poste.save(update_fields=['entreprise'])


def depeupler_entreprise(apps, schema_editor):
    """Reverse : remettre entreprise à NULL"""
    Service = apps.get_model('core', 'Service')
    Poste = apps.get_model('core', 'Poste')
    Service.objects.all().update(entreprise=None)
    Poste.objects.all().update(entreprise=None)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_entreprise_banque_cle_rib_entreprise_banque_code_and_more'),
        ('employes', '0017_ajout_vehicule_assigne'),
    ]

    operations = [
        # 1. Ajouter le champ entreprise (nullable) aux deux modèles
        migrations.AddField(
            model_name='service',
            name='entreprise',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='services',
                to='core.entreprise',
            ),
        ),
        migrations.AddField(
            model_name='poste',
            name='entreprise',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='postes',
                to='core.entreprise',
            ),
        ),

        # 2. Peupler entreprise depuis la chaîne existante
        migrations.RunPython(peupler_entreprise, depeupler_entreprise),

        # 3. Retirer l'ancien unique global sur code_service / code_poste
        migrations.AlterField(
            model_name='service',
            name='code_service',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='poste',
            name='code_poste',
            field=models.CharField(max_length=20),
        ),

        # 4. Ajouter le unique par entreprise
        migrations.AddConstraint(
            model_name='service',
            constraint=models.UniqueConstraint(
                fields=('entreprise', 'code_service'),
                name='unique_service_par_entreprise',
            ),
        ),
        migrations.AddConstraint(
            model_name='poste',
            constraint=models.UniqueConstraint(
                fields=('entreprise', 'code_poste'),
                name='unique_poste_par_entreprise',
            ),
        ),
    ]
