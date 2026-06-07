"""
Views pour la gestion des taux de change
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse
from datetime import datetime, date
import csv
from django.http import HttpResponse
from decimal import Decimal

from core.models import TauxChange, Devise
from core.decorators import entreprise_required


@login_required
@entreprise_required
def liste_taux_change(request):
    """Liste des taux de change"""
    # Filtres
    search = request.GET.get('search', '')
    devise_source_id = request.GET.get('devise_source', '')
    devise_cible_id = request.GET.get('devise_cible', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    
    # Query de base avec filtre entreprise
    taux = TauxChange.objects.filter(
        Q(entreprise=request.user.entreprise) | Q(entreprise__isnull=True)
    )
    
    # Appliquer les filtres
    if search:
        taux = taux.filter(
            Q(devise_source__code__icontains=search) |
            Q(devise_source__nom__icontains=search) |
            Q(devise_cible__code__icontains=search) |
            Q(devise_cible__nom__icontains=search) |
            Q(source__icontains=search)
        )
    
    if devise_source_id:
        taux = taux.filter(devise_source_id=devise_source_id)
    
    if devise_cible_id:
        taux = taux.filter(devise_cible_id=devise_cible_id)
    
    if date_debut:
        taux = taux.filter(date_taux__gte=date_debut)
    
    if date_fin:
        taux = taux.filter(date_taux__lte=date_fin)
    
    # Tri par date décroissante
    taux = taux.select_related('devise_source', 'devise_cible').order_by('-date_taux')
    
    # Pagination
    paginator = Paginator(taux, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Devises pour les filtres
    devises = Devise.objects.filter(actif=True).order_by('code')
    
    context = {
        'page_obj': page_obj,
        'devises': devises,
        'search': search,
        'devise_source_id': devise_source_id,
        'devise_cible_id': devise_cible_id,
        'date_debut': date_debut,
        'date_fin': date_fin,
    }
    
    return render(request, 'core/taux_change/liste.html', context)


@login_required
@entreprise_required
def ajouter_taux_change(request):
    """Ajouter un nouveau taux de change"""
    if request.method == 'POST':
        try:
            # Récupérer les données
            devise_source_id = request.POST.get('devise_source')
            devise_cible_id = request.POST.get('devise_cible')
            taux = request.POST.get('taux')
            date_taux = request.POST.get('date_taux')
            source = request.POST.get('source', '')
            
            # Validation
            if not all([devise_source_id, devise_cible_id, taux, date_taux]):
                raise ValueError("Tous les champs obligatoires doivent être remplis")
            
            devise_source = Devise.objects.get(pk=devise_source_id)
            devise_cible = Devise.objects.get(pk=devise_cible_id)
            
            if devise_source == devise_cible:
                raise ValueError("Les devises source et cible doivent être différentes")
            
            # Créer le taux
            taux_obj = TauxChange.objects.create(
                entreprise=request.user.entreprise,
                devise_source=devise_source,
                devise_cible=devise_cible,
                taux=Decimal(taux),
                date_taux=date_taux,
                source=source
            )
            
            messages.success(request, f"Taux de change {devise_source.code}/{devise_cible.code} ajouté avec succès")
            return redirect('core:liste_taux_change')
            
        except Devise.DoesNotExist:
            messages.error(request, "Devise introuvable")
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout : {str(e)}")
    
    # GET - Afficher le formulaire
    devises = Devise.objects.filter(actif=True).order_by('code')
    context = {
        'devises': devises,
        'today': date.today().strftime('%Y-%m-%d')
    }
    return render(request, 'core/taux_change/form.html', context)


@login_required
@entreprise_required
def modifier_taux_change(request, pk):
    """Modifier un taux de change"""
    taux = get_object_or_404(
        TauxChange,
        pk=pk,
        entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        try:
            # Récupérer les données
            taux_value = request.POST.get('taux')
            date_taux = request.POST.get('date_taux')
            source = request.POST.get('source', '')
            
            # Validation
            if not all([taux_value, date_taux]):
                raise ValueError("Le taux et la date sont obligatoires")
            
            # Mettre à jour
            taux.taux = Decimal(taux_value)
            taux.date_taux = date_taux
            taux.source = source
            taux.save()
            
            messages.success(request, "Taux de change modifié avec succès")
            return redirect('core:liste_taux_change')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification : {str(e)}")
    
    # GET - Afficher le formulaire
    devises = Devise.objects.filter(actif=True).order_by('code')
    context = {
        'taux': taux,
        'devises': devises,
        'is_edit': True
    }
    return render(request, 'core/taux_change/form.html', context)


@login_required
@entreprise_required
def supprimer_taux_change(request, pk):
    """Supprimer un taux de change"""
    taux = get_object_or_404(
        TauxChange,
        pk=pk,
        entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        try:
            taux.delete()
            messages.success(request, "Taux de change supprimé avec succès")
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression : {str(e)}")
        
        return redirect('core:liste_taux_change')
    
    context = {'taux': taux}
    return render(request, 'core/taux_change/delete.html', context)


@login_required
@entreprise_required
def importer_taux_change(request):
    """Importer des taux de change depuis un fichier CSV"""
    if request.method == 'POST':
        try:
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                raise ValueError("Aucun fichier sélectionné")
            
            if not csv_file.name.endswith('.csv'):
                raise ValueError("Le fichier doit être au format CSV")
            
            # Lire le fichier CSV
            decoded_file = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(decoded_file.splitlines())
            
            count = 0
            errors = []
            
            for row in csv_reader:
                try:
                    # Récupérer les devises
                    devise_source = Devise.objects.get(code=row['devise_source'].strip())
                    devise_cible = Devise.objects.get(code=row['devise_cible'].strip())
                    
                    # Créer ou mettre à jour le taux
                    TauxChange.objects.update_or_create(
                        entreprise=request.user.entreprise,
                        devise_source=devise_source,
                        devise_cible=devise_cible,
                        date_taux=row['date_taux'].strip(),
                        defaults={
                            'taux': Decimal(row['taux'].strip()),
                            'source': row.get('source', 'Import CSV').strip()
                        }
                    )
                    count += 1
                    
                except Exception as e:
                    errors.append(f"Ligne {csv_reader.line_num}: {str(e)}")
            
            if count > 0:
                messages.success(request, f"{count} taux de change importés avec succès")
            
            if errors:
                messages.warning(request, f"{len(errors)} erreurs lors de l'import")
                for error in errors[:5]:  # Afficher max 5 erreurs
                    messages.error(request, error)
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Erreur lors de l'import : {str(e)}")
        
        return redirect('core:liste_taux_change')
    
    # GET - Afficher le formulaire d'import
    return render(request, 'core/taux_change/import.html')


@login_required
@entreprise_required
def exporter_taux_change(request):
    """Exporter les taux de change en CSV"""
    # Créer la réponse HTTP
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="taux_change_{date.today()}.csv"'
    
    # Écrire le CSV
    writer = csv.writer(response)
    writer.writerow(['devise_source', 'devise_cible', 'taux', 'date_taux', 'source'])
    
    # Récupérer les taux
    taux = TauxChange.objects.filter(
        Q(entreprise=request.user.entreprise) | Q(entreprise__isnull=True)
    ).select_related('devise_source', 'devise_cible').order_by('-date_taux')
    
    for t in taux:
        writer.writerow([
            t.devise_source.code,
            t.devise_cible.code,
            t.taux,
            t.date_taux,
            t.source or ''
        ])
    
    return response
