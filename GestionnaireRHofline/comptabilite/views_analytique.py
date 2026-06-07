"""Vues dédiées au module de comptabilité analytique."""

from django.db.models import Sum
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import ExerciceComptable
from .models_analytique import (
    SectionAnalytique,
    ImputationAnalytique,
    CentreCouts,
    CommandeAnalytique,
    BudgetAnalytique,
    AnalyseVariance,
)
from .forms_analytique import (
    SectionAnalytiqueForm,
    ImputationAnalytiqueForm,
    BudgetAnalytiqueForm,
    AnalyseVarianceForm,
)
from .views.base.generic import (
    ComptaListView,
    ComptaDetailView,
    ComptaCreateView,
    ComptaUpdateView,
)


class SectionAnalytiqueListView(ComptaListView):
    """Liste des sections analytiques avec filtres et recherche."""

    model = SectionAnalytique
    template_name = "comptabilite/analytique/sections.html"
    context_object_name = "sections"
    paginate_by = 25
    search_fields = ["code", "libelle", "description"]
    ordering = ["code"]

    def get_queryset(self):
        if hasattr(self, "_sections_queryset"):
            return self._sections_queryset

        queryset = (
            super()
            .get_queryset()
            .select_related("centre_couts", "section_parent")
            .order_by(*self.ordering)
        )

        type_section = self.request.GET.get("type_section")
        if type_section:
            queryset = queryset.filter(type_section=type_section)

        est_active = self.request.GET.get("est_active")
        if est_active == "true":
            queryset = queryset.filter(est_active=True)
        elif est_active == "false":
            queryset = queryset.filter(est_active=False)

        self._sections_queryset = queryset
        return self._sections_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_queryset = self.get_queryset()

        querydict = self.request.GET.copy()
        querydict.pop('page', None)
        querystring = querydict.urlencode()

        context.update(
            {
                "types_section": SectionAnalytique.TYPES_SECTION,
                "total_sections": filtered_queryset.count(),
                "active_sections": filtered_queryset.filter(est_active=True).count(),
                "inactive_sections": filtered_queryset.filter(est_active=False).count(),
                "querystring": f"&{querystring}" if querystring else "",
                "breadcrumbs": [
                    {"label": _("Analytique"), "url": "comptabilite:analytique_dashboard"},
                    {"label": _("Sections analytiques"), "url": None},
                ],
            }
        )
        return context


class SectionAnalytiqueDetailView(ComptaDetailView):
    """Affiche le détail d'une section analytique."""

    model = SectionAnalytique
    template_name = "comptabilite/analytique/section_detail.html"
    context_object_name = "section"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("centre_couts", "section_parent")
            .prefetch_related("sous_sections", "commandes", "imputations")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = self.object

        context.update(
            {
                "sous_sections": section.sous_sections.all().order_by("code"),
                "commandes_recents": section.commandes.all().order_by("-date_debut")[:10],
                "imputations_recentes": section.imputations.all().order_by("-date_imputation")[:10],
                "breadcrumbs": [
                    {"label": _("Analytique"), "url": "comptabilite:analytique_dashboard"},
                    {"label": _("Sections analytiques"), "url": "comptabilite:analytique_sections"},
                    {"label": section.libelle, "url": None},
                ],
            }
        )
        return context


class SectionAnalytiqueCreateView(ComptaCreateView):
    """Crée une nouvelle section analytique."""

    model = SectionAnalytique
    form_class = SectionAnalytiqueForm
    template_name = "comptabilite/analytique/section_form.html"
    success_message = _("Section analytique créée avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:analytique_section_detail", kwargs={"pk": self.object.pk})


class SectionAnalytiqueUpdateView(ComptaUpdateView):
    """Met à jour une section analytique existante."""

    model = SectionAnalytique
    form_class = SectionAnalytiqueForm
    template_name = "comptabilite/analytique/section_form.html"
    success_message = _("Section analytique mise à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:analytique_section_detail", kwargs={"pk": self.object.pk})


