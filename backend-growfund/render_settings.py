# Render-optimized settings for memory efficiency
import os
from .settings import *

# Memory optimization for Render
DEBUG = False

# CORS Settings for production - Add current frontend URL
CORS_ALLOWED_ORIGINS = [
    'https://growfund-dashboard.onrender.com',  # Original frontend URL
    'https://dashboard-yfb8.onrender.com',      # Current frontend URL
    'http://localhost:3000',  # Local development
    'http://localhost:3001',
    'http://127.0.0.1:3000',
]

CORS_ALLOW_CREDENTIALS = True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'https://growfun-backend.onrender.com',
    'https://growfund-dashboard.onrender.com',  # Original frontend
    'https://dashboard-yfb8.onrender.com',      # Current frontend
]

# Reduce memory usage
DATABASES['default']['CONN_MAX_AGE'] = 0  # Don't keep connections alive
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 1,  # Limit database connections
}

# Optimize logging to reduce memory
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',  # Only log warnings and errors
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Reduce session memory usage
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour instead of 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Optimize static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Reduce cache memory usage
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Optimize REST framework
REST_FRAMEWORK.update({
    'PAGE_SIZE': 10,  # Reduce page size to save memory
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
})

# Reduce JWT token lifetime to save memory
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # Reduced from 60
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=12),   # Reduced from 24 hours
})

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB instead of 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB instead of 5MB

# Disable unnecessary features in production
USE_TZ = True
USE_I18N = False  # Disable internationalization to save memory
USE_L10N = False  # Disable localization to save memory