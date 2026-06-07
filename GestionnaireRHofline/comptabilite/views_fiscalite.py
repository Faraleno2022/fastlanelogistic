"""Vues dédiées au module de fiscalité."""

from django.db.models import Sum, Count
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import ExerciceComptable
from .models_fiscalite import (
    DossierFiscalComplet,
    DeclarationIS,
    DeclarationCAT,
    DeclarationCVAE,
    LiasseFiscale,
    DocumentationFiscale,
)
from .forms_fiscalite import (
    DossierFiscalForm,
    DeclarationISForm,
    DeclarationCATForm,
    DeclarationCVAEForm,
    LiasseFiscaleForm,
    DocumentationFiscaleForm,
)
from .views.base.generic import (
    ComptaListView,
    ComptaDetailView,
    ComptaCreateView,
    ComptaUpdateView,
)


# ============== DOSSIERS FISCAUX ==============

class DossierFiscalListView(ComptaListView):
    """Liste des dossiers fiscaux."""

    model = DossierFiscalComplet
    template_name = "comptabilite/fiscalite/dossiers.html"
    context_object_name = "dossiers"
    paginate_by = 25
    search_fields = ["reference", "annee_fiscale"]
    ordering = ["-annee_fiscale"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("exercice", "valide_par", "cree_par")
            .order_by(*self.ordering)
        )

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        annee = self.request.GET.get("annee")
        if annee:
            queryset = queryset.filter(annee_fiscale=annee)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        aggregates = self.get_queryset().aggregate(
            total_impots_dus=Sum("total_impots_dus"),
            total_impots_payes=Sum("total_impots_payes"),
        )

        context.update(
            {
                "statuts": DossierFiscalComplet.STATUTS,
                "total_impots_dus": aggregates.get("total_impots_dus") or 0,
                "total_impots_payes": aggregates.get("total_impots_payes") or 0,
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Dossiers fiscaux"), "url": None},
                ],
            }
        )
        return context


class DossierFiscalDetailView(ComptaDetailView):
    """Détail d'un dossier fiscal."""

    model = DossierFiscalComplet
    template_name = "comptabilite/fiscalite/dossier_detail.html"
    context_object_name = "dossier"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("exercice", "valide_par", "cree_par")
            .prefetch_related("declarations_is", "declarations_cat", "declarations_cvae", "liasses")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dossier = self.object

        context.update(
            {
                "declarations_is": dossier.declarations_is.all()[:5],
                "declarations_cat": dossier.declarations_cat.all()[:5],
                "declarations_cvae": dossier.declarations_cvae.all()[:5],
                "liasses": dossier.liasses.all()[:5],
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Dossiers fiscaux"), "url": "comptabilite:fiscalite_dossiers"},
                    {"label": str(dossier), "url": None},
                ],
            }
        )
        return context


class DossierFiscalCreateView(ComptaCreateView):
    """Crée un dossier fiscal."""

    model = DossierFiscalComplet
    form_class = DossierFiscalForm
    template_name = "comptabilite/fiscalite/dossier_form.html"
    success_message = _("Dossier fiscal créé avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_dossier_detail", kwargs={"pk": self.object.pk})


class DossierFiscalUpdateView(ComptaUpdateView):
    """Met à jour un dossier fiscal."""

    model = DossierFiscalComplet
    form_class = DossierFiscalForm
    template_name = "comptabilite/fiscalite/dossier_form.html"
    success_message = _("Dossier fiscal mis à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_dossier_detail", kwargs={"pk": self.object.pk})


# ============== DECLARATIONS IS ==============

class DeclarationISListView(ComptaListView):
    """Liste des déclarations IS."""

    model = DeclarationIS
    template_name = "comptabilite/fiscalite/declarations_is.html"
    context_object_name = "declarations"
    paginate_by = 25
    search_fields = ["reference"]
    ordering = ["-periode_fin"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("dossier_fiscal", "valide_par")
            .order_by(*self.ordering)
        )

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        aggregates = self.get_queryset().aggregate(
            total_is=Sum("is_net"),
            total_solde=Sum("solde_a_payer"),
        )

        context.update(
            {
                "statuts": DeclarationIS.STATUTS,
                "total_is": aggregates.get("total_is") or 0,
                "total_solde": aggregates.get("total_solde") or 0,
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Déclarations IS"), "url": None},
                ],
            }
        )
        return context


