from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Parametres
from .forms import ParametresForm
from .session_helpers import set_contrat_actif, clear_contrat_actif


@login_required
def parametres_edit(request):
    obj = Parametres.load()
    form = ParametresForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Paramètres enregistrés.")
        return redirect("core:parametres")
    return render(request, "_form_generic.html", {
        "form": form, "titre": "Paramètres de l'application",
        "icone": "gear", "retour_url": "dashboard:home",
    })


@login_required
@require_POST
def set_contrat_actif_view(request):
    """Fixe le contrat actif en session. Toutes les nouvelles saisies seront
    pré-remplies avec ce contrat.

    POST params :
      - code: code du contrat (ex: CTR-2026-CBG) ; "" ou absent → efface
      - next: URL de redirection (optionnel, sinon HTTP_REFERER ou home)
    """
    from apps.facturation.models import Contrat
    code = (request.POST.get("code") or "").strip()
    nxt = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"

    if not code:
        clear_contrat_actif(request)
        messages.info(request, "Contrat actif effacé — saisie libre.")
        return redirect(nxt)

    contrat = get_object_or_404(Contrat, code=code, actif=True)
    set_contrat_actif(request, contrat)
    messages.success(
        request,
        f"Contrat actif : {contrat.code} — {contrat.client}. "
        f"Les nouvelles saisies seront automatiquement imputées à ce contrat."
    )
    return redirect(nxt)


@login_required
@require_POST
def clear_contrat_actif_view(request):
    """Efface le contrat actif."""
    clear_contrat_actif(request)
    messages.info(request, "Contrat actif effacé — saisie libre.")
    return redirect(request.META.get("HTTP_REFERER") or "/")
