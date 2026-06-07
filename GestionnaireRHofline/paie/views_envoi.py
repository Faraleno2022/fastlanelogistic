"""
Vues pour l'envoi des bulletins de paie par email et WhatsApp
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from paie.models import BulletinPaie
from paie.services_envoi import BulletinEnvoiService
from core.views import log_activity


@login_required
def envoyer_bulletin_email(request, pk):
    """Envoyer un bulletin par email"""
    bulletin = get_object_or_404(
        BulletinPaie, 
        pk=pk, 
        employe__entreprise=request.user.entreprise
    )
    
    # Récupérer les paramètres de paie
    from paie.models import ParametrePaie
    try:
        params = ParametrePaie.objects.filter(entreprise=request.user.entreprise).first()
    except:
        params = None
    
    if request.method == 'POST':
        email_destinataire = request.POST.get('email', bulletin.employe.email_professionnel)
        message_perso = request.POST.get('message', '')
        
        if not email_destinataire:
            messages.error(request, "Adresse email non renseignée")
            return redirect('paie:detail_bulletin', pk=pk)
        
        service = BulletinEnvoiService(request.user.entreprise)
        success, msg = service.envoyer_email(
            bulletin, 
            email_destinataire, 
            params,
            message_perso if message_perso else None
        )
        
        if success:
            log_activity(
                request,
                f"Envoi bulletin {bulletin.numero_bulletin} par email à {email_destinataire}",
                'paie'
            )
            messages.success(request, f"Bulletin envoyé par email à {email_destinataire}")
        else:
            messages.error(request, msg)
        
        return redirect('paie:detail_bulletin', pk=pk)
    
    return render(request, 'paie/bulletins/envoyer_email.html', {
        'bulletin': bulletin,
        'email_defaut': bulletin.employe.email_professionnel,
    })


@login_required
def envoyer_bulletin_whatsapp(request, pk):
    """Générer le lien WhatsApp pour un bulletin"""
    bulletin = get_object_or_404(
        BulletinPaie, 
        pk=pk, 
        employe__entreprise=request.user.entreprise
    )
    
    service = BulletinEnvoiService(request.user.entreprise)
    
    if request.method == 'POST':
        telephone = request.POST.get('telephone', bulletin.employe.telephone_principal)
        message_perso = request.POST.get('message', '')
        
        lien, msg = service.generer_lien_whatsapp(
            bulletin, 
            telephone,
            message_perso if message_perso else None
        )
        
        if lien:
            log_activity(
                request,
                f"Génération lien WhatsApp bulletin {bulletin.numero_bulletin}",
                'paie'
            )
            return JsonResponse({'success': True, 'lien': lien})
        else:
            return JsonResponse({'success': False, 'error': msg})
    
    # Générer le token public pour le PDF
    try:
        token = bulletin.generer_token_public()
        lien_pdf = f"https://www.guineerh.space/paie/bulletins/public/{token}/"
    except Exception:
        # Si le champ token_public n'existe pas encore (migration non appliquée)
        lien_pdf = ""
    
    # Nom de l'entreprise
    nom_entreprise = request.user.entreprise.nom_entreprise if request.user.entreprise else 'Service RH'
    
    # Message par défaut avec lien PDF
    if lien_pdf:
        message_defaut = f"""Bonjour {bulletin.employe.prenoms},

Veuillez trouver votre bulletin de paie pour la période {bulletin.periode}.

📄 *Télécharger votre bulletin PDF:*
{lien_pdf}

💰 *Détails:*
- Salaire brut: {bulletin.salaire_brut:,.0f} GNF
- Net à payer: {bulletin.net_a_payer:,.0f} GNF

Cordialement,
{nom_entreprise}"""
    else:
        message_defaut = f"""Bonjour {bulletin.employe.prenoms},

Veuillez trouver votre bulletin de paie pour la période {bulletin.periode}.

💰 *Détails:*
- Salaire brut: {bulletin.salaire_brut:,.0f} GNF
- Net à payer: {bulletin.net_a_payer:,.0f} GNF

