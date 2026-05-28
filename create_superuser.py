import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='biki').exists():
    User.objects.create_superuser('biki', 'biki@email.com', 'biki1234')
    print("Superuser created.")
else:
    print("Superuser already exists.")