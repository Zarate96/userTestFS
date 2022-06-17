import os
import dj_database_url
from decouple import config
from fleteSeguro.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['fleteseguro.mx','test.fleteseguro.mx']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

SITE_URL = 'https://fleteseguro.mx'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fleteseguro',
        'USER': 'endicom',
        'PASSWORD': 'Endicom*1307',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