class ImputationAnalytiqueListView(ComptaListView):
    """Liste des imputations analytiques avec filtres et indicateurs."""

    model = ImputationAnalytique
    template_name = "comptabilite/analytique/imputations.html"
    context_object_name = "imputations"
    paginate_by = 25
    search_fields = ["libelle", "periode", "unite", "ecriture__numero_ecriture"]
    ordering = ["-date_imputation", "-date_creation"]

    def get_queryset(self):
        if hasattr(self, "_imputations_queryset"):
            return self._imputations_queryset

        queryset = (
            super()
            .get_queryset()
            .select_related(
                "centre_couts",
                "section",
                "commande",
                "compte",
                "ecriture",
            )
            .order_by(*self.ordering)
        )

        type_imputation = self.request.GET.get("type")
        if type_imputation:
            queryset = queryset.filter(type_imputation=type_imputation)

        centre_id = self.request.GET.get("centre")
        if centre_id:
            queryset = queryset.filter(centre_couts_id=centre_id)

        section_id = self.request.GET.get("section")
        if section_id:
            queryset = queryset.filter(section_id=section_id)

        commande_id = self.request.GET.get("commande")
        if commande_id:
            queryset = queryset.filter(commande_id=commande_id)

        periode = self.request.GET.get("periode")
        if periode:
            queryset = queryset.filter(periode=periode)

        self._imputations_queryset = queryset
        return self._imputations_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_queryset = self.get_queryset()

        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        querystring = querydict.urlencode()

        aggregates = filtered_queryset.aggregate(
            total_debit=Sum("montant_debit"),
            total_credit=Sum("montant_credit"),
        )

        context.update(
            {
                "types_imputation": ImputationAnalytique.TYPES_IMPUTATION,
                "centres": CentreCouts.objects.filter(
                    entreprise=self.request.user.entreprise
                ).order_by("code"),
                "sections": SectionAnalytique.objects.filter(
                    entreprise=self.request.user.entreprise
                ).order_by("code"),
                "commandes": CommandeAnalytique.objects.filter(
                    entreprise=self.request.user.entreprise
                ).order_by("-date_creation"),
                "total_debit": aggregates.get("total_debit") or 0,
                "total_credit": aggregates.get("total_credit") or 0,
                "querystring": f"&{querystring}" if querystring else "",
                "breadcrumbs": [
                    {"label": _("Analytique"), "url": "comptabilite:analytique_dashboard"},
                    {"label": _("Imputations analytiques"), "url": None},
                ],
            }
        )
        return context


class ImputationAnalytiqueDetailView(ComptaDetailView):
    """Affiche le détail d'une imputation analytique."""

    model = ImputationAnalytique
    template_name = "comptabilite/analytique/imputation_detail.html"
    context_object_name = "imputation"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "centre_couts",
                "section",
                "commande",
                "compte",
                "ecriture",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        imputation = self.object

        context.update(
            {
                "breadcrumbs": [
                    {"label": _("Analytique"), "url": "comptabilite:analytique_dashboard"},
                    {
                        "label": _("Imputations analytiques"),
                        "url": "comptabilite:analytique_imputations",
                    },
                    {"label": imputation.libelle, "url": None},
                ],
            }
        )
        return context


class ImputationAnalytiqueCreateView(ComptaCreateView):
    """Crée une imputation analytique."""

    model = ImputationAnalytique
    form_class = ImputationAnalytiqueForm
    template_name = "comptabilite/analytique/imputation_form.html"
    success_message = _("Imputation analytique créée avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:analytique_imputation_detail", kwargs={"pk": self.object.pk})


class ImputationAnalytiqueUpdateView(ComptaUpdateView):
    """Met à jour une imputation analytique."""

    model = ImputationAnalytique
    form_class = ImputationAnalytiqueForm
    template_name = "comptabilite/analytique/imputation_form.html"
    success_message = _("Imputation analytique mise à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:analytique_imputation_detail", kwargs={"pk": self.object.pk})


