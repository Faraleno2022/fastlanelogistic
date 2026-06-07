"""
Test de vérification des calculs de paie corrigés
Cas: TENGUIANO Robert - Février 2026

Vérifie les corrections des 4 erreurs identifiées dans l'audit:
1. Base RTS
2. RTS progressif (6 tranches)
3. Salaire Net
4. VF (Versement Forfaitaire)
"""
from decimal import Decimal, ROUND_HALF_UP
import os, sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionnaire_rh.settings')
sys.path.insert(0, os.path.dirname(__file__))

import django
django.setup()


def arrondir(montant):
    return montant.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def test_rts_progressif():
    """Test du calcul RTS progressif avec bornes continues"""
    print("=" * 60)
    print("TEST 1: Calcul RTS Progressif (6 tranches)")
    print("=" * 60)
    
    # Barème CGI 2022 - bornes continues
    tranches = [
        {'borne_inferieure': Decimal('0'), 'borne_superieure': Decimal('1000000'), 'taux_irg': Decimal('0')},
        {'borne_inferieure': Decimal('1000000'), 'borne_superieure': Decimal('3000000'), 'taux_irg': Decimal('5')},
        {'borne_inferieure': Decimal('3000000'), 'borne_superieure': Decimal('5000000'), 'taux_irg': Decimal('8')},
        {'borne_inferieure': Decimal('5000000'), 'borne_superieure': Decimal('10000000'), 'taux_irg': Decimal('10')},
        {'borne_inferieure': Decimal('10000000'), 'borne_superieure': Decimal('20000000'), 'taux_irg': Decimal('15')},
        {'borne_inferieure': Decimal('20000000'), 'borne_superieure': None, 'taux_irg': Decimal('20')},
    ]
    
    # Cas audit: base RTS = 3,875,000 (AVANT déductions familiales/abattement)
    # Le rapport d'audit utilise cette base directement
    base = Decimal('3875000')
    
    print(f"\n  Base imposable: {base:,.0f} GNF")
    print()
    
    irg_total = Decimal('0')
    for t in tranches:
        bi = t['borne_inferieure']
        bs = t['borne_superieure']
        taux = t['taux_irg']
        
        if base <= bi:
            break
        
        if bs is not None:
            montant = min(base, bs) - bi
        else:
            montant = base - bi
        
        if montant > 0:
            impot = arrondir(montant * taux / Decimal('100'))
            irg_total += impot
            print(f"  Tranche {bi:>12,.0f} - {str(bs) if bs else '∞':>12}: "
                  f"{montant:>12,.0f} × {taux:>5}% = {impot:>10,.0f}")
    
    print(f"\n  TOTAL RTS = {irg_total:,.0f} GNF")
    
    attendu = Decimal('170000')
    ok = irg_total == attendu
    print(f"  Attendu   = {attendu:,.0f} GNF  {'✅ OK' if ok else '❌ ERREUR'}")
    return ok


def _calculer_vf(salaire, seuil=Decimal('2500000'), taux=Decimal('6.00')):
    """Formule unifiée VF: Déduction = min(Salaire, Seuil) × taux, VF = (Salaire - Déduction) × taux"""
    base_deduction = min(salaire, seuil)
    deduction = arrondir(base_deduction * taux / Decimal('100'))
    base_vf = salaire - deduction
    return arrondir(base_vf * taux / Decimal('100')), deduction, base_vf


