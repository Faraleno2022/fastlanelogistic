"""
Vues pour la gestion des licences
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from .models_licence import LicenceLocale, get_machine_id, get_licence_active, valider_cle_hmac


@csrf_exempt
def licence_activation(request):
    """Page d'activation de la licence"""
    
    # Vérifier si une licence est déjà active
    licence_existante = get_licence_active()
    if licence_existante:
        return redirect('dashboard:index')
    
    machine_id = get_machine_id()
    
    if request.method == 'POST':
        cle = request.POST.get('cle_licence', '').strip().upper()
        
        if not cle:
            messages.error(request, "Veuillez entrer une clé de licence.")
            return render(request, 'core/licence/activation.html', {'machine_id': machine_id})
        
        # Valider le format de la clé (XXXX-XXXX-XXXX-XXXX)
        if not valider_format_cle(cle):
            messages.error(request, "Format de clé invalide. Le format attendu est: XXXX-XXXX-XXXX-XXXX")
            return render(request, 'core/licence/activation.html', {'machine_id': machine_id})
        
        # Activer la licence
        resultat = activer_licence_locale(cle, machine_id)
        
        if resultat['success']:
            messages.success(request, f"✅ Licence activée avec succès! Bienvenue {resultat['nom_entreprise']}")
            return redirect('dashboard:index')
        else:
            messages.error(request, resultat['error'])
    
    return render(request, 'core/licence/activation.html', {
        'machine_id': machine_id,
    })


def licence_statut(request):
    """Affiche le statut de la licence"""
    licence = get_licence_active()
    
    return render(request, 'core/licence/statut.html', {
        'licence': licence,
        'machine_id': get_machine_id(),
    })


def licence_expiree(request):
    """Page affichée quand la licence a expiré"""
    licence = LicenceLocale.objects.first()
    
    return render(request, 'core/licence/expiree.html', {
        'licence': licence,
        'machine_id': get_machine_id(),
    })


def valider_format_cle(cle):
    """Valide le format de la clé de licence"""
    import re
    pattern = r'^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$'
    return bool(re.match(pattern, cle))


def activer_licence_locale(cle, machine_id):
    """
    Active une licence localement
    En mode offline, on fait confiance à la clé si elle a le bon format
    Pour plus de sécurité, vous pouvez ajouter une vérification en ligne
    """
    
    # Décoder les informations de la clé
    # Format simplifié: les 2 premiers caractères indiquent le plan
    # ST = Starter, PR = Pro, EN = Enterprise
    # Les 2 suivants indiquent la durée: TR = Trial, ME = Mensuel, AN = Annuel, PE = Perpétuel
    
    try:
        # Vérifier la signature HMAC - seules les clés générées par le développeur sont valides
        if not valider_cle_hmac(cle):
            return {
                'success': False,
                'error': "Clé de licence invalide. Contactez votre fournisseur pour obtenir une clé valide."
            }
        
        premier_segment = cle.split('-')[0]
        
        # Déterminer le plan
        if premier_segment.startswith('ST'):
            plan = 'starter'
            max_employes = 10
            max_utilisateurs = 2
        elif premier_segment.startswith('PR'):
            plan = 'pro'
            max_employes = 50
            max_utilisateurs = 5
        elif premier_segment.startswith('EN'):
            plan = 'enterprise'
            max_employes = 9999
            max_utilisateurs = 99
        else:
            # Plan par défaut basé sur la clé
            plan = 'starter'
            max_employes = 10
            max_utilisateurs = 2
        
        # Déterminer la durée
        deuxieme_segment = cle.split('-')[1] if len(cle.split('-')) > 1 else ''
        
        if deuxieme_segment.startswith('TR'):
            date_expiration = timezone.now() + timezone.timedelta(days=30)
            type_licence = 'Essai 30 jours'
        elif deuxieme_segment.startswith('ME'):
            date_expiration = timezone.now() + timezone.timedelta(days=30)
            type_licence = 'Mensuel'
        elif deuxieme_segment.startswith('AN'):
            date_expiration = timezone.now() + timezone.timedelta(days=365)
            type_licence = 'Annuel'
        elif deuxieme_segment.startswith('PE'):
            date_expiration = None  # Perpétuel
            type_licence = 'Perpétuel'
        else:
            # Par défaut: 1 an
            date_expiration = timezone.now() + timezone.timedelta(days=365)
            type_licence = 'Annuel'
        
        # Supprimer l'ancienne licence si elle existe
        LicenceLocale.objects.all().delete()
        
        # Créer la nouvelle licence
        licence = LicenceLocale.objects.create(
            cle_licence=cle,
            nom_entreprise=f"Client {cle[:4]}",  # Nom temporaire
            plan=plan,
            max_employes=max_employes,
            max_utilisateurs=max_utilisateurs,
            date_activation=timezone.now(),
            date_expiration=date_expiration,
            machine_id=machine_id,
        )
        
        return {
            'success': True,
            'nom_entreprise': licence.nom_entreprise,
            'plan': plan,
            'type_licence': type_licence,
            'date_expiration': date_expiration,
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Erreur lors de l'activation: {str(e)}"
        }


