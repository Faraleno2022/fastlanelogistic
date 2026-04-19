import calendar
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count, Q, ProtectedError

from apps.core.utils import format_protected_error

from .models import Employe, Attendance, HeureSup
from .forms import EmployeForm, AttendanceForm, HeureSupForm


# ---------- Employés ----------

@login_required
def employe_create(request):
    form = EmployeForm(request.POST or None)
    if form.is_valid():
        obj = form.save()
        messages.success(request, f"Employé {obj.prenom} {obj.nom} ajouté.")
        return redirect("rh:liste_employes")
    return render(request, "_form_generic.html", {
        "form": form, "titre": "Ajouter un employé",
        "icone": "person-plus", "retour_url": "rh:liste_employes",
    })


@login_required
def employe_edit(request, pk):
    emp = get_object_or_404(Employe, pk=pk)
    form = EmployeForm(request.POST or None, instance=emp)
    if form.is_valid():
        form.save()
        messages.success(request, f"Employé {emp.prenom} {emp.nom} mis à jour.")
        return redirect("rh:liste_employes")
    return render(request, "_form_generic.html", {
        "form": form, "titre": f"Modifier {emp.prenom} {emp.nom}",
        "icone": "pencil", "retour_url": "rh:liste_employes",
    })


@login_required
def employe_delete(request, pk):
    emp = get_object_or_404(Employe, pk=pk)
    if request.method == "POST":
        try:
            emp.delete()
        except ProtectedError as e:
            messages.error(request, format_protected_error(e))
            return redirect("rh:liste_employes")
        messages.success(request, f"Employé supprimé.")
        return redirect("rh:liste_employes")
    return render(request, "confirm_delete.html", {
        "objet": emp, "titre": "Supprimer l'employé",
        "message": f"Supprimer définitivement l'employé {emp.prenom} {emp.nom} ({emp.code}) ?",
        "retour_url": "rh:liste_employes",
    })


# ---------- Attendance ----------

@login_required
def attendance_create(request):
    form = AttendanceForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Pointage enregistré.")
        return redirect("rh:attendance")
    return render(request, "_form_generic.html", {
        "form": form, "titre": "Ajouter un pointage",
        "icone": "calendar-check", "retour_url": "rh:attendance",
    })


@login_required
def attendance_edit(request, pk):
    obj = get_object_or_404(Attendance, pk=pk)
    form = AttendanceForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Pointage mis à jour.")
        return redirect("rh:attendance")
    return render(request, "_form_generic.html", {
        "form": form, "titre": "Modifier le pointage",
        "icone": "pencil", "retour_url": "rh:attendance",
    })