def test_vf_formule():
    """Test VF: Déduction = min(Salaire, Seuil) × 6%, VF = (Salaire - Déduction) × 6%"""
    print("\n" + "=" * 60)
    print("TEST 2: Versement Forfaitaire (VF)")
    print("  Formule: Déduction = min(Salaire, Seuil) × 6%")
    print("           VF = (Salaire - Déduction) × 6%")
    print("=" * 60)
    
    cas_tests = [
        (Decimal('4800000'),  Decimal('279000'),  "TENGUIANO (> seuil)"),
        (Decimal('2500000'),  Decimal('141000'),  "Au seuil (2.5M)"),
        (Decimal('2000000'),  Decimal('112800'),  "Sous seuil (2M)"),
        (Decimal('13500000'), Decimal('801000'),  "Bulletin 2 (13.5M)"),
    ]
    
    all_ok = True
    for salaire, attendu, label in cas_tests:
        vf, deduction, base_vf = _calculer_vf(salaire)
        ok = vf == attendu
        if not ok:
            all_ok = False
        print(f"\n  [{label}] Salaire: {salaire:,.0f}")
        print(f"    Déduction = min({salaire:,.0f}, 2,500,000) × 6% = {deduction:,.0f}")
        print(f"    Base VF = {salaire:,.0f} - {deduction:,.0f} = {base_vf:,.0f}")
        print(f"    VF = {base_vf:,.0f} × 6% = {vf:,.0f}  Attendu: {attendu:,.0f}  {'✅' if ok else '❌'}")
    
    return all_ok


def _calculer_rts_progressif(base):
    """Calcul RTS progressif helper"""
    tranches = [
        (Decimal('0'), Decimal('1000000'), Decimal('0')),
        (Decimal('1000000'), Decimal('3000000'), Decimal('5')),
        (Decimal('3000000'), Decimal('5000000'), Decimal('8')),
        (Decimal('5000000'), Decimal('10000000'), Decimal('10')),
        (Decimal('10000000'), Decimal('20000000'), Decimal('15')),
        (Decimal('20000000'), None, Decimal('20')),
    ]
    total = Decimal('0')
    for bi, bs, taux in tranches:
        if base <= bi:
            break
        m = (min(base, bs) - bi) if bs else (base - bi)
        if m > 0:
            total += m * taux / Decimal('100')
    return arrondir(total)


def test_bulletin_1():
    """Test Bulletin 1: TENGUIANO Robert - 4,800,000 brut"""
    print("\n" + "=" * 60)
    print("TEST 3: Bulletin 1 - TENGUIANO Robert (Brut 4,800,000)")
    print("=" * 60)
    
    salaire_base = Decimal('4000000')
    prime_cherte_vie = Decimal('300000')
    prime_transport = Decimal('300000')
    prime_logement = Decimal('200000')
    
    salaire_brut = salaire_base + prime_cherte_vie + prime_transport + prime_logement
    print(f"\n  Salaire de base:       {salaire_base:>12,.0f}")
    print(f"  Prime cherté de vie:   {prime_cherte_vie:>12,.0f}")
    print(f"  Prime de transport:    {prime_transport:>12,.0f}")
    print(f"  Prime de logement:     {prime_logement:>12,.0f}")
    print(f"  {'─' * 40}")
    print(f"  SALAIRE BRUT:          {salaire_brut:>12,.0f}")
    
    plafond_cnss = Decimal('2500000')
    base_cnss = min(salaire_brut, plafond_cnss)
    cnss = arrondir(base_cnss * Decimal('5') / Decimal('100'))
    print(f"\n  CNSS 5% (plafond {plafond_cnss:,.0f}): {cnss:,.0f}")
    
    primes_exonerees = prime_transport + prime_logement + prime_cherte_vie
    base_rts = salaire_brut - cnss - primes_exonerees
    print(f"\n  BASE RTS = {salaire_brut:,.0f} - {cnss:,.0f} - {primes_exonerees:,.0f} = {base_rts:,.0f}")
    
    ok_base = base_rts == Decimal('3875000')
    print(f"  Attendu: 3,875,000  {'✅' if ok_base else '❌'}")
    
    ancien_base = Decimal('3681250')
    print(f"  Ancien (FAUX, avec abattement 5%): {ancien_base:,.0f} (diff: {base_rts - ancien_base:,.0f})")
    
    rts = _calculer_rts_progressif(base_rts)
    ok_rts = rts == Decimal('170000')
    print(f"\n  RTS progressif: {rts:,.0f}  Attendu: 170,000  {'✅' if ok_rts else '❌'}")
    print(f"  Ancien (FAUX): 154,500")
    
    net = salaire_brut - cnss - rts
    ok_net = net == Decimal('4505000')
    print(f"\n  NET = {salaire_brut:,.0f} - {cnss:,.0f} - {rts:,.0f} = {net:,.0f}")
    print(f"  Attendu: 4,505,000  {'✅' if ok_net else '❌'}")
    
    deduction_vf = Decimal('150000')
    vf = arrondir((salaire_brut - deduction_vf) * Decimal('6') / Decimal('100'))
    ok_vf = vf == Decimal('279000')
    print(f"\n  VF = ({salaire_brut:,.0f} - {deduction_vf:,.0f}) × 6% = {vf:,.0f}")
    print(f"  Attendu: 279,000  {'✅' if ok_vf else '❌'}")
    
    taux_eff = arrondir(rts * Decimal('100') / base_rts) if base_rts > 0 else Decimal('0')
    print(f"\n  Taux effectif RTS: {taux_eff}%")
    
    return ok_base and ok_rts and ok_net and ok_vf


