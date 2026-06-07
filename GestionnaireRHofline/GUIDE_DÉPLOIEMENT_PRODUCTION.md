
# 🚀 GUIDE DE DÉPLOIEMENT - Congés Auto-Calcul

## Phase 1: Préparation (5 minutes)

### ✅ Vérifier que les modifications sont en place

```bash
# Sur votre machine locale
cd c:\Users\LENO\Desktop\GestionnaireRHofline

# Vérifier les modifications dans services.py
grep -n "_calculer_conges_acquis" paie/services.py
# Devrait trouver 2 occurrences:
# 1. Ligne ~1188: appel dans generer_bulletin()
# 2. Ligne ~1290: définition de la méthode
```

### ✅ Vérifier les fichiers de support

```bash
ls -la PATCH_CONGES_AUTOMATIQUE.py
ls -la CONGÉS_AUTOMATIQUES_IMPLÉMENTATION.md
ls -la RÉSUMÉ_IMPLÉMENTATION_CONGES.md
ls -la fill_conges_acquis.py
# Tous ces fichiers doivent exister
```

---

## Phase 2: Synchronisation Code (2 minutes)

### Option A: Version Control (Recommandé)

```bash
# Committer les modifications
cd c:\Users\LENO\Desktop\GestionnaireRHofline
git status
# Devrait montrer:
#   modified:   paie/services.py
#   new file:   PATCH_CONGES_AUTOMATIQUE.py
#   new file:   CONGÉS_AUTOMATIQUES_IMPLÉMENTATION.md
#   ... etc

# Committer
git add paie/services.py PATCH_CONGES_AUTOMATIQUE.py CONGÉS_AUTOMATIQUES_IMPLÉMENTATION.md RÉSUMÉ_IMPLÉMENTATION_CONGES.md CHANGEMENTS_DÉTAILLÉS_SERVICES_PY.md fill_conges_acquis.py

git commit -m "🔧 Implémentation auto-calcul congés acquis - Code du Travail Guinée Art.195

- Ajout méthodes _calculer_anciennete_mois() et _calculer_conges_acquis() dans MoteurCalculPaie
- Intégration auto-calcul dans generer_bulletin()
- Chaque bulletin crée/met à jour automatiquement SoldeConge avec ancienneté-based calculation
- Respecte ConfigPaieEntreprise.jours_conges_par_mois (défault: 2.5 j/mois)
- Maximum: 30 jours/an
- Conformité: Code du Travail Guinée Article 195 ✅

Documentation:
- PATCH_CONGES_AUTOMATIQUE.py: Patch guide
- CONGÉS_AUTOMATIQUES_IMPLÉMENTATION.md: Implémentation complète
- RÉSUMÉ_IMPLÉMENTATION_CONGES.md: Résumé et checklist
- CHANGEMENTS_DÉTAILLÉS_SERVICES_PY.md: Diff détaillé
- fill_conges_acquis.py: Script de remplissage batch

Priorité: 🔴 HAUTE (Conformité légale)"

git push
```

### Option B: Copie Manuelle

```bash
# Sur le serveur production
cd /home/guineerh/gestionrh

# Télécharger le fichier modifié
# Via SCP:
scp c:\Users\LENO\Desktop\GestionnaireRHofline\paie\services.py guineerh@www.guineerh.space:/home/guineerh/gestionrh/paie/

# Via WinSCP ou autre outil SFTP
# Copier services.py vers le serveur

# Vérifier les permissions
chmod 644 paie/services.py
```

---

## Phase 3: Activation en Production (5 minutes)

### Sur le serveur production (SSH)

```bash
# Connecter au serveur
ssh guineerh@www.guineerh.space

# Aller au répertoire de l'app
cd /home/guineerh/gestionrh

# Vérifier les modifications
grep -n "_calculer_conges_acquis" paie/services.py
# Devrait trouver 2 occurrences ✅

# Créer un backup du fichier original (sécurité)
cp paie/services.py paie/services.py.backup.2026-04-XX

# Si vous avez utilisé git:
git pull origin main  # ou votre branche
# Si copie manuelle: les fichiers sont déjà en place

# Vérifier l'intégrité Python
python3 -m py_compile paie/services.py
# Devrait retourner rien (pas d'erreurs) ✅

# Si erreur: revoir les modifications
```

### Redémarrer l'application

```bash
# Option 1: uWSGI
sudo systemctl restart uWSGI_gestionrh
# Attendre 5-10 secondes

# Option 2: Gunicorn
sudo systemctl restart gunicorn_gestionrh
# Attendre 5-10 secondes

# Option 3: Nginx (s'il est le reverse proxy)
sudo systemctl restart nginx
# Attendre les uWSGI/gunicorn redémarrés

# Vérifier le statut
sudo systemctl status uWSGI_gestionrh
# Devrait montrer "active (running)" ✅

sudo systemctl status nginx
# Devrait montrer "active (running)" ✅
```

### Vérifier les logs

