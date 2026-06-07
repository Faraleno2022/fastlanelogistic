# 🗄️ SCHÉMA DES RELATIONS ENTRE LES TABLES

**Système de Gestion RH - Guinée**  
**Date** : 22 Octobre 2025  
**Total de tables** : 32 tables

---

## 📊 VUE D'ENSEMBLE DES MODULES

```
┌─────────────────────────────────────────────────────────────┐
│                     SYSTÈME GRH GUINÉE                       │
├─────────────────────────────────────────────────────────────┤
│  CORE (9 tables)                                            │
│  EMPLOYÉS (5 tables)                                        │
│  PAIE (11 tables)                                           │
│  TEMPS DE TRAVAIL (8 tables)                               │
│  RECRUTEMENT (3 tables)                                     │
│  FORMATION (1 table)                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 RELATIONS PRINCIPALES

### **TABLE CENTRALE : `Employe`**

L'employé est au cœur du système avec **25 relations** :

```
                    ┌──────────────────┐
                    │     EMPLOYE      │
                    │  (Table Centrale)│
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    ┌───▼───┐          ┌────▼────┐         ┌────▼────┐
    │ CORE  │          │  PAIE   │         │  TEMPS  │
    └───────┘          └─────────┘         └─────────┘
```

---

## 📋 MODULE CORE (9 tables)

### **1. Utilisateur** (utilisateurs)
**Relations :**
- `profil` → **ProfilUtilisateur** (FK)
- `groups` → **auth.Group** (M2M)
- `user_permissions` → **auth.Permission** (M2M)

**Relations inverses :**
- ← **LogActivite** (logs)
- ← **ParametrePaie** (utilisateur_modification)
- ← **PeriodePaie** (utilisateur_cloture)
- ← **HistoriquePaie** (utilisateur)
- ← **Employe** (utilisateur_creation, utilisateur_modification)

### **2. ProfilUtilisateur** (profils_utilisateurs)
**Relations :**
- Aucune FK sortante

**Relations inverses :**
- ← **Utilisateur** (profil)
- ← **DroitAcces** (profil)

### **3. DroitAcces** (droits_acces)
**Relations :**
- `profil` → **ProfilUtilisateur** (FK)

### **4. LogActivite** (logs_activite)
**Relations :**
- `utilisateur` → **Utilisateur** (FK)

### **5. Societe** (societe)
**Relations :**
- Aucune FK sortante

**Relations inverses :**
- ← **Etablissement** (societe)

### **6. Etablissement** (etablissements)
**Relations :**
- `societe` → **Societe** (FK)

**Relations inverses :**
- ← **Service** (etablissement)
- ← **Employe** (etablissement)
- ← **CarriereEmploye** (ancien_etablissement, nouveau_etablissement)

### **7. Service** (services)
**Relations :**
- `etablissement` → **Etablissement** (FK)
- `service_parent` → **Service** (FK auto-référence)
- `responsable_service` → **Employe** (FK)

**Relations inverses :**
- ← **Service** (service_parent) - sous-services
- ← **Poste** (service)
- ← **Employe** (service)
- ← **OffreEmploi** (service)
- ← **CarriereEmploye** (ancien_service, nouveau_service)

### **8. Poste** (postes)
**Relations :**
- `service` → **Service** (FK)

**Relations inverses :**
- ← **Employe** (poste)
- ← **OffreEmploi** (poste)
- ← **CarriereEmploye** (ancien_poste, nouveau_poste)

---

## 👥 MODULE EMPLOYÉS (5 tables)

### **9. Employe** (employes) ⭐ TABLE CENTRALE
**Relations :**
- `etablissement` → **Etablissement** (FK)
- `service` → **Service** (FK)
- `poste` → **Poste** (FK)
- `superieur_hierarchique` → **Employe** (FK auto-référence)
- `utilisateur_creation` → **Utilisateur** (FK)
- `utilisateur_modification` → **Utilisateur** (FK)

**Relations inverses :**
- ← **Employe** (superieur_hierarchique) - subordonnes
- ← **Service** (responsable_service) - services_geres
- ← **ContratEmploye** (employe) - contrats
- ← **FormationEmploye** (employe) - formations
- ← **CarriereEmploye** (employe) - carrieres
- ← **EvaluationEmploye** (employe, evaluateur) - evaluations, evaluations_effectuees
- ← **BulletinPaie** (employe) - bulletins
- ← **ElementSalaire** (employe) - elements_salaire
- ← **CumulPaie** (employe) - cumuls_paie
- ← **HistoriquePaie** (employe) - historique_paie
- ← **Pointage** (employe) - pointages
- ← **Conge** (employe, approbateur, remplacant) - conges, conges_approuves, remplacements
- ← **SoldeConge** (employe) - soldes_conges
- ← **Absence** (employe) - absences
- ← **ArretTravail** (employe) - arrets_travail
- ← **AffectationHoraire** (employe) - affectations_horaires
- ← **OffreEmploi** (responsable_recrutement)

### **10. ContratEmploye** (contrats_employes)
**Relations :**
- `employe` → **Employe** (FK)

### **11. FormationEmploye** (formations_employes)
**Relations :**
- `employe` → **Employe** (FK)

### **12. CarriereEmploye** (carrieres_employes)
**Relations :**
- `employe` → **Employe** (FK)
- `ancien_poste` → **Poste** (FK)
- `nouveau_poste` → **Poste** (FK)
- `ancien_service` → **Service** (FK)
- `nouveau_service` → **Service** (FK)
- `ancien_etablissement` → **Etablissement** (FK)
- `nouveau_etablissement` → **Etablissement** (FK)

### **13. EvaluationEmploye** (evaluations_employes)
**Relations :**
- `employe` → **Employe** (FK)
- `evaluateur` → **Employe** (FK)

---

## 💰 MODULE PAIE (11 tables)

### **14. PeriodePaie** (periodes_paie)
**Relations :**
- `utilisateur_cloture` → **Utilisateur** (FK)

**Relations inverses :**
- ← **BulletinPaie** (periode) - bulletins
- ← **HistoriquePaie** (periode) - historique

**Contrainte unique :** `annee` + `mois`

### **15. RubriquePaie** (rubriques_paie)
**Relations :**
- Aucune FK sortante

**Relations inverses :**
- ← **ElementSalaire** (rubrique) - elements_employes
- ← **LigneBulletin** (rubrique)

### **16. BulletinPaie** (bulletins_paie)
**Relations :**
- `employe` → **Employe** (FK)
- `periode` → **PeriodePaie** (FK)

**Relations inverses :**
- ← **LigneBulletin** (bulletin) - lignes
- ← **HistoriquePaie** (bulletin) - historique

**Contrainte unique :** `employe` + `periode`

### **17. ParametrePaie** (parametres_paie)
**Relations :**
- `utilisateur_modification` → **Utilisateur** (FK)

### **18. Constante** (constantes)
**Relations :**
- Aucune FK sortante

### **19. TrancheIRG** (tranches_irg)
**Relations :**
- Aucune FK sortante

### **20. Variable** (variables)
**Relations :**
- Aucune FK sortante

### **21. ElementSalaire** (elements_salaire)
**Relations :**
- `employe` → **Employe** (FK)
- `rubrique` → **RubriquePaie** (FK)

### **22. LigneBulletin** (lignes_bulletin)
**Relations :**
- `bulletin` → **BulletinPaie** (FK)
- `rubrique` → **RubriquePaie** (FK)

### **23. CumulPaie** (cumuls_paie)
**Relations :**
- `employe` → **Employe** (FK)

**Contrainte unique :** `employe` + `annee`

### **24. HistoriquePaie** (historique_paie)
**Relations :**
- `bulletin` → **BulletinPaie** (FK)
- `periode` → **PeriodePaie** (FK)
- `employe` → **Employe** (FK)
- `utilisateur` → **Utilisateur** (FK)

---

## ⏰ MODULE TEMPS DE TRAVAIL (8 tables)

### **25. JourFerie** (calendrier_jours_feries)
**Relations :**
- Aucune FK sortante

### **26. Conge** (conges)
**Relations :**
- `employe` → **Employe** (FK)
- `approbateur` → **Employe** (FK)
- `remplacant` → **Employe** (FK)

### **27. SoldeConge** (soldes_conges)
**Relations :**
- `employe` → **Employe** (FK)

**Contrainte unique :** `employe` + `annee`

### **28. Pointage** (pointages)
**Relations :**
- `employe` → **Employe** (FK)

**Contrainte unique :** `employe` + `date_pointage`

### **29. Absence** (absences)
**Relations :**
- `employe` → **Employe** (FK)

### **30. ArretTravail** (arrets_travail)
**Relations :**
- `employe` → **Employe** (FK)
- `arret_initial` → **ArretTravail** (FK auto-référence)

**Relations inverses :**
- ← **ArretTravail** (arret_initial) - prolongations

### **31. HoraireTravail** (horaires_travail)
**Relations :**
- Aucune FK sortante

**Relations inverses :**
- ← **AffectationHoraire** (horaire) - affectations

### **32. AffectationHoraire** (affectation_horaires)
**Relations :**
- `employe` → **Employe** (FK)
- `horaire` → **HoraireTravail** (FK)

---

## 💼 MODULE RECRUTEMENT (3 tables)

### **33. OffreEmploi** (offres_emploi)
**Relations :**
- `poste` → **Poste** (FK)
- `service` → **Service** (FK)
- `responsable_recrutement` → **Employe** (FK)

**Relations inverses :**
- ← **Candidature** (offre) - candidatures

### **34. Candidature** (candidatures)
**Relations :**
- `offre` → **OffreEmploi** (FK)

**Relations inverses :**
- ← **EntretienRecrutement** (candidature) - entretiens

### **35. EntretienRecrutement** (entretiens_recrutement)
**Relations :**
- `candidature` → **Candidature** (FK)

---

## 🎓 MODULE FORMATION (1 table)

### **36. FormationConfig** (formation_formationconfig)
**Relations :**
- Aucune FK sortante
- Table de configuration vide

---

## 📊 DIAGRAMME ENTITÉ-RELATION COMPLET

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SCHÉMA RELATIONNEL                           │
└─────────────────────────────────────────────────────────────────────┘

CORE
====
Societe (1)
    └─► Etablissement (1:N)
            ├─► Service (1:N)
            │       ├─► Service (auto-référence) - sous-services
            │       ├─► Poste (1:N)
            │       └─◄ Employe (responsable)
            └─► Employe (1:N)

ProfilUtilisateur (1)
    ├─► Utilisateur (1:N)
    └─► DroitAcces (1:N)

Utilisateur (1)
    ├─► LogActivite (1:N)
    ├─► ParametrePaie (1:1)
    ├─► PeriodePaie (1:N) - cloture
    ├─► HistoriquePaie (1:N)
    └─► Employe (1:N) - creation/modification

EMPLOYÉS
========
Employe ⭐ (CENTRALE)
    ├─► Etablissement (N:1)
    ├─► Service (N:1)
    ├─► Poste (N:1)
    ├─► Employe (auto-référence) - hiérarchie
    ├─► Utilisateur (N:1) - creation
    ├─► Utilisateur (N:1) - modification
    │
    └─► Relations inverses (25):
        ├─► ContratEmploye (1:N)
        ├─► FormationEmploye (1:N)
        ├─► CarriereEmploye (1:N)
        ├─► EvaluationEmploye (1:N) - évalué
        ├─► EvaluationEmploye (1:N) - évaluateur
        ├─► BulletinPaie (1:N)
        ├─► ElementSalaire (1:N)
        ├─► CumulPaie (1:N)
        ├─► HistoriquePaie (1:N)
        ├─► Pointage (1:N)
        ├─► Conge (1:N) - demandeur
        ├─► Conge (1:N) - approbateur
        ├─► Conge (1:N) - remplaçant
        ├─► SoldeConge (1:N)
        ├─► Absence (1:N)
        ├─► ArretTravail (1:N)
        ├─► AffectationHoraire (1:N)
        ├─► Service (1:N) - responsable
        └─► OffreEmploi (1:N) - responsable

PAIE
====
PeriodePaie (1)
    ├─► Utilisateur (N:1) - cloture
    ├─► BulletinPaie (1:N)
    └─► HistoriquePaie (1:N)

RubriquePaie (1)
    ├─► ElementSalaire (1:N)
    └─► LigneBulletin (1:N)

BulletinPaie (1)
    ├─► Employe (N:1)
    ├─► PeriodePaie (N:1)
    ├─► LigneBulletin (1:N)
    └─► HistoriquePaie (1:N)

ElementSalaire (1)
    ├─► Employe (N:1)
    └─► RubriquePaie (N:1)

CumulPaie (1)
    └─► Employe (N:1)

HistoriquePaie (1)
    ├─► BulletinPaie (N:1)
    ├─► PeriodePaie (N:1)
    ├─► Employe (N:1)
    └─► Utilisateur (N:1)

Tables de paramétrage:
- ParametrePaie
- Constante
- TrancheIRG
- Variable

TEMPS DE TRAVAIL
================
Conge (1)
    ├─► Employe (N:1) - demandeur
    ├─► Employe (N:1) - approbateur
    └─► Employe (N:1) - remplaçant

SoldeConge (1)
    └─► Employe (N:1)

Pointage (1)
    └─► Employe (N:1)

Absence (1)
    └─► Employe (N:1)

ArretTravail (1)
    ├─► Employe (N:1)
    └─► ArretTravail (auto-référence) - prolongations

HoraireTravail (1)
    └─► AffectationHoraire (1:N)

AffectationHoraire (1)
    ├─► Employe (N:1)
    └─► HoraireTravail (N:1)

JourFerie (1) - Indépendante

RECRUTEMENT
===========
OffreEmploi (1)
    ├─► Poste (N:1)
    ├─► Service (N:1)
    ├─► Employe (N:1) - responsable
    └─► Candidature (1:N)

Candidature (1)
    ├─► OffreEmploi (N:1)
    └─► EntretienRecrutement (1:N)

EntretienRecrutement (1)
    └─► Candidature (N:1)
```

