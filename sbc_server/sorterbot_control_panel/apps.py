from django.apps import AppConfig


class SorterbotControlPanelConfig(AppConfig):
    name = 'sorterbot_control_panel'

    def ready(self):
        import sorterbot_control_panel.signals
