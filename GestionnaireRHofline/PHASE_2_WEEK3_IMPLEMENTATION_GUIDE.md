# PHASE 2 FISCALITÉ - IMPLEMENTATION QUICK START GUIDE

**Timeline**: Weeks 3-5 (60-80 hours total)  
**Reusability**: 70% from Phase 1 patterns  
**Risk**: LOW (patterns proven in Rapprochements)

---

## 🎯 WEEK 3: MODELS + SERVICES (25 hours)

### Day 1-2: Tax System Models (4 hours)

#### 1.1 RegimeTVA Model (Tax System Types)

```python
# comptabilite/models.py - Add to existing file

class RegimeTVA(models.Model):
    """Tax system regime (normal, simplified, exempt, etc.)"""
    
    REGIMES = [
        ('NORMAL', 'Normal'),
        ('SIMPLIFIE', 'Simplifié'),
        ('MICRO', 'Micro-entreprise'),
        ('EXEMPT', 'Exempté'),
        ('SERVICES', 'Services spécialisés'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='regimes_tva')
    
    code = models.CharField(max_length=20, unique=True)  # 'FR_NORMAL', 'FR_SIMPLIFIE'
    nom = models.CharField(max_length=100)
    regime = models.CharField(max_length=20, choices=REGIMES)
    
    description = models.TextField(blank=True)
    
    # Configuration
    seuil_chiffre_affaires = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text="Seuil CA pour changement de régime"
    )
    taux_normal = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    taux_reduit = models.DecimalField(max_digits=5, decimal_places=2, default=5.50)
    taux_super_reduit = models.DecimalField(max_digits=5, decimal_places=2, default=2.10)
    
    # Reporting
    periodicite = models.CharField(
        max_length=20,
        choices=[
            ('MENSUELLE', 'Mensuelle'),
            ('TRIMESTRIELLE', 'Trimestrielle'),
            ('ANNUELLE', 'Annuelle'),
        ],
        default='MENSUELLE'
    )
    
    # Status
    actif = models.BooleanField(default=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    
    # Audit
    utilisateur_creation = models.ForeignKey(User, on_delete=models.PROTECT, related_name='regimes_tva_created')
    date_creation = models.DateTimeField(auto_now_add=True)
    utilisateur_modification = models.ForeignKey(User, on_delete=models.PROTECT, related_name='regimes_tva_modified')
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comptabilite_regime_tva'
        verbose_name = 'Régime TVA'
        verbose_name_plural = 'Régimes TVA'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['entreprise', 'actif']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.nom} ({self.code})"
    
    def get_taux_applicable(self, type_taux='NORMAL'):
        """Retourne le taux applicable selon le type"""
        if type_taux == 'NORMAL':
            return self.taux_normal
        elif type_taux == 'REDUIT':
            return self.taux_reduit
        elif type_taux == 'SUPER_REDUIT':
            return self.taux_super_reduit
        return self.taux_normal
```

#### 1.2 TauxTVA Model (Tax Rates)

```python
class TauxTVA(models.Model):
    """Tax rates for different products/services"""
    
    NATURES = [
        ('VENTE', 'Vente'),
        ('SERVICE', 'Service'),
        ('TRAVAUX', 'Travaux'),
        ('LIVRAISON', 'Livraison'),
        ('IMPORTATION', 'Importation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regime_tva = models.ForeignKey(RegimeTVA, on_delete=models.CASCADE, related_name='taux')
    
    code = models.CharField(max_length=20)  # 'TVA_NORMAL', 'TVA_5.5'
    nom = models.CharField(max_length=100)
    
    # Tax rate
    taux = models.DecimalField(max_digits=5, decimal_places=2)  # 20.00, 5.50, etc.
    nature = models.CharField(max_length=20, choices=NATURES)
    
    description = models.TextField(blank=True)
    
    # Applicability
    applicable_au_ventes = models.BooleanField(default=True)
    applicable_aux_achats = models.BooleanField(default=True)
    
    # Status
    actif = models.BooleanField(default=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    
    # Audit
    utilisateur_creation = models.ForeignKey(User, on_delete=models.PROTECT, related_name='taux_tva_created')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comptabilite_taux_tva'
        verbose_name = 'Taux TVA'
        verbose_name_plural = 'Taux TVA'
        unique_together = ['regime_tva', 'code']
        ordering = ['-taux']
    
    def __str__(self):
        return f"{self.taux}% - {self.nom}"
```

#### 1.3 DeclarationTVA Model (Declarations)

