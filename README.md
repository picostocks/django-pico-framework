
### Pico framework ###

Quick start
-----------
1. Install pip install git+https://github.com/picostocks/django-pico-framework

2. Add "pico_framework" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'pico_framework',
    ]


3. Run `python manage.py migrate` to create table in DB.

4. Set settings "PICO_FRAMEWORK" in main settings.

Default settings:

    DEFAULTS = {
        'PAIRS': [],    # list by tuples. Example (2, 3) => 'ETH\BTC'
        'SYNC_PRICE_EVERY": 60, (seconds)
        'SYNC_STATS_EVERY': 60, (seconds)
        'CALLBACK_TASKS': [] # list by paths with dote separate to the function
    }

5. Configure you celery_app

    from celery import Celery
    from pico_framework import settings as picofwr_settings
    from django.conf import settings as django_settings
    
    
    app = Celery('myceleryapp')
    app.config_from_object(django_settings, namespace='CELERY')
    picofwr_settings.configure_celery(app)
