"""
Production settings for Django project.
"""
from .settings import *
from decouple import config
import dj_database_url

# Security Settings
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')

# Allowed hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Database
if config('DATABASE_URL', default=None):
    DATABASES = {
        'default': dj_database_url.parse(
            config('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=config('DB_SSL_REQUIRE', default=True, cast=bool)
        )
    }

# Security Middleware
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Static and Media Files
STATIC_ROOT = config('STATIC_ROOT', default='/var/www/static/')
MEDIA_ROOT = config('MEDIA_ROOT', default='/var/www/media/')

# Redis Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')

# CORS (restrictive in production)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]

# Logging
LOGGING['loggers']['django']['level'] = config('LOG_LEVEL', default='INFO')
LOGGING['loggers']['contracts']['level'] = config('LOG_LEVEL', default='INFO')
LOGGING['loggers']['ml_analysis']['level'] = config('LOG_LEVEL', default='INFO')

# Email Configuration (optional)
if config('EMAIL_HOST', default=None):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