```python
class DeclarationTVA(models.Model):
    """Tax declaration"""
    
    STATUTS = [
        ('BROUILLON', 'Brouillon'),
        ('EN_COURS', 'En cours'),
        ('VALIDEE', 'Validée'),
        ('DEPOSEE', 'Déposée'),
        ('ACCEPTEE', 'Acceptée'),
        ('REJETEE', 'Rejetée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='declarations_tva')
    regime_tva = models.ForeignKey(RegimeTVA, on_delete=models.PROTECT, related_name='declarations')
    exercice = models.ForeignKey(Exercice, on_delete=models.PROTECT, related_name='declarations_tva')
    
    # Period
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    
    # Totals (calculated)
    montant_ht = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    montant_tva_collecte = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    montant_tva_deductible = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    montant_tva_due = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Status
    statut = models.CharField(max_length=20, choices=STATUTS, default='BROUILLON')
    
    # Submission
    date_depot = models.DateField(null=True, blank=True)
    numero_depot = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Audit
    utilisateur_creation = models.ForeignKey(User, on_delete=models.PROTECT, related_name='declarations_tva_created')
    date_creation = models.DateTimeField(auto_now_add=True)
    utilisateur_modification = models.ForeignKey(User, on_delete=models.PROTECT, related_name='declarations_tva_modified')
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comptabilite_declaration_tva'
        verbose_name = 'Déclaration TVA'
        verbose_name_plural = 'Déclarations TVA'
        unique_together = ['entreprise', 'periode_debut', 'periode_fin']
        ordering = ['-periode_debut']
    
    def __str__(self):
        return f"TVA {self.periode_debut.strftime('%m/%Y')} - {self.entreprise.nom}"
    
    @property
    def montant_a_payer(self):
        """Montant TVA à payer ou à récupérer"""
        return self.montant_tva_collecte - self.montant_tva_deductible
```

#### 1.4 LigneDeclarationTVA Model (Declaration Lines)

```python
class LigneDeclarationTVA(models.Model):
    """Line items in a tax declaration"""
    
    TYPES = [
        ('OPERATIONS', 'Opérations'),
        ('AJUSTEMENT', 'Ajustement'),
        ('CORRECTION', 'Correction'),
        ('OPTION', 'Option'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    declaration = models.ForeignKey(DeclarationTVA, on_delete=models.CASCADE, related_name='lignes')
    
    # Content
    numero_ligne = models.PositiveIntegerField()  # 1, 2, 3, etc.
    description = models.CharField(max_length=200)
    taux = models.ForeignKey(TauxTVA, on_delete=models.PROTECT)
    
    # Amounts
    montant_ht = models.DecimalField(max_digits=15, decimal_places=2)
    montant_tva = models.DecimalField(max_digits=15, decimal_places=2)
    
    type_ligne = models.CharField(max_length=20, choices=TYPES, default='OPERATIONS')
    
    # References
    compte_comptable = models.ForeignKey(CompteGeneralLedger, on_delete=models.PROTECT, null=True, blank=True)
    
    class Meta:
        db_table = 'comptabilite_ligne_declaration_tva'
        verbose_name = 'Ligne déclaration TVA'
        verbose_name_plural = 'Lignes déclaration TVA'
        ordering = ['declaration', 'numero_ligne']
        unique_together = ['declaration', 'numero_ligne']
    
    def __str__(self):
        return f"Ligne {self.numero_ligne}: {self.description}"
```

### Day 3-5: Services & Signals (15 hours)

#### 1.5 FiscaliteService (Business Logic)