---

## 🔑 CLÉS ÉTRANGÈRES PAR TABLE

### **Tables avec le plus de FK sortantes :**
1. **CarriereEmploye** : 7 FK
2. **Employe** : 6 FK
3. **HistoriquePaie** : 4 FK
4. **Conge** : 3 FK
5. **BulletinPaie** : 2 FK

### **Tables avec le plus de relations inverses :**
1. **Employe** : 25 relations inverses ⭐
2. **Utilisateur** : 7 relations inverses
3. **Service** : 6 relations inverses
4. **RubriquePaie** : 2 relations inverses
5. **PeriodePaie** : 2 relations inverses

---

## 📐 CONTRAINTES D'UNICITÉ

### **Contraintes Simples (unique=True)**
- `Employe.matricule`
- `Employe.num_cnss_individuel`
- `ContratEmploye.num_contrat`
- `Societe.nif`
- `Societe.num_cnss_employeur`
- `Etablissement.code_etablissement`
- `Service.code_service`
- `Poste.code_poste`
- `RubriquePaie.code_rubrique`
- `BulletinPaie.numero_bulletin`
- `HoraireTravail.code_horaire`
- `OffreEmploi.reference_offre`
- `Candidature.numero_candidature`
- `Constante.code`
- `Variable.code`

### **Contraintes Composées (unique_together)**
- `PeriodePaie`: (`annee`, `mois`)
- `BulletinPaie`: (`employe`, `periode`)
- `CumulPaie`: (`employe`, `annee`)
- `SoldeConge`: (`employe`, `annee`)
- `Pointage`: (`employe`, `date_pointage`)
- `DroitAcces`: (`profil`, `module`)

