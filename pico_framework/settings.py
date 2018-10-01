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
