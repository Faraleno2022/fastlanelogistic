from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP

def floor_gnf(x):
    return int(Decimal(str(x)).quantize(Decimal('1'), rounding=ROUND_FLOOR))

def half_up(x):
    return int(Decimal(str(x)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

TRANCHES_RTS = [
    (0, 1000000, Decimal('0.00')),
    (1000000, 3000000, Decimal('0.05')),
    (3000000, 5000000, Decimal('0.08')),
    (5000000, 10000000, Decimal('0.12')),
    (10000000, 20000000, Decimal('0.16')),
    (20000000, 10**18, Decimal('0.20')),
]
PLAFOND_CNSS = Decimal('2500000')

def calcul_rts(base):
    base = Decimal(str(base))
    impot = Decimal('0')
    for bas, haut, taux in TRANCHES_RTS:
        bas, haut = Decimal(str(bas)), Decimal(str(haut))
        if base <= bas: break
        impot += (min(base, haut) - bas) * taux
    return half_up(impot)

def test(brut, indemnites, label):
    brut = Decimal(str(brut))
    indemnites = Decimal(str(max(0, indemnites)))
    cnss = half_up(min(brut, PLAFOND_CNSS) * Decimal('0.05'))
    plafond = floor_gnf(brut * Decimal('0.25'))
    exon = int(min(indemnites, Decimal(str(plafond))))
    depasse = int(max(Decimal('0'), indemnites - plafond))
    base_rts = int(brut) - cnss - exon + depasse
    rts = calcul_rts(base_rts)
    net = int(brut) - cnss - rts
    ok = (int(brut) - cnss - exon + depasse) == base_rts
    statut = 'OK' if ok else 'ECART'
    print(f'{label}: CNSS={cnss:,} Plafond={plafond:,} Exon={exon:,} BaseRTS={base_rts:,} RTS={rts:,} Net={net:,} {statut}')

test(5690002, 2600000, 'T01')
test(4000000, 1000000, 'T04')
test(4000000, 1000001, 'T05')
test(4000000, 0,       'T06')
test(4000000, 3000000, 'T08')
test(2500000, 0,       'T12')
test(0,       0,       'T14')
test(800000,  0,       'T15')
test(5000000, 0,       'T17')