@csrf_exempt
def api_verifier_licence(request):
    """API pour vérifier le statut de la licence (pour intégration externe)"""
    licence = get_licence_active()
    
    if licence:
        return JsonResponse({
            'valide': True,
            'plan': licence.plan,
            'jours_restants': licence.jours_restants,
            'max_employes': licence.max_employes,
        })
    else:
        return JsonResponse({
            'valide': False,
            'message': 'Aucune licence active'
        })


@csrf_exempt
def licence_renouveler(request):
    """Page de renouvellement de la licence"""
    licence = LicenceLocale.objects.first()
    machine_id = get_machine_id()
    
    if not licence:
        messages.error(request, "Aucune licence à renouveler. Veuillez d'abord activer une licence.")
        return redirect('core:licence_activation')
    
    if request.method == 'POST':
        cle_renouvellement = request.POST.get('cle_renouvellement', '').strip().upper()
        
        if not cle_renouvellement:
            messages.error(request, "Veuillez entrer une clé de renouvellement.")
            return render(request, 'core/licence/renouveler.html', {
                'licence': licence,
                'machine_id': machine_id,
            })
        
        # Valider le format de la clé
        if not valider_format_cle(cle_renouvellement):
            messages.error(request, "Format de clé invalide. Le format attendu est: XXXX-XXXX-XXXX-XXXX")
            return render(request, 'core/licence/renouveler.html', {
                'licence': licence,
                'machine_id': machine_id,
            })
        
        # Renouveler la licence
        resultat = renouveler_licence_locale(licence, cle_renouvellement)
        
        if resultat['success']:
            messages.success(request, f"✅ Licence renouvelée avec succès! Nouvelle expiration: {resultat['date_expiration'].strftime('%d/%m/%Y')}")
            return redirect('core:licence_statut')
        else:
            messages.error(request, resultat['error'])
    
    return render(request, 'core/licence/renouveler.html', {
        'licence': licence,
        'machine_id': machine_id,
    })


def renouveler_licence_locale(licence, cle_renouvellement):
    """
    Renouvelle une licence existante avec une clé de renouvellement
    """
    try:
        # Vérifier la signature HMAC
        if not valider_cle_hmac(cle_renouvellement):
            return {
                'success': False,
                'error': "Clé de renouvellement invalide. Contactez votre fournisseur."
            }
        
        # Décoder la durée de renouvellement depuis la clé
        deuxieme_segment = cle_renouvellement.split('-')[1] if len(cle_renouvellement.split('-')) > 1 else ''
        
        if deuxieme_segment.startswith('ME'):
            duree_jours = 30
            type_renouvellement = 'Mensuel (+30 jours)'
        elif deuxieme_segment.startswith('AN'):
            duree_jours = 365
            type_renouvellement = 'Annuel (+1 an)'
        elif deuxieme_segment.startswith('PE'):
            # Licence perpétuelle
            licence.date_expiration = None
            licence.save()
            return {
                'success': True,
                'date_expiration': None,
                'type_renouvellement': 'Perpétuel',
            }
        else:
            # Par défaut: 1 an
            duree_jours = 365
            type_renouvellement = 'Annuel (+1 an)'
        
        # Calculer la nouvelle date d'expiration
        if licence.date_expiration and licence.date_expiration > timezone.now():
            # Ajouter à partir de la date d'expiration actuelle
            nouvelle_expiration = licence.date_expiration + timezone.timedelta(days=duree_jours)
        else:
            # Ajouter à partir de maintenant
            nouvelle_expiration = timezone.now() + timezone.timedelta(days=duree_jours)
        
        licence.date_expiration = nouvelle_expiration
        licence.save()
        
        return {
            'success': True,
            'date_expiration': nouvelle_expiration,
            'type_renouvellement': type_renouvellement,
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Erreur lors du renouvellement: {str(e)}"
        }
