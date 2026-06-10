"""
Vues du module Stock : tableau de bord + CRUD générique piloté par un
registre. Les entrées/sorties mettent à jour le stock automatiquement
(logique dans les modèles).
"""
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F, DecimalField, ExpressionWrapper
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import (
    Depot, CategorieArticle, Fournisseur, Demandeur, Article,
    EntreeStock, SortieStock, MouvementStock, Inventaire, CommandeAchat,
)
from .forms import (
    DepotForm, CategorieForm, FournisseurForm, DemandeurForm, ArticleForm,
    EntreeForm, SortieForm, InventaireForm, CommandeForm,
)


MODULES = {
    'articles': {
        'model': Article, 'form': ArticleForm, 'label': 'Article', 'label_plural': 'Articles',
        'icon': 'bi-box-seam',
        'columns': [('code', 'Code'), ('designation', 'Désignation'), ('categorie', 'Catégorie'),
                    ('depot', 'Dépôt'), ('unite', 'Unité'), ('quantite_stock', 'Stock'),
                    ('stock_min', 'Seuil'), ('prix_achat', "Prix achat")],
        'search': ['code', 'designation', 'emplacement'],
    },
    'entrees': {
        'model': EntreeStock, 'form': EntreeForm, 'label': 'Entrée', 'label_plural': 'Entrées',
        'icon': 'bi-box-arrow-in-down',
        'columns': [('date_entree', 'Date'), ('type_entree', 'Type'), ('article', 'Article'),
                    ('quantite', 'Quantité'), ('fournisseur', 'Fournisseur'), ('bon_livraison', 'BL'),
                    ('prix_unitaire', 'PU')],
        'search': ['bon_livraison'],
    },
    'sorties': {
        'model': SortieStock, 'form': SortieForm, 'label': 'Sortie', 'label_plural': 'Sorties',
        'icon': 'bi-box-arrow-up',
        'columns': [('date_sortie', 'Date'), ('type_sortie', 'Type'), ('article', 'Article'),
                    ('quantite', 'Quantité'), ('demandeur', 'Demandeur'), ('bon_sortie', 'Bon'),
                    ('valide', 'Validé')],
        'search': ['bon_sortie'],
    },
    'mouvements': {
        'model': MouvementStock, 'form': None, 'label': 'Mouvement', 'label_plural': 'Mouvements',
        'icon': 'bi-clock-history', 'readonly': True,
        'columns': [('date_creation', 'Date'), ('type_mouvement', 'Type'), ('article', 'Article'),
                    ('quantite', 'Qté'), ('qte_avant', 'Avant'), ('qte_apres', 'Après'),
                    ('motif', 'Motif'), ('document', 'Doc')],
        'search': ['motif', 'document'],
    },
    'inventaires': {
        'model': Inventaire, 'form': InventaireForm, 'label': 'Inventaire', 'label_plural': 'Inventaires',
        'icon': 'bi-clipboard-check',
        'columns': [('reference', 'Référence'), ('depot', 'Dépôt'), ('date_inventaire', 'Date'),
                    ('statut', 'Statut')],
        'search': ['reference'],
    },
    'commandes': {
        'model': CommandeAchat, 'form': CommandeForm, 'label': "Commande d'achat", 'label_plural': "Commandes d'achat",
        'icon': 'bi-cart',
        'columns': [('reference', 'Référence'), ('fournisseur', 'Fournisseur'), ('date_commande', 'Date'),
                    ('statut', 'Statut')],
        'search': ['reference'],
    },
    'fournisseurs': {
        'model': Fournisseur, 'form': FournisseurForm, 'label': 'Fournisseur', 'label_plural': 'Fournisseurs',
        'icon': 'bi-truck',
        'columns': [('nom', 'Nom'), ('telephone', 'Téléphone'), ('email', 'Email'),
                    ('articles_fournis', 'Articles'), ('delai_livraison_jours', 'Délai (j)'), ('dette', 'Dette')],
        'search': ['nom', 'telephone', 'email'],
    },
    'demandeurs': {
        'model': Demandeur, 'form': DemandeurForm, 'label': 'Demandeur', 'label_plural': 'Demandeurs',
        'icon': 'bi-person-lines-fill',
        'columns': [('nom', 'Nom'), ('type_demandeur', 'Type'), ('telephone', 'Téléphone'), ('email', 'Email')],
        'search': ['nom', 'telephone'],
    },
    'depots': {
        'model': Depot, 'form': DepotForm, 'label': 'Dépôt', 'label_plural': 'Dépôts',
        'icon': 'bi-building',
        'columns': [('nom', 'Nom'), ('type_depot', 'Type'), ('localisation', 'Localisation'),
                    ('responsable', 'Responsable'), ('actif', 'Actif')],
        'search': ['nom', 'localisation', 'responsable'],
    },
    'categories': {
        'model': CategorieArticle, 'form': CategorieForm, 'label': 'Catégorie', 'label_plural': 'Catégories',
        'icon': 'bi-tags',
        'columns': [('nom', 'Nom'), ('description', 'Description')],
        'search': ['nom', 'description'],
    },
}


