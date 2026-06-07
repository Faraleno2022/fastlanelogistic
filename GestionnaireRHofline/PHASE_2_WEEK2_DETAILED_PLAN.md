# 📋 PHASE 2 WEEK 2 - AUDIT & COMPLIANCE

**Status**: Planning detailed implementation
**Date**: 2026-01-20
**Duration**: 40-50 hours
**Modules**: TVA Integration + Audit Module

---

## 🎯 OBJECTIFS WEEK 2

### 1️⃣ TVA Module - COMPLETION (16-20h)

```
Week 2.1-2.2: TVA Integration (Vues + Formulaires + Templates)

✅ Views (6-8h):
   ├─ DeclarationListView (CBV)
   │  ├─ Filtrage par statut
   │  ├─ Filtrage par période
   │  ├─ Pagination
   │  └─ Bulk actions
   │
   ├─ DeclarationDetailView
   │  ├─ Affichage déclaration
   │  ├─ Lignes inline
   │  ├─ Montants calculés
   │  └─ Actions (valider, déposer)
   │
   ├─ DeclarationCreateView
   │  ├─ Créer nouvelle déclaration
   │  ├─ Sélection période/régime
   │  └─ Redirection vers edit
   │
   ├─ DeclarationEditView
   │  ├─ Edit déclaration + lignes
   │  ├─ Formset pour lignes
   │  └─ Validation complète
   │
   ├─ DeclarationValidateView
   │  ├─ Confirmation avant validation
   │  ├─ Recalcul montants
   │  └─ Changement statut
   │
   ├─ DeclarationDepotView
   │  ├─ Confirmation avant dépôt
   │  ├─ Génération numéro
   │  ├─ Export PDF optionnel
   │  └─ Email notification
   │
   ├─ LigneDeclarationCreateView
   │  ├─ Ajouter ligne
   │  ├─ Auto-calcul TVA
   │  └─ Validation taux
   │
   └─ RegimeTVAListView
      ├─ Liste régimes
      ├─ Filtrage actif
      └─ CRUD permissions

✅ Formulaires (4-5h):
   ├─ DeclarationForm
   │  ├─ Fields: periode_debut, periode_fin, regime_tva
   │  ├─ Validation: dates, régime actif
   │  ├─ Widgets: DatePicker, Select
   │  └─ Clean methods
   │
   ├─ LigneDeclarationForm
   │  ├─ Fields: description, taux, montant_ht
   │  ├─ Auto-calcul: montant_tva
   │  ├─ Validation: montant > 0, taux existe
   │  └─ Widget personnalisé montants
   │
   ├─ LigneDeclarationFormSet
   │  ├─ Inline editing de lignes
   │  ├─ Add/remove lignes
   │  ├─ Validation croisée
   │  └─ Widgets personnalisés
   │
   ├─ DeclarationFilterForm
   │  ├─ Filtrage liste
   │  ├─ Par statut, période, régime
   │  ├─ Recherche text
   │  └─ Export options
   │
   ├─ TauxTVAForm
   │  ├─ Admin form pour taux
   │  ├─ Validation: 0-100%
   │  └─ Nature applicabilité
   │
   └─ RegimeTVAForm
      ├─ Admin form régime
      ├─ Validation seuil CA
      └─ Taux défauts

✅ Templates (5-7h):
   ├─ declaration_list.html (150 L)
   │  ├─ Table responsive
   │  ├─ Status badge
   │  ├─ Actions: View, Edit, Delete
   │  ├─ Bulk select + actions
   │  ├─ Pagination
   │  ├─ Filtres sidebar
   │  ├─ Responsive responsive
   │  └─ Export buttons
   │
   ├─ declaration_detail.html (200 L)
   │  ├─ En-tête déclaration
   │  ├─ Infos période/régime
   │  ├─ Table lignes
   │  ├─ Montants résumé
   │  ├─ Status timeline
   │  ├─ Actions boutons
   │  ├─ Audit trail
   │  └─ PDF export
   │
   ├─ declaration_form.html (180 L)
   │  ├─ Form creation/edit
   │  ├─ Period selector
   │  ├─ Regime selection
   │  ├─ Formset lignes inline
   │  ├─ Add ligne dynamique
   │  ├─ Auto-calc montants
   │  ├─ Validation messages
   │  └─ Save/Cancel buttons
   │
   ├─ declaration_validate.html (120 L)
   │  ├─ Confirmation page
   │  ├─ Récapitulatif complet
   │  ├─ Montants finaux
   │  ├─ Confirm/Cancel buttons
   │  └─ Warning messages
   │
   ├─ lignes_table_block.html (80 L)
   │  ├─ Réutilisable
   │  ├─ Table lignes
   │  ├─ Montants avec couleurs
   │  ├─ Actions (edit/delete)
   │  └─ Subtotals
   │
   └─ regime_list.html (100 L)
      ├─ Admin list
      ├─ Table régimes
      ├─ Actions CRUD
      └─ Status indicator

Status: READY FOR PHASE 2 WEEK 2
```

