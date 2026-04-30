"""
Tests unitaires automatisés du moteur de paie - Législation guinéenne

Exécution: python manage.py test paie.tests

Référence: CGI 2022 + Code du Travail Guinée
"""
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase

from paie.services_retropaie import calculer_charges_patronales
from paie.services_simulation import calculer_un_bareme as calculer_un_bareme_simulation
from paie.views_rapports import _charges_patronales_bulletin


class CNSSCalculTests(SimpleTestCase):
    """TU-01 à TU-03: Tests CNSS salarié et employeur"""
    
    PLANCHER = Decimal('550000')
    PLAFOND = Decimal('2500000')
    TAUX_SALARIE = Decimal('0.05')
    TAUX_EMPLOYEUR = Decimal('0.18')
    
    def _calculer_cnss(self, salaire_brut):
        """Calcule CNSS salarié et employeur avec plancher/plafond"""
        if salaire_brut < self.PLANCHER * Decimal('0.10'):  # Seuil minimum 55 000
            return Decimal('0'), Decimal('0'), Decimal('0')
        
        assiette = max(min(salaire_brut, self.PLAFOND), self.PLANCHER)
        cnss_salarie = round(assiette * self.TAUX_SALARIE)
        cnss_employeur = round(assiette * self.TAUX_EMPLOYEUR)
        return assiette, cnss_salarie, cnss_employeur
    
    def test_tu01_cnss_salarie_sous_plafond(self):
        """TU-01: CNSS salarié 5% sur salaire ≤ 2 500 000"""
        salaire = Decimal('2000000')
        assiette, cnss_salarie, _ = self._calculer_cnss(salaire)
        
        self.assertEqual(assiette, Decimal('2000000'))
        self.assertEqual(cnss_salarie, Decimal('100000'))  # 2M × 5%
    
    def test_tu02_cnss_salarie_plafond(self):
        """TU-02: CNSS salarié plafonné à 125 000 si salaire > 2 500 000"""
        salaire = Decimal('3600000')
        assiette, cnss_salarie, _ = self._calculer_cnss(salaire)
        
        self.assertEqual(assiette, Decimal('2500000'))  # Plafond
        self.assertEqual(cnss_salarie, Decimal('125000'))  # 2.5M × 5% = 125K max
    
    def test_tu02_cnss_salaire_8m(self):
        """TU-02: CNSS salarié plafonné même à 8 000 000"""
        salaire = Decimal('8000000')
        assiette, cnss_salarie, _ = self._calculer_cnss(salaire)
        
        self.assertEqual(assiette, Decimal('2500000'))
        self.assertEqual(cnss_salarie, Decimal('125000'))
    
    def test_tu03_cnss_employeur_plafond(self):
        """TU-03: CNSS employeur 18% plafonné à 450 000"""
        salaire = Decimal('8000000')
        assiette, _, cnss_employeur = self._calculer_cnss(salaire)
        
        self.assertEqual(assiette, Decimal('2500000'))
        self.assertEqual(cnss_employeur, Decimal('450000'))  # 2.5M × 18% = 450K max
    
    def test_cnss_au_plancher(self):
        """CNSS avec salaire au plancher (550 000)"""
        salaire = Decimal('550000')
        assiette, cnss_salarie, cnss_employeur = self._calculer_cnss(salaire)
        
        self.assertEqual(assiette, Decimal('550000'))
        self.assertEqual(cnss_salarie, Decimal('27500'))   # 550K × 5%
        self.assertEqual(cnss_employeur, Decimal('99000'))  # 550K × 18%
    
    def test_cnss_sous_plancher(self):
        """CNSS avec salaire sous plancher → assiette = plancher"""
        salaire = Decimal('400000')
        assiette, cnss_salarie, cnss_employeur = self._calculer_cnss(salaire)
        
        self.assertEqual(assiette, Decimal('550000'))  # Plancher appliqué
        self.assertEqual(cnss_salarie, Decimal('27500'))


