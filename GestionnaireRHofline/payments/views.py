from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
import json
import logging

from .models import PlanAbonnement, Transaction, Abonnement
from .services import CinetPayService, activer_abonnement
from .services_paycard import PaycardService

logger = logging.getLogger(__name__)


@login_required
def plans_liste(request):
    """Affiche la liste des plans d'abonnement disponibles"""
    plans = PlanAbonnement.objects.filter(actif=True).order_by('ordre', 'prix_mensuel')
    
    # Abonnement actuel de l'entreprise
    abonnement_actuel = None
    if hasattr(request.user, 'entreprise') and request.user.entreprise:
        try:
            abonnement_actuel = Abonnement.objects.get(entreprise=request.user.entreprise)
        except Abonnement.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Erreur récupération abonnement: {e}")
    
    return render(request, 'payments/plans_liste.html', {
        'plans': plans,
        'abonnement_actuel': abonnement_actuel,
    })


@login_required
def checkout(request, plan_slug):
    """Page de checkout pour un plan"""
    plan = get_object_or_404(PlanAbonnement, slug=plan_slug, actif=True)
    
    if not request.user.entreprise:
        messages.error(request, "Vous devez être associé à une entreprise pour souscrire à un abonnement.")
        return redirect('payments:plans')
    
    # Vérifier si c'est un nouveau abonnement ou un upgrade
    type_transaction = 'abonnement'
    try:
        abonnement = Abonnement.objects.get(entreprise=request.user.entreprise)
        if abonnement.est_actif:
            type_transaction = 'upgrade' if plan.prix_mensuel > abonnement.plan.prix_mensuel else 'renouvellement'
    except Abonnement.DoesNotExist:
        pass
    
    if request.method == 'POST':
        duree = request.POST.get('duree', 'mensuel')
        duree_mois = 12 if duree == 'annuel' else 1
        montant = plan.prix_annuel if duree == 'annuel' else plan.prix_mensuel
        payment_method = request.POST.get('payment_method', '')  # ORANGE_MONEY, MOMO, CREDIT_CARD, PAYCARD
        passerelle = request.POST.get('passerelle', 'paycard')
        
        # Créer la transaction
        transaction = Transaction.objects.create(
            entreprise=request.user.entreprise,
            plan=plan,
            type_transaction=type_transaction,
            montant=montant,
            duree_mois=duree_mois,
            passerelle=passerelle,
            cree_par=request.user,
        )
        
        # URLs de callback
        base_url = request.build_absolute_uri('/')[:-1]
        
        if passerelle == 'paycard':
            # --- Paycard ---
            callback_url = f"{base_url}{reverse('payments:paycard_callback')}?ref={transaction.reference}"
            service = PaycardService()
            result = service.creer_paiement(transaction, callback_url, payment_method or None)
        else:
            # --- CinetPay (legacy) ---
            return_url = f"{base_url}{reverse('payments:success')}?ref={transaction.reference}"
            cancel_url = f"{base_url}{reverse('payments:cancel')}?ref={transaction.reference}"
            notify_url = f"{base_url}{reverse('payments:webhook')}"
            service = CinetPayService()
            result = service.creer_paiement(transaction, return_url, cancel_url, notify_url)
        
        if result.get('success'):
            if result.get('simulation'):
                return redirect('payments:simulate', token=result['token'])
            return redirect(result['url'])
        else:
            messages.error(request, f"Erreur lors de l'initialisation du paiement: {result.get('error')}")
            transaction.statut = 'failed'
            transaction.response_message = result.get('error')
            transaction.save()
            return redirect('payments:checkout', plan_slug=plan_slug)
    
    return render(request, 'payments/checkout.html', {
        'plan': plan,
        'type_transaction': type_transaction,
    })


@login_required
def simulate_payment(request, token):
    """Page de simulation de paiement (mode test)"""
    transaction = get_object_or_404(Transaction, token_paydunya=token)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'pay':
            # Simuler un paiement réussi
            transaction.methode_paiement = 'orange_money'
            activer_abonnement(transaction)
            messages.success(request, "Paiement simulé avec succès!")
            return redirect(f"{reverse('payments:success')}?ref={transaction.reference}")
        else:
            # Annuler
            transaction.statut = 'cancelled'
            transaction.save()
            messages.warning(request, "Paiement annulé.")
            return redirect(f"{reverse('payments:cancel')}?ref={transaction.reference}")
    
    return render(request, 'payments/simulate.html', {
        'transaction': transaction,
    })


@login_required
def payment_success(request):
    """Page de succès après paiement"""
    reference = request.GET.get('ref')
    token = request.GET.get('token')
    
    transaction = None
    if reference:
        transaction = Transaction.objects.filter(reference=reference).first()
    elif token:
        transaction = Transaction.objects.filter(token_paydunya=token).first()
    
    # Vérifier le paiement si pas encore confirmé
    if transaction and transaction.statut == 'pending':
        if getattr(transaction, 'passerelle', '') == 'paycard':
            service = PaycardService()
            result = service.verifier_paiement(transaction.reference)
        else:
            service = CinetPayService()
            result = service.verifier_paiement(f"GRH-{transaction.reference}", transaction.token_paydunya)
        
        if result.get('success') and result.get('status') == 'completed':
            activer_abonnement(transaction)
    
    return render(request, 'payments/success.html', {
        'transaction': transaction,
    })


