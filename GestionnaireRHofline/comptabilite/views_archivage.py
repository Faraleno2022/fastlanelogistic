"""
Vues pour le module Documentation & Archivage
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from .views.base.generic import ComptaListView, ComptaDetailView, ComptaCreateView, ComptaUpdateView
from .models_archivage import (
    ClassementDocument, PolitiqueRetention, ArchiveDocument,
    MatricePiecesJustificatives, ValidationDocument, SuppressionDocument,
    RapportArchivage, AlerteArchivage, TraceAccesDocument
)
from .forms_archivage import (
    ClassementDocumentForm, PolitiqueRetentionForm, ArchiveDocumentForm,
    MatricePiecesForm, ValidationDocumentForm, SuppressionDocumentForm,
    RapportArchivageForm
)


# ============== Dashboard ==============

class ArchivageDashboardView(ComptaListView):
    """Dashboard du module archivage"""
    template_name = 'comptabilite/archivage/dashboard.html'
    model = ArchiveDocument
    context_object_name = 'documents'
    paginate_by = 5

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('-date_archivage')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entreprise = self.request.user.entreprise
        
        if entreprise:
            # Statistiques documents
            docs = ArchiveDocument.objects.filter(entreprise=entreprise)
            context['nb_documents'] = docs.count()
            context['nb_documents_actifs'] = docs.filter(statut='actif').count()
            context['nb_documents_archives'] = docs.filter(statut='archive').count()
            context['nb_documents_a_detruire'] = docs.filter(statut='a_detruire').count()
            
            # Taille totale
            context['taille_totale'] = docs.aggregate(total=Sum('taille_octets'))['total'] or 0
            
            # Documents expirant bientôt (30 jours)
            date_limite = timezone.now().date() + timedelta(days=30)
            context['docs_expirant'] = docs.filter(
                date_expiration__lte=date_limite,
                date_expiration__gte=timezone.now().date(),
                statut='actif'
            ).count()
            
            # Validations en attente
            context['validations_attente'] = ValidationDocument.objects.filter(
                document__entreprise=entreprise,
                statut='en_attente'
            ).count()
            
            # Suppressions planifiées
            context['suppressions_planifiees'] = SuppressionDocument.objects.filter(
                entreprise=entreprise,
                statut__in=['planifiee', 'en_attente_validation', 'validee']
            ).count()
            
            # Alertes non traitées
            context['alertes_non_traitees'] = AlerteArchivage.objects.filter(
                entreprise=entreprise,
                est_traitee=False
            ).count()
            
            # Classements
            context['classements'] = ClassementDocument.objects.filter(
                entreprise=entreprise, est_actif=True
            )[:5]
            
            # Politiques
            context['politiques'] = PolitiqueRetention.objects.filter(
                entreprise=entreprise, est_actif=True
            )[:5]
            
            # Documents récents
            context['documents_recents'] = docs.order_by('-date_archivage')[:5]
            
            # Alertes récentes
            context['alertes_recentes'] = AlerteArchivage.objects.filter(
                entreprise=entreprise,
                est_traitee=False
            ).order_by('-date_alerte')[:5]
        
        return context


# ============== Documents Archivés ==============

class DocumentsArchivesListView(ComptaListView):
    """Liste des documents archivés"""
    model = ArchiveDocument
    template_name = 'comptabilite/archivage/documents.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Filtres
        statut = self.request.GET.get('statut')
        classement = self.request.GET.get('classement')
        search = self.request.GET.get('q')
        
        if statut:
            qs = qs.filter(statut=statut)
        if classement:
            qs = qs.filter(classement_id=classement)
        if search:
            qs = qs.filter(
                Q(reference__icontains=search) |
                Q(titre__icontains=search)
            )
        
        return qs.order_by('-date_archivage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuts'] = ArchiveDocument.STATUTS
        context['classements'] = ClassementDocument.objects.filter(
            entreprise=self.request.user.entreprise, est_actif=True
        ) if self.request.user.entreprise else []
        return context


class DocumentArchiveDetailView(ComptaDetailView):
    """Détail d'un document archivé"""
    model = ArchiveDocument
    template_name = 'comptabilite/archivage/document_detail.html'
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['validations'] = self.object.validations.all()
        context['traces'] = self.object.traces_acces.order_by('-date_acces')[:10]
        return context


class DocumentArchiveCreateView(ComptaCreateView):
    """Création d'un document archivé"""
    model = ArchiveDocument
    form_class = ArchiveDocumentForm
    template_name = 'comptabilite/archivage/document_form.html'
    success_url = reverse_lazy('comptabilite:archivage_documents')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entreprise'] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        form.instance.archive_par = self.request.user
        
        # Calculer la taille du fichier
        if form.cleaned_data.get('fichier'):
            form.instance.taille_octets = form.cleaned_data['fichier'].size
        
        messages.success(self.request, "Document archivé avec succès.")
        return super().form_valid(form)


