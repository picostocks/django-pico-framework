from django.conf import settings as dj_settings
from django.core.signals import setting_changed

DEFAULTS = {
    'PAIRS': [],
    'DJANGO_SETTINGS_MODULE': None,
    'DJANGO_CONFIGURATION': None,
    'SYNC_TASK_EVERY': 15,
    'CALLBACK_TASK': []
}


class Settings(object):
    def __init__(self, default, name):
        for k, v in default.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        if name not in DEFAULTS:
            msg = "'%s' object has no attribute '%s'"
            raise AttributeError(msg % (self.__class__.__name__, name))

        value = self.get_setting(name)

        if not value:
            msg = "'%s' is required attribute'"
            raise AttributeError(msg % value)

        # Cache the result
        setattr(self, name, value)
        return value

    def get_setting(self, setting):
        return getattr(dj_settings.PICO_FRAMEWORK, setting, DEFAULTS[setting])

    def change_setting(self, setting, value, enter, **kwargs):
        # ensure a valid app setting is being overridden
        if setting != 'PICO_FRAMEWORK':
            return

        for k, v in value.items():
            if k not in DEFAULTS:
                msg = "'%s' object has no attribute '%s'"
                raise AttributeError(msg % (self.__class__.__name__, k))
            if enter:
                setattr(self, k, v)
            else:
                delattr(self, k)


tasks_settings = Settings(DEFAULTS, 'PICO_FRAMEWORK')
setting_changed.connect(tasks_settings.change_setting)
