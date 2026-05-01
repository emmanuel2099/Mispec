from rest_framework import serializers
from .models import ChatRoom, Message, CallRoom, Event, Membership, ReportEvent
from profiles.serializers import ProfileSerializer
from profiles.models import Profile



class ChatRoomSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    event_id = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    duration_seconds = serializers.SerializerMethodField()
    room_display_picture = serializers.SerializerMethodField()

    def get_members(self, obj):
        memberships = Membership.objects.filter(chat_room=obj)
        member_data = [{'profile': membership.profile.id, 'blocked': membership.blocked} for membership in memberships]
        return member_data

    def get_event_id(self, obj):
        if obj.room_type == 'group' and hasattr(obj, 'event'):
            return str(obj.event.id)
        return None

    def get_start_time(self, obj):
        if obj.room_type == 'group' and hasattr(obj, 'event'):
            return obj.event.start_time.isoformat() if obj.event.start_time else None
        return None

    def get_duration_seconds(self, obj):
        if obj.room_type == 'group' and hasattr(obj, 'event'):
            return obj.event.duration_seconds
        return None

    def get_room_display_picture(self, obj):
        if obj.room_type == 'group' and hasattr(obj, 'event'):
            if obj.event.room_display_picture:
                return obj.event.room_display_picture.url
        return None

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'room_type', 'description', 'members', 'meeting_id', 'event_id', 'start_time', 'duration_seconds', 'room_display_picture']

        
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'media_file', 'content_type', 'media_url', 'timestamp']


class CallSerializer(serializers.ModelSerializer):
    caller = ProfileSerializer(read_only=True)

    class Meta:
        model = CallRoom
        fields = ['id', 'room', 'call_type', 'caller', 'uid', 'start_time', 'end_time', 'duration']


class CallHistorySerializer(serializers.ModelSerializer):
    call_type = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        model = CallRoom
        fields = ['id', 'start_time', 'call_type', 'participants']

    def get_call_type(self, obj):
        user_profile = self.context['user_profile']
        return 'outgoing' if obj.caller == user_profile else 'incoming'

    def get_participants(self, obj):
        user_profile = self.context['user_profile']
        participants = Membership.objects.filter(chat_room=obj.room).exclude(profile=user_profile).values_list('profile__first_name', flat=True)
        return list(participants)

class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'


class ReportEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportEvent
        fields = '__all__'