class DocumentArchiveUpdateView(ComptaUpdateView):
    """Modification d'un document archivé"""
    model = ArchiveDocument
    form_class = ArchiveDocumentForm
    template_name = 'comptabilite/archivage/document_form.html'
    success_url = reverse_lazy('comptabilite:archivage_documents')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entreprise'] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Document mis à jour avec succès.")
        return super().form_valid(form)


# ============== Classements ==============

class ClassementsListView(ComptaListView):
    """Liste des classements"""
    model = ClassementDocument
    template_name = 'comptabilite/archivage/classements.html'
    context_object_name = 'classements'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        type_classement = self.request.GET.get('type')
        if type_classement:
            qs = qs.filter(type_classement=type_classement)
        return qs.order_by('code')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = ClassementDocument.TYPES_CLASSEMENT
        return context


class ClassementDetailView(ComptaDetailView):
    """Détail d'un classement"""
    model = ClassementDocument
    template_name = 'comptabilite/archivage/classement_detail.html'
    context_object_name = 'classement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.all()[:10]
        context['sous_classements'] = self.object.sous_classements.filter(est_actif=True)
        return context


class ClassementCreateView(ComptaCreateView):
    """Création d'un classement"""
    model = ClassementDocument
    form_class = ClassementDocumentForm
    template_name = 'comptabilite/archivage/classement_form.html'
    success_url = reverse_lazy('comptabilite:archivage_classements')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entreprise'] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        form.instance.cree_par = self.request.user
        
        # Calculer le niveau et le chemin
        if form.instance.parent:
            form.instance.niveau = form.instance.parent.niveau + 1
            form.instance.chemin = f"{form.instance.parent.chemin}/{form.instance.code}"
        else:
            form.instance.niveau = 1
            form.instance.chemin = form.instance.code
        
        messages.success(self.request, "Classement créé avec succès.")
        return super().form_valid(form)


class ClassementUpdateView(ComptaUpdateView):
    """Modification d'un classement"""
    model = ClassementDocument
    form_class = ClassementDocumentForm
    template_name = 'comptabilite/archivage/classement_form.html'
    success_url = reverse_lazy('comptabilite:archivage_classements')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entreprise'] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Classement mis à jour avec succès.")
        return super().form_valid(form)


# ============== Politiques de Rétention ==============

class PolitiquesRetentionListView(ComptaListView):
    """Liste des politiques de rétention"""
    model = PolitiqueRetention
    template_name = 'comptabilite/archivage/politiques.html'
    context_object_name = 'politiques'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('type_document')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = PolitiqueRetention.TYPES_DOCUMENT
        context['bases'] = PolitiqueRetention.BASES_LEGALES
        return context


class PolitiqueDetailView(ComptaDetailView):
    """Détail d'une politique"""
    model = PolitiqueRetention
    template_name = 'comptabilite/archivage/politique_detail.html'
    context_object_name = 'politique'


class PolitiqueCreateView(ComptaCreateView):
    """Création d'une politique"""
    model = PolitiqueRetention
    form_class = PolitiqueRetentionForm
    template_name = 'comptabilite/archivage/politique_form.html'
    success_url = reverse_lazy('comptabilite:archivage_politiques')

    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        messages.success(self.request, "Politique de rétention créée avec succès.")
        return super().form_valid(form)


class PolitiqueUpdateView(ComptaUpdateView):
    """Modification d'une politique"""
    model = PolitiqueRetention
    form_class = PolitiqueRetentionForm
    template_name = 'comptabilite/archivage/politique_form.html'
    success_url = reverse_lazy('comptabilite:archivage_politiques')

    def form_valid(self, form):
        messages.success(self.request, "Politique mise à jour avec succès.")
        return super().form_valid(form)


# ============== Pièces Justificatives ==============

