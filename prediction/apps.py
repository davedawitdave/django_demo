from django.apps import AppConfig
import os
import threading


class PredictionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prediction'

    def ready(self):
        # Only start file watcher in the reloader child process
        if os.environ.get('RUN_MAIN') == 'true':
            # Import here to avoid circular imports
            from .ml_service import start_csv_watcher

            # Start file watcher in a separate thread
            watcher_thread = threading.Thread(target=start_csv_watcher, daemon=True)
            watcher_thread.start()
