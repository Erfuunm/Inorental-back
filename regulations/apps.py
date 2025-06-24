from django.apps import AppConfig


class RegulationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'regulations'
    verbose_name = 'Regulations Management'

    def ready(self):
        # Import signals here to avoid circular imports
        import regulations.signals  # noqa
