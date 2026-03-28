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
        
        # Create test patient if it doesn't exist
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(email='testpatient@curova.com').exists():
            print("Creating test patient user...")
            User.objects.create_user(
                email='testpatient@curova.com',
                username='testpatient',
                password='testpass123',
                first_name='Test',
                last_name='Patient',
                user_type='patient'
            )
            print("Test patient created successfully!")
    except Exception as e:
        print(f"Startup error (continuing anyway): {e}")
