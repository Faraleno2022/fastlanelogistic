"""
Tests de vérification des calculs de paie selon la législation guinéenne.

Ce script vérifie l'exactitude des calculs :
- CNSS avec plancher (550 000 GNF) et plafond (2 500 000 GNF)
- RTS avec le barème CGI 2022 (6 tranches, max 20%)
- Charges patronales (CNSS 18% + VF 6% + TA 2%)

Usage:
    python manage.py test_calculs_paie
"""
from decimal import Decimal, ROUND_HALF_UP
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Teste l\'exactitude des calculs de paie selon la législation guinéenne'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('=' * 70))
        self.stdout.write(self.style.NOTICE('TESTS DE VÉRIFICATION DES CALCULS DE PAIE - GUINÉE'))
        self.stdout.write(self.style.NOTICE('=' * 70))
        
        total_tests = 0
        tests_reussis = 0
        
        # Test 1: CNSS avec plancher et plafond
        r1, t1 = self.test_cnss()
        tests_reussis += r1
        total_tests += t1
        
        # Test 2: Barème RTS 2022+
        r2, t2 = self.test_rts()
        tests_reussis += r2
        total_tests += t2
        
        # Test 3: Charges patronales
        r3, t3 = self.test_charges_patronales()
        tests_reussis += r3
        total_tests += t3
        
        # Test 4: Exemple complet du manuel (8M GNF)
        r4, t4 = self.test_exemple_manuel()
        tests_reussis += r4
        total_tests += t4
        
        # Test 5: Exonération RTS stagiaires/apprentis
        r5, t5 = self.test_exoneration_stagiaire()
        tests_reussis += r5
        total_tests += t5
        
        # Test 6: Plafond 25% indemnités forfaitaires
        r6, t6 = self.test_plafond_indemnites()
        tests_reussis += r6
        total_tests += t6
        
        # Résumé
        self.stdout.write('')
        self.stdout.write('=' * 70)
        if tests_reussis == total_tests:
            self.stdout.write(self.style.SUCCESS(
                f'✅ TOUS LES TESTS RÉUSSIS: {tests_reussis}/{total_tests}'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f'❌ TESTS ÉCHOUÉS: {total_tests - tests_reussis}/{total_tests}'
            ))
        self.stdout.write('=' * 70)

    def _arrondir(self, montant):
        """Arrondir au franc près"""
        return montant.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    def _calculer_cnss(self, salaire_brut):
        """Calcule la CNSS avec plancher et plafond"""
        PLANCHER = Decimal('550000')
        PLAFOND = Decimal('2500000')
        TAUX_EMPLOYE = Decimal('5.00')
        TAUX_EMPLOYEUR = Decimal('18.00')
        SEUIL_MINIMUM = PLANCHER * Decimal('0.10')  # 55 000 GNF
        
        # Si salaire très faible, pas de CNSS
        if salaire_brut < SEUIL_MINIMUM:
            return Decimal('0'), Decimal('0'), Decimal('0')
        
        # Appliquer plancher et plafond
        assiette = max(min(salaire_brut, PLAFOND), PLANCHER)
        
        cnss_employe = self._arrondir(assiette * TAUX_EMPLOYE / Decimal('100'))
        cnss_employeur = self._arrondir(assiette * TAUX_EMPLOYEUR / Decimal('100'))
        
        return assiette, cnss_employe, cnss_employeur

    def _calculer_rts(self, base_imposable):
        """Calcule la RTS selon le barème CGI 2022 (6 tranches)"""
        # Barème RTS CGI 2022 officiel - 6 tranches
        tranches = [
            (Decimal('0'), Decimal('1000000'), Decimal('0')),
            (Decimal('1000001'), Decimal('3000000'), Decimal('5')),
            (Decimal('3000001'), Decimal('5000000'), Decimal('8')),
            (Decimal('5000001'), Decimal('10000000'), Decimal('10')),
            (Decimal('10000001'), Decimal('20000000'), Decimal('15')),
            (Decimal('20000001'), None, Decimal('20')),
        ]
        
        rts_total = Decimal('0')
        details = []
        
        for borne_inf, borne_sup, taux in tranches:
            if base_imposable < borne_inf:
                break
            
            # Calculer le montant dans cette tranche
            if borne_sup is None:
                # Dernière tranche (illimitée)
                montant_tranche = base_imposable - borne_inf + 1
            else:
                # Montant dans la tranche = min(base, borne_sup) - borne_inf + 1
                montant_tranche = min(base_imposable, borne_sup) - borne_inf + 1
            
            if montant_tranche > 0:
                impot_tranche = self._arrondir(montant_tranche * taux / Decimal('100'))
                rts_total += impot_tranche
                details.append((borne_inf, borne_sup, taux, montant_tranche, impot_tranche))
        
        return rts_total, details

    def _calculer_charges_patronales(self, salaire_brut, assiette_cnss):
        """Calcule les charges patronales complètes"""
        TAUX_CNSS_EMPLOYEUR = Decimal('18.00')
        TAUX_VF = Decimal('6.00')
        TAUX_TA = Decimal('2.00')
        
        cnss_employeur = self._arrondir(assiette_cnss * TAUX_CNSS_EMPLOYEUR / Decimal('100'))
        deduction_vf = self._arrondir(min(salaire_brut, Decimal('2500000')) * TAUX_VF / Decimal('100'))
        base_vf = max(Decimal('0'), salaire_brut - deduction_vf)
        vf = self._arrondir(base_vf * TAUX_VF / Decimal('100'))
        ta = self._arrondir(base_vf * TAUX_TA / Decimal('100'))
        
        return cnss_employeur, vf, ta

    def test_cnss(self):
        """Test des calculs CNSS avec plancher et plafond"""
        self.stdout.write('\n📊 TEST 1: CALCUL CNSS (Plancher/Plafond)')
        self.stdout.write('-' * 50)
        
        tests = [
            # (salaire_brut, assiette_attendue, cnss_employe_attendu, cnss_employeur_attendu)
            (Decimal('300000'), Decimal('550000'), Decimal('27500'), Decimal('99000')),  # Sous le plancher
            (Decimal('550000'), Decimal('550000'), Decimal('27500'), Decimal('99000')),  # Au plancher
            (Decimal('1500000'), Decimal('1500000'), Decimal('75000'), Decimal('270000')),  # Entre plancher et plafond
            (Decimal('2500000'), Decimal('2500000'), Decimal('125000'), Decimal('450000')),  # Au plafond
            (Decimal('8000000'), Decimal('2500000'), Decimal('125000'), Decimal('450000')),  # Au-dessus du plafond
            (Decimal('50000'), Decimal('0'), Decimal('0'), Decimal('0')),  # Sous le seuil minimum (pas de CNSS)
        ]
        
        reussis = 0
        for salaire, assiette_att, cnss_emp_att, cnss_pat_att in tests:
            assiette, cnss_emp, cnss_pat = self._calculer_cnss(salaire)
            
            ok = (assiette == assiette_att and cnss_emp == cnss_emp_att and cnss_pat == cnss_pat_att)
            
            if ok:
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Brut {salaire:>12,.0f} → Assiette {assiette:>12,.0f} | '
                    f'CNSS Emp {cnss_emp:>10,.0f} | CNSS Pat {cnss_pat:>10,.0f}'
                ))
                reussis += 1
            else:
                self.stdout.write(self.style.ERROR(
                    f'  ✗ Brut {salaire:>12,.0f} → Assiette {assiette:>12,.0f} (attendu {assiette_att:,.0f}) | '
                    f'CNSS Emp {cnss_emp:>10,.0f} (attendu {cnss_emp_att:,.0f})'
                ))
        
        return reussis, len(tests)

    def test_rts(self):
        """Test du barème RTS 2022+"""
        self.stdout.write('\n📊 TEST 2: BARÈME RTS 2022+ (avec tranche 8%)')
        self.stdout.write('-' * 50)
        
        tests = [
            # (base_imposable, rts_attendu)
            (Decimal('800000'), Decimal('0')),  # Tranche 0%
            (Decimal('1000000'), Decimal('0')),  # Limite tranche 0%
            (Decimal('2000000'), Decimal('50000')),  # 1M × 0% + 1M × 5%
            (Decimal('3000000'), Decimal('100000')),  # 1M × 0% + 2M × 5%
            (Decimal('4000000'), Decimal('180000')),  # 1M × 0% + 2M × 5% + 1M × 8%
            (Decimal('5000000'), Decimal('260000')),  # 1M × 0% + 2M × 5% + 2M × 8%
            (Decimal('7875000'), Decimal('547500')),  # Exemple du manuel
            (Decimal('10000000'), Decimal('760000')),  # Jusqu'à tranche 10%
            (Decimal('15000000'), Decimal('1510000')),  # Jusqu'à tranche 15%
            (Decimal('25000000'), Decimal('3260000')),  # Jusqu'à tranche 20%
        ]
        
        reussis = 0
        for base, rts_attendu in tests:
            rts_calcule, details = self._calculer_rts(base)
            
            ok = (rts_calcule == rts_attendu)
            
            if ok:
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Base {base:>12,.0f} GNF → RTS {rts_calcule:>10,.0f} GNF'
                ))
                reussis += 1
            else:
                self.stdout.write(self.style.ERROR(
                    f'  ✗ Base {base:>12,.0f} GNF → RTS {rts_calcule:>10,.0f} GNF (attendu {rts_attendu:,.0f})'
                ))
                # Afficher le détail pour debug
                for borne_inf, borne_sup, taux, montant, impot in details:
                    self.stdout.write(f'      Tranche {taux}%: {montant:,.0f} → {impot:,.0f}')
        
        return reussis, len(tests)

    def test_charges_patronales(self):
        """Test des charges patronales"""
        self.stdout.write('\n📊 TEST 3: CHARGES PATRONALES (CNSS 18% + VF 6% + TA 2%)')
        self.stdout.write('-' * 50)
        
        tests = [
            # (salaire_brut, assiette_cnss, cnss_pat_att, vf_att, ta_att) - TA = 2% CGI 2022
            (Decimal('8000000'), Decimal('2500000'), Decimal('450000'), Decimal('471000'), Decimal('157000')),
            (Decimal('2000000'), Decimal('2000000'), Decimal('360000'), Decimal('112800'), Decimal('37600')),
            (Decimal('500000'), Decimal('550000'), Decimal('99000'), Decimal('28200'), Decimal('9400')),
        ]
        
        reussis = 0
        for brut, assiette, cnss_att, vf_att, ta_att in tests:
            cnss, vf, ta = self._calculer_charges_patronales(brut, assiette)
            total = cnss + vf + ta
            total_att = cnss_att + vf_att + ta_att
            
            ok = (cnss == cnss_att and vf == vf_att and ta == ta_att)
            
            if ok:
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Brut {brut:>12,.0f} → CNSS Pat {cnss:>10,.0f} | VF {vf:>10,.0f} | TA {ta:>8,.0f} | Total {total:>10,.0f}'
                ))
                reussis += 1
            else:
                self.stdout.write(self.style.ERROR(
                    f'  ✗ Brut {brut:>12,.0f} → CNSS Pat {cnss:>10,.0f} (att {cnss_att:,.0f}) | '
                    f'VF {vf:>10,.0f} (att {vf_att:,.0f}) | TA {ta:>8,.0f} (att {ta_att:,.0f})'
                ))
        
        return reussis, len(tests)

    def test_exemple_manuel(self):
        """Test de l'exemple complet du manuel (salaire 8M GNF)"""
        self.stdout.write('\n📊 TEST 4: EXEMPLE COMPLET DU MANUEL (8 000 000 GNF)')
        self.stdout.write('-' * 50)
        
        # Données de l'exemple
        salaire_brut = Decimal('8000000')
        
        # Valeurs attendues selon le manuel v1.1
        assiette_cnss_attendue = Decimal('2500000')
        cnss_employe_attendu = Decimal('125000')
        base_rts_attendue = Decimal('7875000')
        rts_attendu = Decimal('547500')
        total_retenues_attendu = Decimal('672500')
        net_attendu = Decimal('7327500')
        
        # Charges patronales attendues (TA = 2% CGI 2022)
        cnss_employeur_attendu = Decimal('450000')
        vf_attendu = Decimal('471000')
        ta_attendu = Decimal('157000')
        total_charges_attendu = Decimal('1078000')
        
        # Calculs
        assiette_cnss, cnss_employe, cnss_employeur = self._calculer_cnss(salaire_brut)
        base_rts = salaire_brut - cnss_employe
        rts, _ = self._calculer_rts(base_rts)
        total_retenues = cnss_employe + rts
        net = salaire_brut - total_retenues
        
        _, vf, ta = self._calculer_charges_patronales(salaire_brut, assiette_cnss)
        total_charges = cnss_employeur + vf + ta
        
        # Vérifications
        tests_ok = 0
        total_tests = 8
        
        def check(nom, calcule, attendu):
            nonlocal tests_ok
            if calcule == attendu:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {nom}: {calcule:,.0f} GNF'))
                tests_ok += 1
            else:
                self.stdout.write(self.style.ERROR(f'  ✗ {nom}: {calcule:,.0f} GNF (attendu {attendu:,.0f})'))
        
        self.stdout.write('  --- Calculs employé ---')
        check('Assiette CNSS', assiette_cnss, assiette_cnss_attendue)
        check('CNSS Employé (5%)', cnss_employe, cnss_employe_attendu)
        check('Base RTS', base_rts, base_rts_attendue)
        check('RTS', rts, rts_attendu)
        check('NET À PAYER', net, net_attendu)
        
        self.stdout.write('  --- Charges patronales ---')
        check('CNSS Employeur (18%)', cnss_employeur, cnss_employeur_attendu)
        check('Versement Forfaitaire (6%)', vf, vf_attendu)
        check('Taxe Apprentissage (2%)', ta, ta_attendu)
        
        # Résumé
        self.stdout.write('')
        self.stdout.write(f'  📋 RÉCAPITULATIF:')
        self.stdout.write(f'     Salaire Brut:        {salaire_brut:>12,.0f} GNF')
        self.stdout.write(f'     - CNSS Employé:      {cnss_employe:>12,.0f} GNF')
        self.stdout.write(f'     - RTS:               {rts:>12,.0f} GNF')
        self.stdout.write(f'     = NET À PAYER:       {net:>12,.0f} GNF')
        self.stdout.write(f'     ')
        self.stdout.write(f'     Charges patronales:  {total_charges:>12,.0f} GNF')
        self.stdout.write(f'     Coût total employeur:{salaire_brut + total_charges:>12,.0f} GNF')
        
        return tests_ok, total_tests

    def test_exoneration_stagiaire(self):
        """Test de l'exonération RTS pour stagiaires/apprentis"""
        self.stdout.write('\n📊 TEST 5: EXONÉRATION RTS STAGIAIRES/APPRENTIS')
        self.stdout.write('-' * 50)
        
        SEUIL_EXONERATION = Decimal('1200000')
        
        tests = [
            # (type_contrat, salaire_brut, mois_ecoules, exonere_attendu, description)
            ('stage', Decimal('800000'), 3, True, 'Stagiaire 800K, 3 mois'),
            ('stage', Decimal('1200000'), 6, True, 'Stagiaire 1.2M (seuil), 6 mois'),
            ('stage', Decimal('1500000'), 3, False, 'Stagiaire 1.5M > seuil'),
            ('stage', Decimal('800000'), 15, False, 'Stagiaire 800K, 15 mois > 12'),
            ('apprentissage', Decimal('900000'), 8, True, 'Apprenti 900K, 8 mois'),
            ('apprentissage', Decimal('1200000'), 12, True, 'Apprenti 1.2M, 12 mois (limite)'),
            ('apprentissage', Decimal('1200001'), 6, False, 'Apprenti 1.2M+1 > seuil'),
            ('CDI', Decimal('800000'), 3, False, 'CDI non éligible'),
            ('CDD', Decimal('900000'), 6, False, 'CDD non éligible'),
        ]
        
        reussis = 0
        for type_contrat, salaire, mois, exonere_attendu, desc in tests:
            # Simuler la vérification d'exonération
            est_stagiaire_apprenti = type_contrat in ('stage', 'apprentissage')
            duree_ok = mois <= 12
            montant_ok = salaire <= SEUIL_EXONERATION
            
            exonere = est_stagiaire_apprenti and duree_ok and montant_ok
            
            ok = (exonere == exonere_attendu)
            
            status = "EXONÉRÉ" if exonere else "IMPOSABLE"
            status_att = "EXONÉRÉ" if exonere_attendu else "IMPOSABLE"
            
            if ok:
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ {desc} → {status}'
                ))
                reussis += 1
            else:
                self.stdout.write(self.style.ERROR(
                    f'  ✗ {desc} → {status} (attendu {status_att})'
                ))
        
        # Afficher les règles
        self.stdout.write('')
        self.stdout.write('  📋 RÈGLES D\'EXONÉRATION RTS:')
        self.stdout.write(f'     - Type contrat: Stage ou Apprentissage')
        self.stdout.write(f'     - Durée max: 12 mois')
        self.stdout.write(f'     - Indemnité max: {SEUIL_EXONERATION:,.0f} GNF/mois')
        
        return reussis, len(tests)

    def test_plafond_indemnites(self):
        """Test du plafond 25% pour les indemnités forfaitaires"""
        self.stdout.write('\n📊 TEST 6: PLAFOND 25% INDEMNITÉS FORFAITAIRES')
        self.stdout.write('-' * 50)
        
        TAUX_PLAFOND = Decimal('25')
        
        tests = [
            # (salaire_brut, indemnites_forfaitaires, depassement_attendu, reintegration_attendue, description)
            (Decimal('2000000'), Decimal('400000'), Decimal('0'), Decimal('0'), 'Indemnités 400K = 20% < 25%'),
            (Decimal('2000000'), Decimal('500000'), Decimal('0'), Decimal('0'), 'Indemnités 500K = 25% (limite)'),
            (Decimal('2000000'), Decimal('600000'), Decimal('100000'), Decimal('100000'), 'Indemnités 600K = 30% > 25%'),
            (Decimal('4000000'), Decimal('800000'), Decimal('0'), Decimal('0'), 'Indemnités 800K = 20% < 25%'),
            (Decimal('4000000'), Decimal('1200000'), Decimal('200000'), Decimal('200000'), 'Indemnités 1.2M = 30% > 25%'),
            (Decimal('1000000'), Decimal('300000'), Decimal('50000'), Decimal('50000'), 'Indemnités 300K = 30% > 25%'),
        ]
        
        reussis = 0
        for brut, indemnites, depassement_att, reintegration_att, desc in tests:
            # Calculer le plafond (25% du brut)
            plafond = self._arrondir(brut * TAUX_PLAFOND / Decimal('100'))
            
            # Calculer le dépassement
            if indemnites > plafond:
                depassement = indemnites - plafond
                reintegration = depassement
            else:
                depassement = Decimal('0')
                reintegration = Decimal('0')
            
            ok = (depassement == depassement_att and reintegration == reintegration_att)
            
            if ok:
                if depassement > 0:
                    self.stdout.write(self.style.WARNING(
                        f'  ✓ {desc} → Dépassement {depassement:,.0f} GNF réintégré'
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ {desc} → OK (pas de dépassement)'
                    ))
                reussis += 1
            else:
                self.stdout.write(self.style.ERROR(
                    f'  ✗ {desc} → Dépassement {depassement:,.0f} (attendu {depassement_att:,.0f})'
                ))
        
        # Afficher les règles
        self.stdout.write('')
        self.stdout.write('  📋 RÈGLES PLAFOND INDEMNITÉS:')
        self.stdout.write(f'     - Indemnités concernées: logement, transport, panier')
        self.stdout.write(f'     - Plafond: 25% du salaire brut')
        self.stdout.write(f'     - Excédent: réintégré dans la base imposable RTS')
        
        return reussis, len(tests)
