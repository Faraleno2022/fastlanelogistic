"""Vues dédiées au module Contrôle Interne & Conformité."""

from django.db.models import Count, Avg
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models_controle import (
    MatriceRisques,
    ProcedureControle,
    TestControle,
    NonConformite,
    DelegationPouvoirs,
    WorkflowApprobation,
    RapportControleInterne,
)
from .forms_controle import (
    MatriceRisquesForm,
    ProcedureControleForm,
    TestControleForm,
    NonConformiteForm,
    DelegationPouvoirsForm,
    RapportControleInterneForm,
)
from .views.base.generic import (
    ComptaListView,
    ComptaDetailView,
    ComptaCreateView,
    ComptaUpdateView,
)


# ============== MATRICE DES RISQUES ==============

class MatriceRisquesListView(ComptaListView):
    """Liste des risques."""

    model = MatriceRisques
    template_name = "comptabilite/controle/risques.html"
    context_object_name = "risques"
    paginate_by = 25
    ordering = ["-score_inherent"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("proprietaire", "cree_par")
            .order_by(*self.ordering)
        )

        categorie = self.request.GET.get("categorie")
        if categorie:
            queryset = queryset.filter(categorie=categorie)

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        qs = self.get_queryset()
        context.update(
            {
                "categories": MatriceRisques.CATEGORIES_RISQUE,
                "statuts": MatriceRisques.STATUTS,
                "risques_critiques": qs.filter(score_inherent__gte=15).count(),
                "risques_moderes": qs.filter(score_inherent__gte=8, score_inherent__lt=15).count(),
                "risques_faibles": qs.filter(score_inherent__lt=8).count(),
                "breadcrumbs": [
                    {"label": _("Contrôle interne"), "url": "comptabilite:controle_dashboard"},
                    {"label": _("Matrice des risques"), "url": None},
                ],
            }
        )
        return context


class MatriceRisquesDetailView(ComptaDetailView):
    """Détail d'un risque."""

    model = MatriceRisques
    template_name = "comptabilite/controle/risque_detail.html"
    context_object_name = "risque"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("proprietaire", "cree_par")
            .prefetch_related("procedures", "non_conformites")
        )


class MatriceRisquesCreateView(ComptaCreateView):
    """Crée un risque."""

    model = MatriceRisques
    form_class = MatriceRisquesForm
    template_name = "comptabilite/controle/risque_form.html"
    success_message = _("Risque créé avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:controle_risque_detail", kwargs={"pk": self.object.pk})


class MatriceRisquesUpdateView(ComptaUpdateView):
    """Met à jour un risque."""

    model = MatriceRisques
    form_class = MatriceRisquesForm
    template_name = "comptabilite/controle/risque_form.html"
    success_message = _("Risque mis à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:controle_risque_detail", kwargs={"pk": self.object.pk})


# ============== PROCEDURES DE CONTROLE ==============

class ProcedureControleListView(ComptaListView):
    """Liste des procédures de contrôle."""

    model = ProcedureControle
    template_name = "comptabilite/controle/procedures.html"
    context_object_name = "procedures"
    paginate_by = 25
    ordering = ["code"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("responsable")
            .order_by(*self.ordering)
        )

        type_controle = self.request.GET.get("type")
        if type_controle:
            queryset = queryset.filter(type_controle=type_controle)

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "types_controle": ProcedureControle.TYPES_CONTROLE,
                "statuts": ProcedureControle.STATUTS,
                "breadcrumbs": [
                    {"label": _("Contrôle interne"), "url": "comptabilite:controle_dashboard"},
                    {"label": _("Procédures"), "url": None},
                ],
            }
        )
        return context


class ProcedureControleDetailView(ComptaDetailView):
    """Détail d'une procédure."""

    model = ProcedureControle
    template_name = "comptabilite/controle/procedure_detail.html"
    context_object_name = "procedure"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("responsable")
            .prefetch_related("risques", "tests", "non_conformites")
        )


class ProcedureControleCreateView(ComptaCreateView):
    """Crée une procédure."""

    model = ProcedureControle
    form_class = ProcedureControleForm
    template_name = "comptabilite/controle/procedure_form.html"
    success_message = _("Procédure créée avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:controle_procedure_detail", kwargs={"pk": self.object.pk})


