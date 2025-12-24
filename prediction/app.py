# In prediction/apps.py
from django.apps import AppConfig

class PredictionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prediction'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') == 'true': # Prevents double run
            from .models import start_orchestration
            start_orchestration()