
### Pico framework ###

Quick start
-----------
1. Install pip install git+https://github.com/picostocks/django-pico-framework

2. Add "pico_framework" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'pico_framework',
    ]

3. Added to main urls.py
```python
from django.urls import path, include
from pico_framework import urls

urlpatterns = [
    path('pico-framwork/', include(urls)),
    """Your urls ...."""
]

```
``
url for get stats <your-domain>/pico-framework/stats/?stock_id=1&unit_id=2
&range=24h
``
```text
stock_id - id from https://picostocks.com/
unit_id - id form https://picostocks.com/
range - is period interval statistics (1h, 24h, 1d, 7d, 14d, month, year)
```


4. Run `python manage.py migrate` to create table in DB.

5. Set settings "PICO_FRAMEWORK" in main settings.

Default settings:

    DEFAULTS = {
        'PAIRS': [],    # list by tuples. Example (2, 3) => 'ETH\BTC'
        'SYNC_GRANULARITIES_EVERY": 60, (seconds)
        'SYNC_TASK_EVERY': 15, (seconds)
        'GRANULARITY': ['1h', '24h', '7d', '14d', 'month', 'year']
        'CALLBACK_TASKS': [] # list by paths with dote separate to the function
    }
    
6. Start a celery process
```bash
--app=pico_framework.celeryapp:app beat -l info
```

7. Start a celery worker
```bash
--app=pico_framework.celeryapp:app worker -l info
```

#
Notes that for pico_framework is required PostgresSQL DB.
#
