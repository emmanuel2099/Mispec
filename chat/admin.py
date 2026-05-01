from django.contrib import admin
from .models import ChatRoom, Message, Membership, CallRoom, Event, ReportEvent, CallDuration, MessageAllowance

# Register your models here.
admin.site.register(ChatRoom)
admin.site.register(Membership)
admin.site.register(Message)
# admin.site.register(AgoraCallToken)
admin.site.register(CallRoom)
admin.site.register(Event)
admin.site.register(ReportEvent)
admin.site.register(CallDuration)
admin.site.register(MessageAllowance)