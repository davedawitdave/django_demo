import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_demo.settings')

app = Celery('django_demo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
	'train-model-every-10-minutes': {
		'task': 'prediction.ml_service.celery_train_model',
		'schedule': crontab(minute='*/10'),
	},
	'check-new-data-every-2-minutes': {
		'task': 'prediction.ml_service.celery_check_for_new_data',
		'schedule': crontab(minute='*/2'),  # Check every 2 minutes for more responsiveness
	},
}