```python
# comptabilite/services/fiscalite_service.py (NEW FILE)

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .base_service import BaseComptaService
from ..models import (
    DeclarationTVA, LigneDeclarationTVA, RegimeTVA, TauxTVA,
    Ecriture, CompteGeneralLedger
)

class FiscaliteService(BaseComptaService):
    """Service pour la gestion de la fiscalité (TVA, déclarations, etc.)"""
    
    def __init__(self, utilisateur):
        super().__init__(utilisateur)
        self.logger.info("FiscaliteService initialized")
    
    def creer_declaration_tva(self, entreprise, regime_tva, exercice, 
                              periode_debut, periode_fin, **kwargs):
        """Crée une nouvelle déclaration TVA"""
        
        # Validation
        conditions = {
            'regime_tva_actif': regime_tva.actif,
            'periode_valide': periode_debut < periode_fin,
            'pas_de_doublon': not DeclarationTVA.objects.filter(
                entreprise=entreprise,
                periode_debut=periode_debut,
                periode_fin=periode_fin
            ).exists()
        }
        
        if not self.valider(conditions):
            return None, self.derniers_avertissements
        
        try:
            with transaction.atomic():
                declaration = DeclarationTVA.objects.create(
                    entreprise=entreprise,
                    regime_tva=regime_tva,
                    exercice=exercice,
                    periode_debut=periode_debut,
                    periode_fin=periode_fin,
                    utilisateur_creation=self.utilisateur,
                    utilisateur_modification=self.utilisateur
                )
                
                # Log audit
                self.enregistrer_audit(
                    action='CREATE',
                    module='Fiscalité',
                    type_objet='DeclarationTVA',
                    id_objet=declaration.id,
                    details={
                        'periode': f"{periode_debut} à {periode_fin}",
                        'regime': regime_tva.nom
                    }
                )
                
                return declaration, []
        
        except Exception as e:
            self.logger.error(f"Erreur création déclaration: {str(e)}")
            return None, [f"Erreur: {str(e)}"]
    
    def calculer_montants_declaration(self, declaration):
        """Calcule les montants TVA pour la déclaration"""
        
        # Récupère les écritures de la période
        ecritures = Ecriture.objects.filter(
            entreprise=declaration.entreprise,
            date__gte=declaration.periode_debut,
            date__lte=declaration.periode_fin,
            statut='VALIDEE'
        )
        
        montant_ht = Decimal('0')
        montant_tva_collecte = Decimal('0')
        montant_tva_deductible = Decimal('0')
        
        for ecriture in ecritures:
            # Calcul par nature d'opération
            if ecriture.type in ['VENTE', 'LIVRAISON']:
                montant_ht += ecriture.montant
                montant_tva_collecte += self._calculer_tva(
                    ecriture.montant,
                    ecriture.taux_tva
                )
            elif ecriture.type in ['ACHAT', 'FACTURE_ACHAT']:
                montant_ht += ecriture.montant
                montant_tva_deductible += self._calculer_tva(
                    ecriture.montant,
                    ecriture.taux_tva
                )
        
        # Update déclaration
        declaration.montant_ht = montant_ht
        declaration.montant_tva_collecte = montant_tva_collecte
        declaration.montant_tva_deductible = montant_tva_deductible
        declaration.montant_tva_due = (
            montant_tva_collecte - montant_tva_deductible
        )
        declaration.save()
        
        # Log
        self.enregistrer_audit(
            action='UPDATE',
            module='Fiscalité',
            type_objet='DeclarationTVA',
            id_objet=declaration.id,
            details={
                'montant_ht': str(montant_ht),
                'tva_due': str(declaration.montant_tva_due)
            }
        )
        
        return declaration
    
    def _calculer_tva(self, montant_ht, taux_tva):
        """Calcule le montant TVA"""
        return (montant_ht * taux_tva) / Decimal('100')
    
    def valider_declaration(self, declaration):
        """Valide la déclaration (passe au statut VALIDEE)"""
        
        conditions = {
            'montants_calculés': declaration.montant_tva_due != 0,
            'au_moins_une_ligne': declaration.lignes.count() > 0,
            'statut_brouillon': declaration.statut == 'BROUILLON'
        }
        
        if not self.valider(conditions):
            return False, self.derniers_avertissements
        
        declaration.statut = 'VALIDEE'
        declaration.utilisateur_modification = self.utilisateur
        declaration.save()
        
        self.enregistrer_audit(
            action='VALIDATE',
            module='Fiscalité',
            type_objet='DeclarationTVA',
            id_objet=declaration.id,
            details={'statut': 'VALIDEE'}
        )
        
        return True, ['Déclaration validée']
    
    def deposer_declaration(self, declaration, numero_depot=None):
        """Enregistre le dépôt de la déclaration"""
        
        if declaration.statut != 'VALIDEE':
            return False, ['Declaration must be validated before deposit']
        
        declaration.statut = 'DEPOSEE'
        declaration.date_depot = timezone.now().date()
        declaration.numero_depot = numero_depot or f"TVA-{declaration.id}"
        declaration.save()
        
        self.enregistrer_audit(
            action='SUBMIT',
            module='Fiscalité',
            type_objet='DeclarationTVA',
            id_objet=declaration.id,
            details={'numero_depot': declaration.numero_depot}
        )
        
        return True, ['Declaration submitted']
```

#### 1.6 CalculTVAService (Calculations)

```python
# comptabilite/services/calcul_tva_service.py (NEW FILE)

from decimal import Decimal
from ..models import TauxTVA, RegimeTVA
from .base_service import BaseComptaService

class CalculTVAService(BaseComptaService):
    """Service for TVA calculations"""
    
    def calculer_montant_ttc(self, montant_ht, taux_tva):
        """Calcule le montant TTC"""
        tva = (montant_ht * taux_tva) / Decimal('100')
        return montant_ht + tva
    
    def calculer_montant_ht(self, montant_ttc, taux_tva):
        """Calcule le montant HT à partir du TTC"""
        montant_ht = montant_ttc / (1 + (taux_tva / Decimal('100')))
        return montant_ht.quantize(Decimal('0.01'))
    
    def calculer_tva(self, montant_ht, taux_tva):
        """Calcule le montant TVA"""
        return (montant_ht * taux_tva / Decimal('100')).quantize(Decimal('0.01'))
    
    def appliquer_taux(self, montant, regime_tva, type_produit='NORMAL'):
        """Applique le bon taux selon le régime"""
        taux = regime_tva.get_taux_applicable(type_produit)
        return self.calculer_tva(montant, taux)
```