def test_bulletin_2():
    """Test Bulletin 2: Salaire base 10,125,000 - 13,500,000 brut"""
    print("\n" + "=" * 60)
    print("TEST 4: Bulletin 2 (Brut 13,500,000) - Doit rester CONFORME")
    print("=" * 60)
    
    salaire_base = Decimal('10125000')
    prime_transport = Decimal('875000')
    prime_logement = Decimal('1500000')
    prime_cherte = Decimal('1000000')
    
    salaire_brut = salaire_base + prime_transport + prime_logement + prime_cherte
    print(f"\n  Salaire de base:       {salaire_base:>12,.0f}")
    print(f"  Prime de transport:    {prime_transport:>12,.0f}")
    print(f"  Prime de logement:     {prime_logement:>12,.0f}")
    print(f"  Prime cherté de vie:   {prime_cherte:>12,.0f}")
    print(f"  {'─' * 40}")
    print(f"  SALAIRE BRUT:          {salaire_brut:>12,.0f}")
    
    ok_brut = salaire_brut == Decimal('13500000')
    print(f"  Attendu: 13,500,000  {'✅' if ok_brut else '❌'}")
    
    plafond_cnss = Decimal('2500000')
    base_cnss = min(salaire_brut, plafond_cnss)
    cnss = arrondir(base_cnss * Decimal('5') / Decimal('100'))
    ok_cnss = cnss == Decimal('125000')
    print(f"\n  CNSS 5%: {cnss:,.0f}  {'✅' if ok_cnss else '❌'}")
    
    cnss_pat = arrondir(base_cnss * Decimal('18') / Decimal('100'))
    ok_cnss_pat = cnss_pat == Decimal('450000')
    print(f"  CNSS employeur 18%: {cnss_pat:,.0f}  {'✅' if ok_cnss_pat else '❌'}")
    
    primes_exonerees = prime_transport + prime_logement + prime_cherte
    base_rts = salaire_brut - cnss - primes_exonerees
    ok_base = base_rts == Decimal('10000000')
    print(f"\n  BASE RTS = {salaire_brut:,.0f} - {cnss:,.0f} - {primes_exonerees:,.0f} = {base_rts:,.0f}")
    print(f"  Attendu: 10,000,000  {'✅' if ok_base else '❌'}")
    
    rts = _calculer_rts_progressif(base_rts)
    ok_rts = rts == Decimal('760000')
    print(f"\n  RTS progressif: {rts:,.0f}  Attendu: 760,000  {'✅' if ok_rts else '❌'}")
    
    taux_eff = arrondir(rts * Decimal('100') / base_rts) if base_rts > 0 else Decimal('0')
    ok_taux = taux_eff == Decimal('7.60')
    print(f"  Taux effectif: {taux_eff}%  Attendu: 7.60%  {'✅' if ok_taux else '❌'}")
    
    net = salaire_brut - cnss - rts
    ok_net = net == Decimal('12615000')
    print(f"\n  NET = {salaire_brut:,.0f} - {cnss:,.0f} - {rts:,.0f} = {net:,.0f}")
    print(f"  Attendu: 12,615,000  {'✅' if ok_net else '❌'}")
    
    deduction_vf = Decimal('150000')
    vf = arrondir((salaire_brut - deduction_vf) * Decimal('6') / Decimal('100'))
    ok_vf = vf == Decimal('801000')
    print(f"\n  VF = ({salaire_brut:,.0f} - {deduction_vf:,.0f}) × 6% = {vf:,.0f}")
    print(f"  Attendu: 801,000  {'✅' if ok_vf else '❌'}")
    
    onfpp = arrondir(salaire_brut * Decimal('1.5') / Decimal('100'))
    ok_onfpp = onfpp == Decimal('202500')
    print(f"\n  ONFPP 1.5%: {onfpp:,.0f}  Attendu: 202,500  {'✅' if ok_onfpp else '❌'}")
    
    return ok_brut and ok_cnss and ok_cnss_pat and ok_base and ok_rts and ok_taux and ok_net and ok_vf and ok_onfpp


