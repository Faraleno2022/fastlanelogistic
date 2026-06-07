"""
Corriger soumis_cnss=True pour les primes (transport, logement, cherté de vie)
En droit guinéen, toutes les composantes de rémunération sont soumises à CNSS
(plafonnée à 2 500 000 GNF).
"""
from django.db import migrations


def corriger_soumis_cnss(apps, schema_editor):
    RubriquePaie = apps.get_model('paie', 'RubriquePaie')
    
    # Codes potentiels des primes à corriger
    codes_primes = [
        'PT', 'PRIME_TRANSPORT', 'ALLOC_TRANSPORT', 'TRANSPORT',
        'PL', 'ALLOC_LOGEMENT', 'IND_LOGEMENT', 'LOGEMENT',
        'PCV', 'CHERTE_VIE', 'PRIME_CHERTE_VIE', 'IND_CHERTE_VIE',
    ]
    
    updated = RubriquePaie.objects.filter(
        code_rubrique__in=codes_primes,
        type_rubrique='gain',
    ).update(soumis_cnss=True)
    
    # Aussi mettre à jour par libellé au cas où les codes diffèrent
    from django.db.models import Q
    RubriquePaie.objects.filter(
        Q(libelle_rubrique__icontains='transport') |
        Q(libelle_rubrique__icontains='logement') |
        Q(libelle_rubrique__icontains='chert'),
        type_rubrique='gain',
    ).update(soumis_cnss=True)


def reverse(apps, schema_editor):
    pass  # Pas de rollback automatique


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0107_add_rubriques_logement_cherte_vie'),
    ]

    operations = [
        migrations.RunPython(corriger_soumis_cnss, reverse),
    ]
