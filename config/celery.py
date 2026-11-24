import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from celery import Celery

app = Celery('config')
app.config_from_object('config.settings', namespace='CELERY')
app.autodiscover_tasks()