---

## 🔄 AUTO-RÉFÉRENCES (Relations récursives)

1. **Employe.superieur_hierarchique** → Employe
   - Permet la hiérarchie organisationnelle

2. **Service.service_parent** → Service
   - Permet l'arborescence des services

3. **ArretTravail.arret_initial** → ArretTravail
   - Permet le suivi des prolongations

---

## 📊 TYPES DE RELATIONS

### **One-to-Many (1:N)** - Majoritaires
- Employe → BulletinPaie
- PeriodePaie → BulletinPaie
- Employe → Pointage
- etc.

### **Many-to-Many (M:N)** - Via tables intermédiaires
- Employe ↔ RubriquePaie (via ElementSalaire)
- Employe ↔ HoraireTravail (via AffectationHoraire)
- Utilisateur ↔ Group (Django)
- Utilisateur ↔ Permission (Django)

### **One-to-One (1:1)** - Rares
- Aucune relation stricte 1:1
- Certaines relations N:1 peuvent être 1:1 en pratique (ex: ParametrePaie)

---

## 🎯 TABLES INDÉPENDANTES (Sans FK)

1. **JourFerie** - Calendrier des jours fériés
2. **Constante** - Paramètres de calcul
3. **TrancheIRG** - Barème IRG
4. **Variable** - Variables de paie
5. **Societe** - Racine de l'organisation
6. **ProfilUtilisateur** - Profils de sécurité
7. **FormationConfig** - Configuration

