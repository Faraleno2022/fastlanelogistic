from decimal import Decimal

from django.test import SimpleTestCase

from dashboard.views import _build_paie_totaux_context


class DashboardPaieTotauxTests(SimpleTestCase):
    def test_totaux_paie_dashboard_utilisent_les_montants_bulletins(self):
        context = _build_paie_totaux_context({
            'brut': Decimal('247628100'),
            'net': Decimal('201392500'),
            'base_vf': Decimal('247628100'),
            'trs': Decimal('20413988'),
            'vf': Decimal('14857686'),
            'ta': Decimal('0'),
            'onfpp': Decimal('3714422'),
            'cnss_5': Decimal('3125000'),
            'cnss_18': Decimal('11250000'),
        })

        self.assertEqual(context['salaire_brut'], Decimal('247628100'))
        self.assertEqual(context['masse_salariale'], Decimal('277450208'))
        self.assertEqual(context['total_net_a_payer'], Decimal('201392500'))
        self.assertEqual(context['total_cnss_23'], Decimal('14375000'))
        self.assertEqual(context['total_declaration_sociale'], Decimal('14375000'))
        self.assertEqual(context['total_dmu'], Decimal('35271674'))
        self.assertEqual(context['total_etax'], Decimal('35271674'))
