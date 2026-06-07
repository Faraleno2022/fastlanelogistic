"""
Vues pour le module Gestion Comptable des Contrats
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .views.base.generic import ComptaListView, ComptaDetailView, ComptaCreateView, ComptaUpdateView
from .models_contrats_comptables import (
    ContratFournisseur, ContratClient, ConditionsPaiement,
    ConditionsLivraison, PointGaranti, PenaliteRetard,
    ReclamationContractuelle, AlerteContrat
)
from .forms_contrats import (
    ContratFournisseurForm, ContratClientForm, ConditionsPaiementForm,
    PointGarantiForm, PenaliteRetardForm, ReclamationContractuelleForm,
    AlerteContratForm
)


# ============== DASHBOARD ==============

class ContratsDashboardView(ComptaListView):
    """Dashboard du module contrats"""
    model = ContratFournisseur
    template_name = "comptabilite/contrats/dashboard.html"
    context_object_name = "contrats_fournisseurs"

    def get_queryset(self):
        return ContratFournisseur.objects.filter(
            entreprise=self.request.user.entreprise
        ).select_related('fournisseur')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entreprise = self.request.user.entreprise
        today = timezone.now().date()

        # Contrats fournisseurs
        contrats_fournisseurs = ContratFournisseur.objects.filter(entreprise=entreprise)
        context['nb_contrats_fournisseurs'] = contrats_fournisseurs.count()
        context['contrats_fournisseurs_actifs'] = contrats_fournisseurs.filter(statut='actif').count()
        context['montant_contrats_fournisseurs'] = contrats_fournisseurs.filter(
            statut='actif'
        ).aggregate(total=Sum('montant_total'))['total'] or 0

        # Contrats clients
        contrats_clients = ContratClient.objects.filter(entreprise=entreprise)
        context['nb_contrats_clients'] = contrats_clients.count()
        context['contrats_clients_actifs'] = contrats_clients.filter(statut='actif').count()
        context['montant_contrats_clients'] = contrats_clients.filter(
            statut='actif'
        ).aggregate(total=Sum('montant_total'))['total'] or 0

        # Alertes actives
        context['alertes_actives'] = AlerteContrat.objects.filter(
            entreprise=entreprise, statut='active'
        ).count()

        # Contrats expirant bientôt (30 jours)
        date_limite = today + timezone.timedelta(days=30)
        context['contrats_expirant'] = contrats_fournisseurs.filter(
            statut='actif', date_fin__lte=date_limite, date_fin__gte=today
        ).count() + contrats_clients.filter(
            statut='actif', date_fin__lte=date_limite, date_fin__gte=today
        ).count()

        # Réclamations ouvertes
        context['reclamations_ouvertes'] = ReclamationContractuelle.objects.filter(
            entreprise=entreprise, statut__in=['ouverte', 'en_cours', 'en_attente']
        ).count()

        # Derniers contrats clients
        context['contrats_clients_recents'] = ContratClient.objects.filter(
            entreprise=entreprise
        ).select_related('client')[:5]

        # Alertes récentes
        context['alertes_recentes'] = AlerteContrat.objects.filter(
            entreprise=entreprise, statut='active'
        ).order_by('-date_alerte')[:5]

        return context


# ============== CONTRATS FOURNISSEURS ==============

class ContratFournisseurListView(ComptaListView):
    """Liste des contrats fournisseurs"""
    model = ContratFournisseur
    template_name = "comptabilite/contrats/fournisseurs.html"
    context_object_name = "contrats"
    paginate_by = 25
    ordering = ['-date_debut']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('fournisseur', 'responsable')

        # Filtres
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)

        type_contrat = self.request.GET.get('type')
        if type_contrat:
            queryset = queryset.filter(type_contrat=type_contrat)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero_contrat__icontains=search) |
                Q(objet__icontains=search) |
                Q(fournisseur__nom__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        context.update({
            'statuts': ContratFournisseur.STATUTS,
            'types_contrat': ContratFournisseur.TYPES_CONTRAT,
            'nb_actifs': qs.filter(statut='actif').count(),
            'nb_expires': qs.filter(statut='expire').count(),
            'nb_en_negociation': qs.filter(statut='en_negociation').count(),
            'montant_total': qs.filter(statut='actif').aggregate(total=Sum('montant_total'))['total'] or 0,
        })
        return context


class ContratFournisseurDetailView(ComptaDetailView):
    """Détail d'un contrat fournisseur"""
    model = ContratFournisseur
    template_name = "comptabilite/contrats/fournisseur_detail.html"
    context_object_name = "contrat"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrat = self.object

        context['conditions_paiement'] = contrat.conditions_paiement.all()
        context['conditions_livraison'] = contrat.conditions_livraison.all()
        context['garanties'] = contrat.garanties.all()
        context['penalites'] = contrat.penalites.all()
        context['reclamations'] = contrat.reclamations.all()
        context['suivi'] = contrat.suivi.all()[:10]
        context['alertes'] = contrat.alertes.filter(statut='active')

        return context


