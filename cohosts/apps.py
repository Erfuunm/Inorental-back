from django.apps import AppConfig


class CohostsConfig(AppConfig):
    """
    AppConfig for the cohosts app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cohosts'
    verbose_name = 'Co-Hosts Management'
    
    def ready(self):
        """
        Override this method to perform initialization tasks.
        """
        # Import signals to register them
        import cohosts.signals  # noqa
