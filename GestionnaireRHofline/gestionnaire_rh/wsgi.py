"""
WSGI config for gestionnaire_rh project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionnaire_rh.settings')

application = get_wsgi_application()