class DeclarationISDetailView(ComptaDetailView):
    """Détail d'une déclaration IS."""

    model = DeclarationIS
    template_name = "comptabilite/fiscalite/declaration_is_detail.html"
    context_object_name = "declaration"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Déclarations IS"), "url": "comptabilite:fiscalite_declarations_is"},
                    {"label": str(self.object), "url": None},
                ],
            }
        )
        return context


class DeclarationISCreateView(ComptaCreateView):
    """Crée une déclaration IS."""

    model = DeclarationIS
    form_class = DeclarationISForm
    template_name = "comptabilite/fiscalite/declaration_is_form.html"
    success_message = _("Déclaration IS créée avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_declaration_is_detail", kwargs={"pk": self.object.pk})


class DeclarationISUpdateView(ComptaUpdateView):
    """Met à jour une déclaration IS."""

    model = DeclarationIS
    form_class = DeclarationISForm
    template_name = "comptabilite/fiscalite/declaration_is_form.html"
    success_message = _("Déclaration IS mise à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_declaration_is_detail", kwargs={"pk": self.object.pk})


# ============== DECLARATIONS CAT ==============

class DeclarationCATListView(ComptaListView):
    """Liste des déclarations CAT."""

    model = DeclarationCAT
    template_name = "comptabilite/fiscalite/declarations_cat.html"
    context_object_name = "declarations"
    paginate_by = 25
    search_fields = ["reference"]
    ordering = ["-annee", "-mois"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("dossier_fiscal")
            .order_by(*self.ordering)
        )

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        annee = self.request.GET.get("annee")
        if annee:
            queryset = queryset.filter(annee=annee)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        aggregates = self.get_queryset().aggregate(
            total_cat=Sum("cat_nette"),
        )

        context.update(
            {
                "statuts": DeclarationCAT.STATUTS,
                "total_cat": aggregates.get("total_cat") or 0,
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Déclarations CAT"), "url": None},
                ],
            }
        )
        return context


class DeclarationCATDetailView(ComptaDetailView):
    """Détail d'une déclaration CAT."""

    model = DeclarationCAT
    template_name = "comptabilite/fiscalite/declaration_cat_detail.html"
    context_object_name = "declaration"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Déclarations CAT"), "url": "comptabilite:fiscalite_declarations_cat"},
                    {"label": str(self.object), "url": None},
                ],
            }
        )
        return context


class DeclarationCATCreateView(ComptaCreateView):
    """Crée une déclaration CAT."""

    model = DeclarationCAT
    form_class = DeclarationCATForm
    template_name = "comptabilite/fiscalite/declaration_cat_form.html"
    success_message = _("Déclaration CAT créée avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_declaration_cat_detail", kwargs={"pk": self.object.pk})


class DeclarationCATUpdateView(ComptaUpdateView):
    """Met à jour une déclaration CAT."""

    model = DeclarationCAT
    form_class = DeclarationCATForm
    template_name = "comptabilite/fiscalite/declaration_cat_form.html"
    success_message = _("Déclaration CAT mise à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_declaration_cat_detail", kwargs={"pk": self.object.pk})


# ============== DECLARATIONS CVAE ==============

class DeclarationCVAEListView(ComptaListView):
    """Liste des déclarations CVAE."""

    model = DeclarationCVAE
    template_name = "comptabilite/fiscalite/declarations_cvae.html"
    context_object_name = "declarations"
    paginate_by = 25
    search_fields = ["reference"]
    ordering = ["-annee"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("dossier_fiscal")
            .order_by(*self.ordering)
        )

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        aggregates = self.get_queryset().aggregate(
            total_cvae=Sum("cvae_nette"),
        )

        context.update(
            {
                "statuts": DeclarationCVAE.STATUTS,
                "total_cvae": aggregates.get("total_cvae") or 0,
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Déclarations CVAE"), "url": None},
                ],
            }
        )
        return context


class DeclarationCVAEDetailView(ComptaDetailView):
    """Détail d'une déclaration CVAE."""

    model = DeclarationCVAE
    template_name = "comptabilite/fiscalite/declaration_cvae_detail.html"
    context_object_name = "declaration"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Déclarations CVAE"), "url": "comptabilite:fiscalite_declarations_cvae"},
                    {"label": str(self.object), "url": None},
                ],
            }
        )
        return context


