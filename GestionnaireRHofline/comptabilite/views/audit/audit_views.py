"""
Vues pour la gestion de l'audit et de la conformité.

Fournissent:
- Gestion des rapports d'audit
- Affichage des alertes de non-conformité
- Dashboard audit avec KPIs
- Historique des modifications
- Vérification de conformité
"""

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
import logging

from ...models import (
    RapportAudit, AlerteNonConformite, ReglesConformite, HistoriqueModification
)
from ...services.audit_service import AuditService, ConformiteService, HistoriqueModificationService
from ...mixins.views import ComptabiliteAccessMixin, EntrepriseFilterMixin, AuditMixin
from ...forms import (
    RapportAuditForm, AlerteNonConformiteForm, ReglesConformiteForm,
    ConformiteCheckForm, RapportAuditFilterForm
)

logger = logging.getLogger(__name__)


# ============================================================================
# RAPPORT AUDIT VIEWS
# ============================================================================

class RapportAuditListView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    ListView
):
    """Liste les rapports d'audit de l'entreprise."""
    
    model = RapportAudit
    template_name = 'comptabilite/audit/rapport_list.html'
    context_object_name = 'rapports'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Filtrer par statut si fourni
        statut = self.request.GET.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        
        # Filtrer par date
        date_depuis = self.request.GET.get('date_depuis')
        if date_depuis:
            qs = qs.filter(date_debut__gte=date_depuis)
        
        return qs.order_by('-date_debut').prefetch_related('alertes')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Rapports d'audit")
        context['statuts'] = RapportAudit.STATUT_CHOICES
        context['statut_actuel'] = self.request.GET.get('statut', '')
        context['total_rapports'] = self.get_queryset().count()
        context['rapports_en_cours'] = self.get_queryset().filter(
            statut='EN_COURS'
        ).count()
        return context


class RapportAuditDetailView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    DetailView
):
    """Affiche les détails d'un rapport d'audit avec alertes et résumé."""
    
    model = RapportAudit
    template_name = 'comptabilite/audit/rapport_detail.html'
    context_object_name = 'rapport'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Rapport d'audit: %(code)s") % {'code': self.object.code}
        
        # Alertes groupées par sévérité
        alertes = self.object.alertes.all()
        context['alertes_critiques'] = alertes.filter(severite='CRITIQUE')
        context['alertes_majeures'] = alertes.filter(severite='MAJEURE')
        context['alertes_mineures'] = alertes.filter(severite='MINEURE')
        
        context['total_alertes'] = alertes.count()
        context['alertes_non_resolues'] = alertes.filter(
            statut__in=['DETECTEE', 'EN_CORRECTION']
        ).count()
        context['alertes_resolues'] = alertes.filter(
            statut__in=['CORRIGEE', 'VERIFIEE', 'ACCEPTEE']
        ).count()
        
        # Historique des modifications
        context['modifications'] = HistoriqueModification.objects.filter(
            entreprise=self.request.user.entreprise,
            type_objet='RAPPORT_AUDIT',
            id_objet=str(self.object.id)
        ).order_by('-date_modification')[:10]
        
        return context


class RapportAuditCreateView(
    ComptabiliteAccessMixin,
    AuditMixin,
    SuccessMessageMixin,
    CreateView
):
    """Crée un nouveau rapport d'audit."""
    
    model = RapportAudit
    form_class = RapportAuditForm
    template_name = 'comptabilite/audit/rapport_form.html'
    success_message = _("Rapport d'audit '%(code)s' créé avec succès")
    
    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        form.instance.cree_par = self.request.user
        form.instance.auditeur = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.get_absolute_url()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Créer un rapport d'audit")
        context['action'] = 'create'
        return context


class RapportAuditUpdateView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    AuditMixin,
    SuccessMessageMixin,
    UpdateView
):
    """Modifie un rapport d'audit existant."""
    
    model = RapportAudit
    form_class = RapportAuditForm
    template_name = 'comptabilite/audit/rapport_form.html'
    success_message = _("Rapport d'audit modifié avec succès")
    
    def get_success_url(self):
        return self.object.get_absolute_url()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Modifier le rapport d'audit")
        context['action'] = 'update'
        return context


# ============================================================================
# ALERTE NON-CONFORMITÉ VIEWS
# ============================================================================

