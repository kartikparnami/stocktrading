"""Local settings."""

from stocktrading.settings import *

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'quandl_db.sqlite3'),
    }
}

QUANDL_API_KEY = '***'
