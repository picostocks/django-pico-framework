=====
Pico framework
=====

Quick start
-----------

1. Add "currency_price" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'pico_framework',
    ]


2. Run `python manage.py migrate` to create table in DB.

3. Set settings "PICO_FRAMEWORK" in main settings.

Default settings:

    DEFAULTS = {
        'PAIRS': [],    # list by tuples. Example ('ETH', 'BTC') => 'ETH\BTC'
        'DJANGO_SETTINGS_MODULE': None, # required
        'DJANGO_CONFIGURATION': None, # required
        'SYNC_TASK_EVERY': 15,
        'CALLBACK_TASKS': [] # list by paths with dote separate to the function
    }

