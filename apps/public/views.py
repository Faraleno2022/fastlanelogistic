from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import AppelOffreForm, ContactForm, EvenementForm
from .models import AppelOffre, ContactMessage, Evenement, PageAPropos


def home(request):
    aujourdhui = timezone.localdate()
    prochains_events = (Evenement.objects
                        .filter(statut="publie", date_evenement__gte=aujourdhui)
                        .order_by("date_evenement")[:3])
    derniers_events = (Evenement.objects
                       .filter(statut="publie")
                       .order_by("-date_evenement")[:3])
    appels_ouverts = (AppelOffre.objects
                      .filter(statut="ouvert", date_limite__gte=aujourdhui)
                      .order_by("date_limite")[:3])

    # Flotte — aperçu public (masque volontairement les prix / infos sensibles)
    return render(request, "public/home.html", {
        "prochains_events": prochains_events,
        "derniers_events": derniers_events,
        "appels_ouverts": appels_ouverts,
    })


def a_propos(request):
    page = PageAPropos.load()
    return render(request, "public/a_propos.html", {"page": page})


def evenements_liste(request):
    evts = Evenement.objects.filter(statut="publie")
    return render(request, "public/evenements_liste.html", {"evenements": evts})


def evenement_detail(request, slug):
    evt = get_object_or_404(Evenement, slug=slug, statut="publie")
    return render(request, "public/evenement_detail.html", {"evt": evt})


def appels_offres_liste(request):
    aujourdhui = timezone.localdate()
    appels = AppelOffre.objects.exclude(statut="brouillon")
    ouverts = appels.filter(statut="ouvert", date_limite__gte=aujourdhui)
    clos = appels.exclude(pk__in=ouverts.values("pk"))
    return render(request, "public/appels_offres_liste.html", {
        "ouverts": ouverts,
        "clos": clos,
    })


def appel_offre_detail(request, slug):
    ao = get_object_or_404(AppelOffre, slug=slug)
    if ao.statut == "brouillon":
        # Les brouillons ne sont pas accessibles au public
        from django.http import Http404
        raise Http404
    return render(request, "public/appel_offre_detail.html", {"ao": ao})


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def contact(request):
    page = PageAPropos.load()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.ip = _client_ip(request)
            msg.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
            msg.save()

            # Tentative d'envoi d'e-mail (silencieux si SMTP non configuré)
            try:
                dest = page.email or getattr(settings, "DEFAULT_FROM_EMAIL", "") \
                       or "contact@fastlanelogisticgn.com"
                from_addr = getattr(settings, "DEFAULT_FROM_EMAIL",
                                    "no-reply@fastlanelogisticgn.com")
                subject = f"[Contact site] {msg.get_sujet_display()} — {msg.nom}"
                body = (
                    f"Nouveau message depuis le site public.\n\n"
                    f"Nom        : {msg.nom}\n"
                    f"Entreprise : {msg.entreprise or '—'}\n"
                    f"E-mail     : {msg.email}\n"
                    f"Téléphone  : {msg.telephone or '—'}\n"
                    f"Sujet      : {msg.get_sujet_display()}\n"
                    f"Reçu le    : {msg.created_at:%d/%m/%Y %H:%M}\n\n"
                    f"Message :\n{msg.message}\n"
                )
                send_mail(subject, body, from_addr, [dest], fail_silently=True)
            except Exception:
                pass

            messages.success(
                request,
                "Votre message a bien été envoyé. Notre équipe vous recontactera "
                "dans les meilleurs délais."
            )
            return redirect("public:contact")
    else:
        form = ContactForm()

    return render(request, "public/contact.html", {
        "form": form,
        "page": page,
    })


@login_required
def gestion_messages(request):
    messages_contact = ContactMessage.objects.all()
    return render(request, "public/gestion_messages.html", {
        "messages_contact": messages_contact,
    })


@login_required
def gestion_message_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        msg.traite = request.POST.get("traite") == "on"
        msg.reponse_interne = request.POST.get("reponse_interne", "").strip()
        msg.save(update_fields=["traite", "reponse_interne", "updated_at"])
        messages.success(request, "Message mis à jour.")
        return redirect("public:gestion_message_detail", pk=msg.pk)
    return render(request, "public/gestion_message_detail.html", {"msg": msg})


