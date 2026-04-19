from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import render, get_object_or_404, redirect

from apps.core.utils import format_protected_error

from .models import Contrat, Facture
from .forms import ContratForm, FactureForm


@login_required
def liste_factures(request):
    factures = Facture.objects.all().select_related("contrat")
    return render(request, "facturation/liste_factures.html", {"factures": factures})


@login_required
def detail_facture(request, numero):
    facture = get_object_or_404(Facture, numero=numero)
    if request.method == "POST" and request.POST.get("action") == "recalculer":
        facture.recalculer()
        facture.save()
        messages.success(request, f"Facture {facture.numero} recalculée avec succès.")
        return redirect("facturation:detail", numero=facture.numero)
    return render(request, "facturation/detail_facture.html", {"facture": facture})


@login_required
def liste_contrats(request):
    contrats = Contrat.objects.all()
    return render(request, "facturation/liste_contrats.html", {"contrats": contrats})


# ---------- Contrats ----------

@login_required
def contrat_create(request):
    form = ContratForm(request.POST or None)
    if form.is_valid():
        obj = form.save()
        messages.success(request, f"Contrat {obj.code} créé.")
        return redirect("facturation:contrats")
    return render(request, "_form_generic.html", {
        "form": form, "titre": "Nouveau contrat",
        "icone": "file-earmark-plus", "retour_url": "facturation:contrats",
    })


@login_required
def contrat_edit(request, pk):
    obj = get_object_or_404(Contrat, pk=pk)
    form = ContratForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, f"Contrat {obj.code} mis à jour.")
        return redirect("facturation:contrats")
    return render(request, "_form_generic.html", {
        "form": form, "titre": f"Modifier contrat {obj.code}",
        "icone": "pencil", "retour_url": "facturation:contrats",
    })


@login_required
def contrat_delete(request, pk):
    obj = get_object_or_404(Contrat, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
        except ProtectedError as e:
            messages.error(request, format_protected_error(e))
            return redirect("facturation:contrats")
        messages.success(request, f"Contrat {obj.code} supprimé.")
        return redirect("facturation:contrats")
    return render(request, "confirm_delete.html", {
        "objet": obj, "titre": "Supprimer le contrat",
        "message": f"Supprimer le contrat {obj.code} — {obj.client} ?",
        "retour_url": "facturation:contrats",
    })


# ---------- Factures ----------

@login_required
def facture_create(request):
    form = FactureForm(request.POST or None)
    if form.is_valid():
        obj = form.save()
        obj.recalculer()
        obj.save()
        messages.success(request, f"Facture {obj.numero} créée et calculée.")
        return redirect("facturation:detail", numero=obj.numero)
    return render(request, "_form_generic.html", {
        "form": form, "titre": "Nouvelle facture",
        "icone": "receipt", "retour_url": "facturation:liste",
    })


@login_required
def facture_edit(request, numero):
    obj = get_object_or_404(Facture, numero=numero)
    form = FactureForm(request.POST or None, instance=obj)
    if form.is_valid():
        obj = form.save()
        obj.recalculer()
        obj.save()
        messages.success(request, f"Facture {obj.numero} mise à jour.")
        return redirect("facturation:detail", numero=obj.numero)
    return render(request, "_form_generic.html", {
        "form": form, "titre": f"Modifier facture {obj.numero}",
        "icone": "pencil", "retour_url": "facturation:liste",
    })


@login_required
def facture_delete(request, numero):
    obj = get_object_or_404(Facture, numero=numero)
    if request.method == "POST":
        try:
            obj.delete()
        except ProtectedError as e:
            messages.error(request, format_protected_error(e))
            return redirect("facturation:liste")
        messages.success(request, f"Facture {numero} supprimée.")
        return redirect("facturation:liste")
    return render(request, "confirm_delete.html", {
        "objet": obj, "titre": "Supprimer la facture",
        "message": f"Supprimer la facture {obj.numero} ?",
        "retour_url": "facturation:liste",
    })
