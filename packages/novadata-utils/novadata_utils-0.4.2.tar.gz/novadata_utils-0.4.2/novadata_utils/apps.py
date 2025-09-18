from django.apps import AppConfig


class NovadataUtilsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'novadata_utils'

    def ready(self):
        import novadata_utils.signals