@login_required
def gestion_evenements(request):
    evenements = Evenement.objects.all()
    return render(request, "public/gestion_evenements.html", {
        "evenements": evenements,
    })


@login_required
def evenement_create(request):
    form = EvenementForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save()
        messages.success(request, f"Événement « {obj.titre} » ajouté.")
        return redirect("public:gestion_evenements")
    return render(request, "_form_generic.html", {
        "form": form,
        "titre": "Nouvel événement",
        "icone": "calendar-plus",
        "retour_url": "public:gestion_evenements",
    })


@login_required
def evenement_edit(request, pk):
    obj = get_object_or_404(Evenement, pk=pk)
    form = EvenementForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, f"Événement « {obj.titre} » mis à jour.")
        return redirect("public:gestion_evenements")
    return render(request, "_form_generic.html", {
        "form": form,
        "titre": f"Modifier événement : {obj.titre}",
        "icone": "pencil",
        "retour_url": "public:gestion_evenements",
    })


@login_required
def evenement_delete(request, pk):
    obj = get_object_or_404(Evenement, pk=pk)
    if request.method == "POST":
        titre = obj.titre
        obj.delete()
        messages.success(request, f"Événement « {titre} » supprimé.")
        return redirect("public:gestion_evenements")
    return render(request, "confirm_delete.html", {
        "objet": obj,
        "titre": "Supprimer l'événement",
        "message": f"Supprimer l'événement « {obj.titre} » ?",
        "retour_url": "public:gestion_evenements",
    })


@login_required
def gestion_appels_offres(request):
    appels = AppelOffre.objects.all()
    return render(request, "public/gestion_appels_offres.html", {
        "appels": appels,
    })


@login_required
def appel_offre_create(request):
    form = AppelOffreForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save()
        messages.success(request, f"Appel d'offres {obj.reference} ajouté.")
        return redirect("public:gestion_appels_offres")
    return render(request, "_form_generic.html", {
        "form": form,
        "titre": "Nouvel appel d'offres",
        "icone": "file-earmark-plus",
        "retour_url": "public:gestion_appels_offres",
    })


@login_required
def appel_offre_edit(request, pk):
    obj = get_object_or_404(AppelOffre, pk=pk)
    form = AppelOffreForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, f"Appel d'offres {obj.reference} mis à jour.")
        return redirect("public:gestion_appels_offres")
    return render(request, "_form_generic.html", {
        "form": form,
        "titre": f"Modifier appel d'offres : {obj.reference}",
        "icone": "pencil",
        "retour_url": "public:gestion_appels_offres",
    })


@login_required
def appel_offre_delete(request, pk):
    obj = get_object_or_404(AppelOffre, pk=pk)
    if request.method == "POST":
        reference = obj.reference
        obj.delete()
        messages.success(request, f"Appel d'offres {reference} supprimé.")
        return redirect("public:gestion_appels_offres")
    return render(request, "confirm_delete.html", {
        "objet": obj,
        "titre": "Supprimer l'appel d'offres",
        "message": f"Supprimer l'appel d'offres {obj.reference} ?",
        "retour_url": "public:gestion_appels_offres",
    })


def robots_txt(request):
    """
    /robots.txt — autorise les moteurs sur tout le site public, bloque
    les zones privées (admin, dashboard, espace authentifié) et annonce
    l'emplacement du sitemap.
    """
    site_url = getattr(settings, "SEO_SITE_URL", "").rstrip("/")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /connexion/",
        "Disallow: /dashboard/",
        "Disallow: /core/",
        "Disallow: /flotte/",
        "Disallow: /rh/",
        "Disallow: /operations/",
        "Disallow: /facturation/",
        "",
        # Crawl-delay raisonnable pour ne pas surcharger le serveur PA
        "Crawl-delay: 2",
        "",
        f"Sitemap: {site_url}/sitemap.xml" if site_url else "Sitemap: /sitemap.xml",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def google_site_verification(request):
    """
    Fichier de validation de propriété Google Search Console.
    Doit répondre exactement :
        google-site-verification: google10babad53f3eade7.html
    à l'URL https://www.fastlanelogisticgn.com/google10babad53f3eade7.html
    """
    return HttpResponse(
        "google-site-verification: google10babad53f3eade7.html",
        content_type="text/html",
    )