@login_required
def attendance_delete(request, pk):
    obj = get_object_or_404(Attendance, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
        except ProtectedError as e:
            messages.error(request, format_protected_error(e))
            return redirect("rh:attendance")
        messages.success(request, "Pointage supprimé.")
        return redirect("rh:attendance")
    return render(request, "confirm_delete.html", {
        "objet": obj, "titre": "Supprimer le pointage",
        "message": f"Supprimer le pointage de {obj.employe} du {obj.date} ?",
        "retour_url": "rh:attendance",
    })


# ---------- Heures supplémentaires ----------

@login_required
def hs_create(request):
    form = HeureSupForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Heures supplémentaires enregistrées.")
        return redirect("rh:heures_sup")
    return render(request, "_form_generic.html", {
        "form": form, "titre": "Ajouter des heures supplémentaires",
        "icone": "clock-history", "retour_url": "rh:heures_sup",
    })


@login_required
def hs_edit(request, pk):
    obj = get_object_or_404(HeureSup, pk=pk)
    form = HeureSupForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Heures supplémentaires mises à jour.")
        return redirect("rh:heures_sup")
    return render(request, "_form_generic.html", {
        "form": form, "titre": "Modifier les heures supplémentaires",
        "icone": "pencil", "retour_url": "rh:heures_sup",
    })


@login_required
def hs_delete(request, pk):
    obj = get_object_or_404(HeureSup, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
        except ProtectedError as e:
            messages.error(request, format_protected_error(e))
            return redirect("rh:heures_sup")
        messages.success(request, "Heures supplémentaires supprimées.")
        return redirect("rh:heures_sup")
    return render(request, "confirm_delete.html", {
        "objet": obj, "titre": "Supprimer",
        "message": f"Supprimer les HS de {obj.employe} du {obj.date} ?",
        "retour_url": "rh:heures_sup",
    })


@login_required
def liste_employes(request):
    employes = Employe.objects.all().order_by("-created_at", "code")
    return render(request, "rh/liste_employes.html", {"employes": employes})


@login_required
def attendance_mensuel(request):
    today = date.today()
    try:
        mois = int(request.GET.get("mois", today.month))
        annee = int(request.GET.get("annee", today.year))
    except (ValueError, TypeError):
        mois, annee = today.month, today.year

    nb_jours = calendar.monthrange(annee, mois)[1]
    jours = [date(annee, mois, d) for d in range(1, nb_jours + 1)]

    employes = Employe.objects.filter(actif=True)
    # construire {employe_id: {date: code}}
    start = date(annee, mois, 1)
    end = date(annee, mois, nb_jours)
    pointages = Attendance.objects.filter(date__gte=start, date__lte=end)
    grid = {e.id: {} for e in employes}
    for p in pointages:
        grid.setdefault(p.employe_id, {})[p.date] = p.code

    rows = []
    for e in employes:
        pres = 0
        abs_ = 0
        cong = 0
        mal = 0
        dim_t = 0
        jours_codes = []
        for j in jours:
            c = grid.get(e.id, {}).get(j, "")
            jours_codes.append((j, c))
            if c == "P" or c == "D":
                pres += 1
            if c == "A":
                abs_ += 1
            if c == "C":
                cong += 1
            if c == "M":
                mal += 1
            if c == "D":
                dim_t += 1
        salaire_base = (pres - dim_t) * (e.salaire_jour or Decimal(0))
        montant_dim = dim_t * (e.salaire_jour or Decimal(0)) * Decimal(2)
        salaire_net = salaire_base + montant_dim
        rows.append({
            "employe": e, "jours_codes": jours_codes,
            "pres": pres, "abs": abs_, "cong": cong, "mal": mal,
            "dim_t": dim_t, "salaire_base": salaire_base,
            "montant_dim": montant_dim, "salaire_net": salaire_net,
        })

    return render(request, "rh/attendance.html", {
        "rows": rows, "jours": jours,
        "mois": mois, "annee": annee, "nb_jours": nb_jours,
        "mois_label": calendar.month_name[mois].capitalize(),
    })


@login_required
def liste_heures_sup(request):
    today = date.today()
    try:
        mois = int(request.GET.get("mois", today.month))
        annee = int(request.GET.get("annee", today.year))
    except (ValueError, TypeError):
        mois, annee = today.month, today.year

    hs = HeureSup.objects.filter(date__month=mois, date__year=annee).select_related("employe")
    total_montant = sum((h.montant for h in hs), Decimal(0))
    total_heures = sum((h.nb_heures for h in hs), Decimal(0))

    # Synthèse par employé
    synth = {}
    for h in hs:
        s = synth.setdefault(h.employe_id, {"employe": h.employe, "nb_heures": Decimal(0), "montant": Decimal(0), "count": 0})
        s["nb_heures"] += h.nb_heures
        s["montant"] += h.montant
        s["count"] += 1

    return render(request, "rh/heures_sup.html", {
        "heures": hs, "total_montant": total_montant,
        "total_heures": total_heures, "synth": synth.values(),
        "mois": mois, "annee": annee,
        "mois_label": calendar.month_name[mois].capitalize(),
    })
