"""
Vues pour la gestion des rapprochements bancaires.

Implémente le CRUD complet avec:
- Création/édition/suppression de rapprochements
- Import d'opérations bancaires
- Lettrage (matching) des opérations
- Génération de rapports
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.http import JsonResponse
from decimal import Decimal
import logging

from comptabilite.models import (
    RapprochementBancaire, CompteBancaire, OperationBancaire, 
    EcritureComptable, EcartBancaire
)
from comptabilite.forms import (
    CompteBancaireForm, RapprochementBancaireForm,
    OperationImportForm, EcartBancaireForm, BulkLettrageForm
)
from comptabilite.services.rapprochement_service import RapprochementService
from comptabilite.views.base.generic import (
    ComptaListView, ComptaDetailView, ComptaCreateView,
    ComptaUpdateView, ComptaDeleteView, ComptaAjaxView
)


class CompteBancaireListView(ComptaListView):
    """Liste des comptes bancaires."""
    
    model = CompteBancaire
    template_name = 'comptabilite/rapprochements/compte_list.html'
    search_fields = ['code', 'iban', 'libelle']
    filter_fields = ['banque', 'est_actif']
    ordering = ['code']  # Correction: utiliser 'code' au lieu de 'numero_compte'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoute des statistiques
        context['total_solde'] = sum(
            c.solde_initial for c in context['objects']
        ) if context['objects'] else Decimal('0.00')
        return context


class CompteBancaireDetailView(ComptaDetailView):
    """Détail d'un compte bancaire."""
    
    model = CompteBancaire
    template_name = 'comptabilite/rapprochements/compte_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Opérations non lettrées
        context['operations_non_lettrees'] = self.object.operations.filter(
            lettre=False
        ).order_by('-date')[:10]
        
        # Dernier rapprochement
        context['dernier_rapprochement'] = self.object.rapprochements.filter(
            statut='FINALIZE'
        ).order_by('-date_rapprochement').first()
        
        # Solde comptable actuel
        service = RapprochementService(
            self.request.user.entreprise,
            self.request.user
        )
        context['solde_comptable'] = service.calculer_solde_comptable(
            self.object, None
        )
        
        return context


class CompteBancaireCreateView(ComptaCreateView):
    """Création d'un compte bancaire."""
    
    model = CompteBancaire
    form_class = CompteBancaireForm
    template_name = 'comptabilite/rapprochements/compte_form.html'
    success_url = reverse_lazy('comptabilite:compte-bancaire-list')  # Correction: utiliser le bon nom d'URL
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class CompteBancaireUpdateView(ComptaUpdateView):
    """Édition d'un compte bancaire."""
    
    model = CompteBancaire
    form_class = CompteBancaireForm
    template_name = 'comptabilite/rapprochements/compte_form.html'
    success_url = reverse_lazy('comptabilite:compte-bancaire-list')  # Correction: utiliser le bon nom d'URL
    


class CompteBancaireDeleteView(ComptaDeleteView):
    """Suppression d'un compte bancaire."""
    
    model = CompteBancaire
    success_url = reverse_lazy('comptabilite:compte-bancaire-list')


class RapprochementListView(ComptaListView):
    """Liste des rapprochements bancaires."""
    
    model = RapprochementBancaire
    template_name = 'comptabilite/rapprochements/rapprochement_list.html'
    search_fields = ['compte_bancaire__code', 'compte_bancaire__libelle', 'notes']
    filter_fields = ['statut', 'compte_bancaire']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques
        rapprochements = context['objects']
        context['total_comptable'] = sum(
            r.solde_comptable for r in rapprochements
        ) if rapprochements else Decimal('0.00')
        context['total_bancaire'] = sum(
            r.solde_bancaire for r in rapprochements
        ) if rapprochements else Decimal('0.00')
        
        return context


class RapprochementDetailView(ComptaDetailView):
    """Détail d'un rapprochement."""
    
    model = RapprochementBancaire
    template_name = 'comptabilite/rapprochements/rapprochement_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Opérations du compte
        context['operations'] = OperationBancaire.objects.filter(
            compte_bancaire=self.object.compte_bancaire,
            date__lte=self.object.date_releve_bancaire
        )
        
        # Écarts
        context['ecarts'] = EcartBancaire.objects.filter(
            rapprochement=self.object
        )
        
        # Écritures comptables associées
        context['ecritures'] = EcritureComptable.objects.filter(
            compte=self.object.compte_bancaire.numero_compte,
            date__lte=self.object.date_rapprochement
        )
        
        return context


