# =============================================================================
# CONFIGURACIÓN DE SETTINGS PARA PRODUCCIÓN
# =============================================================================

"""
Configuración adicional de Django para producción.
Añadir estas configuraciones al final de settings.py
"""

import os
from decouple import config

# 1. CONFIGURACIONES DE PRODUCCIÓN ADICIONALES
if not config('DEBUG', default=True, cast=bool):
    
    # Security Settings
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
    SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Static Files
    STATIC_ROOT = config('STATIC_ROOT', default='/var/www/contract-analysis/static/')
    MEDIA_ROOT = config('MEDIA_ROOT', default='/var/www/contract-analysis/media/')
    
    # WhiteNoise for static files
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # CORS actualizado para producción
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
    CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=False, cast=bool)
    
    # Cache con Redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
    
    # Logging para producción
    LOGGING['handlers']['file']['filename'] = config('LOG_FILE', default='/var/log/contract-analysis/django.log')
    LOGGING['root'] = {
        'level': config('LOG_LEVEL', default='INFO'),
        'handlers': ['file', 'console'],
    }

# 2. CONFIGURACIÓN DE EMAIL (opcional)
if config('EMAIL_HOST', default=''):
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = config('EMAIL_HOST')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# 3. CONFIGURACIONES ESPECÍFICAS PARA ML
# Aumentar timeouts para procesamiento ML
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB

# Configurar path de modelos ML
ML_MODELS_PATH = BASE_DIR / 'ml_models'
if not ML_MODELS_PATH.exists():
    ML_MODELS_PATH.mkdir(exist_ok=True)

# 4. CONFIGURACIÓN DE CELERY PARA PRODUCCIÓN
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    # Ejemplo: limpiar archivos temporales cada día
    'cleanup-temp-files': {
        'task': 'contracts.tasks.cleanup_temp_files',
        'schedule': 24 * 60 * 60,  # 24 horas
    },
}

# 5. CONFIGURACIONES DE APIS EXTERNAS
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
TOGETHER_API_KEY = config('TOGETHER_API_KEY', default='')

# 6. CONFIGURACIÓN DE MONITORING (opcional)
# Sentry para tracking de errores
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(auto_enabling=True),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True
    )