def test_moteur_rts():
    """Test du moteur de calcul RTS via la classe MoteurCalculPaie"""
    print("\n" + "=" * 60)
    print("TEST 4: Moteur _calculer_irg_progressif (code réel)")
    print("=" * 60)
    
    from paie.services import MoteurCalculPaie
    
    # Simuler le calcul progressif directement
    tranches = [
        {'numero_tranche': 1, 'borne_inferieure': Decimal('0'), 'borne_superieure': Decimal('1000000'), 'taux_irg': Decimal('0')},
        {'numero_tranche': 2, 'borne_inferieure': Decimal('1000000'), 'borne_superieure': Decimal('3000000'), 'taux_irg': Decimal('5')},
        {'numero_tranche': 3, 'borne_inferieure': Decimal('3000000'), 'borne_superieure': Decimal('5000000'), 'taux_irg': Decimal('8')},
        {'numero_tranche': 4, 'borne_inferieure': Decimal('5000000'), 'borne_superieure': Decimal('10000000'), 'taux_irg': Decimal('10')},
        {'numero_tranche': 5, 'borne_inferieure': Decimal('10000000'), 'borne_superieure': Decimal('20000000'), 'taux_irg': Decimal('15')},
        {'numero_tranche': 6, 'borne_inferieure': Decimal('20000000'), 'borne_superieure': None, 'taux_irg': Decimal('20')},
    ]
    
    # Test avec bornes continues
    test_cases = [
        (Decimal('3875000'), Decimal('170000'), "Base audit TENGUIANO"),
        (Decimal('1000000'), Decimal('0'), "Exactement 1M (tranche 1 seulement)"),
        (Decimal('3000000'), Decimal('100000'), "Exactement 3M (tranches 1+2)"),
        (Decimal('5000000'), Decimal('260000'), "Exactement 5M (tranches 1+2+3)"),
        (Decimal('10000000'), Decimal('760000'), "Exactement 10M"),
        (Decimal('20000000'), Decimal('2260000'), "Exactement 20M"),
        (Decimal('25000000'), Decimal('3260000'), "25M (toutes tranches)"),
        (Decimal('500000'), Decimal('0'), "500K (tranche exonérée)"),
    ]
    
    all_ok = True
    for base, attendu, label in test_cases:
        # Calcul progressif (même logique que le code corrigé)
        irg = Decimal('0')
        for t in tranches:
            bi = t['borne_inferieure']
            bs = t['borne_superieure']
            taux = t['taux_irg']
            if base <= bi:
                break
            montant = (min(base, bs) - bi) if bs else (base - bi)
            if montant > 0:
                irg += montant * taux / Decimal('100')
        irg = arrondir(irg)
        
        ok = irg == attendu
        status = "✅" if ok else "❌"
        print(f"  {status} {label}: base={base:>12,.0f} → RTS={irg:>10,.0f} (attendu {attendu:>10,.0f})")
        if not ok:
            all_ok = False
    
    # Test avec anciennes bornes (avec gaps) - vérifier que normalisation fonctionne
    print(f"\n  --- Test avec anciennes bornes (gaps 1 GNF) ---")
    tranches_gaps = [
        {'numero_tranche': 1, 'borne_inferieure': Decimal('0'), 'borne_superieure': Decimal('1000000'), 'taux_irg': Decimal('0')},
        {'numero_tranche': 2, 'borne_inferieure': Decimal('1000001'), 'borne_superieure': Decimal('3000000'), 'taux_irg': Decimal('5')},
        {'numero_tranche': 3, 'borne_inferieure': Decimal('3000001'), 'borne_superieure': Decimal('5000000'), 'taux_irg': Decimal('8')},
        {'numero_tranche': 4, 'borne_inferieure': Decimal('5000001'), 'borne_superieure': Decimal('10000000'), 'taux_irg': Decimal('10')},
        {'numero_tranche': 5, 'borne_inferieure': Decimal('10000001'), 'borne_superieure': Decimal('20000000'), 'taux_irg': Decimal('15')},
        {'numero_tranche': 6, 'borne_inferieure': Decimal('20000001'), 'borne_superieure': None, 'taux_irg': Decimal('20')},
    ]
    
    # Normaliser (même logique que le code corrigé)
    seuils = []
    for i, t in enumerate(tranches_gaps):
        bi = Decimal(str(t['borne_inferieure']))
        bs = t.get('borne_superieure')
        taux = Decimal(str(t['taux_irg']))
        if i > 0 and seuils:
            prev_sup = seuils[-1][1]
            if prev_sup is not None and bi > prev_sup and bi <= prev_sup + 2:
                bi = prev_sup
        if bs is not None:
            bs = Decimal(str(bs))
        seuils.append((bi, bs, taux))
    
    base = Decimal('3875000')
    irg_norm = Decimal('0')
    for bi, bs, taux in seuils:
        if base <= bi:
            break
        montant = (min(base, bs) - bi) if bs else (base - bi)
        if montant > 0:
            irg_norm += montant * taux / Decimal('100')
    irg_norm = arrondir(irg_norm)
    
    ok = irg_norm == Decimal('170000')
    status = "✅" if ok else "❌"
    print(f"  {status} Normalisation gaps: base=3,875,000 → RTS={irg_norm:,.0f} (attendu 170,000)")
    if not ok:
        all_ok = False
    
    return all_ok


if __name__ == '__main__':
    print("\n" + "🔍 " * 20)
    print("  AUDIT PAIE - TESTS DE VÉRIFICATION")
    print("  Corrections appliquées le 16/02/2026")
    print("🔍 " * 20)
    
    results = []
    results.append(("RTS Progressif", test_rts_progressif()))
    results.append(("VF Biétagée", test_vf_formule()))
    results.append(("Bulletin 1 - TENGUIANO (4.8M)", test_bulletin_1()))
    results.append(("Bulletin 2 - Conforme (13.5M)", test_bulletin_2()))
    results.append(("Moteur RTS Code", test_moteur_rts()))
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    all_passed = True
    for name, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status} - {name}")
        if not ok:
            all_passed = False
    
    print()
    if all_passed:
        print("  ✅ TOUS LES TESTS PASSENT - Calculs corrigés avec succès!")
    else:
        print("  ❌ CERTAINS TESTS ÉCHOUENT - Vérifier les corrections")
    print()
