#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser from environment variables if it doesn't exist yet
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@procuregov.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        is_staff=True,
        is_superuser=True,
    )
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists or no password set — skipping.")
EOF