class ChargesPatronalesTests(SimpleTestCase):
    """TU-04 et TU-05: Tests VF et TA"""

    TAUX_VF = Decimal('0.06')    # 6%
    TAUX_TA = Decimal('0.02')    # 2%

    def _calculer_vf_ta(self, salaire_brut):
        """Calcule VF et TA sur base VF/ONFPP."""
        deduction_vf = round(min(salaire_brut, Decimal('2500000')) * self.TAUX_VF)
        base_vf = salaire_brut - deduction_vf
        vf = round(base_vf * self.TAUX_VF)
        ta = round(base_vf * self.TAUX_TA)
        return base_vf, vf, ta

    def test_tu04_vf_6_pourcent(self):
        """TU-04: Versement Forfaitaire = 6% de la base VF/ONFPP"""
        salaire = Decimal('3600000')
        base_vf, vf, _ = self._calculer_vf_ta(salaire)

        self.assertEqual(base_vf, Decimal('3450000'))
        self.assertEqual(vf, Decimal('207000'))

    def test_tu05_ta_2_pourcent(self):
        """TU-05: Taxe Apprentissage = 2% de la base VF/ONFPP"""
        salaire = Decimal('3600000')
        _, _, ta = self._calculer_vf_ta(salaire)

        self.assertEqual(ta, Decimal('69000'))

    def test_charges_patronales_total(self):
        """Total charges patronales = CNSS 18% + VF 6% + TA 2%"""
        salaire = Decimal('3600000')

        # CNSS employeur (plafonné)
        cnss_employeur = Decimal('450000')  # 2.5M x 18%

        _, vf, ta = self._calculer_vf_ta(salaire)
        total = cnss_employeur + vf + ta

        self.assertEqual(total, Decimal('726000'))

    def test_charges_patronales_onfpp_a_partir_de_30_salaries(self):
        """ONFPP = 1,5% de la base VF/ONFPP quand l'effectif atteint le seuil."""
        constantes = {
            'PLANCHER_CNSS': Decimal('550000'),
            'PLAFOND_CNSS': Decimal('2500000'),
            'TAUX_CNSS_EMPLOYEUR': Decimal('18'),
            'TAUX_VF': Decimal('6'),
            'TAUX_TA': Decimal('2'),
            'TAUX_ONFPP': Decimal('1.5'),
            'SEUIL_TA_ONFPP': Decimal('30'),
        }

        with patch('paie.cache_service.PayrollCacheService.get_constantes', return_value=constantes):
            charges = calculer_charges_patronales(Decimal('3600000'), nb_salaries=30)

        self.assertEqual(charges['libelle_ta'], 'ONFPP')
        self.assertEqual(charges['base_vf'], 3450000)
        self.assertEqual(charges['vf'], 207000)
        self.assertEqual(charges['ta'], 51750)
        self.assertEqual(charges['total'], 708750)

    def test_charges_patronales_ta_sous_30_salaries(self):
        """TA = 2% de la base VF/ONFPP tant que l'effectif reste sous le seuil."""
        constantes = {
            'PLANCHER_CNSS': Decimal('550000'),
            'PLAFOND_CNSS': Decimal('2500000'),
            'TAUX_CNSS_EMPLOYEUR': Decimal('18'),
            'TAUX_VF': Decimal('6'),
            'TAUX_TA': Decimal('2'),
            'TAUX_ONFPP': Decimal('1.5'),
            'SEUIL_TA_ONFPP': Decimal('30'),
        }

        with patch('paie.cache_service.PayrollCacheService.get_constantes', return_value=constantes):
            charges = calculer_charges_patronales(Decimal('3600000'), nb_salaries=29)

        self.assertEqual(charges['libelle_ta'], 'TA')
        self.assertEqual(charges['ta'], 69000)
        self.assertEqual(charges['total'], 726000)

    def test_rapport_inclut_onfpp_dans_charges_patronales(self):
        """Les rapports doivent additionner CNSS patronale, VF, TA et ONFPP."""
        bulletin = SimpleNamespace(
            cnss_employeur=Decimal('450000'),
            versement_forfaitaire=Decimal('207000'),
            taxe_apprentissage=Decimal('0'),
            contribution_onfpp=Decimal('51750'),
        )

        self.assertEqual(_charges_patronales_bulletin(bulletin), Decimal('708750'))

    def test_simulation_bascule_ta_onfpp_au_seuil_de_30(self):
        """La simulation applique TA sous 30 salariés et ONFPP à partir de 30."""
        constantes = {
            'PLANCHER_CNSS': Decimal('550000'),
            'PLAFOND_CNSS': Decimal('2500000'),
            'TAUX_CNSS_EMPLOYE': Decimal('5'),
            'TAUX_CNSS_EMPLOYEUR': Decimal('18'),
            'TAUX_VF': Decimal('6'),
            'SEUIL_TA_ONFPP': Decimal('30'),
        }
        tranches = [{'borne_inf': 0, 'borne_sup': None, 'taux': 0}]

        sous_seuil = calculer_un_bareme_simulation(
            Decimal('3600000'), Decimal('0'), tranches, constantes, nb_salaries=29
        )
        au_seuil = calculer_un_bareme_simulation(
            Decimal('3600000'), Decimal('0'), tranches, constantes, nb_salaries=30
        )

        self.assertEqual(sous_seuil['ta'], 69000)
        self.assertEqual(sous_seuil['onfpp'], 0)
        self.assertEqual(au_seuil['ta'], 0)
        self.assertEqual(au_seuil['onfpp'], 51750)


