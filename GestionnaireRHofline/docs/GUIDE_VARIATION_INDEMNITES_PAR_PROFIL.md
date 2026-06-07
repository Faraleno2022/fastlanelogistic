# Guide d'utilisation - Variation des indemnites par profil

## Objectif

Ce document explique comment utiliser une variation d'indemnites forfaitaires selon le profil du salarie :

- Profil prudent : 20%
- Profil standard : 23%
- Profil maximum : 25%

Ces pourcentages servent a definir le niveau d'indemnites forfaitaires par rapport au salaire brut. Ils permettent d'adapter la structure du bulletin selon le profil du personnel, tout en gardant une limite claire pour l'audit paie.

## Principe general

Les indemnites forfaitaires concernent notamment :

- prime de transport ;
- prime de logement ;
- prime de cherte de vie ;
- autres primes forfaitaires assimilees a des indemnites.

La regle de controle reste simple :

```text
Indemnites forfaitaires <= Salaire brut x taux du profil
```

Le taux du profil ne doit jamais depasser 25% sans validation speciale, car 25% correspond au plafond maximal utilise pour l'exoneration des indemnites forfaitaires.

## Profils recommandes

| Profil | Taux | Usage recommande | Niveau de risque audit |
|---|---:|---|---|
| Prudent | 20% | Employes standards, profils administratifs, situations simples | Faible |
| Standard | 23% | Profils avec indemnites regulieres mais controlees | Modere |
| Maximum | 25% | Cadres, profils negocies, cas ou l'entreprise utilise le plafond maximal | Eleve mais acceptable si justifie |

## Formule si on part du salaire brut

Lorsque le salaire brut est deja connu :

```text
Indemnites forfaitaires = Salaire brut x taux profil
Salaire de base = Salaire brut - Indemnites forfaitaires
```

Exemple avec un brut de 10 000 000 GNF :

| Profil | Calcul | Indemnites | Salaire de base |
|---|---:|---:|---:|
| 20% | 10 000 000 x 20% | 2 000 000 | 8 000 000 |
| 23% | 10 000 000 x 23% | 2 300 000 | 7 700 000 |
| 25% | 10 000 000 x 25% | 2 500 000 | 7 500 000 |

## Formule si on part du salaire de base

Lorsque le salaire de base est deja connu et que l'on veut obtenir un brut ou les indemnites representent exactement 20%, 23% ou 25% du brut :

```text
Salaire brut = Salaire de base / (1 - taux profil)
Indemnites forfaitaires = Salaire brut - Salaire de base
```

Exemple avec un salaire de base de 3 000 000 GNF :

| Profil | Calcul brut | Salaire brut | Indemnites |
|---|---:|---:|---:|
| 20% | 3 000 000 / 0,80 | 3 750 000 | 750 000 |
| 23% | 3 000 000 / 0,77 | 3 896 104 | 896 104 |
| 25% | 3 000 000 / 0,75 | 4 000 000 | 1 000 000 |

## Methode d'utilisation dans la paie

1. Identifier le profil du salarie.
2. Choisir le taux applicable : 20%, 23% ou 25%.
3. Calculer les indemnites forfaitaires selon la methode de depart :
   - brut connu : `brut x taux` ;
   - base connue : `base / (1 - taux) - base`.
4. Repartir le montant des indemnites entre les rubriques utiles :
   - transport ;
   - logement ;
   - cherte de vie ;
   - autre indemnite forfaitaire si besoin.
5. Verifier que le total des indemnites ne depasse pas le taux du profil.
6. Calculer le bulletin.
7. Controler la base RTS et le net a payer.

## Exemple de repartition

Brut cible : 10 000 000 GNF  
Profil : standard 23%  
Indemnites totales : 2 300 000 GNF

Repartition possible :

| Rubrique | Montant |
|---|---:|
| Prime transport | 600 000 |
| Prime logement | 1 200 000 |
| Prime cherte de vie | 500 000 |
| Total indemnites | 2 300 000 |

Controle :

```text
2 300 000 / 10 000 000 = 23%
```

Le profil est respecte.

## Regles de controle avant validation

Avant de valider les bulletins, verifier :

- le taux d'indemnites applique au salarie ;
- le total des indemnites forfaitaires ;
- la base RTS ;
- la CNSS employee et employeur ;
- le VF ;
- l'ONFPP si l'effectif est superieur ou egal a 30 salaries ;
- le net a payer.

## Traitement des depassements

Si les indemnites depassent le taux du profil :

| Situation | Action recommandee |
|---|---|
| Depassement leger | Repartir ou reduire les indemnites avant validation |
| Depassement justifie | Ajouter une observation sur le bulletin ou dans le dossier paie |
| Depassement au-dessus de 25% | A traiter comme exception : l'excedent peut etre reintegre dans la base RTS |

## Bonnes pratiques

- Utiliser 20% pour les cas simples et peu sensibles.
- Utiliser 23% comme profil equilibre pour les salaries avec indemnites regulieres.
- Utiliser 25% seulement lorsque le dossier est justifie et documente.
- Eviter de modifier le profil d'un salarie en cours de mois sans trace.
- Garder la meme logique pour tous les salaries d'une meme categorie.

## Synthese rapide

```text
Profil prudent  = indemnites <= 20% du brut
Profil standard = indemnites <= 23% du brut
Profil maximum  = indemnites <= 25% du brut
```

La variation par profil permet d'introduire de la souplesse dans la paie sans perdre la coherence fiscale et l'auditabilite.