class AlerteNonConformiteListView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    ListView
):
    """Liste les alertes de non-conformité de l'entreprise."""
    
    model = AlerteNonConformite
    template_name = 'comptabilite/audit/alerte_list.html'
    context_object_name = 'alertes'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Filtrer par sévérité
        severite = self.request.GET.get('severite')
        if severite:
            qs = qs.filter(severite=severite)
        
        # Filtrer par statut
        statut = self.request.GET.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        
        # Filtrer par domaine
        domaine = self.request.GET.get('domaine')
        if domaine:
            qs = qs.filter(domaine=domaine)
        
        return qs.order_by('-date_creation').select_related('rapport')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Alertes de non-conformité")
        context['severites'] = AlerteNonConformite.SEVERITE_CHOICES
        context['statuts'] = AlerteNonConformite.STATUT_CHOICES
        
        # Statistiques
        alertes = self.get_queryset()
        context['total_alertes'] = alertes.count()
        context['alertes_critiques'] = alertes.filter(severite='CRITIQUE').count()
        context['alertes_non_resolues'] = alertes.filter(
            statut__in=['DETECTEE', 'EN_CORRECTION']
        ).count()
        
        return context


class AlerteNonConformiteCreateView(
    ComptabiliteAccessMixin,
    AuditMixin,
    SuccessMessageMixin,
    CreateView
):
    """Crée une alerte de non-conformité."""
    
    model = AlerteNonConformite
    form_class = AlerteNonConformiteForm
    template_name = 'comptabilite/audit/alerte_form.html'
    success_message = _("Alerte créée avec succès")
    
    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('comptabilite:alerte_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Créer une alerte")
        return context


class AlerteNonConformiteUpdateView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    AuditMixin,
    SuccessMessageMixin,
    UpdateView
):
    """Modifie une alerte (enregistre correction)."""
    
    model = AlerteNonConformite
    form_class = AlerteNonConformiteForm
    template_name = 'comptabilite/audit/alerte_form.html'
    success_message = _("Alerte modifiée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('comptabilite:alerte_list')


# ============================================================================
# HISTORIQUE MODIFICATIONS VIEWS
# ============================================================================

class HistoriqueModificationListView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    ListView
):
    """Affiche l'historique des modifications récentes."""
    
    model = HistoriqueModification
    template_name = 'comptabilite/audit/historique_list.html'
    context_object_name = 'modifications'
    paginate_by = 50
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Filtrer par type d'objet
        type_objet = self.request.GET.get('type_objet')
        if type_objet:
            qs = qs.filter(type_objet=type_objet)
        
        # Filtrer par action
        action = self.request.GET.get('action')
        if action:
            qs = qs.filter(action=action)
        
        # Filtrer par utilisateur
        utilisateur_id = self.request.GET.get('utilisateur')
        if utilisateur_id:
            qs = qs.filter(utilisateur_id=utilisateur_id)
        
        return qs.order_by('-date_modification').select_related('utilisateur')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Historique des modifications")
        context['types_objet'] = HistoriqueModification.TYPE_OBJET_CHOICES
        context['actions'] = [
            ('CREATE', _('Création')),
            ('UPDATE', _('Modification')),
            ('DELETE', _('Suppression')),
            ('APPROVE', _('Approbation')),
        ]
        
        # Statistiques
        qs = self.get_queryset()
        context['total_modifications'] = qs.count()
        context['modifications_auj'] = qs.filter(
            date_modification__date=timezone.now().date()
        ).count()
        
        return context


# ============================================================================
# CONFORMITÉ & AUDIT DASHBOARD
# ============================================================================

