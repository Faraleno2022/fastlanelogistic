"""Test de verification des calculs de paie - Bulletin Camara Amadou
Reproduit fidellement la logique de paie/services.py
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionnaire_rh.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from decimal import Decimal, ROUND_HALF_UP

def arrondir(montant):
    return montant.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# === Donnees bulletin Camara Amadou ===
salaire_base = Decimal('1190042')
prime_transport = Decimal('100000')
prime_logement = Decimal('100000')
prime_cherte_vie = Decimal('194737')

brut = salaire_base + prime_transport + prime_logement + prime_cherte_vie
print("=== GAINS ===")
print(f"Salaire de base:      {salaire_base:>15,.0f}")
print(f"Prime transport:      {prime_transport:>15,.0f}")
print(f"Prime logement:       {prime_logement:>15,.0f}")
print(f"Prime cherte de vie:  {prime_cherte_vie:>15,.0f}")
print(f"TOTAL BRUT:           {brut:>15,.0f}")

# === CNSS (toutes primes soumis_cnss=True) ===
plafond = Decimal('2500000')
# cnss_base = brut (toutes les primes sont soumises CNSS apres correction)
cnss_base = brut  # < plafond donc pas de plafonnement
cnss_employe = arrondir(min(cnss_base, plafond) * Decimal('5') / Decimal('100'))
cnss_employeur = arrondir(min(cnss_base, plafond) * Decimal('18') / Decimal('100'))
print("\n=== CNSS ===")
print(f"Base CNSS (= brut, plafond 2.5M): {min(cnss_base, plafond):>10,.0f}")
print(f"CNSS Employe (5%):                {cnss_employe:>10,.0f}")
print(f"CNSS Employeur (18%):             {cnss_employeur:>10,.0f}")

# === RTS (identique a _calculer_irg dans services.py) ===
# Charger les constantes depuis la BD
from paie.models import Constante
constantes = {}
for c in Constante.objects.all():
    try:
        constantes[c.code] = Decimal(str(c.valeur))
    except:
        pass

# base_imposable = imposable - cnss_employe (PAS d'abattement pour la RTS)
# 'imposable' = somme des gains avec soumis_irg=True
# Les primes forfaitaires (transport, logement, cherte de vie) ont soumis_irg=False
# Seul le salaire de base est soumis_irg=True
imposable = salaire_base  # primes exonerees de RTS
base_rts = imposable - cnss_employe

print(f"\n=== RTS (bareme progressif, PAS d'abattement) ===")
print(f"Imposable (brut):                 {imposable:>10,.0f}")
print(f"CNSS employe:                    -{cnss_employe:>10,.0f}")
print(f"Base RTS:                         {base_rts:>10,.0f}")

# Bareme RTS CGI 2022 (fallback hardcode dans services.py)
tranches = [
    (Decimal('0'), Decimal('1000000'), Decimal('0')),
    (Decimal('1000000'), Decimal('3000000'), Decimal('5')),
    (Decimal('3000000'), Decimal('5000000'), Decimal('8')),
    (Decimal('5000000'), Decimal('10000000'), Decimal('10')),
    (Decimal('10000000'), Decimal('20000000'), Decimal('15')),
    (Decimal('20000000'), None, Decimal('20')),
]

rts = Decimal('0')
for borne_inf, borne_sup, taux in tranches:
    if base_rts <= borne_inf:
        break
    if borne_sup is not None:
        montant_tranche = min(base_rts, borne_sup) - borne_inf
    else:
        montant_tranche = base_rts - borne_inf
    if montant_tranche > 0:
        impot = montant_tranche * taux / Decimal('100')
        print(f"  {borne_inf:>12,.0f} - {str(borne_sup) if borne_sup else '...':>12} x {taux:>5}% = {impot:>10,.2f}")
        rts += impot

rts = arrondir(rts)
taux_effectif = arrondir(rts * Decimal('100') / base_rts) if base_rts > 0 else Decimal('0')
print(f"RTS total (arrondi):              {rts:>10,.0f}")
print(f"Taux effectif:                    {taux_effectif:>9}%")

# === NET ===
net = brut - cnss_employe - rts
print(f"\n=== NET A PAYER ===")
print(f"{brut:,.0f} - {cnss_employe:,.0f} - {rts:,.0f} = {net:,.0f}")

# === CHARGES PATRONALES ===
taux_vf = constantes.get('TAUX_VF', Decimal('6'))
seuil_vf = plafond
base_deduction_vf = min(brut, seuil_vf)
deduction_vf = arrondir(base_deduction_vf * taux_vf / Decimal('100'))
base_vf_nette = brut - deduction_vf
vf = arrondir(base_vf_nette * taux_vf / Decimal('100'))

taux_ta = constantes.get('TAUX_TA', Decimal('1.50'))
ta = arrondir(brut * taux_ta / Decimal('100'))

total_charges = cnss_employeur + vf + ta

print(f"\n=== CHARGES PATRONALES ===")
print(f"CNSS Employeur (18% de {min(cnss_base, plafond):,.0f}): {cnss_employeur:>10,.0f}")
print(f"Deduction VF = min({brut:,.0f}, {seuil_vf:,.0f}) x {taux_vf}% = {deduction_vf:,.0f}")
print(f"Base VF nette = {brut:,.0f} - {deduction_vf:,.0f} = {base_vf_nette:,.0f}")
print(f"VF ({taux_vf}% de {base_vf_nette:,.0f}):          {vf:>10,.0f}")
print(f"TA ({taux_ta}% de {brut:,.0f}):          {ta:>10,.0f}")
print(f"Total charges patronales:             {total_charges:>10,.0f}")

# === COMPARAISON ===
print("\n" + "="*65)
print("COMPARAISON CALCUL LOCAL vs BULLETIN PRODUCTION")
print("="*65)
bulletin_vals = {
    'Brut': Decimal('1584779'),
    'CNSS sal': Decimal('79239'),
    'RTS': Decimal('5540'),
    'Net': Decimal('1500000'),
    'CNSS pat': Decimal('285260'),
    'VF': Decimal('89382'),
    'TA': Decimal('23772'),
    'Total ch': Decimal('398413'),
}
calcul_vals = {
    'Brut': brut,
    'CNSS sal': cnss_employe,
    'RTS': rts,
    'Net': net,
    'CNSS pat': cnss_employeur,
    'VF': vf,
    'TA': ta,
    'Total ch': total_charges,
}
print(f"{'Element':<12} {'Calcul':>12} {'Bulletin':>12} {'Ecart':>8} {'Status'}")
print("-" * 65)
for key in bulletin_vals:
    calc = calcul_vals[key]
    bull = bulletin_vals[key]
    ecart = calc - bull
    status = "OK" if abs(ecart) <= 1 else f"ECART {ecart:+,.0f}"
    print(f"{key:<12} {calc:>12,.0f} {bull:>12,.0f} {ecart:>+8,.0f}  {status}")

# === Constantes chargees ===
print(f"\n=== CONSTANTES BD LOCALE ===")
for code in sorted(constantes.keys()):
    print(f"  {code}: {constantes[code]}")

# Note sur TA
print(f"\n=== NOTE ===")
print(f"TAUX_TA en BD locale: {taux_ta}%")
print(f"TAUX_TA en production: 1.50% (23,772 / 1,584,779 = 1.50%)")
if taux_ta != Decimal('1.50'):
    print(f"  => ECART: BD locale a {taux_ta}% vs production 1.50%")
