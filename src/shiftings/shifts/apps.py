from django.apps import AppConfig


class ShiftsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shiftings.shifts'

    # noinspection PyUnresolvedReferences
    def ready(self):
        from . import signals
