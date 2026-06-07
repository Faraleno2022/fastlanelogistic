"""
1. Corriger TAUX_TA de 2% a 1.5% (conformement au droit guineen)
2. S'assurer que les primes forfaitaires (transport, logement, cherte de vie) 
   ont soumis_irg=False (exonerees de RTS en tant qu'indemnites forfaitaires)
"""
from decimal import Decimal
from django.db import migrations


def corriger_constantes_et_flags(apps, schema_editor):
    Constante = apps.get_model('paie', 'Constante')
    RubriquePaie = apps.get_model('paie', 'RubriquePaie')
    
    # 1. Corriger TAUX_TA de 2% a 1.5%
    Constante.objects.filter(code='TAUX_TA').update(valeur=Decimal('1.5000'))
    
    # 2. Les primes forfaitaires ne sont PAS soumises a l'IRG/RTS
    # (exonerees en tant qu'indemnites forfaitaires, plafond 25% gere par le service)
    codes_exoneres_rts = [
        'PT', 'PRIME_TRANSPORT', 'ALLOC_TRANSPORT', 'TRANSPORT',
        'PL', 'ALLOC_LOGEMENT', 'IND_LOGEMENT', 'LOGEMENT',
        'PCV', 'CHERTE_VIE', 'PRIME_CHERTE_VIE', 'IND_CHERTE_VIE',
    ]
    RubriquePaie.objects.filter(
        code_rubrique__in=codes_exoneres_rts,
        type_rubrique='gain',
    ).update(soumis_irg=False)
    
    # Aussi par libelle
    from django.db.models import Q
    RubriquePaie.objects.filter(
        Q(libelle_rubrique__icontains='transport') |
        Q(libelle_rubrique__icontains='logement') |
        Q(libelle_rubrique__icontains='chert'),
        type_rubrique='gain',
    ).update(soumis_irg=False)


def reverse(apps, schema_editor):
    Constante = apps.get_model('paie', 'Constante')
    Constante.objects.filter(code='TAUX_TA').update(valeur=Decimal('2.0000'))


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0108_fix_soumis_cnss_primes'),
    ]

    operations = [
        migrations.RunPython(corriger_constantes_et_flags, reverse),
    ]