def _check_access(request):
    if request.user.is_superuser:
        return True
    ent = getattr(request.user, 'entreprise', None)
    if ent is None:
        return False
    return getattr(ent, 'has_stock', False) or ent.type_module == 'stock'


def _get_config(slug):
    cfg = MODULES.get(slug)
    if not cfg:
        raise Http404("Module stock inconnu")
    return cfg


def _display(obj, field):
    disp = getattr(obj, f'get_{field}_display', None)
    if callable(disp):
        return disp()
    val = getattr(obj, field, '')
    if isinstance(val, bool):
        return 'Oui' if val else 'Non'
    return val


# ----------------------------- Tableau de bord -----------------------------
@login_required
def dashboard(request):
    if not _check_access(request):
        messages.error(request, "Votre compte n'a pas accès au module Stock.")
        return redirect('core:index')

    ent = request.user.entreprise
    today = timezone.now().date()
    articles = Article.objects.filter(entreprise=ent) if ent else Article.objects.none()

    valeur = articles.aggregate(
        v=Sum(ExpressionWrapper(F('quantite_stock') * F('prix_achat'),
                                output_field=DecimalField(max_digits=20, decimal_places=2)))
    )['v'] or 0
    ruptures = articles.filter(quantite_stock__lte=0)
    proches = articles.filter(quantite_stock__gt=0, stock_min__gt=0,
                              quantite_stock__lte=F('stock_min'))

    def mois_sum(model, champ_date):
        return model.objects.filter(
            entreprise=ent, **{f'{champ_date}__year': today.year, f'{champ_date}__month': today.month}
        ).aggregate(s=Sum('quantite'))['s'] or 0

    contexte = {
        'stock_total': articles.aggregate(s=Sum('quantite_stock'))['s'] or 0,
        'nb_articles': articles.count(),
        'nb_ruptures': ruptures.count(),
        'nb_proches': proches.count(),
        'valeur_stock': valeur,
        'entrees_mois': mois_sum(EntreeStock, 'date_entree') if ent else 0,
        'sorties_mois': mois_sum(SortieStock, 'date_sortie') if ent else 0,
        'alertes': list(ruptures[:10]) + list(proches[:10]),
        'modules': MODULES,
        'today': today,
    }
    return render(request, 'stock/dashboard.html', contexte)


# ----------------------------- Liste -----------------------------
@login_required
def liste(request, slug):
    if not _check_access(request):
        return redirect('core:index')
    cfg = _get_config(slug)
    qs = cfg['model'].objects.filter(entreprise=request.user.entreprise)

    q = request.GET.get('q', '').strip()
    if q and cfg.get('search'):
        cond = Q()
        for f in cfg['search']:
            cond |= Q(**{f'{f}__icontains': q})
        qs = qs.filter(cond)

    page = Paginator(qs, 25).get_page(request.GET.get('page'))
    rows = [{'pk': o.pk, 'cells': [_display(o, f) for f, _ in cfg['columns']],
             'statut': getattr(o, 'statut_stock', None)} for o in page]

    return render(request, 'stock/generic_list.html', {
        'slug': slug, 'cfg': cfg, 'page': page, 'rows': rows,
        'headers': [h for _, h in cfg['columns']], 'q': q, 'modules': MODULES,
    })


# ----------------------------- Créer / Éditer -----------------------------
@login_required
def creer(request, slug):
    return _form(request, slug, None)


@login_required
def modifier(request, slug, pk):
    return _form(request, slug, pk)


def _form(request, slug, pk):
    if not _check_access(request):
        return redirect('core:index')
    cfg = _get_config(slug)
    if cfg.get('readonly') or cfg['form'] is None:
        messages.info(request, "Ce journal est en lecture seule.")
        return redirect('stock:liste', slug=slug)

    instance = None
    if pk is not None:
        instance = get_object_or_404(cfg['model'], pk=pk, entreprise=request.user.entreprise)

    if request.method == 'POST':
        form = cfg['form'](request.POST, request.FILES, instance=instance,
                           entreprise=request.user.entreprise)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.entreprise = request.user.entreprise
            if obj.cree_par_id is None:
                obj.cree_par = request.user
            obj.save()
            messages.success(request, f"{cfg['label']} enregistré(e) avec succès.")
            return redirect('stock:liste', slug=slug)
    else:
        form = cfg['form'](instance=instance, entreprise=request.user.entreprise)

    return render(request, 'stock/generic_form.html', {
        'slug': slug, 'cfg': cfg, 'form': form, 'instance': instance, 'modules': MODULES,
    })


# ----------------------------- Supprimer -----------------------------
@login_required
def supprimer(request, slug, pk):
    if not _check_access(request):
        return redirect('core:index')
    cfg = _get_config(slug)
    obj = get_object_or_404(cfg['model'], pk=pk, entreprise=request.user.entreprise)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f"{cfg['label']} supprimé(e).")
        return redirect('stock:liste', slug=slug)
    return render(request, 'stock/generic_confirm_delete.html', {
        'slug': slug, 'cfg': cfg, 'objet': obj, 'modules': MODULES,
    })
