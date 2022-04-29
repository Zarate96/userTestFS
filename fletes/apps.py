from django.apps import AppConfig

class FletesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fletes'

    def ready(self):
        from task import updater
        updater.start()