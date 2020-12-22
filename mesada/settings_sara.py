# Sarait's local environment settings

from .settings import *

DEBUG = True

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'solaria',
    'USER': 'solaria',
    'PASSWORD': '453672',
    'HOST': '127.0.0.1',
    'PORT': '5432',
    }
}

INSTALLED_APPS += ('debug_toolbar', )