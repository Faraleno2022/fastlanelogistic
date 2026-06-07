#!/bin/bash
# PHASE 1 FOUNDATION - COMMANDES DE DÉMARRAGE RAPIDE

echo "🚀 Initialisation Phase 1 Foundation - Rapprochements bancaires"
echo ""

# 1. Créer les fichiers __init__.py
echo "📁 Création fichiers __init__.py..."
touch comptabilite/views/__init__.py
touch comptabilite/views/base/__init__.py
touch comptabilite/views/rapprochements/__init__.py
touch comptabilite/forms/__init__.py
touch comptabilite/mixins/__init__.py
touch comptabilite/permissions/__init__.py
touch comptabilite/utils/__init__.py
echo "✅ Fichiers __init__.py créés"

# 2. Générer les migrations
echo ""
echo "📦 Générer les migrations..."
python manage.py makemigrations
echo "✅ Migrations générées"

# 3. Appliquer les migrations
echo ""
echo "📝 Appliquer les migrations..."
python manage.py migrate
echo "✅ Migrations appliquées"

# 4. Créer les groupes de permissions
echo ""
echo "🔐 Créer les groupes de permissions..."
python manage.py shell << EOF
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from comptabilite.models import ExerciceComptable

# Créer les groupes
comptables, _ = Group.objects.get_or_create(name='Comptables')
assistants, _ = Group.objects.get_or_create(name='Assistants comptables')
responsables, _ = Group.objects.get_or_create(name='Responsables comptabilité')

print("✅ Groupes de permissions créés")
EOF

# 5. Vérifier la syntaxe des fichiers
echo ""
echo "✔️  Vérification de la syntaxe..."
python -m py_compile comptabilite/services/base_service.py
python -m py_compile comptabilite/services/rapprochement_service.py
python -m py_compile comptabilite/views/base/generic.py
python -m py_compile comptabilite/forms/base.py
python -m py_compile comptabilite/mixins/views.py
python -m py_compile comptabilite/permissions/decorators.py
python -m py_compile comptabilite/utils/helpers.py
echo "✅ Tous les fichiers compilent correctement"

# 6. Lancer les tests
echo ""
echo "🧪 Lancer les tests..."
python manage.py test comptabilite.tests --keepdb
echo "✅ Tests complétés"

# 7. Afficher les URLs
echo ""
echo "🌐 URLs disponibles:"
python manage.py show_urls | grep "comptabilite"

# 8. Créer superuser (optionnel)
echo ""
read -p "Créer un superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python manage.py createsuperuser
fi

# 9. Fin
echo ""
echo "🎉 Initialisation complétée!"
echo ""
echo "Prochaines étapes:"
echo "1. Démarrer le serveur: python manage.py runserver"
echo "2. Accéder à: http://localhost:8000/comptabilite/rapprochements/"
echo "3. S'authentifier avec les credentials créés"
echo "4. Tester la création d'un compte bancaire"
echo ""
echo "Documentation:"
echo "- PHASE_1_FOUNDATION_COMPLETE.md (vue d'ensemble)"
echo "- PHASE_1_EXECUTIVE_SUMMARY.md (résumé exécutif)"
echo "- INTEGRATION_GUIDE_PHASE1.md (guide d'intégration)"
echo "- PHASE_1_IMPLEMENTATION_CHECKLIST.md (checklist)"
echo ""