class ConformiteDashboardView(
    ComptabiliteAccessMixin,
    TemplateView
):
    """Dashboard d'audit avec KPIs et résumé de conformité."""
    
    template_name = 'comptabilite/audit/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entreprise = self.request.user.entreprise
        
        # Score de conformité global
        service_conformite = ConformiteService(self.request.user)
        score_data = service_conformite.obtenir_conformite_globale()
        context['score_conformite'] = score_data['score']
        context['total_alertes'] = score_data['alertes_non_resolues']
        context['alertes_critiques'] = score_data['alertes_critiques']
        
        # Rapports
        rapports = RapportAudit.objects.filter(
            entreprise=entreprise
        ).order_by('-date_debut')
        context['total_rapports'] = rapports.count()
        context['rapports_termines'] = rapports.filter(statut='TERMINE').count()
        context['rapport_recent'] = rapports.first()
        
        # Alertes
        alertes = AlerteNonConformite.objects.filter(
            entreprise=entreprise
        )
        context['alertes_par_severite'] = {
            'CRITIQUE': alertes.filter(severite='CRITIQUE').count(),
            'MAJEURE': alertes.filter(severite='MAJEURE').count(),
            'MINEURE': alertes.filter(severite='MINEURE').count(),
        }
        context['alertes_par_statut'] = {
            'DETECTEE': alertes.filter(statut='DETECTEE').count(),
            'EN_CORRECTION': alertes.filter(statut='EN_CORRECTION').count(),
            'RESOLUE': alertes.filter(statut__in=['CORRIGEE', 'VERIFIEE', 'ACCEPTEE']).count(),
        }
        
        # Modifications récentes
        service_histo = HistoriqueModificationService(self.request.user)
        context['modifications_recentes'] = service_histo.obtenir_modifications_recentes(heures=24)[:10]
        context['total_modifications'] = HistoriqueModification.objects.filter(
            entreprise=entreprise
        ).count()
        
        # Regles de conformité
        regles = ReglesConformite.objects.filter(
            entreprise=entreprise,
            actif=True
        )
        context['total_regles'] = regles.count()
        context['regles_par_module'] = {
            'TVA': regles.filter(module_concerne='TVA').count(),
            'Comptabilité': regles.filter(module_concerne='Comptabilité').count(),
            'Paie': regles.filter(module_concerne='Paie').count(),
        }
        
        # Timeline récente
        context['timeline_events'] = self._construire_timeline()
        
        context['titre'] = _("Tableau de bord audit et conformité")
        return context
    
    def _construire_timeline(self):
        """Construit une timeline des événements importants."""
        events = []
        
        # Rapports récents
        rapports = RapportAudit.objects.filter(
            entreprise=self.request.user.entreprise
        ).order_by('-date_modification')[:5]
        for rapport in rapports:
            events.append({
                'type': 'rapport',
                'titre': f"Rapport {rapport.code}",
                'date': rapport.date_modification,
                'icone': 'fa-file-pdf',
                'couleur': 'primary',
            })
        
        # Alertes critiques récentes
        alertes = AlerteNonConformite.objects.filter(
            entreprise=self.request.user.entreprise,
            severite='CRITIQUE'
        ).order_by('-date_creation')[:3]
        for alerte in alertes:
            events.append({
                'type': 'alerte',
                'titre': f"Alerte: {alerte.titre}",
                'date': alerte.date_creation,
                'icone': 'fa-exclamation-triangle',
                'couleur': 'danger',
            })
        
        return sorted(events, key=lambda x: x['date'], reverse=True)[:10]


class ConformiteCheckView(
    ComptabiliteAccessMixin,
    View
):
    """Effectue une vérification de conformité manuelle."""
    
    def post(self, request):
        """Lance une vérification de conformité."""
        try:
            service = ConformiteService(request.user)
            
            # Vérifier les règles
            alertes = service.verifier_regles()
            
            if alertes:
                messages.warning(
                    request,
                    _("Vérification complétée: %(count)d anomalies détectées") % {
                        'count': len(alertes)
                    }
                )
            else:
                messages.success(
                    request,
                    _("Vérification complétée: Aucune anomalie détectée")
                )
            
            return redirect('comptabilite:audit_dashboard')
        
        except Exception as e:
            logger.error(f"Erreur vérification conformité: {e}")
            messages.error(request, _("Erreur lors de la vérification"))
            return redirect('comptabilite:audit_dashboard')


class ReglesConformiteListView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    ListView
):
    """Liste les règles de conformité configurées."""
    
    model = ReglesConformite
    template_name = 'comptabilite/audit/regles_list.html'
    context_object_name = 'regles'
    paginate_by = 30
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Filtrer par module
        module = self.request.GET.get('module')
        if module:
            qs = qs.filter(module_concerne=module)
        
        # Filtrer par criticité
        criticite = self.request.GET.get('criticite')
        if criticite:
            qs = qs.filter(criticite=criticite)
        
        return qs.order_by('module_concerne', 'code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Règles de conformité")
        
        regles = self.get_queryset()
        context['total_regles'] = regles.count()
        context['regles_actives'] = regles.filter(actif=True).count()
        
        # Modules disponibles
        context['modules'] = regles.values('module_concerne').distinct()
        
        return context


class ReglesConformiteCreateView(
    ComptabiliteAccessMixin,
    AuditMixin,
    SuccessMessageMixin,
    CreateView
):
    """Crée une nouvelle règle de conformité."""
    
    model = ReglesConformite
    form_class = ReglesConformiteForm
    template_name = 'comptabilite/audit/regles_form.html'
    success_message = _("Règle de conformité créée avec succès")
    
    def form_valid(self, form):
        form.instance.entreprise = self.request.user.entreprise
        form.instance.cree_par = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('comptabilite:regles_list')
