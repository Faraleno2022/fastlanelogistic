from django.db import migrations


def copy_legacy_quantity(apps, schema_editor):
    BonTransport = apps.get_model("operations", "BonTransport")
    for bon in BonTransport.objects.all().iterator():
        detail_total = (
            (bon.quantite_1 or 0)
            + (bon.quantite_2 or 0)
            + (bon.quantite_3 or 0)
            + (bon.quantite_4 or 0)
        )
        if bon.quantite and not detail_total:
            bon.quantite_1 = bon.quantite
            bon.save(update_fields=["quantite_1"])


def clear_backfilled_quantity(apps, schema_editor):
    BonTransport = apps.get_model("operations", "BonTransport")
    for bon in BonTransport.objects.all().iterator():
        detail_total = (
            (bon.quantite_2 or 0)
            + (bon.quantite_3 or 0)
            + (bon.quantite_4 or 0)
        )
        if bon.quantite and bon.quantite_1 == bon.quantite and not detail_total:
            bon.quantite_1 = 0
            bon.save(update_fields=["quantite_1"])


class Migration(migrations.Migration):

    dependencies = [
        ("operations", "0006_restructure_bontransport"),
    ]

    operations = [
        migrations.RunPython(copy_legacy_quantity, clear_backfilled_quantity),
    ]
