from .base import *
import os
import dj_database_url

DEBUG = False

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'procuregov.onrender.com').split(',')

# ── HTTPS / SSL ───────────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT             = True
SECURE_HSTS_SECONDS             = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS  = True
SECURE_HSTS_PRELOAD             = True
SESSION_COOKIE_SECURE           = True
CSRF_COOKIE_SECURE              = True
SECURE_BROWSER_XSS_FILTER       = True
SECURE_CONTENT_TYPE_NOSNIFF     = True
X_FRAME_OPTIONS                 = 'DENY'

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
        conn_max_age=600,
        ssl_require=True,
    )
}

# ── Static files ──────────────────────────────────────────────────────────────
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Cloudinary media storage ──────────────────────────────────────────────────
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY':    os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}
# django-axes brute force protection
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 10                  
AXES_COOLOFF_TIME = 1                    
AXES_LOCKOUT_PARAMETERS = ['username']   
AXES_NEVER_LOCKOUT_WHITELIST = True
AXES_IP_WHITELIST = []                   


AXES_USERNAME_WHITELIST = ['admin', 'agency_admin']