# Note audit - Base VF avec deduction CGI

## Objectif

Cette note documente la regle appliquee par le moteur de paie pour le calcul de la base VF, afin que la logique soit explicite en cas de controle ou d'audit.

## Regle appliquee

Le moteur calcule la VF et l'ONFPP sur une base commune :

```text
deduction_vf = min(salaire_brut, plafond_cnss) x taux_vf
base_vf = salaire_brut - deduction_vf
vf = base_vf x taux_vf
onfpp = base_vf x taux_onfpp
```

Avec les constantes actuelles :

```text
plafond_cnss = 2 500 000 GNF
taux_vf = 6%
deduction_vf maximale = 2 500 000 x 6% = 150 000 GNF
```

## Exemple

Pour un salaire brut de `9 483 784 GNF` :

```text
deduction_vf = min(9 483 784, 2 500 000) x 6%
deduction_vf = 150 000 GNF

base_vf = 9 483 784 - 150 000
base_vf = 9 333 784 GNF

vf = 9 333 784 x 6%
vf = 560 027 GNF

onfpp = 9 333 784 x 1,5%
onfpp = 140 007 GNF
```

## Exemple bulletin controle

Pour un salaire brut de `4 479 445 GNF` :

```text
deduction_vf = min(4 479 445, 2 500 000) x 6%
deduction_vf = 150 000 GNF

base_vf_onfpp = 4 479 445 - 150 000
base_vf_onfpp = 4 329 445 GNF

vf = 4 329 445 x 6%
vf = 259 767 GNF

onfpp = 4 329 445 x 1,5%
onfpp = 64 942 GNF

charges_patronales = 450 000 + 259 767 + 64 942
charges_patronales = 774 709 GNF
```

## Tracabilite dans l'application

La reponse du moteur de simulation expose maintenant :

- `charges_employeur.base_vf`
- `charges_employeur.deduction_vf`
- `regles.base_vf_formule`
- `regles.vf_formule`
- `regles.reference_vf`

Ces informations sont affichees dans les details techniques de la structuration salariale pour rendre la base VF auditable.

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