class BudgetAnalytiqueListView(ComptaListView):
    """Liste des budgets analytiques avec filtres et indicateurs."""

    model = BudgetAnalytique
    template_name = "comptabilite/analytique/budgets.html"
    context_object_name = "budgets"
    paginate_by = 25
    search_fields = ["periode"]
    ordering = ["-exercice__date_debut", "-periode"]

    def get_queryset(self):
        if hasattr(self, "_budgets_queryset"):
            return self._budgets_queryset

        queryset = (
            super()
            .get_queryset()
            .select_related("exercice", "centre_couts", "section")
            .order_by(*self.ordering)
        )

        type_budget = self.request.GET.get("type")
        if type_budget:
            queryset = queryset.filter(type_budget=type_budget)

        exercice_id = self.request.GET.get("exercice")
        if exercice_id:
            queryset = queryset.filter(exercice_id=exercice_id)

        centre_id = self.request.GET.get("centre")
        if centre_id:
            queryset = queryset.filter(centre_couts_id=centre_id)

        section_id = self.request.GET.get("section")
        if section_id:
            queryset = queryset.filter(section_id=section_id)

        periode = self.request.GET.get("periode")
        if periode:
            queryset = queryset.filter(periode=periode)

        self._budgets_queryset = queryset
        return self._budgets_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_queryset = self.get_queryset()

        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        querystring = querydict.urlencode()

        aggregates = filtered_queryset.aggregate(
            total_charges=Sum("budget_charges"),
            total_produits=Sum("budget_produits"),
        )

        context.update(
            {
                "types_budget": BudgetAnalytique.TYPES_BUDGET,
                "exercices": ExerciceComptable.objects.filter(
                    entreprise=self.request.user.entreprise
                ).order_by("-date_debut"),
                "centres": CentreCouts.objects.filter(
                    entreprise=self.request.user.entreprise
                ).order_by("code"),
                "sections": SectionAnalytique.objects.filter(
                    entreprise=self.request.user.entreprise
                ).order_by("code"),
                "total_charges": aggregates.get("total_charges") or 0,
                "total_produits": aggregates.get("total_produits") or 0,
                "querystring": f"&{querystring}" if querystring else "",
                "breadcrumbs": [
                    {"label": _("Analytique"), "url": "comptabilite:analytique_dashboard"},
                    {"label": _("Budgets analytiques"), "url": None},
                ],
            }
        )
        return context


class BudgetAnalytiqueDetailView(ComptaDetailView):
    """Affiche le détail d'un budget analytique."""

    model = BudgetAnalytique
    template_name = "comptabilite/analytique/budget_detail.html"
    context_object_name = "budget"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("exercice", "centre_couts", "section")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budget = self.object

        context.update(
            {
                "breadcrumbs": [
                    {"label": _("Analytique"), "url": "comptabilite:analytique_dashboard"},
                    {"label": _("Budgets analytiques"), "url": "comptabilite:analytique_budgets"},
                    {"label": str(budget), "url": None},
                ],
            }
        )
        return context


class BudgetAnalytiqueCreateView(ComptaCreateView):
    """Crée un budget analytique."""

    model = BudgetAnalytique
    form_class = BudgetAnalytiqueForm
    template_name = "comptabilite/analytique/budget_form.html"
    success_message = _("Budget analytique créé avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:analytique_budget_detail", kwargs={"pk": self.object.pk})


class BudgetAnalytiqueUpdateView(ComptaUpdateView):
    """Met à jour un budget analytique."""

    model = BudgetAnalytique
    form_class = BudgetAnalytiqueForm
    template_name = "comptabilite/analytique/budget_form.html"
    success_message = _("Budget analytique mis à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:analytique_budget_detail", kwargs={"pk": self.object.pk})