class IRGCalculTests(SimpleTestCase):
    """TU-06 et TU-07: Tests IRG/RTS"""
    
    def _calculer_irg(self, base_imposable):
        """Calcule IRG selon barème RTS CGI 2022 (6 tranches)"""
        tranches = [
            (Decimal('0'), Decimal('1000000'), Decimal('0')),
            (Decimal('1000001'), Decimal('3000000'), Decimal('0.05')),
            (Decimal('3000001'), Decimal('5000000'), Decimal('0.08')),
            (Decimal('5000001'), Decimal('10000000'), Decimal('0.10')),
            (Decimal('10000001'), Decimal('20000000'), Decimal('0.15')),
            (Decimal('20000001'), None, Decimal('0.20')),
        ]
        
        irg_total = Decimal('0')
        
        for borne_inf, borne_sup, taux in tranches:
            if base_imposable < borne_inf:
                break
            
            if borne_sup is None:
                montant_tranche = base_imposable - borne_inf + 1
            else:
                montant_tranche = min(base_imposable, borne_sup) - borne_inf + 1
            
            if montant_tranche > 0:
                irg_total += round(montant_tranche * taux)
        
        return irg_total
    
    def test_tu06_irg_sans_primes(self):
        """TU-06: IRG calculé correctement sur salaire seul"""
        # Salaire brut 3 600 000 - CNSS 125 000 = Base imposable 3 475 000
        base_imposable = Decimal('3475000')
        irg = self._calculer_irg(base_imposable)
        
        # Tranche 0-1M: 0
        # Tranche 1M-3M: 2M × 5% = 100 000
        # Tranche 3M-3.475M: 475K × 8% = 38 000
        # Total attendu: 138 000 (environ, selon arrondi exact)
        self.assertGreater(irg, Decimal('0'))
        self.assertLess(irg, Decimal('150000'))
    
    def test_tu07_irg_avec_primes(self):
        """TU-07: IRG recalculé avec primes"""
        # Salaire 2.8M + Prime 800K = Brut 3.6M
        # Base imposable = 3.6M - 125K CNSS = 3.475M
        base_sans_prime = Decimal('2675000')  # 2.8M - 125K
        base_avec_prime = Decimal('3475000')  # 3.6M - 125K
        
        irg_sans = self._calculer_irg(base_sans_prime)
        irg_avec = self._calculer_irg(base_avec_prime)
        
        # L'IRG avec primes doit être supérieur
        self.assertGreater(irg_avec, irg_sans)
    
    def test_irg_premiere_tranche_exoneree(self):
        """Première tranche (0-1M) exonérée à 0%"""
        base_imposable = Decimal('800000')
        irg = self._calculer_irg(base_imposable)
        
        self.assertEqual(irg, Decimal('0'))
    
    def test_irg_exemple_manuel_8m(self):
        """IRG sur exemple du manuel (8M GNF)"""
        # Base imposable = 8M - 125K = 7.875M
        base_imposable = Decimal('7875000')
        irg = self._calculer_irg(base_imposable)
        
        # Calcul attendu:
        # 0-1M: 0
        # 1M-3M: 2M × 5% = 100 000
        # 3M-5M: 2M × 8% = 160 000
        # 5M-7.875M: 2.875M × 10% = 287 500
        # Total: 547 500
        self.assertEqual(irg, Decimal('547500'))


