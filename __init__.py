# Load Celery app when Django starts
from prediction.celery_app import app as celery_app

__all__ = ('celery_app',)