class AnalyseVarianceListView(ComptaListView):
    """Liste des analyses de variance avec filtres et indicateurs."""

    model = AnalyseVariance
    template_name = "comptabilite/analytique/variances.html"
    context_object_name = "variances"
    paginate_by = 25
    search_fields = ["periode", "explication"]
    ordering = ["-periode", "-ecart_montant"]

    def get_queryset(self):
        if hasattr(self, "_variances_queryset"):
            return self._variances_queryset

        queryset = (
            super()
            .get_queryset()
            .select_related("exercice", "centre_couts", "section", "analyse_par")
            .order_by(*self.ordering)
        )

        type_ecart = self.request.GET.get("type")
        if type_ecart:
            queryset = queryset.filter(type_ecart=type_ecart)

        exercice_id = self.request.GET.get("exercice")
        if exercice_id:
            queryset = queryset.filter(exercice_id=exercice_id)

        centre_id = self.request.GET.get("centre")
        if centre_id:
            queryset = queryset.filter(centre_couts_id=centre_id)

        section_id = self.request.GET.get("section")
        if section_id:
            queryset = queryset.filter(section_id=section_id)

        favorable = self.request.GET.get("favorable")
        if favorable == "true":
            queryset = queryset.filter(favorable=True)
        elif favorable == "false":
            queryset = queryset.filter(favorable=False)

        periode = self.request.GET.get("periode")
        if periode:
            queryset = queryset.filter(periode=periode)

        self._variances_queryset = queryset
        return self._variances_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_queryset = self.get_queryset()

        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        querystring = querydict.urlencode()

        aggregates = filtered_queryset.aggregate(
            total_ecart=Sum("ecart_montant"),
        )
        favorable_count = filtered_queryset.filter(favorable=True).count()
        defavorable_count = filtered_queryset.filter(favorable=False).count()

        context.update(
            {
                "types_ecart": AnalyseVariance.TYPES_ECART,
                "exercices": ExerciceComptable.objects.filter(
                    entreprise=self.request.user.entreprise
                ).order_by("-date_debut"),
                "centres": CentreCouts.objects.filter(
                    entreprise=self.request.user.entreprise
                ).order_by("code"),
                "sections": SectionAnalytique.objects.filter(
                    entreprise=self.request.user.entreprise
                ).order_by("code"),
                "total_ecart": aggregates.get("total_ecart") or 0,
                "favorable_count": favorable_count,
                "defavorable_count": defavorable_count,
                "querystring": f"&{querystring}" if querystring else "",
                "breadcrumbs": [
                    {"label": _("Analytique"), "url": "comptabilite:analytique_dashboard"},
                    {"label": _("Analyses de variance"), "url": None},
                ],
            }
        )
        return context


class AnalyseVarianceDetailView(ComptaDetailView):
    """Affiche le détail d'une analyse de variance."""

    model = AnalyseVariance
    template_name = "comptabilite/analytique/variance_detail.html"
    context_object_name = "variance"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("exercice", "centre_couts", "section", "analyse_par")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        variance = self.object

        context.update(
            {
                "breadcrumbs": [
                    {"label": _("Analytique"), "url": "comptabilite:analytique_dashboard"},
                    {"label": _("Analyses de variance"), "url": "comptabilite:analytique_variances"},
                    {"label": str(variance), "url": None},
                ],
            }
        )
        return context


class AnalyseVarianceCreateView(ComptaCreateView):
    """Crée une analyse de variance."""

    model = AnalyseVariance
    form_class = AnalyseVarianceForm
    template_name = "comptabilite/analytique/variance_form.html"
    success_message = _("Analyse de variance créée avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.analyse_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:analytique_variance_detail", kwargs={"pk": self.object.pk})


class AnalyseVarianceUpdateView(ComptaUpdateView):
    """Met à jour une analyse de variance."""

    model = AnalyseVariance
    form_class = AnalyseVarianceForm
    template_name = "comptabilite/analytique/variance_form.html"
    success_message = _("Analyse de variance mise à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:analytique_variance_detail", kwargs={"pk": self.object.pk})