class DeclarationCVAECreateView(ComptaCreateView):
    """Crée une déclaration CVAE."""

    model = DeclarationCVAE
    form_class = DeclarationCVAEForm
    template_name = "comptabilite/fiscalite/declaration_cvae_form.html"
    success_message = _("Déclaration CVAE créée avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_declaration_cvae_detail", kwargs={"pk": self.object.pk})


class DeclarationCVAEUpdateView(ComptaUpdateView):
    """Met à jour une déclaration CVAE."""

    model = DeclarationCVAE
    form_class = DeclarationCVAEForm
    template_name = "comptabilite/fiscalite/declaration_cvae_form.html"
    success_message = _("Déclaration CVAE mise à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_declaration_cvae_detail", kwargs={"pk": self.object.pk})


# ============== LIASSES FISCALES ==============

class LiasseFiscaleListView(ComptaListView):
    """Liste des liasses fiscales."""

    model = LiasseFiscale
    template_name = "comptabilite/fiscalite/liasses.html"
    context_object_name = "liasses"
    paginate_by = 25
    search_fields = ["reference"]
    ordering = ["-annee"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("dossier_fiscal", "valide_par")
            .order_by(*self.ordering)
        )

        statut = self.request.GET.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)

        type_liasse = self.request.GET.get("type")
        if type_liasse:
            queryset = queryset.filter(type_liasse=type_liasse)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "statuts": LiasseFiscale.STATUTS,
                "types_liasse": LiasseFiscale.TYPES_LIASSE,
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Liasses fiscales"), "url": None},
                ],
            }
        )
        return context


class LiasseFiscaleDetailView(ComptaDetailView):
    """Détail d'une liasse fiscale."""

    model = LiasseFiscale
    template_name = "comptabilite/fiscalite/liasse_detail.html"
    context_object_name = "liasse"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("dossier_fiscal", "valide_par")
            .prefetch_related("annexes")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Liasses fiscales"), "url": "comptabilite:fiscalite_liasses"},
                    {"label": str(self.object), "url": None},
                ],
            }
        )
        return context


class LiasseFiscaleCreateView(ComptaCreateView):
    """Crée une liasse fiscale."""

    model = LiasseFiscale
    form_class = LiasseFiscaleForm
    template_name = "comptabilite/fiscalite/liasse_form.html"
    success_message = _("Liasse fiscale créée avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_liasse_detail", kwargs={"pk": self.object.pk})


class LiasseFiscaleUpdateView(ComptaUpdateView):
    """Met à jour une liasse fiscale."""

    model = LiasseFiscale
    form_class = LiasseFiscaleForm
    template_name = "comptabilite/fiscalite/liasse_form.html"
    success_message = _("Liasse fiscale mise à jour avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_liasse_detail", kwargs={"pk": self.object.pk})


# ============== DOCUMENTATION FISCALE ==============

class DocumentationFiscaleListView(ComptaListView):
    """Liste de la documentation fiscale."""

    model = DocumentationFiscale
    template_name = "comptabilite/fiscalite/documentation.html"
    context_object_name = "documents"
    paginate_by = 25
    search_fields = ["titre", "description"]
    ordering = ["-date_creation"]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("dossier_fiscal", "cree_par")
            .order_by(*self.ordering)
        )

        type_doc = self.request.GET.get("type")
        if type_doc:
            queryset = queryset.filter(type_document=type_doc)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "types_document": DocumentationFiscale.TYPES_DOCUMENT,
                "breadcrumbs": [
                    {"label": _("Fiscalité"), "url": "comptabilite:fiscalite_dashboard"},
                    {"label": _("Documentation fiscale"), "url": None},
                ],
            }
        )
        return context


class DocumentationFiscaleCreateView(ComptaCreateView):
    """Ajoute un document fiscal."""

    model = DocumentationFiscale
    form_class = DocumentationFiscaleForm
    template_name = "comptabilite/fiscalite/documentation_form.html"
    success_message = _("Document fiscal ajouté avec succès.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["entreprise"] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comptabilite:fiscalite_documentation")