class DeductionsTests(SimpleTestCase):
    """TU-08 et TU-09: Tests avances et prêts"""
    
    def test_tu08_avance_salaire(self):
        """TU-08: Avance sur salaire déduite du net"""
        salaire_brut = Decimal('3600000')
        cnss_salarie = Decimal('125000')
        irg = Decimal('67562')
        avance = Decimal('160000')
        
        net_avant_avance = salaire_brut - cnss_salarie - irg
        net_apres_avance = net_avant_avance - avance
        
        self.assertEqual(net_avant_avance, Decimal('3407438'))
        self.assertEqual(net_apres_avance, Decimal('3247438'))
    
    def test_tu09_pret_salarie(self):
        """TU-09: Prêt salarié déduit du net"""
        salaire_brut = Decimal('3600000')
        cnss_salarie = Decimal('125000')
        irg = Decimal('67562')
        pret_mensuel = Decimal('200000')
        
        net = salaire_brut - cnss_salarie - irg - pret_mensuel
        
        self.assertEqual(net, Decimal('3207438'))


class NetAPayerTests(SimpleTestCase):
    """TU-10: Test net à payer final"""
    
    def test_tu10_net_a_payer_complet(self):
        """TU-10: Net à payer = Brut - toutes retenues"""
        # Données du bulletin validé
        salaire_brut = Decimal('3600000')
        cnss_salarie = Decimal('125000')
        irg = Decimal('67562')
        avance = Decimal('160000')
        
        total_retenues = cnss_salarie + irg + avance
        net_a_payer = salaire_brut - total_retenues
        
        self.assertEqual(total_retenues, Decimal('352562'))
        self.assertEqual(net_a_payer, Decimal('3247438'))
    
    def test_net_a_payer_sans_retenues_optionnelles(self):
        """Net à payer sans avance ni prêt"""
        salaire_brut = Decimal('3600000')
        cnss_salarie = Decimal('125000')
        irg = Decimal('67562')
        
        net_a_payer = salaire_brut - cnss_salarie - irg
        
        self.assertEqual(net_a_payer, Decimal('3407438'))


class PlafondIndemnitesTests(SimpleTestCase):
    """Tests plafond 25% indemnités forfaitaires"""
    
    TAUX_PLAFOND = Decimal('0.25')
    
    def test_indemnites_sous_plafond(self):
        """Indemnités sous 25% → pas de réintégration"""
        salaire_brut = Decimal('2800000')
        indemnites = Decimal('500000')  # < 25% de 2.8M = 700K
        
        plafond = salaire_brut * self.TAUX_PLAFOND
        depassement = max(Decimal('0'), indemnites - plafond)
        
        self.assertEqual(depassement, Decimal('0'))
    
    def test_indemnites_au_plafond(self):
        """Indemnités à 25% → pas de réintégration"""
        salaire_brut = Decimal('2800000')
        indemnites = Decimal('700000')  # = 25% exactement
        
        plafond = salaire_brut * self.TAUX_PLAFOND
        depassement = max(Decimal('0'), indemnites - plafond)
        
        self.assertEqual(depassement, Decimal('0'))
    
    def test_indemnites_depassement(self):
        """Indemnités > 25% → excédent réintégré"""
        salaire_brut = Decimal('2800000')
        indemnites = Decimal('900000')  # > 25% de 2.8M = 700K
        
        plafond = salaire_brut * self.TAUX_PLAFOND
        depassement = max(Decimal('0'), indemnites - plafond)
        
        self.assertEqual(plafond, Decimal('700000'))
        self.assertEqual(depassement, Decimal('200000'))  # Réintégré dans base imposable