class ContratFournisseurCreateView(ComptaCreateView):
    """Création d'un contrat fournisseur"""
    model = ContratFournisseur
    form_class = ContratFournisseurForm
    template_name = "comptabilite/contrats/fournisseur_form.html"
    success_message = _("Contrat fournisseur créé avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entreprise'] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('comptabilite:contrats_fournisseur_detail', kwargs={'pk': self.object.pk})


class ContratFournisseurUpdateView(ComptaUpdateView):
    """Modification d'un contrat fournisseur"""
    model = ContratFournisseur
    form_class = ContratFournisseurForm
    template_name = "comptabilite/contrats/fournisseur_form.html"
    success_message = _("Contrat fournisseur modifié avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entreprise'] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse('comptabilite:contrats_fournisseur_detail', kwargs={'pk': self.object.pk})


# ============== CONTRATS CLIENTS ==============

class ContratClientListView(ComptaListView):
    """Liste des contrats clients"""
    model = ContratClient
    template_name = "comptabilite/contrats/clients.html"
    context_object_name = "contrats"
    paginate_by = 25
    ordering = ['-date_debut']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('client', 'responsable')

        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)

        type_contrat = self.request.GET.get('type')
        if type_contrat:
            queryset = queryset.filter(type_contrat=type_contrat)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero_contrat__icontains=search) |
                Q(objet__icontains=search) |
                Q(client__nom__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        context.update({
            'statuts': ContratClient.STATUTS,
            'types_contrat': ContratClient.TYPES_CONTRAT,
            'nb_actifs': qs.filter(statut='actif').count(),
            'nb_expires': qs.filter(statut='expire').count(),
            'nb_en_negociation': qs.filter(statut='en_negociation').count(),
            'montant_total': qs.filter(statut='actif').aggregate(total=Sum('montant_total'))['total'] or 0,
        })
        return context


class ContratClientDetailView(ComptaDetailView):
    """Détail d'un contrat client"""
    model = ContratClient
    template_name = "comptabilite/contrats/client_detail.html"
    context_object_name = "contrat"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrat = self.object

        context['conditions_paiement'] = contrat.conditions_paiement.all()
        context['conditions_livraison'] = contrat.conditions_livraison.all()
        context['garanties'] = contrat.garanties.all()
        context['penalites'] = contrat.penalites.all()
        context['reclamations'] = contrat.reclamations.all()
        context['suivi'] = contrat.suivi.all()[:10]
        context['alertes'] = contrat.alertes.filter(statut='active')

        return context


class ContratClientCreateView(ComptaCreateView):
    """Création d'un contrat client"""
    model = ContratClient
    form_class = ContratClientForm
    template_name = "comptabilite/contrats/client_form.html"
    success_message = _("Contrat client créé avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entreprise'] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('comptabilite:contrats_client_detail', kwargs={'pk': self.object.pk})


class ContratClientUpdateView(ComptaUpdateView):
    """Modification d'un contrat client"""
    model = ContratClient
    form_class = ContratClientForm
    template_name = "comptabilite/contrats/client_form.html"
    success_message = _("Contrat client modifié avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entreprise'] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse('comptabilite:contrats_client_detail', kwargs={'pk': self.object.pk})


# ============== CONDITIONS PAIEMENT ==============

class ConditionsPaiementListView(ComptaListView):
    """Liste des conditions de paiement"""
    model = ConditionsPaiement
    template_name = "comptabilite/contrats/conditions_paiement.html"
    context_object_name = "conditions"
    paginate_by = 25

    def get_queryset(self):
        entreprise = self.request.user.entreprise
        return ConditionsPaiement.objects.filter(
            Q(contrat_fournisseur__entreprise=entreprise) |
            Q(contrat_client__entreprise=entreprise)
        ).select_related('contrat_fournisseur', 'contrat_client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modes_paiement'] = ConditionsPaiement.MODES_PAIEMENT
        context['echeances'] = ConditionsPaiement.ECHEANCES
        return context


# ============== GARANTIES ==============

class GarantiesListView(ComptaListView):
    """Liste des garanties"""
    model = PointGaranti
    template_name = "comptabilite/contrats/garanties.html"
    context_object_name = "garanties"
    paginate_by = 25

    def get_queryset(self):
        entreprise = self.request.user.entreprise
        return PointGaranti.objects.filter(
            Q(contrat_fournisseur__entreprise=entreprise) |
            Q(contrat_client__entreprise=entreprise)
        ).select_related('contrat_fournisseur', 'contrat_client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types_garantie'] = PointGaranti.TYPES_GARANTIE
        return context


# ============== PENALITES ==============

class PenalitesListView(ComptaListView):
    """Liste des pénalités"""
    model = PenaliteRetard
    template_name = "comptabilite/contrats/penalites.html"
    context_object_name = "penalites"
    paginate_by = 25

    def get_queryset(self):
        entreprise = self.request.user.entreprise
        return PenaliteRetard.objects.filter(
            Q(contrat_fournisseur__entreprise=entreprise) |
            Q(contrat_client__entreprise=entreprise)
        ).select_related('contrat_fournisseur', 'contrat_client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types_penalite'] = PenaliteRetard.TYPES_PENALITE
        context['modes_calcul'] = PenaliteRetard.MODES_CALCUL
        return context


# ============== RECLAMATIONS ==============

class ReclamationsListView(ComptaListView):
    """Liste des réclamations"""
    model = ReclamationContractuelle
    template_name = "comptabilite/contrats/reclamations.html"
    context_object_name = "reclamations"
    paginate_by = 25
    ordering = ['-date_reclamation']

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'contrat_fournisseur', 'contrat_client', 'responsable'
        )

        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)

        priorite = self.request.GET.get('priorite')
        if priorite:
            queryset = queryset.filter(priorite=priorite)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        context.update({
            'statuts': ReclamationContractuelle.STATUTS,
            'priorites': ReclamationContractuelle.PRIORITES,
            'types_reclamation': ReclamationContractuelle.TYPES_RECLAMATION,
            'nb_ouvertes': qs.filter(statut='ouverte').count(),
            'nb_en_cours': qs.filter(statut='en_cours').count(),
            'nb_resolues': qs.filter(statut='resolue').count(),
        })
        return context


class ReclamationDetailView(ComptaDetailView):
    """Détail d'une réclamation"""
    model = ReclamationContractuelle
    template_name = "comptabilite/contrats/reclamation_detail.html"
    context_object_name = "reclamation"


class ReclamationCreateView(ComptaCreateView):
    """Création d'une réclamation"""
    model = ReclamationContractuelle
    form_class = ReclamationContractuelleForm
    template_name = "comptabilite/contrats/reclamation_form.html"
    success_message = _("Réclamation créée avec succès.")

    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('comptabilite:contrats_reclamation_detail', kwargs={'pk': self.object.pk})


class ReclamationUpdateView(ComptaUpdateView):
    """Modification d'une réclamation"""
    model = ReclamationContractuelle
    form_class = ReclamationContractuelleForm
    template_name = "comptabilite/contrats/reclamation_form.html"
    success_message = _("Réclamation modifiée avec succès.")

    def get_success_url(self):
        return reverse('comptabilite:contrats_reclamation_detail', kwargs={'pk': self.object.pk})


# ============== ALERTES ==============

class AlertesListView(ComptaListView):
    """Liste des alertes contrats"""
    model = AlerteContrat
    template_name = "comptabilite/contrats/alertes.html"
    context_object_name = "alertes"
    paginate_by = 25
    ordering = ['-date_alerte']

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'contrat_fournisseur', 'contrat_client', 'acquittee_par'
        )

        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)

        niveau = self.request.GET.get('niveau')
        if niveau:
            queryset = queryset.filter(niveau=niveau)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        context.update({
            'statuts': AlerteContrat.STATUTS,
            'niveaux': AlerteContrat.NIVEAUX,
            'types_alerte': AlerteContrat.TYPES_ALERTE,
            'nb_actives': qs.filter(statut='active').count(),
            'nb_critiques': qs.filter(statut='active', niveau='critical').count(),
            'nb_warnings': qs.filter(statut='active', niveau='warning').count(),
        })
        return context
