"""
Module Gestion de Stock.

Entités : Dépôt, Catégorie, Fournisseur, Demandeur, Article,
Entrée, Sortie, Inventaire (+lignes), Commande d'achat (+lignes),
Mouvement (traçabilité). Multi-tenant (rattaché à une entreprise).

Le stock de chaque article (quantite_stock) est mis à jour
automatiquement à chaque entrée/sortie, et chaque mouvement est tracé.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone


class StockBase(models.Model):
    entreprise = models.ForeignKey('core.Entreprise', on_delete=models.CASCADE, related_name='%(class)ss')
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ------------------------------------------------------------------
# Référentiels
# ------------------------------------------------------------------
class Depot(StockBase):
    TYPES = [('principal', 'Magasin principal'), ('secondaire', 'Dépôt secondaire'),
             ('vehicule', 'Véhicule (stock mobile)'), ('atelier', 'Atelier')]
    nom = models.CharField(max_length=150)
    type_depot = models.CharField(max_length=15, choices=TYPES, default='principal')
    localisation = models.CharField(max_length=200, blank=True)
    responsable = models.CharField(max_length=150, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Dépôt'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class CategorieArticle(StockBase):
    nom = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Fournisseur(StockBase):
    nom = models.CharField(max_length=200)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    articles_fournis = models.CharField(max_length=255, blank=True, help_text='Principaux articles')
    delai_livraison_jours = models.PositiveIntegerField(default=0, verbose_name='Délai livraison (jours)')
    dette = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Dette fournisseur (GNF)')

    class Meta:
        verbose_name = 'Fournisseur'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Demandeur(StockBase):
    TYPES = [('client', 'Client externe'), ('service', 'Service interne'),
             ('atelier', 'Atelier'), ('chantier', 'Chantier'), ('departement', 'Département')]
    nom = models.CharField(max_length=200)
    type_demandeur = models.CharField(max_length=15, choices=TYPES, default='service')
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        verbose_name = 'Demandeur'
        ordering = ['nom']

    def __str__(self):
        return self.nom


# ------------------------------------------------------------------
# Article
# ------------------------------------------------------------------
class Article(StockBase):
    UNITES = [('piece', 'Pièce'), ('carton', 'Carton'), ('kg', 'Kg'),
              ('litre', 'Litre'), ('metre', 'Mètre'), ('lot', 'Lot')]
    code = models.CharField(max_length=30, blank=True, verbose_name='Code article')
    designation = models.CharField(max_length=200)
    categorie = models.ForeignKey(CategorieArticle, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    depot = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    unite = models.CharField(max_length=10, choices=UNITES, default='piece')
    prix_achat = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Prix d'achat (GNF)")
    prix_vente = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, verbose_name='Prix de vente (GNF)')
    stock_min = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Seuil d'alerte")
    stock_max = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Stock maximum')
    quantite_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Stock actuel')
    emplacement = models.CharField(max_length=120, blank=True)
    date_expiration = models.DateField(null=True, blank=True, verbose_name='Date péremption')

    class Meta:
        verbose_name = 'Article'
        ordering = ['designation']

    def __str__(self):
        return f"{self.code or '—'} · {self.designation}"

    def save(self, *args, **kwargs):
        if not self.code and self.entreprise_id:
            n = Article.objects.filter(entreprise=self.entreprise).count() + 1
            self.code = f"STK-{n:04d}"
        super().save(*args, **kwargs)

    @property
    def valeur_stock(self):
        return (self.quantite_stock or 0) * (self.prix_achat or 0)

    @property
    def statut_stock(self):
        if self.quantite_stock <= 0:
            return 'rupture'
        if self.stock_min and self.quantite_stock <= self.stock_min:
            return 'alerte'
        if self.stock_max and self.quantite_stock >= self.stock_max:
            return 'surstock'
        return 'ok'


# ------------------------------------------------------------------
# Mouvements (entrées / sorties) + traçabilité
# ------------------------------------------------------------------
class MouvementStock(StockBase):
    """Journal de traçabilité (qui, quand, avant/après, motif)."""
    TYPES = [('entree', 'Entrée'), ('sortie', 'Sortie'), ('ajustement', 'Ajustement')]
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=12, choices=TYPES)
    quantite = models.DecimalField(max_digits=12, decimal_places=2)
    qte_avant = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qte_apres = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    motif = models.CharField(max_length=255, blank=True)
    document = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Mouvement'
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.get_type_mouvement_display()} · {self.article} · {self.quantite}"


def _appliquer_mouvement(instance, sens, motif, document):
    """Met à jour le stock de l'article et journalise (sens = +1 / -1)."""
    if not instance.article_id:
        return
    art = instance.article
    # delta par rapport à l'ancienne valeur (gère l'édition)
    old_qte = Decimal('0')
    if not instance._state.adding:
        try:
            old_qte = type(instance).objects.get(pk=instance.pk).quantite
        except type(instance).DoesNotExist:
            old_qte = Decimal('0')
    return old_qte, art, sens


