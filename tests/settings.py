# ensure package/conf is importable
from pico_framework.settings import DEFAULTS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'pico_framework',
    'tests',
)

MIDDLEWARE = []

ROOT_URLCONF = 'tests.urls'

USE_TZ = True

SECRET_KEY = 'foobar'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
}]


STATIC_URL = '/static/'

PICO_FRAMEWORK = {
    'PAIRS': [
        ('BIT', 'ETH'),
    ],
    'DJANGO_SETTINGS_MODULE': 'tests.settings',
    'DJANGO_CONFIGURATION': 'LocalTest'
}
