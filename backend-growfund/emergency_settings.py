# Emergency settings to fix 502 Bad Gateway and CORS issues
from .settings import *

# Temporarily allow all origins to fix CORS immediately
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Ensure DEBUG is properly set
DEBUG = config('DEBUG', default=True, cast=bool)

# Simplified database settings
DATABASES['default']['CONN_MAX_AGE'] = 0

# Minimal logging to avoid issues
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Ensure all required apps are properly configured
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # Local apps
    'accounts',
    'investments',
    'transactions',
    'referrals',
    'notifications',
]