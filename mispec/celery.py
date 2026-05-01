from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mispec.settings')

app = Celery('mispec')


app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Define the broker URL for Redis
app.conf.broker_url = settings.CELERY_BROKER_URL

# Optional: Define result backend for Redis (if you need to store task results)
app.conf.result_backend = settings.CELERY_BROKER_URL

# Ensure broker connection retries on startup
app.conf.broker_connection_retry_on_startup = True

# Add SSL options to Celery configuration
app.conf.broker_transport_options = settings.CELERY_BROKER_TRANSPORT_OPTIONS
app.conf.redis_backend_use_ssl = settings.CELERY_REDIS_BACKEND_USE_SSL

# Use django-celery-beat scheduler
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

# Limit concurrency to reduce memory usage
app.conf.worker_concurrency = 2  # This controls how many tasks can run at once

# Set time limits for tasks to prevent them from running indefinitely
app.conf.task_time_limit = 300
app.conf.task_soft_time_limit = 180

# Task routing: Send geocoding tasks to a specific queue
app.conf.task_routes = {
    'profiles.tasks.process_geocoding': {'queue': 'geocoding_queue'},
}

# Define task retry policies for failed tasks (optional)
app.conf.task_default_retry_delay = 60
app.conf.task_max_retries = 3

# ---- BEAT SCHEDULE (PERIODIC TASKS) ----

# Define the beat schedule for periodic tasks
app.conf.beat_schedule = {
    'check-user-plans-every-day': {
        'task': 'profiles.tasks.check_user_plans',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
    'reset-call-durations-monthly': {
        'task': 'chat.tasks.reset_call_durations',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),  # Run monthly
    },
}

# ---- DEBUG TASK ----

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