@login_required
def payment_cancel(request):
    """Page d'annulation de paiement"""
    reference = request.GET.get('ref')
    transaction = None
    
    if reference:
        transaction = Transaction.objects.filter(reference=reference).first()
        if transaction and transaction.statut == 'pending':
            transaction.statut = 'cancelled'
            transaction.save()
    
    return render(request, 'payments/cancel.html', {
        'transaction': transaction,
    })


@csrf_exempt
@require_POST
def webhook(request):
    """Webhook pour recevoir les notifications PayDunya"""
    try:
        data = json.loads(request.body)
        logger.info(f"Webhook PayDunya reçu: {data}")
        
        # Extraire les informations
        token = data.get('token') or data.get('invoice', {}).get('token')
        status = data.get('status') or data.get('invoice', {}).get('status')
        
        if not token:
            logger.warning("Webhook sans token")
            return JsonResponse({'status': 'error', 'message': 'Token manquant'}, status=400)
        
        # Trouver la transaction
        transaction = Transaction.objects.filter(token_paydunya=token).first()
        
        if not transaction:
            logger.warning(f"Transaction non trouvée pour token: {token}")
            return JsonResponse({'status': 'error', 'message': 'Transaction non trouvée'}, status=404)
        
        # Mettre à jour selon le statut
        if status == 'completed':
            if transaction.statut != 'completed':
                activer_abonnement(transaction)
                logger.info(f"Abonnement activé pour transaction: {transaction.reference}")
        elif status == 'failed':
            transaction.statut = 'failed'
            transaction.response_message = data.get('response_text', 'Paiement échoué')
            transaction.save()
        elif status == 'cancelled':
            transaction.statut = 'cancelled'
            transaction.save()
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError:
        logger.error("Webhook: JSON invalide")
        return JsonResponse({'status': 'error', 'message': 'JSON invalide'}, status=400)
    except Exception as e:
        logger.exception(f"Erreur webhook: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def historique_transactions(request):
    """Historique des transactions de l'entreprise"""
    if not request.user.entreprise:
        messages.error(request, "Vous n'êtes associé à aucune entreprise.")
        return redirect('dashboard:index')
    
    transactions = Transaction.objects.filter(
        entreprise=request.user.entreprise
    ).select_related('plan').order_by('-date_creation')
    
    return render(request, 'payments/historique.html', {
        'transactions': transactions,
    })


def paycard_callback(request):
    """
    Callback GET de Paycard après paiement.
    Paycard envoie : ?paycard-operation-reference=REF&ref=REF
    """
    # Récupérer la référence (Paycard envoie paycard-operation-reference)
    reference = (
        request.GET.get('paycard-operation-reference')
        or request.GET.get('ref')
    )

    if not reference:
        messages.error(request, "Référence de paiement manquante.")
        return redirect('payments:plans')

    transaction = Transaction.objects.filter(reference=reference).first()
    if not transaction:
        messages.error(request, "Transaction introuvable.")
        return redirect('payments:plans')

    # Vérifier le statut auprès de Paycard
    if transaction.statut == 'pending':
        service = PaycardService()
        result = service.verifier_paiement(reference)

        if result.get('success'):
            status = result.get('status', 'pending')
            if status == 'completed':
                # Mapper la méthode de paiement
                pm = result.get('payment_method', '')
                method_map = {
                    'ORANGE_MONEY': 'orange_money',
                    'MOMO': 'mtn_money',
                    'CREDIT_CARD': 'visa',
                    'PAYCARD': 'paycard',
                }
                transaction.methode_paiement = method_map.get(pm, 'paycard')
                transaction.response_code = 'success'
                transaction.response_message = json.dumps(result.get('raw_data', {}))
                transaction.save(update_fields=['methode_paiement', 'response_code', 'response_message'])
                activer_abonnement(transaction)
                messages.success(request, "Paiement effectué avec succès !")
                return redirect(f"{reverse('payments:success')}?ref={reference}")
            elif status == 'failed':
                transaction.statut = 'failed'
                transaction.response_message = 'Paiement refusé par Paycard'
                transaction.save()
                messages.error(request, "Le paiement a échoué.")
                return redirect(f"{reverse('payments:cancel')}?ref={reference}")
        else:
            logger.warning(f"Paycard callback: vérification échouée pour {reference}")

    # Si déjà complété ou en attente
    if transaction.statut == 'completed':
        return redirect(f"{reverse('payments:success')}?ref={reference}")

    return redirect(f"{reverse('payments:cancel')}?ref={reference}")


@login_required
def mon_abonnement(request):
    """Affiche l'abonnement actuel de l'entreprise"""
    if not request.user.entreprise:
        messages.error(request, "Vous n'êtes associé à aucune entreprise.")
        return redirect('dashboard:index')
    
    abonnement = None
    try:
        abonnement = Abonnement.objects.select_related('plan', 'derniere_transaction').get(
            entreprise=request.user.entreprise
        )
    except Abonnement.DoesNotExist:
        pass
    
    plans = PlanAbonnement.objects.filter(actif=True).order_by('ordre')
    
    return render(request, 'payments/mon_abonnement.html', {
        'abonnement': abonnement,
        'plans': plans,
    })
