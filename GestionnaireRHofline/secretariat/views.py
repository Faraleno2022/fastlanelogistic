"""
Vues du module Secrétariat.

CRUD générique piloté par un registre MODULES : chaque entité partage
les mêmes vues liste/création/édition/suppression, filtrées par entreprise.
"""
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import (
    Courrier, RendezVous, Visiteur, Appel,
    DocumentSecretariat, Tache, Contact, Reunion,
)
from .forms import (
    CourrierForm, RendezVousForm, VisiteurForm, AppelForm,
    DocumentForm, TacheForm, ContactForm, ReunionForm,
)


# Registre : slug -> configuration de l'entité
MODULES = {
    'courriers': {
        'model': Courrier, 'form': CourrierForm, 'label': 'Courrier',
        'label_plural': 'Courriers', 'icon': 'bi-envelope-paper',
        'columns': [('numero_ordre', "N° ordre"), ('type_courrier', 'Type'),
                    ('objet', 'Objet'), ('expediteur', 'Expéditeur'),
                    ('destinataire', 'Destinataire'), ('date_courrier', 'Date'),
                    ('statut', 'Statut')],
        'search': ['numero_ordre', 'objet', 'expediteur', 'destinataire'],
    },
    'rendez-vous': {
        'model': RendezVous, 'form': RendezVousForm, 'label': 'Rendez-vous',
        'label_plural': 'Rendez-vous', 'icon': 'bi-calendar-event',
        'columns': [('visiteur_nom', 'Visiteur'), ('motif', 'Motif'),
                    ('personne_concernee', 'Concerne'), ('date_heure', 'Date/heure'),
                    ('statut', 'Statut')],
        'search': ['visiteur_nom', 'motif', 'personne_concernee'],
    },
    'visiteurs': {
        'model': Visiteur, 'form': VisiteurForm, 'label': 'Visiteur',
        'label_plural': 'Visiteurs', 'icon': 'bi-person-badge',
        'columns': [('nom', 'Nom'), ('telephone', 'Téléphone'),
                    ('structure', 'Structure'), ('motif', 'Motif'),
                    ('service_visite', 'Service visité'), ('date_visite', 'Date'),
                    ('heure_arrivee', 'Arrivée'), ('heure_sortie', 'Sortie')],
        'search': ['nom', 'telephone', 'structure', 'service_visite'],
    },
    'appels': {
        'model': Appel, 'form': AppelForm, 'label': 'Appel',
        'label_plural': 'Appels', 'icon': 'bi-telephone',
        'columns': [('sens', 'Sens'), ('appelant_nom', 'Appelant'),
                    ('telephone', 'Téléphone'), ('objet', 'Objet'),
                    ('date_heure', 'Date/heure'), ('suivi_requis', 'Suivi')],
        'search': ['appelant_nom', 'telephone', 'objet'],
    },
    'documents': {
        'model': DocumentSecretariat, 'form': DocumentForm, 'label': 'Document',
        'label_plural': 'Documents', 'icon': 'bi-folder',
        'columns': [('titre', 'Titre'), ('categorie', 'Catégorie'),
                    ('date_document', 'Date'), ('fichier', 'Fichier')],
        'search': ['titre', 'description'],
    },
    'taches': {
        'model': Tache, 'form': TacheForm, 'label': 'Tâche',
        'label_plural': 'Tâches', 'icon': 'bi-check2-square',
        'columns': [('titre', 'Titre'), ('priorite', 'Priorité'),
                    ('responsable', 'Responsable'), ('date_limite', 'Échéance'),
                    ('etat', 'État')],
        'search': ['titre', 'description', 'responsable'],
    },
    'contacts': {
        'model': Contact, 'form': ContactForm, 'label': 'Contact',
        'label_plural': 'Contacts', 'icon': 'bi-person-lines-fill',
        'columns': [('nom', 'Nom'), ('type_contact', 'Type'),
                    ('telephone', 'Téléphone'), ('email', 'Email'),
                    ('fonction', 'Fonction'), ('organisation', 'Organisation')],
        'search': ['nom', 'telephone', 'email', 'organisation', 'fonction'],
    },
    'reunions': {
        'model': Reunion, 'form': ReunionForm, 'label': 'Réunion',
        'label_plural': 'Réunions', 'icon': 'bi-people',
        'columns': [('titre', 'Titre'), ('date_heure', 'Date/heure'),
                    ('lieu', 'Lieu')],
        'search': ['titre', 'lieu', 'ordre_du_jour'],
    },
}