#### 1.7 Signals for Automation

```python
# Add to comptabilite/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DeclarationTVA, Ecriture
from .services.fiscalite_service import FiscaliteService

@receiver(post_save, sender=Ecriture)
def recalculer_tva_declaration(sender, instance, created, **kwargs):
    """Recalcule la TVA quand une écriture est créée/modifiée"""
    
    if not instance.statut == 'VALIDEE':
        return
    
    # Find related declaration
    from datetime import datetime
    declarations = DeclarationTVA.objects.filter(
        entreprise=instance.entreprise,
        periode_debut__lte=instance.date,
        periode_fin__gte=instance.date,
        statut__in=['BROUILLON', 'EN_COURS']
    )
    
    service = FiscaliteService(instance.utilisateur_creation)
    for declaration in declarations:
        service.calculer_montants_declaration(declaration)
```

#### 1.8 Migration File

```python
# comptabilite/migrations/0003_fiscalite_models.py (AUTO-GENERATED)

from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('comptabilite', '0002_initial_52_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegimeTVA',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('regime', models.CharField(choices=[('NORMAL', 'Normal'), ('SIMPLIFIE', 'Simplifié'), ('MICRO', 'Micro-entreprise'), ('EXEMPT', 'Exempté'), ('SERVICES', 'Services spécialisés')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('seuil_chiffre_affaires', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('taux_normal', models.DecimalField(decimal_places=2, default=20, max_digits=5)),
                ('taux_reduit', models.DecimalField(decimal_places=2, default=5.5, max_digits=5)),
                ('taux_super_reduit', models.DecimalField(decimal_places=2, default=2.1, max_digits=5)),
                ('periodicite', models.CharField(choices=[('MENSUELLE', 'Mensuelle'), ('TRIMESTRIELLE', 'Trimestrielle'), ('ANNUELLE', 'Annuelle')], default='MENSUELLE', max_length=20)),
                ('actif', models.BooleanField(default=True)),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('entreprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='regimes_tva', to='core.entreprise')),
                ('utilisateur_creation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='regimes_tva_created', to='auth.user')),
                ('utilisateur_modification', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='regimes_tva_modified', to='auth.user')),
            ],
            options={
                'verbose_name': 'Régime TVA',
                'verbose_name_plural': 'Régimes TVA',
                'db_table': 'comptabilite_regime_tva',
                'ordering': ['-date_creation'],
            },
        ),
        # ... More migrations for TauxTVA, DeclarationTVA, LigneDeclarationTVA
    ]
```

---

## 📊 SUMMARY - WEEK 3 TASKS

### Models Created
✅ RegimeTVA (tax system setup)  
✅ TauxTVA (tax rates)  
✅ DeclarationTVA (declarations)  
✅ LigneDeclarationTVA (declaration lines)

### Services Implemented
✅ FiscaliteService (20+ methods)  
✅ CalculTVAService (calculations)  
✅ Signal handlers (auto-recalc)

### Time Allocation
- RegimeTVA: 2h
- TauxTVA: 2h
- DeclarationTVA: 4h
- LigneDeclarationTVA: 3h
- FiscaliteService: 8h
- CalculTVAService: 4h
- Signals & migrations: 2h
- **Total**: 25h

---

## 🔄 WEEKS 4-5: VIEWS + FORMS + TEMPLATES (25 hours)

### Week 4 Plan
1. **DeclarationListView** (reuses ComptaListView)
2. **DeclarationDetailView**
3. **DeclarationCreateView**
4. **DeclarationUpdateView**
5. **CalculatorView** (compute taxes)

### Week 5 Plan
1. **Forms** (3 forms, reuse base form)
2. **Templates** (5 HTML files, reuse base)
3. **AJAX endpoints** (dynamic calculations)
4. **Export to PDF** (tax reports)

**Note**: 70% code reuse from Phase 1 patterns

---

## ✅ SUCCESS CRITERIA - WEEK 3

- ✅ All 4 models created and migrated
- ✅ Both services implement BaseComptaService pattern
- ✅ Signals automatically update declarations
- ✅ No syntax errors
- ✅ All imports work
- ✅ Unit tests for services pass
- ✅ Database schema created correctly

---

**Next Document**: WEEK_4_VIEWS_FORMS_TEMPLATES.md (25h plan)