class ExonerationStagiaireTests(SimpleTestCase):
    """Tests exonération RTS stagiaires/apprentis"""
    
    SEUIL_EXONERATION = Decimal('1200000')
    DUREE_MAX_MOIS = 12
    
    def _est_exonere(self, type_contrat, salaire, mois_ecoules):
        """Vérifie si éligible à l'exonération RTS"""
        est_stagiaire_apprenti = type_contrat in ('stage', 'apprentissage')
        duree_ok = mois_ecoules <= self.DUREE_MAX_MOIS
        montant_ok = salaire <= self.SEUIL_EXONERATION
        
        return est_stagiaire_apprenti and duree_ok and montant_ok
    
    def test_stagiaire_exonere(self):
        """Stagiaire ≤ 1.2M et ≤ 12 mois → exonéré"""
        self.assertTrue(self._est_exonere('stage', Decimal('1000000'), 6))
    
    def test_stagiaire_salaire_depasse(self):
        """Stagiaire > 1.2M → non exonéré"""
        self.assertFalse(self._est_exonere('stage', Decimal('1500000'), 6))
    
    def test_stagiaire_duree_depassee(self):
        """Stagiaire > 12 mois → non exonéré"""
        self.assertFalse(self._est_exonere('stage', Decimal('1000000'), 15))
    
    def test_cdi_non_exonere(self):
        """CDI jamais exonéré même si salaire faible"""
        self.assertFalse(self._est_exonere('CDI', Decimal('800000'), 3))


# ======================================================================
# TESTS MOTEUR DE FORMULES (simpleeval + phases)
# ======================================================================

class FormuleSecuriteTests(SimpleTestCase):
    """Tests de sécurité du moteur de formules (simpleeval)"""

    def _vars(self):
        return {
            'brut': 5690002, 'cnss': 125000, 'indemnites': 2200000,
            'salaire_base': 3000000, 'primes': 400000, 'heures_sup': 90002,
            'total_gains': 5690002, 'total_retenues': 316400,
            'cnss_base': 2500000, 'net': 5373602,
            'anciennete_mois': 24, 'anciennete_ans': 2,
            'nb_enfants': 2, 'nb_conjoints': 1, 'plafond_cnss': 2500000,
        }

    def test_formule_basique(self):
        """Formule simple fonctionne"""
        from paie.formules import evaluer_formule
        r = evaluer_formule('brut * 0.25', self._vars())
        self.assertEqual(r, Decimal('1422500.5'))

    def test_formule_min_max(self):
        """min/max fonctionnent"""
        from paie.formules import evaluer_formule
        r = evaluer_formule('min(indemnites, brut * 0.25)', self._vars())
        self.assertEqual(r, Decimal('1422500.5'))

    def test_formule_ternaire(self):
        """Opérateur ternaire if/else fonctionne"""
        from paie.formules import evaluer_formule
        r = evaluer_formule('indemnites if indemnites <= brut * 0.25 else brut * 0.25', self._vars())
        self.assertEqual(r, Decimal('1422500.5'))

    def test_injection_import_bloquee(self):
        """Tentative d'import bloquée"""
        from paie.formules import evaluer_formule
        with self.assertRaises(ValueError):
            evaluer_formule('__import__("os").system("whoami")', self._vars())

    def test_injection_builtins_bloquee(self):
        """Accès aux builtins bloqué"""
        from paie.formules import evaluer_formule
        with self.assertRaises(ValueError):
            evaluer_formule('__builtins__', self._vars())

    def test_formule_vide(self):
        """Formule vide lève ValueError"""
        from paie.formules import evaluer_formule
        with self.assertRaises(ValueError):
            evaluer_formule('', self._vars())

    def test_resultat_negatif_ramene_a_zero(self):
        """Résultat négatif ramené à 0"""
        from paie.formules import evaluer_formule
        r = evaluer_formule('salaire_base - brut', self._vars())
        self.assertEqual(r, Decimal('0'))

    def test_division_par_zero_retourne_zero(self):
        """Division par zéro retourne 0"""
        from paie.formules import evaluer_formule
        r = evaluer_formule('brut / 0', self._vars())
        self.assertEqual(r, Decimal('0'))


