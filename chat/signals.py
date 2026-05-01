from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CallRoom, CallDuration

@receiver(post_save, sender=CallRoom)
def update_call_duration(sender, instance, **kwargs):
    if instance.duration:
        user_profile = instance.caller
        call_duration = instance.duration

        call_duration_record, created = CallDuration.objects.get_or_create(profile=user_profile)
        call_duration_record.total_minutes += call_duration
        call_duration_record.save()
