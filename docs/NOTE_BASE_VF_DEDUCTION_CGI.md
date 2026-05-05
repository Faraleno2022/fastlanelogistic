# Note audit - Base VF / ONFPP

## Objectif

Cette note documente la regle appliquee par le moteur de paie pour le calcul de la base VF/ONFPP, afin que la logique soit explicite en cas de controle ou d'audit.

## Regle appliquee

En mode optimise GuineeRH, le moteur calcule la VF et l'ONFPP sur une base commune :

```text
indemnites_exonerees = min(indemnites_forfaitaires, salaire_brut x 25%)
base_vf_onfpp = salaire_brut - indemnites_exonerees
vf = base_vf_onfpp x 6%
onfpp = base_vf_onfpp x 1,5%
```

En mode strict fiscal, la base reste le brut :

```text
base_vf_onfpp = salaire_brut
vf = salaire_brut x 6%
onfpp = salaire_brut x 1,5%
```

## Exemple

Pour un salaire brut de `9 484 637 GNF` structure a 25% d'indemnites :

```text
indemnites_exonerees = 2 371 157 GNF
base_vf_onfpp = 9 484 637 - 2 371 157
base_vf_onfpp = 7 113 480 GNF

vf = 7 113 480 x 6%
vf = 426 809 GNF

onfpp = 7 113 480 x 1,5%
onfpp = 106 702 GNF

charges_patronales = 450 000 + 426 809 + 106 702
charges_patronales = 983 511 GNF
```

## Tracabilite dans l'application

La reponse du moteur et les bulletins exposent :

- `base_vf`
- `deduction_vf`
- `mode_base_vf`
- `taux_optimisation_vf_onfpp`
- `risque_fiscal_bulletin`

La phrase a afficher en audit est :

```text
Base VF/ONFPP = Brut - indemnites exonerees plafonnees a 25% du brut.
```

## Verrou CNSS

Le moteur verrouille aussi les parametres CNSS legaux afin d'eviter les erreurs de taux ou d'arrondi :

```text
base_cnss = min(max(brut, plancher_cnss), plafond_cnss)
plancher_cnss = 550 000 GNF
plafond_cnss = 2 500 000 GNF
cnss_employe = base_cnss x 5%
cnss_employeur = base_cnss x 18%
```

Pour tout brut superieur au plafond CNSS, les montants attendus sont donc :

```text
cnss_employe = 2 500 000 x 5% = 125 000 GNF
cnss_employeur = 2 500 000 x 18% = 450 000 GNF
```