```bash
# Logs d'application
tail -f /var/log/uWSGI_gestionrh.log
# Ou pour gunicorn
tail -f /var/log/gunicorn_gestionrh.log

# Vérifier qu'aucune erreur:
# ✅ No ImportError
# ✅ No SyntaxError
# ✅ No Module errors
# Attendre ~30 secondes, puis fermer
```

---

## Phase 4: Test dans l'Interface Web (5 minutes)

### Accéder à l'interface

1. Ouvrir: https://www.guineerh.space/paie/bulletins/
2. Identifier un employé actif: **FARA LENO** (embauche 26/01/2026)
3. Générer un bulletin pour **Avril 2026**

### Test 1: Vérifier la Création Automatique

```
1. Aller à Django Admin (https://www.guineerh.space/admin/)
2. Naviguer: Temps Travail > Soldes Congés
3. Chercher: FARA LENO, année 2026
4. Vérifier:
   ✅ Record créé automatiquement
   ✅ conges_acquis = ~7.50 (3 mois × 2.5)
   ✅ conges_pris = 0
```

### Test 2: Affichage sur le Bulletin

```
1. Aller à: Paie > Bulletins de Paie
2. Cliquer sur le bulletin généré
3. Regarder la section "Congés":
   ✅ "Congés acquis: 7.50 j"
   ✅ "Congés pris: 0 j"
   ✅ "Solde congés: 7.50 j"
   
   Si AVANT: "Congés acquis: 0 j" ❌
   Alors: Le calcul automatique fonctionne ✅
```

### Test 3: Télécharger PDF

```
1. Sur le bulletin, cliquer "Télécharger PDF"
2. Ouvrir le PDF
3. Vérifier page 3 (congés):
   ✅ "Solde de congés: 7.50 j"
   ✅ Valeurs cohérentes avec HTML
```

---

## Phase 5: Remplissage Rétroactif (Optionnel - 5 minutes)

### Remplir les bulletins/employes existants

```bash
# Sur le serveur, en SSH
cd /home/guineerh/gestionrh
source venv/bin/activate

# Copier le script si non présent
# Sinon il doit être dans le workspace
cp fill_conges_acquis.py .

# Exécuter
python3 fill_conges_acquis.py

# Sortie attendue:
# ════════════════════════════════════════════════════════════════════════════
# 📊 REMPLISSAGE AUTOMATIQUE DES CONGÉS ACQUIS - CODE DU TRAVAIL GUINÉE
# ════════════════════════════════════════════════════════════════════════════
# 
# 🔍 Recherche des employés actifs...
# 🔍 Nombre d'employés actifs: X
# 
# 📋 Calcul des congés pour chaque employé...
#   ✅ FARA LENO      (26/01/2026): 7.50 j acquis, 0 pris, 7.50 restants
#   ✅ DAV JOB        (15/02/2026): 6.00 j acquis, 0 pris, 6.00 restants
#   ...
# 
# ═════════════════════════════════════════════════════════════════════════════
# ✅ Résumé: X employés mis à jour
#    • Nombre de SoldeConge créés: Y
#    • Nombre de SoldeConge mis à jour: Z
#    • Congés totaux acquis: WWW jours
# ═════════════════════════════════════════════════════════════════════════════
```

### Vérifier le Remplissage

```bash
# Admin: Temps Travail > Soldes Congés
# Vous devriez voir tous les employés listés avec:
# ✅ conges_acquis > 0
# ✅ conges_pris = 0
# ✅ conges_restants > 0 (calculated)

# Ou en Django shell
python3 manage.py shell
>>> from temps_travail.models import SoldeConge
>>> SoldeConge.objects.filter(annee=2026).count()
# Devrait montrer: X records (non-zéro)
>>> SoldeConge.objects.filter(annee=2026, conges_acquis=0).count()
# Devrait montrer: 0 (aucun zéro après remplissage)
```

---

## Phase 6: Validation Complète (10 minutes)

### Test 1: Calcul Correct pour Différentes Anciennetés

```python
# Via Django shell
python3 manage.py shell

>>> from temps_travail.models import SoldeConge
>>> 
>>> # FARA LENO: embauche 26/01/2026 → 3.13 mois
>>> fara = SoldeConge.objects.get(employe__nombre='FARA LENO', annee=2026)
>>> print(f"FARA: {fara.conges_acquis} (attendu: ~7.8)")
# ✅ Devrait afficher: Decimal('7.50') ou Decimal('7.80')
>>>
>>> # DAV JOB: embauche 15/02/2026 → 2.5 mois
>>> dav = SoldeConge.objects.get(employe__nombre='DAV JOB', annee=2026)
>>> print(f"DAV: {dav.conges_acquis} (attendu: ~6.25)")
# ✅ Devrait afficher: Decimal('6.00') ou Decimal('6.25')
```

### Test 2: Configuration Respected

```python
>>> from enterprises.models import ConfigPaieEntreprise
>>> config = ConfigPaieEntreprise.objects.first()
>>> print(f"Jours congés/mois: {config.jours_conges_par_mois}")
# Devrait afficher: 2.50 (Code du Travail) ou 1.50 (Convention)

# Vérifier règle appliquée
>>> dav_mois = 2.5  # APPROXIMATIF
>>> expected = dav_mois * float(config.jours_conges_par_mois)
>>> print(f"Attendu pour DAV: {expected}")
# Devrait matcher le conges_acquis calculé
```

