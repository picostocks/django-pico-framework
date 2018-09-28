# ensure package/conf is importable

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_db.sqlite3',
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
