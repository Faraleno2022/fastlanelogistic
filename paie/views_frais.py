"""
Vues pour la gestion des notes de frais.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.utils import timezone
from django.utils.text import slugify
from datetime import date
from decimal import Decimal

from .views import parse_montant
from employes.models import Employe
from .models_frais import CategoriesFrais, NoteFrais, LigneFrais, BaremeFrais


def _normaliser_libelle_categorie(libelle):
    """Nettoie un libelle saisi librement."""
    return ' '.join((libelle or '').split())


def _generer_code_categorie_frais(libelle):
    """Genere un code unique de 20 caracteres max pour une categorie de frais."""
    base = slugify(libelle).upper().replace('-', '_')[:20] or 'FRAIS'
    code = base
    suffixe = 1
    while CategoriesFrais.objects.filter(code=code).exists():
        suffixe += 1
        suffixe_txt = f"_{suffixe}"
        code = f"{base[:20 - len(suffixe_txt)]}{suffixe_txt}"
    return code


def _obtenir_ou_creer_categorie_frais(libelle, justificatif_obligatoire=True):
    """Retourne une categorie existante par libelle ou en cree une nouvelle."""
    libelle = _normaliser_libelle_categorie(libelle)
    if not libelle:
        return None

    categorie = CategoriesFrais.objects.filter(libelle__iexact=libelle).first()
    if categorie:
        if not categorie.actif:
            categorie.actif = True
            categorie.save(update_fields=['actif'])
        return categorie

    return CategoriesFrais.objects.create(
        code=_generer_code_categorie_frais(libelle),
        libelle=libelle,
        justificatif_obligatoire=justificatif_obligatoire,
        actif=True,
    )


@login_required
def liste_notes_frais(request):
    """Liste des notes de frais"""
    notes = NoteFrais.objects.filter(
        employe__entreprise=request.user.entreprise
    ).select_related('employe', 'employe__service', 'valideur')
    
    # Filtres
    employe_id = request.GET.get('employe')
    statut = request.GET.get('statut')
    mois = request.GET.get('mois')
    annee = request.GET.get('annee', date.today().year)
    
    if employe_id:
        notes = notes.filter(employe_id=employe_id)
    if statut:
        notes = notes.filter(statut=statut)
    if mois:
        notes = notes.filter(date_debut__month=int(mois))
    if annee:
        notes = notes.filter(date_debut__year=int(annee))
    
    # Statistiques
    stats = notes.aggregate(
        total_soumis=Sum('montant_total', filter=Q(statut='soumise')),
        total_valide=Sum('montant_valide', filter=Q(statut='validee')),
        total_rembourse=Sum('montant_rembourse', filter=Q(statut='remboursee')),
        nb_en_attente=Count('id', filter=Q(statut='soumise')),
    )
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'paie/frais/liste.html', {
        'notes': notes[:100],
        'stats': stats,
        'employes': employes,
        'statuts': NoteFrais.STATUTS,
        'annee': int(annee),
        'mois': mois,
        'filtre_employe': employe_id,
        'filtre_statut': statut,
    })


@login_required
def creer_note_frais(request):
    """Créer une nouvelle note de frais"""
    if request.method == 'POST':
        employe_id = request.POST.get('employe')
        titre = request.POST.get('titre')
        description = request.POST.get('description', '')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        mission = request.POST.get('mission', '')
        
        employe = get_object_or_404(
            Employe,
            pk=employe_id,
            entreprise=request.user.entreprise
        )
        
        note = NoteFrais.objects.create(
            employe=employe,
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            mission=mission,
            statut='brouillon',
        )
        
        messages.success(request, f"Note de frais {note.reference} créée")
        return redirect('paie:detail_note_frais', pk=note.pk)
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'paie/frais/creer.html', {
        'employes': employes,
    })


@login_required
def detail_note_frais(request, pk):
    """Détail d'une note de frais"""
    note = get_object_or_404(
        NoteFrais,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    lignes = note.lignes.select_related('categorie').all()
    categories = CategoriesFrais.objects.filter(actif=True).order_by('libelle')
    
    # Totaux par catégorie
    totaux_categories = lignes.values('categorie__libelle').annotate(
        total=Sum('montant')
    ).order_by('-total')
    
    return render(request, 'paie/frais/detail.html', {
        'note': note,
        'lignes': lignes,
        'categories': categories,
        'totaux_categories': totaux_categories,
    })


@login_required
def ajouter_ligne_frais(request, pk):
    """Ajouter une ligne à une note de frais"""
    note = get_object_or_404(
        NoteFrais,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if note.statut not in ['brouillon', 'rejetee']:
        messages.error(request, "Cette note ne peut plus être modifiée")
        return redirect('paie:detail_note_frais', pk=pk)
    
    if request.method == 'POST':
        categorie_id = request.POST.get('categorie')
        nouvelle_categorie = request.POST.get('nouvelle_categorie', '')
        nouvelle_categorie_justif = request.POST.get('nouvelle_categorie_justificatif_obligatoire') == 'on'
        date_depense = request.POST.get('date_depense')
        description = request.POST.get('description')
        montant = request.POST.get('montant')
        numero_facture = request.POST.get('numero_facture', '')
        justificatif = request.FILES.get('justificatif')

        if _normaliser_libelle_categorie(nouvelle_categorie):
            categorie = _obtenir_ou_creer_categorie_frais(
                nouvelle_categorie,
                justificatif_obligatoire=nouvelle_categorie_justif,
            )
        elif categorie_id:
            categorie = get_object_or_404(CategoriesFrais, pk=categorie_id, actif=True)
        else:
            messages.error(request, "Choisissez une catégorie ou saisissez une nouvelle catégorie.")
            return redirect('paie:detail_note_frais', pk=pk)
        
        ligne = LigneFrais.objects.create(
            note_frais=note,
            categorie=categorie,
            date_depense=date_depense,
            description=description,
            montant=parse_montant(montant) or Decimal('0'),
            numero_facture=numero_facture,
            justificatif=justificatif,
        )
        
        messages.success(request, f"Ligne ajoutée: {ligne.montant} GNF")
    
    return redirect('paie:detail_note_frais', pk=pk)


@login_required
def supprimer_ligne_frais(request, pk, ligne_pk):
    """Supprimer une ligne de frais"""
    note = get_object_or_404(
        NoteFrais,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if note.statut not in ['brouillon', 'rejetee']:
        messages.error(request, "Cette note ne peut plus être modifiée")
        return redirect('paie:detail_note_frais', pk=pk)
    
    ligne = get_object_or_404(LigneFrais, pk=ligne_pk, note_frais=note)
    ligne.delete()
    
    # Recalculer le total
    note.calculer_total()
    note.save()
    
    messages.success(request, "Ligne supprimée")
    return redirect('paie:detail_note_frais', pk=pk)


@login_required
def soumettre_note_frais(request, pk):
    """Soumettre une note de frais pour validation"""
    note = get_object_or_404(
        NoteFrais,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if note.statut not in ['brouillon', 'rejetee']:
        messages.error(request, "Cette note ne peut pas être soumise")
        return redirect('paie:detail_note_frais', pk=pk)
    
    if not note.lignes.exists():
        messages.error(request, "Ajoutez au moins une ligne de frais")
        return redirect('paie:detail_note_frais', pk=pk)
    
    # Vérifier les justificatifs obligatoires
    for ligne in note.lignes.all():
        if ligne.categorie.justificatif_obligatoire and not ligne.justificatif:
            messages.error(request, f"Justificatif manquant pour: {ligne.description}")
            return redirect('paie:detail_note_frais', pk=pk)
    
    note.statut = 'soumise'
    note.date_soumission = timezone.now()
    note.calculer_total()
    note.save()
    
    messages.success(request, f"Note {note.reference} soumise pour validation")
    return redirect('paie:liste_notes_frais')


@login_required
def valider_note_frais(request, pk):
    """Valider une note de frais"""
    note = get_object_or_404(
        NoteFrais,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if note.statut != 'soumise':
        messages.error(request, "Cette note ne peut pas être validée")
        return redirect('paie:detail_note_frais', pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        commentaire = request.POST.get('commentaire', '')
        
        # Récupérer l'employé valideur
        valideur = Employe.objects.filter(
            utilisateur=request.user
        ).first()
        
        if action == 'valider':
            # Valider toutes les lignes
            for ligne in note.lignes.all():
                ligne.valide = True
                ligne.montant_valide = ligne.montant
                ligne.save()
            
            note.statut = 'validee'
            note.date_validation = timezone.now()
            note.valideur = valideur
            note.commentaire_validation = commentaire
            note.calculer_valide()
            note.save()
            
            messages.success(request, f"Note {note.reference} validée: {note.montant_valide} GNF")
        
        elif action == 'rejeter':
            note.statut = 'rejetee'
            note.date_validation = timezone.now()
            note.valideur = valideur
            note.commentaire_validation = commentaire
            note.save()
            
            messages.warning(request, f"Note {note.reference} rejetée")
        
        return redirect('paie:liste_notes_frais')
    
    return render(request, 'paie/frais/valider.html', {
        'note': note,
    })


@login_required
def rembourser_note_frais(request, pk):
    """Marquer une note comme remboursée"""
    note = get_object_or_404(
        NoteFrais,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if note.statut != 'validee':
        messages.error(request, "Cette note doit être validée avant remboursement")
        return redirect('paie:detail_note_frais', pk=pk)
    
    note.statut = 'remboursee'
    note.date_remboursement = timezone.now()
    note.montant_rembourse = note.montant_valide
    note.save()
    
    messages.success(request, f"Note {note.reference} remboursée: {note.montant_rembourse} GNF")
    return redirect('paie:liste_notes_frais')


@login_required
def supprimer_note_frais(request, pk):
    """Supprimer une note de frais"""
    note = get_object_or_404(
        NoteFrais,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if note.statut not in ['brouillon', 'rejetee']:
        messages.error(request, "Seules les notes en brouillon ou rejetées peuvent être supprimées")
        return redirect('paie:detail_note_frais', pk=pk)
    
    reference = note.reference
    note.delete()
    
    messages.success(request, f"Note {reference} supprimée")
    return redirect('paie:liste_notes_frais')


@login_required
def recap_frais(request):
    """Récapitulatif des frais par employé et catégorie"""
    annee = int(request.GET.get('annee', date.today().year))
    
    # Par employé
    recap_employes = NoteFrais.objects.filter(
        employe__entreprise=request.user.entreprise,
        date_debut__year=annee,
        statut__in=['validee', 'remboursee']
    ).values(
        'employe__nom', 'employe__prenoms', 'employe__matricule'
    ).annotate(
        total_valide=Sum('montant_valide'),
        total_rembourse=Sum('montant_rembourse'),
        nb_notes=Count('id')
    ).order_by('-total_valide')
    
    # Par catégorie
    recap_categories = LigneFrais.objects.filter(
        note_frais__employe__entreprise=request.user.entreprise,
        note_frais__date_debut__year=annee,
        note_frais__statut__in=['validee', 'remboursee'],
        valide=True
    ).values('categorie__libelle').annotate(
        total=Sum('montant_valide')
    ).order_by('-total')
    
    # Totaux globaux
    totaux = NoteFrais.objects.filter(
        employe__entreprise=request.user.entreprise,
        date_debut__year=annee,
        statut__in=['validee', 'remboursee']
    ).aggregate(
        total_valide=Sum('montant_valide'),
        total_rembourse=Sum('montant_rembourse'),
        nb_notes=Count('id'),
    )
    
    return render(request, 'paie/frais/recap.html', {
        'recap_employes': recap_employes,
        'recap_categories': recap_categories,
        'totaux': totaux,
        'annee': annee,
    })


@login_required
def gestion_categories_frais(request):
    """Gestion des catégories de frais"""
    categories = CategoriesFrais.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'creer':
            code = request.POST.get('code')
            libelle = request.POST.get('libelle')
            description = request.POST.get('description', '')
            plafond = request.POST.get('plafond_journalier')
            justificatif_obligatoire = request.POST.get('justificatif_obligatoire') == 'on'
            
            CategoriesFrais.objects.create(
                code=code,
                libelle=libelle,
                description=description,
                plafond_journalier=Decimal(plafond) if plafond else None,
                justificatif_obligatoire=justificatif_obligatoire,
            )
            messages.success(request, f"Catégorie '{libelle}' créée")
        
        elif action == 'supprimer':
            cat_id = request.POST.get('categorie_id')
            cat = get_object_or_404(CategoriesFrais, pk=cat_id)
            if cat.lignes_frais.exists():
                messages.error(request, "Cette catégorie est utilisée")
            else:
                cat.delete()
                messages.success(request, "Catégorie supprimée")
        
        return redirect('paie:gestion_categories_frais')
    
    return render(request, 'paie/frais/categories.html', {
        'categories': categories,
    })