class PiecesJustificativesListView(ComptaListView):
    """Liste des matrices de pièces justificatives"""
    model = MatricePiecesJustificatives
    template_name = 'comptabilite/archivage/pieces.html'
    context_object_name = 'matrices'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('type_operation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = MatricePiecesJustificatives.TYPES_OPERATION
        return context


class MatriceCreateView(ComptaCreateView):
    """Création d'une matrice"""
    model = MatricePiecesJustificatives
    form_class = MatricePiecesForm
    template_name = 'comptabilite/archivage/matrice_form.html'
    success_url = reverse_lazy('comptabilite:archivage_pieces')

    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        messages.success(self.request, "Matrice créée avec succès.")
        return super().form_valid(form)


class MatriceUpdateView(ComptaUpdateView):
    """Modification d'une matrice"""
    model = MatricePiecesJustificatives
    form_class = MatricePiecesForm
    template_name = 'comptabilite/archivage/matrice_form.html'
    success_url = reverse_lazy('comptabilite:archivage_pieces')

    def form_valid(self, form):
        messages.success(self.request, "Matrice mise à jour avec succès.")
        return super().form_valid(form)


# ============== Validations ==============

class ValidationsListView(ComptaListView):
    """Liste des validations"""
    model = ValidationDocument
    template_name = 'comptabilite/archivage/validations.html'
    context_object_name = 'validations'
    paginate_by = 20

    def get_queryset(self):
        entreprise = self.request.user.entreprise
        if entreprise:
            qs = ValidationDocument.objects.filter(document__entreprise=entreprise)
        else:
            qs = ValidationDocument.objects.none()
        
        statut = self.request.GET.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        
        return qs.order_by('-document__date_archivage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuts'] = ValidationDocument.STATUTS
        
        entreprise = self.request.user.entreprise
        if entreprise:
            context['nb_en_attente'] = ValidationDocument.objects.filter(
                document__entreprise=entreprise, statut='en_attente'
            ).count()
            context['nb_valides'] = ValidationDocument.objects.filter(
                document__entreprise=entreprise, statut='valide'
            ).count()
            context['nb_rejetes'] = ValidationDocument.objects.filter(
                document__entreprise=entreprise, statut='rejete'
            ).count()
        
        return context


class ValidationUpdateView(ComptaUpdateView):
    """Traitement d'une validation"""
    model = ValidationDocument
    form_class = ValidationDocumentForm
    template_name = 'comptabilite/archivage/validation_form.html'
    success_url = reverse_lazy('comptabilite:archivage_validations')

    def form_valid(self, form):
        form.instance.validateur = self.request.user
        form.instance.date_validation = timezone.now()
        messages.success(self.request, "Validation traitée avec succès.")
        return super().form_valid(form)


# ============== Suppressions ==============

class SuppressionsListView(ComptaListView):
    """Liste des demandes de suppression"""
    model = SuppressionDocument
    template_name = 'comptabilite/archivage/suppressions.html'
    context_object_name = 'suppressions'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        statut = self.request.GET.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        return qs.order_by('-date_planifiee')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuts'] = SuppressionDocument.STATUTS
        
        entreprise = self.request.user.entreprise
        if entreprise:
            context['nb_planifiees'] = SuppressionDocument.objects.filter(
                entreprise=entreprise, statut='planifiee'
            ).count()
            context['nb_en_attente'] = SuppressionDocument.objects.filter(
                entreprise=entreprise, statut='en_attente_validation'
            ).count()
            context['nb_executees'] = SuppressionDocument.objects.filter(
                entreprise=entreprise, statut='executee'
            ).count()
        
        return context


class SuppressionCreateView(ComptaCreateView):
    """Création d'une demande de suppression"""
    model = SuppressionDocument
    form_class = SuppressionDocumentForm
    template_name = 'comptabilite/archivage/suppression_form.html'
    success_url = reverse_lazy('comptabilite:archivage_suppressions')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entreprise'] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        form.instance.cree_par = self.request.user
        messages.success(self.request, "Demande de suppression créée avec succès.")
        return super().form_valid(form)


class SuppressionUpdateView(ComptaUpdateView):
    """Modification d'une demande de suppression"""
    model = SuppressionDocument
    form_class = SuppressionDocumentForm
    template_name = 'comptabilite/archivage/suppression_form.html'
    success_url = reverse_lazy('comptabilite:archivage_suppressions')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entreprise'] = self.request.user.entreprise
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Demande de suppression mise à jour avec succès.")
        return super().form_valid(form)


# ============== Rapports ==============

class RapportsArchivageListView(ComptaListView):
    """Liste des rapports d'archivage"""
    model = RapportArchivage
    template_name = 'comptabilite/archivage/rapports.html'
    context_object_name = 'rapports'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        type_rapport = self.request.GET.get('type')
        if type_rapport:
            qs = qs.filter(type_rapport=type_rapport)
        return qs.order_by('-date_generation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = RapportArchivage.TYPES_RAPPORT
        return context


class RapportDetailView(ComptaDetailView):
    """Détail d'un rapport"""
    model = RapportArchivage
    template_name = 'comptabilite/archivage/rapport_detail.html'
    context_object_name = 'rapport'


class RapportCreateView(ComptaCreateView):
    """Création d'un rapport"""
    model = RapportArchivage
    form_class = RapportArchivageForm
    template_name = 'comptabilite/archivage/rapport_form.html'
    success_url = reverse_lazy('comptabilite:archivage_rapports')

    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        form.instance.genere_par = self.request.user
        
        # Calculer les statistiques
        entreprise = self.request.user.entreprise
        if entreprise:
            docs = ArchiveDocument.objects.filter(
                entreprise=entreprise,
                date_document__gte=form.instance.date_debut,
                date_document__lte=form.instance.date_fin
            )
            form.instance.nombre_documents = docs.count()
            taille = docs.aggregate(total=Sum('taille_octets'))['total'] or 0
            form.instance.taille_totale_mo = taille / (1024 * 1024)
        
        messages.success(self.request, "Rapport généré avec succès.")
        return super().form_valid(form)
