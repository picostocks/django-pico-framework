from django.conf import settings

FRAMEWORK_SETTINGS_NAME = "PICO_FRAMEWORK"

DEFAULTS = {
    'PAIRS': [],
    'SYNC_PRICE_EVERY': 60,
    'SYNC_STATS_EVERY': 60,
    'CALLBACK_TASK': [],
}


def get_settings(name):
    framework_settings = getattr(settings, FRAMEWORK_SETTINGS_NAME, DEFAULTS)
    return framework_settings.get(name, DEFAULTS.get(name))


def configure_celery(celery_app):
    _sync_stats_every = get_settings('SYNC_STATS_EVERY')

    if _sync_stats_every is not None:
        celery_app.conf.beat_schedule['pico_fwm_sync_stats'] = {
            'task': 'pico_framework.tasks.sync_stats_task',
            'schedule': _sync_stats_every
        }

    _sync_price_every = get_settings('SYNC_PRICE_EVERY')
    if _sync_price_every is not None:
        celery_app.conf.beat_schedule['pico_fwm_sync_current_price_task'] = {
            'task': 'pico_framework.tasks.sync_current_price_task',
            'schedule': _sync_price_every

        }
