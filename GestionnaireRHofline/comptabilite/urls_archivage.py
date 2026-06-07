"""
URLs pour le module Documentation & Archivage
"""

from django.urls import path

from .views_archivage import (
    ArchivageDashboardView,
    DocumentsArchivesListView, DocumentArchiveDetailView,
    DocumentArchiveCreateView, DocumentArchiveUpdateView,
    ClassementsListView, ClassementDetailView,
    ClassementCreateView, ClassementUpdateView,
    PolitiquesRetentionListView, PolitiqueDetailView,
    PolitiqueCreateView, PolitiqueUpdateView,
    PiecesJustificativesListView, MatriceCreateView, MatriceUpdateView,
    ValidationsListView, ValidationUpdateView,
    SuppressionsListView, SuppressionCreateView, SuppressionUpdateView,
    RapportsArchivageListView, RapportDetailView, RapportCreateView
)

urlpatterns = [
    # Dashboard
    path('', ArchivageDashboardView.as_view(), name='archivage_dashboard'),
    
    # Documents archivés
    path('documents/', DocumentsArchivesListView.as_view(), name='archivage_documents'),
    path('documents/nouveau/', DocumentArchiveCreateView.as_view(), name='archivage_document_create'),
    path('documents/<uuid:pk>/', DocumentArchiveDetailView.as_view(), name='archivage_document_detail'),
    path('documents/<uuid:pk>/modifier/', DocumentArchiveUpdateView.as_view(), name='archivage_document_update'),
    
    # Classements
    path('classements/', ClassementsListView.as_view(), name='archivage_classements'),
    path('classements/nouveau/', ClassementCreateView.as_view(), name='archivage_classement_create'),
    path('classements/<uuid:pk>/', ClassementDetailView.as_view(), name='archivage_classement_detail'),
    path('classements/<uuid:pk>/modifier/', ClassementUpdateView.as_view(), name='archivage_classement_update'),
    
    # Politiques de rétention
    path('politiques/', PolitiquesRetentionListView.as_view(), name='archivage_politiques'),
    path('politiques/nouveau/', PolitiqueCreateView.as_view(), name='archivage_politique_create'),
    path('politiques/<uuid:pk>/', PolitiqueDetailView.as_view(), name='archivage_politique_detail'),
    path('politiques/<uuid:pk>/modifier/', PolitiqueUpdateView.as_view(), name='archivage_politique_update'),
    
    # Pièces justificatives
    path('pieces/', PiecesJustificativesListView.as_view(), name='archivage_pieces'),
    path('pieces/nouveau/', MatriceCreateView.as_view(), name='archivage_matrice_create'),
    path('pieces/<uuid:pk>/modifier/', MatriceUpdateView.as_view(), name='archivage_matrice_update'),
    
    # Validations
    path('validations/', ValidationsListView.as_view(), name='archivage_validations'),
    path('validations/<uuid:pk>/traiter/', ValidationUpdateView.as_view(), name='archivage_validation_update'),
    
    # Suppressions
    path('suppressions/', SuppressionsListView.as_view(), name='archivage_suppressions'),
    path('suppressions/nouveau/', SuppressionCreateView.as_view(), name='archivage_suppression_create'),
    path('suppressions/<uuid:pk>/modifier/', SuppressionUpdateView.as_view(), name='archivage_suppression_update'),
    
    # Rapports
    path('rapports/', RapportsArchivageListView.as_view(), name='archivage_rapports'),
    path('rapports/nouveau/', RapportCreateView.as_view(), name='archivage_rapport_create'),
    path('rapports/<uuid:pk>/', RapportDetailView.as_view(), name='archivage_rapport_detail'),
]
