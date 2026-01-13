from django.apps import AppConfig


class BloginfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blogInfo'

    def ready(self):
        import blogInfo.signals  # Importar señales para manejar eventos relacionados con el modelo Usuario
        