---

## 💡 POINTS CLÉS

### **1. Centralité de l'Employé**
- **25 relations** font de `Employe` la table centrale
- Tous les modules métier gravitent autour de l'employé

### **2. Traçabilité**
- Champs `utilisateur_creation` et `utilisateur_modification`
- Table `HistoriquePaie` pour l'audit
- Table `LogActivite` pour les actions utilisateurs

### **3. Flexibilité**
- Champs JSON dans `CumulPaie` et `HistoriquePaie`
- Relations optionnelles (null=True, blank=True)
- Soft delete via champs `actif`

### **4. Intégrité Référentielle**
- `CASCADE` : Suppression en cascade (ex: Employe → Pointage)
- `SET_NULL` : Préservation des données (ex: Employe → Service)
- `PROTECT` : Protection (non utilisé, préférence pour SET_NULL)

### **5. Performance**
- Index automatiques sur FK
- `unique_together` pour contraintes métier
- `related_name` pour requêtes inverses optimisées

---

## 📝 RECOMMANDATIONS

### **Optimisation des Requêtes**
```python
# Utiliser select_related pour FK
employes = Employe.objects.select_related(
    'service', 'poste', 'etablissement'
)

# Utiliser prefetch_related pour relations inverses
employes = Employe.objects.prefetch_related(
    'bulletins', 'pointages', 'conges'
)
```

### **Intégrité des Données**
- Toujours valider les contraintes unique_together
- Vérifier les dates (debut < fin)
- Valider les montants (> 0)

### **Sécurité**
- Filtrer par établissement/service selon les droits
- Logger toutes les modifications sensibles
- Vérifier les permissions avant modification

---

## ✅ CONCLUSION

Le schéma de base de données est **bien structuré** avec :

✅ **32 tables** organisées en 6 modules  
✅ **Table centrale** (Employe) bien identifiée  
✅ **Relations claires** et cohérentes  
✅ **Contraintes d'intégrité** bien définies  
✅ **Traçabilité** complète  
✅ **Flexibilité** pour évolutions futures  

**Le système est prêt pour la production !** 🎉

---

**Développé avec ❤️ pour la Guinée**  
*Architecture de données robuste et évolutive*