def _check_access(request):
    """L'utilisateur doit avoir une entreprise avec accès secrétariat
    (ou être superuser)."""
    if request.user.is_superuser:
        return True
    ent = getattr(request.user, 'entreprise', None)
    if ent is None:
        return False
    return getattr(ent, 'has_secretariat', False) or ent.type_module == 'secretariat'


def _get_config(slug):
    cfg = MODULES.get(slug)
    if not cfg:
        raise Http404("Module secrétariat inconnu")
    return cfg


def _display(obj, field):
    """Valeur d'affichage : gère les choices et booléens."""
    disp = getattr(obj, f'get_{field}_display', None)
    if callable(disp):
        return disp()
    val = getattr(obj, field, '')
    if isinstance(val, bool):
        return 'Oui' if val else 'Non'
    return val


def _qs(request, cfg):
    return cfg['model'].objects.filter(entreprise=request.user.entreprise)


# ----------------------------- Tableau de bord -----------------------------
@login_required
def dashboard(request):
    if not _check_access(request):
        messages.error(request, "Votre compte n'a pas accès au module Secrétariat.")
        return redirect('core:index')

    ent = request.user.entreprise
    today = timezone.now().date()

    def c(model, **flt):
        return model.objects.filter(entreprise=ent, **flt).count()

    contexte = {
        'rdv_jour': RendezVous.objects.filter(
            entreprise=ent, date_heure__date=today).exclude(statut='annule').order_by('date_heure'),
        'courriers_a_traiter': c(Courrier, statut__in=['recu', 'en_attente']),
        'taches_urgentes': Tache.objects.filter(
            entreprise=ent, priorite='urgente').exclude(etat='termine').order_by('date_limite')[:8],
        'appels_suivi': c(Appel, suivi_requis=True),
        'documents_total': c(DocumentSecretariat),
        'stats': {
            'courriers': c(Courrier),
            'rendez-vous': c(RendezVous),
            'visiteurs': c(Visiteur),
            'appels': c(Appel),
            'documents': c(DocumentSecretariat),
            'taches': c(Tache),
            'contacts': c(Contact),
            'reunions': c(Reunion),
        },
        'modules': MODULES,
        'today': today,
    }
    return render(request, 'secretariat/dashboard.html', contexte)


# ----------------------------- Liste -----------------------------
@login_required
def liste(request, slug):
    if not _check_access(request):
        return redirect('core:index')
    cfg = _get_config(slug)
    qs = _qs(request, cfg)

    q = request.GET.get('q', '').strip()
    if q and cfg.get('search'):
        cond = Q()
        for f in cfg['search']:
            cond |= Q(**{f'{f}__icontains': q})
        qs = qs.filter(cond)

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))

    rows = []
    for obj in page:
        rows.append({
            'pk': obj.pk,
            'cells': [_display(obj, f) for f, _ in cfg['columns']],
        })

    return render(request, 'secretariat/generic_list.html', {
        'slug': slug, 'cfg': cfg, 'page': page, 'rows': rows,
        'headers': [h for _, h in cfg['columns']], 'q': q,
        'modules': MODULES,
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
    instance = None
    if pk is not None:
        instance = get_object_or_404(cfg['model'], pk=pk, entreprise=request.user.entreprise)

    if request.method == 'POST':
        form = cfg['form'](request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.entreprise = request.user.entreprise
            if obj.cree_par_id is None:
                obj.cree_par = request.user
            obj.save()
            messages.success(request, f"{cfg['label']} enregistré(e) avec succès.")
            return redirect('secretariat:liste', slug=slug)
    else:
        form = cfg['form'](instance=instance)

    return render(request, 'secretariat/generic_form.html', {
        'slug': slug, 'cfg': cfg, 'form': form, 'instance': instance,
        'modules': MODULES,
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
        return redirect('secretariat:liste', slug=slug)
    return render(request, 'secretariat/generic_confirm_delete.html', {
        'slug': slug, 'cfg': cfg, 'objet': obj, 'modules': MODULES,
    })
