from celery import shared_task
from .models import CallDuration

@shared_task
def reset_call_durations():
    CallDuration.objects.update(total_minutes=0)