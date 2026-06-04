from .base import *

DEBUG = True
SECRET_KEY = 'dev-secret-key-change-in-prod'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ── Django Axes (brute force protection) ──────────────────────────────────
AXES_ENABLED = False   # Keep False during normal development to avoid lockouts
                       # Change to True temporarily if you want to test the feature
AXES_FAILURE_LIMIT = 10
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_PARAMETERS = ['username']
AXES_USERNAME_WHITELIST = ['admin', 'agency_admin']