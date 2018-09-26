# ensure package/conf is importable
from pico_framework.settings import DEFAULTS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pico_test',
        'USER': 'pico_test',
        'PASSWORD': 'qwerty',
        'HOST': 'localhost',
        'PORT': '',
    }
}


INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'pico_framework',
    'tests',
)

MIDDLEWARE = []

ROOT_URLCONF = 'pico_framework.urls'

USE_TZ = True

TIME_ZONE = 'Europe/Warsaw'

USE_L10N = True

SECRET_KEY = 'foobar'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
}]


STATIC_URL = '/static/'

PICO_FRAMEWORK = {
    'PAIRS': [
        (2, 3),
    ],
    'DJANGO_SETTINGS_MODULE': 'tests.settings',
    'DJANGO_CONFIGURATION': 'LocalTest'
}
