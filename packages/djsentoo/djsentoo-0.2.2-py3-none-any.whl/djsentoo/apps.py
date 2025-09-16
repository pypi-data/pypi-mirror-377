from django.apps import AppConfig


class DjsentooConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djsentoo"

    def ready(self):
        import djsentoo.signals  # noqa: F401 - Import needed for signals to register