---

### 2️⃣ AUDIT Module - NEW (20-30h)

```
Week 2.3-2.5: Audit & Compliance Module

✅ Modèles (4-6h):
   ├─ PisteAudit (EXISTS - enhance)
   │  ├─ id (UUID)
   │  ├─ utilisateur (FK User)
   │  ├─ action (CREATE|UPDATE|DELETE|VIEW)
   │  ├─ module (module_name)
   │  ├─ type_objet (model_name)
   │  ├─ id_objet (object_uuid)
   │  ├─ valeurs_avant (JSON)
   │  ├─ valeurs_apres (JSON)
   │  ├─ details (JSONField)
   │  ├─ adresse_ip (CharField)
   │  ├─ user_agent (TextField)
   │  ├─ date_action (DateTimeField)
   │  └─ statut (valide|supprimé)
   │
   ├─ RapportAudit (NEW - 15 fields)
   │  ├─ id (UUID)
   │  ├─ entreprise (FK)
   │  ├─ titre (CharField)
   │  ├─ type (COMPLIANCE|SECURITY|OPERATIONAL)
   │  ├─ periode_debut/fin (DateField)
   │  ├─ statut (DRAFT|FINALIZED)
   │  ├─ contenu (JSONField - serialized data)
   │  ├─ nombre_actions (IntegerField)
   │  ├─ nombre_erreurs (IntegerField)
   │  ├─ nombre_avertissements (IntegerField)
   │  ├─ nombre_changements (IntegerField)
   │  ├─ utilisateur_creation (FK User)
   │  ├─ date_creation (auto_now_add)
   │  └─ date_modification (auto_now)
   │
   ├─ AlerteNonConformite (NEW - 12 fields)
   │  ├─ id (UUID)
   │  ├─ entreprise (FK)
   │  ├─ titre (CharField)
   │  ├─ description (TextField)
   │  ├─ severite (LOW|MEDIUM|HIGH|CRITICAL)
   │  ├─ type_regle (FISCAL|COMPTABLE|SOCIAL|AUTRE)
   │  ├─ statut (ACTIF|RESOLU|IGNORER)
   │  ├─ date_detection (DateTimeField)
   │  ├─ date_resolution (DateTimeField, nullable)
   │  ├─ utilisateur_assignee (FK User)
   │  ├─ notes (TextField)
   │  └─ piste_audit (FK PisteAudit)
   │
   ├─ ReglesConformite (NEW - 15 fields)
   │  ├─ id (UUID)
   │  ├─ code (CharField unique)
   │  ├─ libelle (CharField)
   │  ├─ description (TextField)
   │  ├─ domaine (FISCAL|COMPTABLE|SOCIAL)
   │  ├─ severite (LOW|MEDIUM|HIGH|CRITICAL)
   │  ├─ regle_sql (TextField - query à checker)
   │  ├─ message_erreur (TextField)
   │  ├─ action_recommandee (TextField)
   │  ├─ lien_documentation (URLField)
   │  ├─ actif (BooleanField)
   │  ├─ date_debut_validite (DateField)
   │  ├─ date_fin_validite (DateField nullable)
   │  ├─ utilisateur_creation (FK User)
   │  └─ date_creation (auto_now_add)
   │
   └─ HistoriqueModification (OPTIONAL)
      ├─ id (UUID)
      ├─ piste_audit (FK)
      ├─ champ_modifie (CharField)
      ├─ valeur_ancienne (JSONField)
      ├─ valeur_nouvelle (JSONField)
      └─ type_changement (ADDED|MODIFIED|DELETED)

Migration: 0004_audit_compliance_models.py

✅ Services (6-8h):
   ├─ AuditService (hérité BaseComptaService)
   │  ├─ generer_rapport_audit(periode, module)
   │  ├─ verifier_conformite(regles, donnees)
   │  ├─ creer_alerte(regle, details)
   │  ├─ lister_modifications(periode, type_objet)
   │  ├─ comparer_versions(ancien, nouveau)
   │  ├─ exporter_rapport(format: PDF|Excel|JSON)
   │  ├─ archiver_rapport(rapport)
   │  └─ nettoyer_anciennes_pistes(jours: int)
   │
   ├─ ConformiteService (hérité BaseComptaService)
   │  ├─ evaluer_conformite(entreprise)
   │  ├─ checker_regle(regle, data)
   │  ├─ generer_score_conformite()
   │  ├─ lister_violations()
   │  ├─ resoudre_alerte(alerte)
   │  ├─ generer_rapport_conformite()
   │  └─ auto_check_conformite()
   │
   └─ HistoriqueModificationService (hérité BaseComptaService)
      ├─ enregistrer_modification(piste_audit, champ, ancien, nouveau)
      ├─ comparer_objects(obj1, obj2)
      ├─ creer_diff_report(obj1, obj2)
      ├─ lister_changements(type_objet, id_objet)
      └─ generer_timeline()

✅ Vues (6-8h):
   ├─ AuditListView
   │  ├─ Liste pistes audit
   │  ├─ Filtrage: utilisateur, action, module
   │  ├─ Pagination
   │  ├─ Recherche texte
   │  └─ Export CSV
   │
   ├─ AuditDetailView
   │  ├─ Détail action audit
   │  ├─ Valeurs avant/après
   │  ├─ IP et User-Agent
   │  ├─ Modifications dans diff view
   │  └─ Related pistes
   │
   ├─ RapportAuditListView
   │  ├─ Liste rapports
   │  ├─ Filtrage période
   │  ├─ Type rapport
   │  └─ Actions (view, delete)
   │
   ├─ RapportAuditDetailView
   │  ├─ Rapport complet
   │  ├─ Statistiques
   │  ├─ Graphiques données
   │  ├─ Actions recommandées
   │  ├─ Export PDF/Excel
   │  └─ Historique versions
   │
   ├─ ConformiteReportView
   │  ├─ Score conformité global
   │  ├─ Par domaine (Fiscal, Comptable, Social)
   │  ├─ Graphiques tendance
   │  ├─ Violations actuelles
   │  └─ Timeline corrections
   │
   ├─ AlertesListView
   │  ├─ Liste alertes
   │  ├─ Filtrage severité
   │  ├─ Assignation
   │  ├─ Status change
   │  └─ Bulk resolution
   │
   └─ ReglesConformiteListView
      ├─ Admin liste regles
      ├─ CRUD regles
      ├─ Activation/désactivation
      └─ Test regle

✅ Formulaires (3-4h):
   ├─ RapportAuditForm
   ├─ AlerteResolutionForm
   ├─ ReglesConformiteForm
   ├─ AuditFilterForm
   └─ ConformiteFilterForm

✅ Templates (4-5h):
   ├─ audit_list.html (150 L)
   ├─ audit_detail.html (180 L)
   ├─ rapport_list.html (140 L)
   ├─ rapport_detail.html (220 L)
   ├─ conformite_report.html (250 L)
   ├─ alertes_list.html (160 L)
   ├─ alerte_detail.html (140 L)
   └─ regles_admin.html (120 L)

Status: READY FOR IMPLEMENTATION
```

