# Note audit - Base VF avec deduction CGI

## Objectif

Cette note documente la regle appliquee par le moteur de paie pour le calcul de la base VF, afin que la logique soit explicite en cas de controle ou d'audit.

## Regle appliquee

Le moteur calcule la VF en deux etapes :

```text
deduction_vf = min(salaire_brut, plafond_cnss) x taux_vf
base_vf = salaire_brut - deduction_vf
vf = base_vf x taux_vf
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
```

## Tracabilite dans l'application

La reponse du moteur de simulation expose maintenant :

- `charges_employeur.base_vf`
- `charges_employeur.deduction_vf`
- `regles.base_vf_formule`
- `regles.vf_formule`
- `regles.reference_vf`

Ces informations sont affichees dans les details techniques de la structuration salariale pour rendre la base VF auditable.
