"""
Vues pour la gestion du barème IRPP et simulation de calcul
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal, InvalidOperation
from datetime import date

from paie.models import TrancheRTS
from paie.services_irpp.irpp import IRPPService
from core.views import log_activity


@login_required
def bareme_irpp_liste(request):
    """Liste des tranches IRPP par année"""
    annee = request.GET.get('annee', date.today().year)
    try:
        annee = int(annee)
    except ValueError:
        annee = date.today().year
    
    tranches = TrancheRTS.objects.filter(
        annee_validite=annee
    ).order_by('numero_tranche')
    
    # Liste des années disponibles
    annees = TrancheRTS.objects.values_list(
        'annee_validite', flat=True
    ).distinct().order_by('-annee_validite')
    
    return render(request, 'paie/bareme_irpp/liste.html', {
        'tranches': tranches,
        'annee_selectionnee': annee,
        'annees': annees,
    })


@login_required
def bareme_irpp_ajouter(request):
    """Ajouter une nouvelle tranche IRPP"""
    if request.method == 'POST':
        try:
            tranche = TrancheRTS.objects.create(
                numero_tranche=int(request.POST['numero_tranche']),
                borne_inferieure=Decimal(request.POST['borne_inferieure']),
                borne_superieure=Decimal(request.POST['borne_superieure']) if request.POST.get('borne_superieure') else None,
                taux_irg=Decimal(request.POST['taux_irg']),
                annee_validite=int(request.POST['annee_validite']),
                date_debut_validite=request.POST['date_debut_validite'],
                date_fin_validite=request.POST.get('date_fin_validite') or None,
                actif=request.POST.get('actif', 'off') == 'on'
            )
            
            log_activity(
                request,
                f"Création tranche IRPP {tranche.numero_tranche} - {tranche.annee_validite}",
                'paie',
                'tranches_irg',
                tranche.id
            )
            
            messages.success(request, f'Tranche {tranche.numero_tranche} créée avec succès')
            return redirect('paie:bareme_irpp_liste')
            
        except (ValueError, InvalidOperation) as e:
            messages.error(request, f'Erreur de validation: {e}')
    
    annee_defaut = date.today().year
    return render(request, 'paie/bareme_irpp/form.html', {
        'annee_defaut': annee_defaut,
        'date_defaut': date(annee_defaut, 1, 1).isoformat(),
    })


@login_required
def bareme_irpp_modifier(request, pk):
    """Modifier une tranche IRPP"""
    tranche = get_object_or_404(TrancheRTS, pk=pk)
    
    if request.method == 'POST':
        try:
            tranche.numero_tranche = int(request.POST['numero_tranche'])
            tranche.borne_inferieure = Decimal(request.POST['borne_inferieure'])
            tranche.borne_superieure = Decimal(request.POST['borne_superieure']) if request.POST.get('borne_superieure') else None
            tranche.taux_irg = Decimal(request.POST['taux_irg'])
            tranche.annee_validite = int(request.POST['annee_validite'])
            tranche.date_debut_validite = request.POST['date_debut_validite']
            tranche.date_fin_validite = request.POST.get('date_fin_validite') or None
            tranche.actif = request.POST.get('actif', 'off') == 'on'
            tranche.save()
            
            log_activity(
                request,
                f"Modification tranche IRPP {tranche.numero_tranche}",
                'paie',
                'tranches_irg',
                tranche.id
            )
            
            messages.success(request, f'Tranche {tranche.numero_tranche} modifiée avec succès')
            return redirect('paie:bareme_irpp_liste')
            
        except (ValueError, InvalidOperation) as e:
            messages.error(request, f'Erreur de validation: {e}')
    
    return render(request, 'paie/bareme_irpp/form.html', {
        'tranche': tranche,
        'modification': True,
    })


@login_required
def bareme_irpp_supprimer(request, pk):
    """Supprimer une tranche IRPP"""
    tranche = get_object_or_404(TrancheRTS, pk=pk)
    
    if request.method == 'POST':
        numero = tranche.numero_tranche
        annee = tranche.annee_validite
        tranche.delete()
        
        log_activity(
            request,
            f"Suppression tranche IRPP {numero} - {annee}",
            'paie',
            'tranches_irg',
            pk
        )
        
        messages.success(request, f'Tranche {numero} supprimée')
        return redirect('paie:bareme_irpp_liste')
    
    return render(request, 'paie/bareme_irpp/supprimer.html', {
        'tranche': tranche,
    })


@login_required
def bareme_irpp_dupliquer(request):
    """Dupliquer le barème d'une année vers une autre"""
    if request.method == 'POST':
        annee_source = int(request.POST['annee_source'])
        annee_cible = int(request.POST['annee_cible'])
        
        if annee_source == annee_cible:
            messages.error(request, 'Les années source et cible doivent être différentes')
            return redirect('paie:bareme_irpp_liste')
        
        # Vérifier si des tranches existent déjà pour l'année cible
        if TrancheRTS.objects.filter(annee_validite=annee_cible).exists():
            messages.error(request, f'Des tranches existent déjà pour {annee_cible}')
            return redirect('paie:bareme_irpp_liste')
        
        # Dupliquer les tranches
        tranches_source = TrancheRTS.objects.filter(annee_validite=annee_source)
        count = 0
        for t in tranches_source:
            TrancheRTS.objects.create(
                numero_tranche=t.numero_tranche,
                borne_inferieure=t.borne_inferieure,
                borne_superieure=t.borne_superieure,
                taux_irg=t.taux_irg,
                annee_validite=annee_cible,
                date_debut_validite=date(annee_cible, 1, 1),
                actif=True
            )
            count += 1
        
        log_activity(
            request,
            f"Duplication barème IRPP {annee_source} vers {annee_cible}",
            'paie'
        )
        
        messages.success(request, f'{count} tranches dupliquées de {annee_source} vers {annee_cible}')
        return redirect('paie:bareme_irpp_liste')
    
    annees = TrancheRTS.objects.values_list(
        'annee_validite', flat=True
    ).distinct().order_by('-annee_validite')
    
    return render(request, 'paie/bareme_irpp/dupliquer.html', {
        'annees': annees,
        'annee_suivante': date.today().year + 1,
    })


