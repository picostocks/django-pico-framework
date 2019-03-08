
# Pico framework

## What do I need?

### Python3
A compatible version comes preinstalled with most current Linux systems.
If that is not the case consult your distribution for instructions 
on how to install Python 3.

### Django
Version 2.0.4 or later is required.
See detailed [installation instructions](https://docs.djangoproject.com/en/dev/intro/install/).

### Django REST framework
See detailed [installation instructions](https://www.django-rest-framework.org/#installation).

### Requests
See detailed [installation instructions](http://docs.python-requests.org/en/master/user/install/).

### Celery
Version 4.2 or later is required. 
See detailed [installation instructions](http://www.celeryproject.org/install/).

## Get started
1. Install `django-pico-framework` using pip:
 
    `pip install git+https://github.com/picostocks/django-pico-framework`

1. Add `pico_framework` to INSTALLED_APPS in `settings.py` module:

    ```
    INSTALLED_APPS = [
        ...
        'pico_framework',
        ...
    ]
    ```
1. Apply migrations to your database:

    `python manage.py migrate`

1. Define custom configuration values in your project's `settings.py` module.

    Settings for `pico_framework` are kept in a configuration dictionary named `PICO_FRAMEWORK`. 
    
    Default settings:
    
    ```python
    PICO_FRAMEWORK = {
        'PAIRS': [],
        'SYNC_PRICE_EVERY': 60,
        'SYNC_STATS_EVERY': 60,
        'CALLBACK_TASK': [] 
    }
    ```
    
    - **PICO_FRAMEWORK['PAIRS']**
    
        List of tuples. Each tuple should contain two integers, representing market.
        Reference [python-picostocks-api](https://github.com/picostocks/python-picostocks-api)
        for more information on how to find stock IDs.
        
        Example:
        
        `PICO_FRAMEWORK['PAIRS'] = [(3,2), (4,2)]`
        
        The code example above sets `PAIRS` to ETH/BTC and BST/BTC markets.
    
    - **PICO_FRAMEWORK['SYNC_PRICE_EVERY']**
    
        Number of **seconds** that determines how often prices should be synced.
    
    - **PICO_FRAMEWORK['SYNC_STATS_EVERY']**
    
        Number of **seconds** that determines how often stats should be synced.
    
    - **PICO_FRAMEWORK['CALLBACK_TASK']**
    
        List of strings. Each string should be absolute path to a callable.
        The callable should accept one parameter,
        which is a list of newly created `pico_framework.models.StatsMarketPrice` instances.
        
        Each element of `CALLBACK_TASK` will be called after price syncing task is executed.
        
        Example:
        
        `PICO_FRAMEWORK['CALLBACK_TASK'] = ['myproject.myapp.callbacks.price_callback']`

5. Configure celery
    ```python
    from celery import Celery
    from pico_framework import settings as pico_settings
    
    
    app = Celery('myceleryapp')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    pico_settings.configure_celery(app)
    ```
    
    Reference [celery documentation](http://docs.celeryproject.org/en/stable/django/first-steps-with-django.html)
    for more details on how to configure celery in your Django project.