from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count, ProtectedError

from apps.core.utils import format_protected_error

from .models import Camion
from .forms import CamionForm


@login_required
def liste_camions(request):
    camions = Camion.objects.all().order_by("-created_at", "code")
    totaux = camions.aggregate(
        total_prix=Sum("prix_achat"),
        total_capacite=Sum("capacite_tonnes"),
        nombre=Count("id"),
    )
    total_amort_mensuel = sum((c.amortissement_mensuel for c in camions), 0)
    return render(request, "flotte/liste_camions.html", {
        "camions": camions,
        "totaux": totaux,
        "total_amort_mensuel": total_amort_mensuel,
    })


@login_required
def detail_camion(request, code):
    camion = get_object_or_404(Camion, code=code)
    tableau = camion.tableau_amortissement()
    return render(request, "flotte/detail_camion.html", {
        "camion": camion,
        "tableau": tableau,
    })


@login_required
def amortissement_global(request):
    camions = Camion.objects.all()
    data = []
    for c in camions:
        data.append({
            "camion": c,
            "rows": c.tableau_amortissement(),
        })
    return render(request, "flotte/amortissement.html", {"data": data})


@login_required
def camion_create(request):
    form = CamionForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Camion ajouté avec succès.")
        return redirect("flotte:liste")
    return render(request, "flotte/form_camion.html", {"form": form, "titre": "Ajouter un camion"})


@login_required
def camion_edit(request, code):
    camion = get_object_or_404(Camion, code=code)
    form = CamionForm(request.POST or None, instance=camion)
    if form.is_valid():
        form.save()
        messages.success(request, f"Camion {camion.code} mis à jour.")
        return redirect("flotte:liste")
    return render(request, "flotte/form_camion.html", {"form": form, "titre": f"Modifier {camion.code}", "camion": camion})


@login_required
def camion_delete(request, code):
    camion = get_object_or_404(Camion, code=code)
    if request.method == "POST":
        try:
            camion.delete()
        except ProtectedError as e:
            messages.error(request, format_protected_error(e))
            return redirect("flotte:liste")
        messages.success(request, f"Camion {code} supprimé.")
        return redirect("flotte:liste")
    return render(request, "confirm_delete.html", {
        "objet": camion, "titre": "Supprimer le camion",
        "message": f"Êtes-vous sûr de vouloir supprimer le camion {camion.code} — {camion.immatriculation} ?",
        "retour_url": "flotte:liste",
    })
