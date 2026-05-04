from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0136_align_onfpp_brut_help_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulletinpaie',
            name='contribution_onfpp',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='ONFPP 1,5% sur base VF/ONFPP',
                max_digits=15,
            ),
        ),
    ]
