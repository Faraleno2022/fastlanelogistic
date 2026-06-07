# 📋 Décision Technique : RTS vs IRG

**Date** : Janvier 2026  
**Statut** : Option C - Alias en place  
**Impact** : Aucune migration requise

---

## Contexte

Le système utilisait historiquement le terme **IRG** (Impôt sur le Revenu Global) dans les modèles de données. La législation guinéenne utilise désormais le terme **RTS** (Retenue à la Source).

## Décision

### Option retenue : **Option C - Alias**

Les champs internes `irg` sont **conservés** pour compatibilité avec :
- La base de données existante
- Les exports historiques
- Les rapports archivés

Des **alias RTS** sont ajoutés via des propriétés Python pour que le code métier utilise la terminologie actuelle.

## Implémentation

### Modèles concernés

| Modèle | Champ interne | Alias RTS |
|--------|---------------|-----------|
| `BulletinPaie` | `irg` | `rts` |
| `RubriquePaie` | `soumis_irg` | `soumis_rts` |
| `TrancheRTS` | `taux_irg` | `taux_rts` |
| `ParametrePaie` | `plafond_abattement_irg` | `plafond_abattement_rts` |
| `ParametrePaie` | `taux_abattement_irg` | `taux_abattement_rts` |
| `CumulPaie` | `cumul_irg` | `cumul_rts` |

### Exemple d'utilisation

```python
# Les deux syntaxes sont équivalentes
bulletin.irg = 150000      # Historique (fonctionne toujours)
bulletin.rts = 150000      # Recommandé (nouveau code)

# Lecture
montant_impot = bulletin.rts  # Retourne la valeur de irg
```

### Commentaires dans le code

Chaque champ IRG est documenté :
```python
# Champ historique IRG – alias RTS utilisé côté métier (Option C)
irg = models.DecimalField(...)
```

## Avantages de cette approche

| Critère | Résultat |
|---------|----------|
| Migration base de données | ❌ Non requise |
| Risque en production | ✅ Zéro |
| Compatibilité historique | ✅ Totale |
| Nouveau code utilise RTS | ✅ Oui |
| Préparation version majeure | ✅ Oui |

## Évolution future (Option A)

Lors d'une **version majeure** (ex: v4.0), le renommage complet sera effectué :

1. Migration base de données (renommage colonnes)
2. Mise à jour des modèles (`irg` → `rts`)
3. Suppression des alias (devenus inutiles)
4. Changelog clair pour les utilisateurs

### Prérequis avant Option A

- [ ] Fenêtre de maintenance planifiée
- [ ] Backup complet de la base
- [ ] Script de migration testé en staging
- [ ] Documentation utilisateur mise à jour

---

## Résumé pour les développeurs

> **Règle simple** : Utiliser `rts` dans tout nouveau code.  
> Le champ `irg` existe pour l'historique, ne pas l'utiliser directement.

---

*Document technique - Janvier 2026*  
*GestionnaireRH - Conforme CGI 2022*
