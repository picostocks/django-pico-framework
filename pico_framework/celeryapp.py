import os
from pico_framework.settings import tasks_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      tasks_settings.DJANGO_SETTINGS_MODULE, )
os.environ.setdefault("DJANGO_CONFIGURATION",
                      tasks_settings.DJANGO_CONFIGURATION)

import configurations
configurations.setup()

from django.conf import settings
from celery import Celery

app = Celery('celery-pico-framework')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