class ProcedureControleUpdateView(ComptaUpdateView):
    """Met à jour une procédure."""

    model = ProcedureControle
    form_class = ProcedureControleForm
    template_name = "comptabilite/controle/procedure_form.html"
    success_message = _("Procédure mise à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:controle_procedure_detail", kwargs={"pk": self.object.pk})


# ============== TESTS DE CONTROLE ==============

class TestControleListView(ComptaListView):
    """Liste des tests de contrôle."""

    model = TestControle
    template_name = "comptabilite/controle/tests.html"
    context_object_name = "tests"
    paginate_by = 25
    ordering = ["-date_execution"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("procedure", "execute_par")
            .filter(procedure__entreprise=self.request.user.entreprise)
            .order_by(*self.ordering)
        )

        resultat = self.request.GET.get("resultat")
        if resultat:
            queryset = queryset.filter(resultat=resultat)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        qs = self.get_queryset()
        context.update(
            {
                "resultats": TestControle.RESULTATS,
                "tests_reussis": qs.filter(resultat="reussi").count(),
                "tests_echoues": qs.filter(resultat="echoue").count(),
                "tests_en_cours": qs.filter(resultat="en_cours").count(),
                "breadcrumbs": [
                    {"label": _("Contrôle interne"), "url": "comptabilite:controle_dashboard"},
                    {"label": _("Tests de contrôle"), "url": None},
                ],
            }
        )
        return context


class TestControleDetailView(ComptaDetailView):
    """Détail d'un test."""

    model = TestControle
    template_name = "comptabilite/controle/test_detail.html"
    context_object_name = "test"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("procedure", "execute_par")
            .filter(procedure__entreprise=self.request.user.entreprise)
        )


class TestControleCreateView(ComptaCreateView):
    """Crée un test."""

    model = TestControle
    form_class = TestControleForm
    template_name = "comptabilite/controle/test_form.html"
    success_message = _("Test créé avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.execute_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:controle_test_detail", kwargs={"pk": self.object.pk})


class TestControleUpdateView(ComptaUpdateView):
    """Met à jour un test."""

    model = TestControle
    form_class = TestControleForm
    template_name = "comptabilite/controle/test_form.html"
    success_message = _("Test mis à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:controle_test_detail", kwargs={"pk": self.object.pk})


# ============== NON-CONFORMITES ==============

class NonConformiteListView(ComptaListView):
    """Liste des non-conformités."""

    model = NonConformite
    template_name = "comptabilite/controle/non_conformites.html"
    context_object_name = "non_conformites"
    paginate_by = 25
    ordering = ["-date_detection"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("responsable_correction", "procedure", "risque")
            .order_by(*self.ordering)
        )

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        gravite = self.request.GET.get("gravite")
        if gravite:
            queryset = queryset.filter(niveau_gravite=gravite)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        qs = self.get_queryset()
        context.update(
            {
                "statuts": NonConformite.STATUTS,
                "niveaux_gravite": NonConformite.NIVEAUX_GRAVITE,
                "nc_ouvertes": qs.filter(statut="ouverte").count(),
                "nc_en_correction": qs.filter(statut="en_correction").count(),
                "nc_cloturees": qs.filter(statut="cloturee").count(),
                "breadcrumbs": [
                    {"label": _("Contrôle interne"), "url": "comptabilite:controle_dashboard"},
                    {"label": _("Non-conformités"), "url": None},
                ],
            }
        )
        return context


class NonConformiteDetailView(ComptaDetailView):
    """Détail d'une non-conformité."""

    model = NonConformite
    template_name = "comptabilite/controle/non_conformite_detail.html"
    context_object_name = "nc"


class NonConformiteCreateView(ComptaCreateView):
    """Crée une non-conformité."""

    model = NonConformite
    form_class = NonConformiteForm
    template_name = "comptabilite/controle/non_conformite_form.html"
    success_message = _("Non-conformité créée avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:controle_non_conformite_detail", kwargs={"pk": self.object.pk})


class NonConformiteUpdateView(ComptaUpdateView):
    """Met à jour une non-conformité."""

    model = NonConformite
    form_class = NonConformiteForm
    template_name = "comptabilite/controle/non_conformite_form.html"
    success_message = _("Non-conformité mise à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:controle_non_conformite_detail", kwargs={"pk": self.object.pk})


# ============== DELEGATIONS DE POUVOIRS ==============

