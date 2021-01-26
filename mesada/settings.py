"""
Django settings for mesada project.

Generated by 'django-admin startproject' using Django 1.11.29.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

import django_cache_url
import environ

root = environ.Path(__file__) - 3  # get root of the project
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "3w4x62a8bdkdv%z@1z7t9y7gf=ircv!bdj9q9rm%6)_f#t3k5t"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "usa-testing.mesada.io",
    "usa.mesada.io",
    "localhost",
    "usa-production.mesada.io",
    "mesada-usa-testing.eba-aw53wdis.us-east-1.elasticbeanstalk.com",
    "testserver",
]

AUTH_USER_MODEL = "account.User"
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "corsheaders",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mesada.account",
    "mesada.checkout",
    "mesada.core",
    "mesada.galactus",
    "mesada.graphql",
    "mesada.payment",
    "mesada.transfer",
    "mesada.withdrawal",
    "django_extensions",
    "graphene_django",
    "django_filters",
    "phonenumber_field",
    "djmoney",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
]

# this have to change to CORS_ORIGIN_WHITELIST in production env
CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = "mesada.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_ROOT, "templates")],
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "string_if_invalid": '<< MISSING VARIABLE "%s" >>' if DEBUG else "",
        },
    }
]

WSGI_APPLICATION = "mesada.wsgi.application"

# Database

# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {"default": env.db("DATABASE_URL")}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": ("django.contrib.auth.password_validation.CommonPasswordValidator")},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/static/"

ALLOWED_GRAPHQL_ORIGINS = os.environ.get("ALLOWED_GRAPHQL_ORIGINS", "*")

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

GRAPHENE = {
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware"],
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": True,
    "RELAY_CONNECTION_MAX_LIMIT": 100,
}

CACHES = {"default": django_cache_url.config()}

# CIRCLE
CIRCLE_API_KEY = env("CIRCLE_API_KEY")
CIRCLE_BASE_URL = env("CIRCLE_BASE_URL")
CIRCLE_WALLET_ID = env("CIRCLE_WALLET_ID")
CIRCLE_BLOCKCHAIN_CHAIN = env("CIRCLE_BLOCKCHAIN_CHAIN")
BITSO_BLOCKCHAIN_ADDRESS = env("BITSO_BLOCKCHAIN_ADDRESS")

# Verify Twilio
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_VERIFICATION_SID = os.environ.get("TWILIO_SERVICE")

# Plaid credentials
PLAID_CLIENT_ID = env("PLAID_CLIENT_ID")
PLAID_SECRET_KEY = env("PLAID_SECRET_KEY")
PLAID_ENVIRONMENT = os.getenv("PLAID_ENVIRONMENT")
PLAID_PROCESSOR = os.getenv("PLAID_PROCESSOR")

# Plaid countries array
PLAID_COUNTRIES = ["US"]

# Plaid products array
PLAID_PRODUCTS = ["auth"]

# celery configuration
BROKER_URL = os.getenv("BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Mexico_City"

# Task Beat Time Configuration

CELERY_CHECK_PAYMENT_STATUS = 60.0
CELERY_CHECK_TRANSFER_STATUS = 60.0
CELERY_UPDATE_PENDING_ORDER_STATUS = 60.0

# Bitso credentials
BITSO_API_KEY = os.getenv("BITSO_API_KEY")
BITSO_SECRET = os.getenv("BITSO_SECRET")
