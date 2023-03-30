

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_shop.settings')
app = Celery('online_shop')
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'everyday-task': {
        'task': 'users.tasks.remove_data_pending',
        'schedule': crontab(minute=0, hour=6)
        }
    }
