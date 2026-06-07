# 🚀 Quick Start - Gestionnaire RH Guinée

## ✅ Phases A & B Complétées (21 Oct 2025)

### Lancer le projet
```bash
python manage.py runserver
```

### Accéder à l'admin
```
URL : http://127.0.0.1:8000/admin/
User: LENO
Pass: 1994
```

### Nouveaux modules disponibles

#### 📋 Paie
- Paramètres de paie ✅
- Constantes (SMIG, CNSS, INAM) ✅
- Barème IRG 2025 ✅
- Variables ✅

#### ⏰ Temps de travail
- Jours fériés (11 jours 2025) ✅
- Pointages ✅
- Congés ✅
- Absences ✅
- Arrêts de travail ✅
- Horaires ✅

### Données initialisées
- 9 constantes guinéennes
- 6 tranches IRG
- 11 jours fériés 2025
- 3 variables

### Commandes utiles
```bash
# Réinitialiser les paramètres de paie
python manage.py init_paie_guinee

# Réinitialiser les jours fériés
python manage.py init_jours_feries_guinee --annee 2025
```

### Documentation complète
- `LIRE_MOI_PHASES_A_B.md` - Guide complet
- `docs/PHASES_A_B_COMPLETEES.md` - Documentation technique
- `docs/RESUME_PHASES_A_B.md` - Résumé visuel

### Progression
```
Projet : 30% complété
Phase A : 100% ✅
Phase B : 100% ✅
Prochaine : Phase C (Calcul de Paie)
```

🇬🇳 **Made in Guinea**