class RapprochementCreateView(ComptaCreateView):
    """Création d'un rapprochement."""
    
    model = RapprochementBancaire
    form_class = RapprochementBancaireForm
    template_name = 'comptabilite/rapprochements/rapprochement_form.html'
    success_url = reverse_lazy('comptabilite:rapprochement-list')
    
    def form_valid(self, form):
        """Crée le rapprochement via le service."""
        try:
            service = RapprochementService(
                self.request.user.entreprise,
                self.request.user
            )
            
            rapprochement = service.creer_rapprochement(
                form.cleaned_data['compte_bancaire'],
                None,  # releve
                form.cleaned_data['date_rapprochement']
            )
            
            messages.success(
                self.request,
                _("Rapprochement créé avec succès")
            )
            self.object = rapprochement
            return redirect(self.success_url)
            
        except Exception as e:
            messages.error(self.request, f"Erreur: {e}")
            return self.form_invalid(form)


class RapprochementUpdateView(ComptaUpdateView):
    """Édition d'un rapprochement."""
    
    model = RapprochementBancaire
    form_class = RapprochementBancaireForm
    template_name = 'comptabilite/rapprochements/rapprochement_form.html'
    success_url = reverse_lazy('comptabilite:rapprochement-list')


class RapprochementDeleteView(ComptaDeleteView):
    """Suppression d'un rapprochement."""
    
    model = RapprochementBancaire
    success_url = reverse_lazy('comptabilite:rapprochement-list')


class OperationImportView(ComptaCreateView):
    """Import d'opérations bancaires."""
    
    form_class = OperationImportForm
    template_name = 'comptabilite/rapprochements/import_operations.html'
    success_url = reverse_lazy('comptabilite:operation-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comptes'] = CompteBancaire.objects.filter(
            entreprise=self.request.user.entreprise
        )
        return context
    
    def form_valid(self, form):
        """Traite l'import."""
        try:
            fichier = form.cleaned_data['fichier']
            format_fichier = form.cleaned_data['format_fichier']
            encodage = form.cleaned_data['encodage']
            
            # À implémenter: parsing selon format
            nombre_operations = 0
            
            messages.success(
                self.request,
                _(f"{nombre_operations} opérations importées")
            )
            return redirect(self.success_url)
            
        except Exception as e:
            messages.error(self.request, f"Erreur d'import: {e}")
            return self.form_invalid(form)


class LettrageView(ComptaAjaxView):
    """AJAX pour le lettrage (matching) d'opérations."""
    
    def post(self, request, *args, **kwargs):
        """Lettre une opération à une écriture comptable."""
        try:
            operation_id = request.POST.get('operation_id')
            ecriture_id = request.POST.get('ecriture_id')
            
            operation = get_object_or_404(
                OperationBancaire, id=operation_id
            )
            ecriture = get_object_or_404(
                EcritureComptable, id=ecriture_id
            )
            
            # Vérifie l'accès
            if operation.compte_bancaire.entreprise != request.user.entreprise:
                return self.get_error_response(
                    _("Accès refusé"), 403
                )
            
            # Lettre
            service = RapprochementService(
                request.user.entreprise,
                request.user
            )
            service.lettrer_operation(operation, ecriture)
            
            return self.get_success_response(
                _("Opération lettrée avec succès")
            )
            
        except Exception as e:
            return self.get_error_response(str(e))


class LettrageAnnulationView(ComptaAjaxView):
    """AJAX pour annuler un lettrage."""
    
    def post(self, request, *args, **kwargs):
        """Annule le lettrage d'une opération."""
        try:
            operation_id = request.POST.get('operation_id')
            
            operation = get_object_or_404(
                OperationBancaire, id=operation_id
            )
            
            if operation.compte_bancaire.entreprise != request.user.entreprise:
                return self.get_error_response(
                    _("Accès refusé"), 403
                )
            
            operation.lettre = False
            operation.ecriture_lettre = None
            operation.save()
            
            return self.get_success_response(
                _("Lettrage annulé")
            )
            
        except Exception as e:
            return self.get_error_response(str(e))


class RapprochementFinalisationView(ComptaAjaxView):
    """Finalise un rapprochement."""
    
    def post(self, request, *args, **kwargs):
        """Finalise un rapprochement."""
        try:
            rapprochement_id = request.POST.get('rapprochement_id')
            
            rapprochement = get_object_or_404(
                RapprochementBancaire, id=rapprochement_id
            )
            
            if rapprochement.entreprise != request.user.entreprise:
                return self.get_error_response(
                    _("Accès refusé"), 403
                )
            
            # Finalise via service
            service = RapprochementService(
                request.user.entreprise,
                request.user
            )
            service.valider_rapprochement(rapprochement)
            
            return self.get_success_response(
                _("Rapprochement finalisé")
            )
            
        except Exception as e:
            return self.get_error_response(str(e))