class EntreeStock(StockBase):
    TYPES = [('achat', 'Achat fournisseur'), ('retour', 'Retour client'),
             ('ajustement', 'Ajustement positif'), ('transfert', 'Transfert reçu'),
             ('don', 'Don / récupération')]
    date_entree = models.DateField(default=timezone.now)
    type_entree = models.CharField(max_length=12, choices=TYPES, default='achat')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='entrees')
    bon_livraison = models.CharField(max_length=60, blank=True, verbose_name='Bon de livraison')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='entrees')
    quantite = models.DecimalField(max_digits=12, decimal_places=2)
    prix_unitaire = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Prix unitaire (GNF)')

    class Meta:
        verbose_name = 'Entrée'
        ordering = ['-date_entree', '-id']

    def __str__(self):
        return f"Entrée {self.article} · {self.quantite}"

    def save(self, *args, **kwargs):
        old = Decimal('0')
        if not self._state.adding:
            try:
                old = EntreeStock.objects.get(pk=self.pk).quantite
            except EntreeStock.DoesNotExist:
                old = Decimal('0')
        super().save(*args, **kwargs)
        delta = (self.quantite or 0) - old
        if self.article_id and delta:
            art = self.article
            avant = art.quantite_stock or 0
            art.quantite_stock = avant + delta
            art.save(update_fields=['quantite_stock'])
            MouvementStock.objects.create(
                entreprise=self.entreprise, cree_par=self.cree_par, article=art,
                type_mouvement='entree', quantite=delta, qte_avant=avant,
                qte_apres=art.quantite_stock, motif=self.get_type_entree_display(),
                document=self.bon_livraison)


class SortieStock(StockBase):
    TYPES = [('vente', 'Vente'), ('service', 'Livraison service interne'),
             ('perte', 'Perte / casse'), ('transfert', 'Transfert sortant'),
             ('interne', 'Utilisation interne')]
    date_sortie = models.DateField(default=timezone.now)
    type_sortie = models.CharField(max_length=12, choices=TYPES, default='vente')
    demandeur = models.ForeignKey(Demandeur, on_delete=models.SET_NULL, null=True, blank=True, related_name='sorties')
    bon_sortie = models.CharField(max_length=60, blank=True, verbose_name='Bon de sortie')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='sorties')
    quantite = models.DecimalField(max_digits=12, decimal_places=2)
    valide = models.BooleanField(default=False, verbose_name='Validé par responsable')

    class Meta:
        verbose_name = 'Sortie'
        ordering = ['-date_sortie', '-id']

    def __str__(self):
        return f"Sortie {self.article} · {self.quantite}"

    def save(self, *args, **kwargs):
        old = Decimal('0')
        if not self._state.adding:
            try:
                old = SortieStock.objects.get(pk=self.pk).quantite
            except SortieStock.DoesNotExist:
                old = Decimal('0')
        super().save(*args, **kwargs)
        delta = (self.quantite or 0) - old
        if self.article_id and delta:
            art = self.article
            avant = art.quantite_stock or 0
            art.quantite_stock = avant - delta
            art.save(update_fields=['quantite_stock'])
            MouvementStock.objects.create(
                entreprise=self.entreprise, cree_par=self.cree_par, article=art,
                type_mouvement='sortie', quantite=delta, qte_avant=avant,
                qte_apres=art.quantite_stock, motif=self.get_type_sortie_display(),
                document=self.bon_sortie)


# ------------------------------------------------------------------
# Inventaire
# ------------------------------------------------------------------
class Inventaire(StockBase):
    STATUTS = [('en_cours', 'En cours'), ('valide', 'Validé')]
    reference = models.CharField(max_length=40, blank=True)
    depot = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventaires')
    date_inventaire = models.DateField(default=timezone.now)
    statut = models.CharField(max_length=10, choices=STATUTS, default='en_cours')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Inventaire'
        ordering = ['-date_inventaire', '-id']

    def __str__(self):
        return f"{self.reference or 'Inventaire'} · {self.date_inventaire:%d/%m/%Y}"


class LigneInventaire(models.Model):
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE, related_name='lignes')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    qte_theorique = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qte_reelle = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    justification = models.CharField(max_length=255, blank=True)

    @property
    def ecart(self):
        return (self.qte_reelle or 0) - (self.qte_theorique or 0)

    def __str__(self):
        return f"{self.article} · écart {self.ecart}"


# ------------------------------------------------------------------
# Commande d'achat
# ------------------------------------------------------------------
class CommandeAchat(StockBase):
    STATUTS = [('demande', 'Demandé'), ('commande', 'Commandé'),
               ('recu', 'Reçu'), ('annule', 'Annulé')]
    reference = models.CharField(max_length=40, blank=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='commandes')
    date_commande = models.DateField(default=timezone.now)
    statut = models.CharField(max_length=10, choices=STATUTS, default='demande')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Commande d'achat"
        ordering = ['-date_commande', '-id']

    def __str__(self):
        return f"{self.reference or 'CMD'} · {self.get_statut_display()}"

    def save(self, *args, **kwargs):
        if not self.reference and self.entreprise_id:
            annee = timezone.now().year
            n = CommandeAchat.objects.filter(entreprise=self.entreprise, date_commande__year=annee).count() + 1
            self.reference = f"CMD-{annee}-{n:04d}"
        super().save(*args, **kwargs)


class LigneCommande(models.Model):
    commande = models.ForeignKey(CommandeAchat, on_delete=models.CASCADE, related_name='lignes')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    prix_unitaire = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    @property
    def total(self):
        return (self.quantite or 0) * (self.prix_unitaire or 0)

    def __str__(self):
        return f"{self.article} x {self.quantite}"