@login_required
def simulateur_irpp(request):
    """Simulateur de calcul IRPP"""
    resultat = None
    
    if request.method == 'POST':
        try:
            salaire_brut = Decimal(request.POST['salaire_brut'].replace(' ', '').replace(',', '.'))
            annee = int(request.POST.get('annee', date.today().year))
            
            # Situation familiale
            situation = {
                'conjoint_charge': request.POST.get('conjoint_charge') == 'on',
                'nombre_enfants': int(request.POST.get('nombre_enfants', 0)),
                'nombre_ascendants': int(request.POST.get('nombre_ascendants', 0)),
            }
            
            # Calcul
            service = IRPPService(annee)
            resultat = service.simuler_irpp(salaire_brut)
            resultat['situation'] = situation
            
        except (ValueError, InvalidOperation) as e:
            messages.error(request, f'Erreur: {e}')
    
    # Charger le barème actuel pour affichage
    bareme = IRPPService.get_bareme_actuel()
    
    return render(request, 'paie/bareme_irpp/simulateur.html', {
        'resultat': resultat,
        'bareme': bareme,
        'annee': date.today().year,
    })


@login_required
def api_calculer_irpp(request):
    """API pour calculer l'IRPP (pour appels AJAX)"""
    try:
        salaire_brut = Decimal(request.GET.get('salaire', '0'))
        annee = int(request.GET.get('annee', date.today().year))
        
        service = IRPPService(annee)
        resultat = service.simuler_irpp(salaire_brut)
        
        # Convertir Decimal en float pour JSON
        return JsonResponse({
            'success': True,
            'salaire_brut': float(resultat['salaire_brut']),
            'cnss': float(resultat['cnss']),
            'base_imposable': float(resultat['base_imposable']),
            'irpp': float(resultat['irpp_net']),
            'salaire_net': float(resultat['salaire_net']),
            'details': [
                {
                    'tranche': d['tranche'],
                    'taux': float(d['taux']),
                    'montant': float(d['montant_imposable']),
                    'irpp': float(d['irpp'])
                }
                for d in resultat['details_tranches']
            ]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
