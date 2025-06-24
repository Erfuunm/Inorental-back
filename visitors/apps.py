from django.apps import AppConfig


class VisitorsConfig(AppConfig):
    """
    Configuration class for the visitors app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'visitors'
    verbose_name = 'Visitor Management'
