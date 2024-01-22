"""
Django settings for test_appstorespy_1 project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv
import redis

# load_dotenv()
# Load environment definition file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-u!ir*qid6as6l63718!rkbz1_sz8lrj-&4mht7mlkf1*y&m*p@'
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-u!ir*qid6as6l63718!rkbz1_sz8lrj-&4mht7mlkf1*y&m*p@"
)

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = os.environ.get("DEBUG", 1)

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # for Auth0 settings
    'app_auth0',
    'social_django',

    # 'backend.apps.BackendConfig',
    'regloginout',
    'uploader',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'django_rest_passwordreset',
    # The following apps are required for allauth:
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... include the providers to enable:
    'allauth.socialaccount.providers.mailru',
    # for django-silk
    'silk',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # for auth0 api
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    # for django-silk
    'silk.middleware.SilkyMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'test_appstorespy_1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'test_appstorespy_1.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DB_SQLITE = "sqlite"
DB_POSTGRESQL = "postgresql"

DATABASES_ALL = {
    DB_SQLITE: {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    DB_POSTGRESQL: {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "NAME": os.environ.get("POSTGRES_NAME", "postgres"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "password"),
        "PORT": int(os.environ.get("POSTGRES_PORT", "5432")),
    },
}

DATABASES = {"default": DATABASES_ALL[os.environ.get("DJANGO_DB", DB_SQLITE)]}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_AUTO_FIELD ='django.db.models.AutoField'

AUTH_USER_MODEL = 'regloginout.User'

REST_FRAMEWORK = {
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    #     'rest_framework.permissions.IsAdminUser',
    # ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # for auth0 api
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 40,
    #
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework.renderers.JSONRenderer',
    #     'rest_framework.renderers.BrowsableAPIRenderer',
    # ),
    #
    # 'DEFAULT_THROTTLE_CLASSES': [
    #     'rest_framework.throttling.AnonRateThrottle',
    #     'rest_framework.throttling.UserRateThrottle'
    # ],
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '100/day',
    #     'user': '1000/day'
    # },
    # 'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

INTERNAL_IPS = [
    '127.0.0.1',
]

# Celery Configuration Options
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

SPECTACULAR_SETTINGS = {
    'TITLE': 'Project Appstorespy API',
    'DESCRIPTION': 'Testing task for junior python dev',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

# for allauth
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    # for auth0 web
    'social_core.backends.auth0.Auth0OAuth2',
    # for auth0 api
    'django.contrib.auth.backends.RemoteUserBackend',
]

# Specifies the login method to use for allauth
ACCOUNT_AUTHENTICATION_METHOD='email'
ACCOUNT_EMAIL_REQUIRED=True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
#>

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.mail.ru")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "test@mail.ru")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "password")
EMAIL_PORT = '465'
EMAIL_USE_SSL = True
SERVER_EMAIL = EMAIL_HOST_USER
#< добавлено для устранения ошибки SMTP:550 при регистрации через allauth
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
#>

# Auth0 settings
# SOCIAL_AUTH_TRAILING_SLASH = False  # Remove trailing slash from routes
AUTH0_DOMAIN =  os.environ.get("AUTH0-DOMAIN")
AUTH0_CLIENT_ID = os.environ.get("AUTH0-CLIENT-ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0-CLIENT-SECRET")
# SOCIAL_AUTH_AUTH0_SCOPE = [
#     'openid',
#     'profile',
#     'email'
# ]

# Auth0 settings
LOGIN_URL = '/login/auth0'
LOGIN_REDIRECT_URL = '/login/auth0'
LOGOUT_REDIRECT_URL = '/login/auth0'

# for Auth0 api
JWT_AUTH = {
    'JWT_PAYLOAD_GET_USERNAME_HANDLER':
        'app_auth0.utils.jwt_get_username_from_payload_handler',
    'JWT_DECODE_HANDLER':
        'app_auth0.utils.jwt_decode_token',
    'JWT_ALGORITHM': 'RS256',
    'JWT_AUDIENCE': os.environ.get("JWT_AUDIENCE"), # yourApiIdentifier
    'JWT_ISSUER': os.environ.get("JWT_ISSUER"), # yourDomain
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}

SITE_ID = 1
#< уточнен id сайта exemple.com, без этого при обращении к /admin/ выдавал ошибку:
# "django.contrib.sites.models.Site.DoesNotExist: Site matching query does not exist"
# Решение - в консоле:
# python manage.py shell
# from django.contrib.sites.models import Site
# Site.objects.create(name='example.com',domain='example.com').save()
# s=Site.objects.filter(name='example.com')[0]
# s.id
# 4
# SITE_ID = 4
#>
