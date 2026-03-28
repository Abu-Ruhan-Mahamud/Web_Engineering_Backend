"""
WSGI config for curova_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curova_backend.settings')

application = get_wsgi_application()

# Auto-run migrations on startup (for production deployments)
if 'runserver' not in sys.argv and 'manage.py' not in sys.argv:
    try:
        call_command('migrate', '--noinput', verbosity=1)
    except Exception as e:
        print(f"Migration error (continuing anyway): {e}")