class DelegationPouvoirsListView(ComptaListView):
    """Liste des délégations de pouvoirs."""

    model = DelegationPouvoirs
    template_name = "comptabilite/controle/delegations.html"
    context_object_name = "delegations"
    paginate_by = 25
    ordering = ["-date_debut"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("delegant", "delegataire")
            .order_by(*self.ordering)
        )

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "statuts": DelegationPouvoirs.STATUTS,
                "types_pouvoir": DelegationPouvoirs.TYPES_POUVOIR,
                "breadcrumbs": [
                    {"label": _("Contrôle interne"), "url": "comptabilite:controle_dashboard"},
                    {"label": _("Délégations"), "url": None},
                ],
            }
        )
        return context


class DelegationPouvoirsDetailView(ComptaDetailView):
    """Détail d'une délégation."""

    model = DelegationPouvoirs
    template_name = "comptabilite/controle/delegation_detail.html"
    context_object_name = "delegation"


class DelegationPouvoirsCreateView(ComptaCreateView):
    """Crée une délégation."""

    model = DelegationPouvoirs
    form_class = DelegationPouvoirsForm
    template_name = "comptabilite/controle/delegation_form.html"
    success_message = _("Délégation créée avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:controle_delegation_detail", kwargs={"pk": self.object.pk})


class DelegationPouvoirsUpdateView(ComptaUpdateView):
    """Met à jour une délégation."""

    model = DelegationPouvoirs
    form_class = DelegationPouvoirsForm
    template_name = "comptabilite/controle/delegation_form.html"
    success_message = _("Délégation mise à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:controle_delegation_detail", kwargs={"pk": self.object.pk})


# ============== WORKFLOWS ==============

class WorkflowListView(ComptaListView):
    """Liste des workflows d'approbation."""

    model = WorkflowApprobation
    template_name = "comptabilite/controle/workflows.html"
    context_object_name = "workflows"
    paginate_by = 25
    ordering = ["-date_demande"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("matrice", "demandeur")
            .filter(matrice__entreprise=self.request.user.entreprise)
            .order_by(*self.ordering)
        )

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        qs = self.get_queryset()
        context.update(
            {
                "statuts": WorkflowApprobation.STATUTS,
                "en_attente": qs.filter(statut="en_attente").count(),
                "approuves": qs.filter(statut="approuve").count(),
                "rejetes": qs.filter(statut="rejete").count(),
                "breadcrumbs": [
                    {"label": _("Contrôle interne"), "url": "comptabilite:controle_dashboard"},
                    {"label": _("Workflows"), "url": None},
                ],
            }
        )
        return context


# ============== RAPPORTS ==============

class RapportControleListView(ComptaListView):
    """Liste des rapports de contrôle."""

    model = RapportControleInterne
    template_name = "comptabilite/controle/rapports.html"
    context_object_name = "rapports"
    paginate_by = 25
    ordering = ["-date_fin_periode"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("redige_par", "valide_par")
            .order_by(*self.ordering)
        )

        type_rapport = self.request.GET.get("type")
        if type_rapport:
            queryset = queryset.filter(type_rapport=type_rapport)

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "types_rapport": RapportControleInterne.TYPES_RAPPORT,
                "statuts": RapportControleInterne.STATUTS,
                "breadcrumbs": [
                    {"label": _("Contrôle interne"), "url": "comptabilite:controle_dashboard"},
                    {"label": _("Rapports"), "url": None},
                ],
            }
        )
        return context


class RapportControleDetailView(ComptaDetailView):
    """Détail d'un rapport."""

    model = RapportControleInterne
    template_name = "comptabilite/controle/rapport_detail.html"
    context_object_name = "rapport"


class RapportControleCreateView(ComptaCreateView):
    """Crée un rapport."""

    model = RapportControleInterne
    form_class = RapportControleInterneForm
    template_name = "comptabilite/controle/rapport_form.html"
    success_message = _("Rapport créé avec succès.")

    def form_valid(self, form):
        form.instance.redige_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:controle_rapport_detail", kwargs={"pk": self.object.pk})


class RapportControleUpdateView(ComptaUpdateView):
    """Met à jour un rapport."""

    model = RapportControleInterne
    form_class = RapportControleInterneForm
    template_name = "comptabilite/controle/rapport_form.html"
    success_message = _("Rapport mis à jour avec succès.")

    def get_success_url(self):
        return reverse("comptabilite:controle_rapport_detail", kwargs={"pk": self.object.pk})
