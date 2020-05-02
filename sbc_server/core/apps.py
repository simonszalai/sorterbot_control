from django.apps import AppConfig


class SorterbotControlPanelConfig(AppConfig):
    name = 'core'

    def ready(self):
        import core.signals
