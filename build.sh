#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser and default agency admin if they don't exist
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
import os

# ── Superuser ─────────────────────────────────────────────────────────────────
su_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
su_email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@procuregov.com')
su_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if su_password and not User.objects.filter(username=su_username).exists():
    User.objects.create_superuser(
        username=su_username,
        email=su_email,
        password=su_password,
        is_staff=True,
        is_superuser=True,
    )
    print(f"Superuser '{su_username}' created.")
else:
    print(f"Superuser '{su_username}' already exists — skipping.")

# ── Agency Admin ──────────────────────────────────────────────────────────────
aa_username = os.environ.get('AGENCY_ADMIN_USERNAME', 'agency_admin')
aa_email    = os.environ.get('AGENCY_ADMIN_EMAIL', 'agency@procuregov.com')
aa_password = os.environ.get('AGENCY_ADMIN_PASSWORD')
aa_org      = os.environ.get('AGENCY_ADMIN_ORG', 'Carigara LGU')

if aa_password and not User.objects.filter(username=aa_username).exists():
    User.objects.create_user(
        username=aa_username,
        email=aa_email,
        password=aa_password,
        role='AGENCY_ADMIN',
        organization=aa_org,
        is_verified=True,
    )
    print(f"Agency admin '{aa_username}' created.")
else:
    print(f"Agency admin '{aa_username}' already exists — skipping.")
EOF