Cordialement,
{nom_entreprise}"""
    
    return render(request, 'paie/bulletins/envoyer_whatsapp.html', {
        'bulletin': bulletin,
        'telephone_defaut': bulletin.employe.telephone_principal,
        'message_defaut': message_defaut,
        'lien_pdf': lien_pdf,
    })


@login_required
def envoyer_bulletins_masse(request):
    """Interface pour envoi en masse des bulletins"""
    entreprise = request.user.entreprise
    
    # Filtrer les bulletins
    periode = request.GET.get('periode', '')
    statut = request.GET.get('statut', 'valide')
    
    bulletins = BulletinPaie.objects.filter(
        employe__entreprise=entreprise
    ).select_related('employe')
    
    if periode:
        bulletins = bulletins.filter(periode=periode)
    if statut:
        bulletins = bulletins.filter(statut_bulletin=statut)
    
    bulletins = bulletins.order_by('-periode', 'employe__nom')
    
    # Périodes disponibles
    periodes = BulletinPaie.objects.filter(
        employe__entreprise=entreprise
    ).values_list('periode', flat=True).distinct().order_by('-periode')
    
    return render(request, 'paie/bulletins/envoyer_masse.html', {
        'bulletins': bulletins,
        'periodes': periodes,
        'periode_filtre': periode,
        'statut_filtre': statut,
    })


@login_required
@require_POST
def envoyer_masse_email(request):
    """Envoyer plusieurs bulletins par email"""
    bulletin_ids = request.POST.getlist('bulletins')
    
    if not bulletin_ids:
        messages.error(request, "Aucun bulletin sélectionné")
        return redirect('paie:envoyer_masse')
    
    bulletins = BulletinPaie.objects.filter(
        id__in=bulletin_ids,
        employe__entreprise=request.user.entreprise
    ).select_related('employe')
    
    # Paramètres de paie
    from paie.models import ParametrePaie
    try:
        params = ParametrePaie.objects.filter(entreprise=request.user.entreprise).first()
    except:
        params = None
    
    message_perso = request.POST.get('message', '')
    
    service = BulletinEnvoiService(request.user.entreprise)
    resultats = service.envoyer_masse_email(
        bulletins, 
        params,
        message_perso if message_perso else None
    )
    
    nb_succes = len(resultats['succes'])
    nb_echecs = len(resultats['echecs'])
    
    log_activity(
        request,
        f"Envoi masse emails: {nb_succes} succès, {nb_echecs} échecs",
        'paie'
    )
    
    if nb_succes > 0:
        messages.success(request, f"{nb_succes} bulletin(s) envoyé(s) par email")
    if nb_echecs > 0:
        messages.warning(request, f"{nb_echecs} envoi(s) échoué(s)")
    
    return render(request, 'paie/bulletins/resultats_envoi.html', {
        'resultats': resultats,
        'type_envoi': 'email',
    })


@login_required
@require_POST
def generer_liens_whatsapp_masse(request):
    """Générer les liens WhatsApp pour plusieurs bulletins"""
    bulletin_ids = request.POST.getlist('bulletins')
    
    if not bulletin_ids:
        messages.error(request, "Aucun bulletin sélectionné")
        return redirect('paie:envoyer_masse')
    
    bulletins = BulletinPaie.objects.filter(
        id__in=bulletin_ids,
        employe__entreprise=request.user.entreprise
    ).select_related('employe')
    
    service = BulletinEnvoiService(request.user.entreprise)
    liens = service.generer_liens_whatsapp_masse(bulletins)
    
    log_activity(
        request,
        f"Génération liens WhatsApp pour {len(bulletin_ids)} bulletins",
        'paie'
    )
    
    return render(request, 'paie/bulletins/liens_whatsapp.html', {
        'liens': liens,
    })


@login_required
def modal_envoyer_bulletin(request, pk):
    """Modal pour choisir le mode d'envoi"""
    bulletin = get_object_or_404(
        BulletinPaie, 
        pk=pk, 
        employe__entreprise=request.user.entreprise
    )
    
    return render(request, 'paie/bulletins/modal_envoyer.html', {
        'bulletin': bulletin,
    })
