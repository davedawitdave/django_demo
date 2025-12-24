from django.apps import AppConfig
import os


class PredictionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prediction'

    def ready(self):
        # Only start orchestration in the reloader child process
        if os.environ.get('RUN_MAIN') == 'true':
            from .models import start_orchestration
            start_orchestration()