### Test 3: Bulletins Historiques

```
1. Accéder à un ancien bulletin (avant le déploiement)
2. Si SoldeConge n'existe pas → reste 0
3. Si SoldeConge existe → affiche le value (possibl. 0 s'il n'a pas été rempli)
4. 📝 NOTER: Après remplissage batch, tous affichent congés corrects

Solution: Régénérer le bulletin
1. Éditer > Forcer recalcul > Sauvegarder
2. Ou supprimer et créer nouveau
```

---

## Phase 7: Monitoring Post-Déploiement (24h)

### Surveiller Pendant 24h

```bash
# Vérifier régulièrement les logs
# Rechercher: "Erreur" ou "Error"
tail -100 /var/log/uWSGI_gestionrh.log | grep -i error

# Vérifier les bulletins générés
# Interface > Paie > Bulletins > Voir congés sur récents

# Vérifier performance
# Charger plusieurs bulletins, vérifier temps chargement
# Devrait rester < 2 secondes (pas d'impact)
```

### KPIs à surveiller

| Métrique | Avant | Attendu Après |
|----------|-------|---------------|
| Temps génération bulletin | ~2s | ~2.1s (impact negligeable) |
| Bulletins avec congés=0 | 100% | 0% (après remplissage) |
| Erreurs dans logs | Aucune | Aucune (ou très rares) |
| SoldeConge créés | ~0 | Tous employés actifs |

---

## Phase 8: Rollback (En Cas de Problème)

Si quelque chose va mal, revert rapidement:

```bash
# SSH sur serveur
cd /home/guineerh/gestionrh

# Revert au backup
cp paie/services.py.backup.2026-04-XX paie/services.py

# Ou viaGit
git revert HEAD  # Last commit
git push

# Redémarrer
sudo systemctl restart uWSGI_gestionrh

# Vérifier
# http://www.guineerh.space/paie/bulletins/
# Devrait fonctionner comme avant
```

---

## ✅ Checklist de Déploiement

### Avant Déploiement
- [ ] Modifications en place dans `paie/services.py`
- [ ] Tous les fichiers de support créés
- [ ] Code validé (pas d'erreurs syntax)
- [ ] Test local effectué (si possible)
- [ ] Backup pris de l'original

### Pendant Déploiement
- [ ] Code synchronisé sur serveur
- [ ] Serveur restarté sans erreurs
- [ ] Logs vérifiés (no errors)
- [ ] Interface accessible

### Après Déploiement
- [ ] Test interface: générer bulletin avec congés
- [ ] Vérifier SoldeConge créé automatiquement
- [ ] Vérifier calcul correct (ancienneté × 2.5)
- [ ] Vérifier affichage HTML et PDF
- [ ] Exécuter script batch (si remplissage rétro désiré)
- [ ] Surveiller logs 24h

### Validation Finale
- [ ] ✅ Bulletins générés affichent congés corrects
- [ ] ✅ SoldeConge créés/mis à jour automatiquement
- [ ] ✅ Conformité Code du Travail Guinée Art.195
- [ ] ✅ Performance pas impactée
- [ ] ✅ Pas de nouvelles erreurs

---

## 📞 Support / Dépannage

### Problème: Serveur ne redémarre pas

```bash
# Vérifier erreurs syntax
python3 -m py_compile paie/services.py

# Si erreur: revert
cp paie/services.py.backup paie/services.py

# Vérifier les logs
journalctl -u uWSGI_gestionrh -n 50
```

### Problème: Congés toujours 0

```bash
# Vérifier configuration
python3 manage.py shell
>>> from enterprises.models import ConfigPaieEntreprise
>>> c = ConfigPaieEntreprise.objects.first()
>>> print(c.jours_conges_par_mois)
# Si aucune → créer une via admin

# Exécuter script batch
python3 fill_conges_acquis.py
```

### Problème: SoldeConge pas créé

```bash
# Vérifier migrations temps_travail
python3 manage.py migrate temps_travail

# Vérifier l'employé a une date_embauche
python3 manage.py shell
>>> from employes.models import Employe
>>> e = Employe.objects.get(id=123)
>>> print(e.date_embauche)
# Doit avoir une date valide
```

---

## 🎉 Résumé du Déploiement

| Phase | Durée | Étape |
|-------|-------|-------|
| 1. Préparation | 5 min | Vérifier modifications |
| 2. Synchronisation | 2 min | Code sur serveur |
| 3. Activation | 5 min | Redémarrer app |
| 4. Test Web | 5 min | Générer bulletin test |
| 5. Remplissage | 5 min | Script batch (optionnel) |
| 6. Validation | 10 min | Tests complets |
| 7. Monitoring | 24h | Surveillance |

**Total: ~30 minutes** (avec remplissage batch optionnel)

---

**Statut:** ✅ PRÊT POUR PRODUCTION  
**Priorité:** 🔴 HAUTE  
**Date:** Avril 2026