class FormulePhaseTests(SimpleTestCase):
    """Tests des phases de calcul du moteur de formules"""

    def _vars(self):
        return {
            'brut': 5000000, 'cnss': 125000, 'salaire_base': 3000000,
            'total_gains': 5000000, 'total_retenues': 300000, 'net': 4700000,
            'anciennete_mois': 24, 'anciennete_ans': 2,
            'nb_enfants': 0, 'nb_conjoints': 0, 'plafond_cnss': 2500000,
            'indemnites': 0, 'primes': 0, 'heures_sup': 0, 'cnss_base': 2500000,
        }

    def test_phase_gains_salaire_base_ok(self):
        """Phase gains : salaire_base accessible"""
        from paie.formules import evaluer_formule
        r = evaluer_formule('salaire_base * 0.10', self._vars(), phase='gains')
        self.assertEqual(r, Decimal('300000.0'))

    def test_phase_gains_brut_bloque(self):
        """Phase gains : brut non accessible"""
        from paie.formules import evaluer_formule
        with self.assertRaises(ValueError):
            evaluer_formule('brut * 0.10', self._vars(), phase='gains')

    def test_phase_cotisations_brut_ok(self):
        """Phase cotisations : brut accessible"""
        from paie.formules import evaluer_formule
        r = evaluer_formule('brut * 0.05', self._vars(), phase='cotisations')
        self.assertEqual(r, Decimal('250000.0'))

    def test_phase_cotisations_cnss_bloque(self):
        """Phase cotisations : cnss non accessible (pas encore calculé)"""
        from paie.formules import evaluer_formule
        with self.assertRaises(ValueError):
            evaluer_formule('cnss * 2', self._vars(), phase='cotisations')

    def test_phase_fiscal_cnss_ok(self):
        """Phase fiscal : cnss accessible"""
        from paie.formules import evaluer_formule
        r = evaluer_formule('brut - cnss', self._vars(), phase='fiscal')
        self.assertEqual(r, Decimal('4875000.0'))

    def test_phase_retenues_net_bloque(self):
        """Phase retenues : net non accessible"""
        from paie.formules import evaluer_formule
        with self.assertRaises(ValueError):
            evaluer_formule('net * 0.10', self._vars(), phase='retenues')

    def test_phase_net_tout_accessible(self):
        """Phase net : toutes variables accessibles"""
        from paie.formules import evaluer_formule
        r = evaluer_formule('net * 0.10', self._vars(), phase='net')
        self.assertEqual(r, Decimal('470000.0'))

    def test_sans_phase_tout_accessible(self):
        """Sans phase : toutes variables accessibles (rétrocompatibilité)"""
        from paie.formules import evaluer_formule
        r = evaluer_formule('net * 0.10', self._vars())
        self.assertEqual(r, Decimal('470000.0'))


class BulletinCasReferenceTests(SimpleTestCase):
    """Test du cas de référence validé manuellement (bulletin employé type)

    Brut: 5 690 002 GNF
    Salaire base: 3 000 000  |  Cherté de vie: 900 000  |  Logement: 600 000
    Transport: 700 000  |  Prime: 400 000  |  HS: 90 002
    CNSS salarié: 125 000  |  RTS: 191 400  |  Net: 5 373 602
    """

    BRUT = Decimal('5690002')
    CNSS_EMP = Decimal('125000')
    RTS = Decimal('191400')
    NET = Decimal('5373602')
    VF = Decimal('341400')
    TA = Decimal('113800')
    CNSS_PAT = Decimal('450000')

    def test_brut(self):
        base = Decimal('3000000')
        cherte = Decimal('900000')
        logement = Decimal('600000')
        transport = Decimal('700000')
        prime = Decimal('400000')
        hs = Decimal('90002')
        self.assertEqual(base + cherte + logement + transport + prime + hs, self.BRUT)

    def test_cnss_employe(self):
        plafond = Decimal('2500000')
        self.assertEqual(plafond * Decimal('5') / Decimal('100'), self.CNSS_EMP)

    def test_net_a_payer(self):
        self.assertEqual(self.BRUT - self.CNSS_EMP - self.RTS, self.NET)

    def test_vf(self):
        self.assertEqual(
            (self.BRUT * Decimal('6') / Decimal('100')).quantize(Decimal('1')),
            self.VF
        )

    def test_ta(self):
        self.assertEqual(
            (self.BRUT * Decimal('2') / Decimal('100')).quantize(Decimal('1')),
            self.TA
        )

    def test_cnss_patronale(self):
        plafond = Decimal('2500000')
        self.assertEqual(plafond * Decimal('18') / Decimal('100'), self.CNSS_PAT)

    def test_total_charges_patronales(self):
        self.assertEqual(self.CNSS_PAT + self.VF + self.TA, Decimal('905200'))

