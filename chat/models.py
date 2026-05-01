from django.db import models
import uuid
from profiles.models import Profile
from users.models import CustomUser
from django.utils import timezone
from datetime import timedelta

# Create your models here.


class Membership(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True)
    chat_room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE, blank=True)
    blocked = models.BooleanField(default=False, blank=True, null=True)
    is_event_admin = models.BooleanField(default=False, blank=True, null=True)


    def __str__(self):
        return f"{self.chat_room}"

class ChatRoom(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    ROOM_TYPE_CHOICES = [
        ('private', 'Private'),
        ('group', 'Group'),
    ]
    description = models.CharField(max_length=250, blank=True, null=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, blank=True, null=True)
    meeting_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
    
    
class Message(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, blank=True, null=True)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    media_file = models.FileField(upload_to='upload/chat_media', blank=True, null=True)
    content_type = models.CharField(max_length=250, blank=True, null=True)
    media_url = models.CharField(max_length=500, blank=True, null=True)
    # is_read = models.BooleanField(default=False, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.sender.first_name
    
    def save(self, *args, **kwargs):
        if self.timestamp is None:
            self.timestamp = timezone.localtime(timezone.now())

        super(Message, self).save(*args, **kwargs)

class MessageAllowance(models.Model):
    sender = models.ForeignKey(Profile, related_name='sent_allowances', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profile, related_name='received_allowances', on_delete=models.CASCADE)
    remaining_messages = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.sender.user.email} to {self.receiver.user.email}: {self.remaining_messages} messages"

    

class CallRoom(models.Model):
    CALL_TYPE_CHOICES = [
        ('outgoing', 'Outgoing'),
        ('incoming', 'Incoming'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    uid = models.IntegerField(blank=True, null=True)
    call_type = models.CharField(max_length=10, choices=CALL_TYPE_CHOICES, blank=True, null=True)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, blank=True, null=True)
    caller = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)

    def __str__(self):
        return self.caller.first_name
    
    def save(self, *args, **kwargs):
        if self.start_time is None:
            self.start_time = timezone.localtime(timezone.now())
        if self.end_time and self.start_time and not self.duration:
            self.duration = (self.end_time - self.start_time).total_seconds() // 60
        super(CallRoom, self).save(*args, **kwargs)


class CallDuration(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, blank=True,null=True)
    total_minutes = models.IntegerField(default=0)

    def __str__(self):
        return self.profile.email

    
    
class Event(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    event_room = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, blank=True, null=True)
    room_display_picture = models.ImageField(upload_to='upload/room_picture', blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.IntegerField(blank=True, null=True)
    is_ended = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.event_room.name if self.event_room else "No Room"

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            self.duration_seconds = int((self.end_time - self.start_time).total_seconds())
        super().save(*args, **kwargs)


    
class ReportEvent(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    reported_by = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    reason = models.CharField(max_length=250, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.reported_by.email