---

## 📊 DÉTAIL SEMAINE 2

```
LUNDI (Jour 1-2):
├─ Morning: TVA Views creation (DeclarationList/DetailView)
├─ Afternoon: DeclarationCreate/EditView
└─ Evening: Tests vues TVA

MARDI (Jour 2-3):
├─ Morning: TVA Forms (DeclarationForm, FormSet)
├─ Afternoon: TVA Templates (list, detail, form)
└─ Evening: Template tests + responsive

MERCREDI (Jour 3-4):
├─ Morning: TVA Integration (URLs, Permissions)
├─ Afternoon: E2E Tests TVA complet
└─ Evening: TVA Module COMPLETE ✅

JEUDI (Jour 4-5):
├─ Morning: Audit Models (4 nouveaux modèles)
├─ Afternoon: Migration file + AuditService
└─ Evening: ConformiteService

VENDREDI (Jour 5):
├─ Morning: Audit Views (List, Detail, Reports)
├─ Afternoon: Audit Templates
├─ Evening: Tests + Code Review
└─ Deploy ready ✅

WEEKEND (Review):
├─ Saturday: QA + Bug fixes
└─ Sunday: Documentation + Training material
```

---

## 🔧 OUTILS & DÉPENDANCES

```
Python packages à ajouter:
├─ django-filter        (advanced filtering)
├─ django-crispy-forms  (form rendering)
├─ reportlab           (PDF generation)
├─ openpyxl            (Excel export)
├─ django-cors-headers (API CORS)
└─ Pillow              (image handling)

Frontend:
├─ Bootstrap 5.3
├─ Chart.js (graphiques)
├─ DataTables.js (tableaux)
├─ Select2 (dropdowns)
├─ DatePicker.js
└─ Moment.js (dates)
```

---

## 📈 MÉTRIQUES SUCCESS

```
Cible:
├─ TVA: 4 vues + 3 formulaires + 5 templates
├─ Audit: 6 vues + 5 formulaires + 8 templates
├─ Tests: 50+ test methods
├─ Coverage: 85%+ overall
├─ Performance: < 2s pour chaque vue
└─ Bugs: 0 critical, < 5 minor

Validation:
├─ ✅ Toutes migrations passent
├─ ✅ Tous tests passent
├─ ✅ Code review approuvé
├─ ✅ Security scan OK
└─ ✅ Performance metrics OK
```

---

## 📋 NEXT: PHASE 3 PREVIEW

Après Phase 2 Week 2:
```
Phase 3 (PAIE):
├─ Module Paie intégrée (50-60h)
├─ Module Temps & Absences (40-50h)
├─ Module Formations (40-50h)
└─ Total: 150-160 heures
```

---

Generated: 2026-01-20 | Phase 2 Week 2 Planning Complete
