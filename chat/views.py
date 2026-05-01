from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Message, ChatRoom, Membership, MessageAllowance, Event, CallDuration, CallRoom
from .serializers import *
from profiles.models import Profile, Notification
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, date
from firebase_admin import messaging
from django.core.exceptions import PermissionDenied
import requests
import time
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from .agora_key.ChatTokenBuilder2 import *
from .agora_key.RtmTokenBuilder2 import *
from .agora_key.RtcTokenBuilder2 import *
from .pusher import pusher_client
from django.utils.timezone import now
from django.conf import settings
from .dyte_api_client import DyteAPIClient
import uuid
from profiles.models import UserPlan
import json
from uuid import UUID
        

class CreateRoom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        receiver_id = request.data.get('receiver')

        if not receiver_id:
            return Response({"error": "Missing receiver ID"}, status=status.HTTP_400_BAD_REQUEST)

        sender_profile = Profile.objects.get(user=request.user)
        receiver_profile = Profile.objects.get(id=receiver_id)

        existing_chat_rooms = ChatRoom.objects.filter(
            membership__profile=sender_profile
        ).filter(
            membership__profile=receiver_profile
        ).filter(
            room_type='private'
        )

        chat_room = None
        if existing_chat_rooms.exists():
            chat_room = existing_chat_rooms.first()
        else:
            chat_room_name = f"{sender_profile.user.email}-{receiver_profile.user.email}"
            chat_room = ChatRoom.objects.create(name=chat_room_name, room_type='private')
            Membership.objects.create(profile=sender_profile, chat_room=chat_room)
            Membership.objects.create(profile=receiver_profile, chat_room=chat_room)

        serializer = ChatRoomSerializer(chat_room)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class CreateEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        name = request.data.get('name')
        description = request.data.get('description')
        duration_str = request.data.get('duration')

        try:
            duration_seconds = self.parse_duration(duration_str)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        event_admin = Profile.objects.get(user=request.user)

        chat_room = ChatRoom.objects.create(name=name, description=description, room_type='group')
        member = Membership.objects.create(profile=event_admin, chat_room=chat_room, is_event_admin="True")
        
        start_time = timezone.now()
        end_time = start_time + timedelta(seconds=duration_seconds)
        
        event = Event.objects.create(event_room=chat_room, name=name, start_time=start_time, end_time=end_time, duration_seconds=duration_seconds)

        serializer = ChatRoomSerializer(chat_room)

        response_data = serializer.data
        response_data['room_id'] = chat_room.id
        response_data['event_id'] = event.id
        response_data['start_time'] = event.start_time
        response_data['duration'] = event.duration_seconds
        response_data['is_event_owner'] = member.is_event_admin

        return Response(response_data, status=status.HTTP_201_CREATED)

    def parse_duration(self, duration_str):
        parts = duration_str.split(':')
        if len(parts) != 2:
            raise ValueError("Duration should be in the format 'HH:MM'")

        try:
            hours = int(parts[0])
            minutes = int(parts[1])
        except ValueError:
            raise ValueError("Invalid duration format")

        if hours < 0 or minutes < 0 or minutes >= 60:
            raise ValueError("Invalid duration")

        duration_seconds = hours * 3600 + minutes * 60
        return duration_seconds
    

class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        event_id = request.data.get('event_id')

        if not event_id:
            return Response({"error": "Event ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        event = get_object_or_404(Event, id=event_id)
        chat_room = event.event_room

        event_serializer = EventSerializer(event)
        chat_room_serializer = ChatRoomSerializer(chat_room)

        # Get members of the chatroom
        memberships = Membership.objects.filter(chat_room=chat_room)
        members_data = []
        for membership in memberships:
            profile_serializer = ProfileSerializer(membership.profile)
            member_data = {
                'profile': profile_serializer.data,
                'blocked': membership.blocked
            }
            members_data.append(member_data)


        response_data = {
            "event": event_serializer.data,
            "chat_room": chat_room_serializer.data,
            "members": members_data
        }
        return Response(response_data, status=status.HTTP_200_OK)
        



class EditEventView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, format=None):
        event_id = request.data.get('event_id')
        
        if not event_id:
            return Response({"error": "Event ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        event = get_object_or_404(Event, id=event_id)
        
        if not Membership.objects.filter(profile__user=request.user, chat_room=event.event_room).exists():
            raise PermissionDenied("You do not have permission to edit this event")

        name = request.data.get('name')
        description = request.data.get('description')
        room_display_picture = request.data.get('room_display_picture')
        
        if name:
            event.name = name
            event.event_room.name = name
            event.event_room.save()
        
        if description:
            event.description = description
            event.event_room.description = description
            event.event_room.save()

        if room_display_picture:
            event.room_display_picture = room_display_picture
        
        event.save()
        
        event_serializer = EventSerializer(event)
        chat_room_serializer = ChatRoomSerializer(event.event_room)
        
        response_data = {
            "event": event_serializer.data,
            "chat_room": chat_room_serializer.data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

class AddToEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        chat_room_id = request.data.get('chat_room')
        member_ids = request.data.get('members')

        if not isinstance(member_ids, list) or not all(isinstance(id, str) and self.is_valid_uuid(id) for id in member_ids):
            return Response({"error": "members should be a list of valid UUID strings"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the chat room
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)

        # Retrieve or create the associated event
        event, created = Event.objects.get_or_create(event_room=chat_room)
        event.start_time = now()
        event.end_time = event.start_time + timedelta(seconds=event.duration_seconds)
        event.save()

        # Serialize chat room and event data
        serialized_chat_room = ChatRoomSerializer(chat_room).data
        serialized_event = EventSerializer(event).data

        # Prepare initial response data
        response_data = {
            "chat_room": serialized_chat_room,
            "event": serialized_event,
            "members": []
        }

        # Get the profile of the user adding the participants
        group_admin = Profile.objects.get(user=request.user)

        # Retrieve profiles associated with the chat room
        profiles = Profile.objects.filter(membership__chat_room=chat_room)
        profiles_serializer = ProfileSerializer(profiles, many=True)

        try:
            # Retrieve event details for notification and serialization
            event = Event.objects.get(event_room=chat_room)
            event_serializer = EventSerializer(event)
            room_display_picture = event_serializer.data.get('room_display_picture')
            start_time = event.start_time.isoformat()  # Convert datetime to ISO format string
            duration_seconds = event.duration_seconds
            event_id = event.id
        except Event.DoesNotExist:
            room_display_picture = None
            start_time = None
            duration_seconds = None
            event_id = None

        # Check if the current user is an event admin
        membership = Membership.objects.get(chat_room=chat_room, profile=group_admin)
        is_event_owner = membership.is_event_admin

        # Prepare group chat room data for notification
        group_chat_room_data = {
            'chat_room': serialized_chat_room,
            'room_display_picture': room_display_picture,
            'duration_seconds': duration_seconds,
            'event_id': str(event_id) if event_id else None,
            'is_event_owner': is_event_owner
        }

        # Process each member ID provided in the request
        for member_id in member_ids:
            try:
                # Retrieve the profile of the member to be added
                member_profile = Profile.objects.get(id=member_id)
            except Profile.DoesNotExist:
                # Handle case where profile for member_id does not exist
                response_data["members"].append({
                    "member_id": member_id,
                    "status": "error",
                    "message": "Profile does not exist"
                })
                continue

            # Check if the member is already part of the event
            existing_membership = Membership.objects.filter(profile=member_profile, chat_room=chat_room)
            if existing_membership.exists():
                response_data["members"].append({
                    "member_id": member_id,
                    "status": "error",
                    "message": "This member already exists in the event"
                })
                continue

            # Add the member to the event
            membership, created = Membership.objects.get_or_create(profile=member_profile, chat_room=chat_room)
            response_data["members"].append({
                "member_id": member_id,
                "status": "added" if created else "already_exists"
            })

            # Create a new notification for the added member
            new_notification = Notification.objects.create(
                recipient=member_profile,
                notification_type='event',
                message=f"{group_admin.first_name} added you to {chat_room.name} event."
            )

            # Prepare notification message for Firebase Cloud Messaging
            if member_profile.fcm_token:
                # Serialize receiver profile data
                receiver_profile_serializer = ProfileSerializer(member_profile)
                receiver_profile_data = receiver_profile_serializer.data

                # Convert UUIDs and datetimes to strings for JSON serialization
                chat_room_data = self.convert_uuids_to_strings(group_chat_room_data)
                receiver_profile_data = self.convert_uuids_to_strings(receiver_profile_data)

                message = messaging.Message(
                    notification=messaging.Notification(
                        title="Event Notification",
                        body=new_notification.message
                    ),
                    token=member_profile.fcm_token,
                    data={
                        "notification_type": "event",
                        "chat_room_id": str(chat_room.id),
                        "chat_room_name": chat_room.name,
                        "chat_room_type": chat_room.room_type,
                        "receiver_id": str(member_profile.id),
                        "receiver_name": member_profile.first_name,
                        "chat_room_data": json.dumps(chat_room_data)
                    }
                )
                # Send the FCM message
                response = messaging.send(message)
                print("FCM message sent successfully:", response)

        # Return the final response data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @staticmethod
    def is_valid_uuid(value):
        try:
            uuid.UUID(str(value))
            return True
        except ValueError:
            return False

    @staticmethod
    def convert_uuids_to_strings(data):
        """Recursively convert UUID objects to strings in a dictionary."""
        if isinstance(data, dict):
            return {k: AddToEventView.convert_uuids_to_strings(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [AddToEventView.convert_uuids_to_strings(item) for item in data]
        elif isinstance(data, uuid.UUID):
            return str(data)
        else:
            return data

    @staticmethod
    def convert_datetime_to_string(data):
        """Recursively convert datetime objects to ISO format strings in a dictionary."""
        if isinstance(data, dict):
            return {k: AddToEventView.convert_datetime_to_string(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [AddToEventView.convert_datetime_to_string(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data

    

class StopEventView(APIView):
    def post(self, request, format=None):
        event_id = request.data.get('event_id')
        if not event_id:
            return Response({"error": "Event ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        event = get_object_or_404(Event, id=event_id)

        if event.is_ended:
            return Response({"error": "Event already ended"}, status=status.HTTP_400_BAD_REQUEST)

        event.is_ended = True
        event.save()

        return Response({"message": "Event stopped successfully"}, status=status.HTTP_200_OK)


class MessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        chat_room_id = request.data.get('chat_room')
        content = request.data.get('content')
        media_file = request.data.get('media_file')
        content_type = request.data.get('content_type')
        media_url = request.data.get('media_url')

        sender_profile = Profile.objects.get(user=request.user)

        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the recipient profile
        membership = Membership.objects.filter(chat_room=chat_room).exclude(profile=sender_profile).first()
        if not membership:
            return Response({"error": "Recipient not found in the chat room"}, status=status.HTTP_400_BAD_REQUEST)
        receiver_profile = membership.profile

        if not sender_profile.has_active_plan() and not receiver_profile.has_active_plan():
            # Check message allowance for non-subscribed users
            #  and for if they are both free users
            sender_to_receiver_allowance = MessageAllowance.objects.filter(sender=sender_profile, receiver=receiver_profile).first()
            if not sender_to_receiver_allowance or sender_to_receiver_allowance.remaining_messages <= 0:
                return Response({"error": "Insufficient message allowance"}, status=status.HTTP_403_FORBIDDEN)

            # Deduct one message from the allowance
            with transaction.atomic():
                sender_to_receiver_allowance.remaining_messages -= 1
                sender_to_receiver_allowance.save()
   
        message = Message.objects.create(room=chat_room, sender=sender_profile, content=content, media_file=media_file, content_type=content_type, media_url=media_url)

        serializer = MessageSerializer(message)

        pusher_data = {
            'room': str(chat_room_id),
            'sender': str(sender_profile.id),
            'content': content,
            'content_type': content_type,
            'media_url': media_url,
            'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

        if media_file:
            media_file_url = media_file
            pusher_data['media_file_url'] = media_file_url

            pusher_data.pop('media_file_url', None)
            
        serializer_data = MessageSerializer(message).data

        pusher_data.update(serializer_data)

        pusher_data['room'] = str(pusher_data['room'])
        pusher_data['sender'] = str(pusher_data['sender'])

        print("Pusher Data:", pusher_data)

        pusher_client.trigger(str(chat_room_id), 'new-message', pusher_data)
        print("Pusher event triggered successfully for chat room:", chat_room.name)

        print("Pusher Data after triggering event:", pusher_data)

        try:
            membership = Membership.objects.filter(chat_room=chat_room).exclude(profile=sender_profile).first()

            notification_count = Notification.objects.filter(recipient=receiver_profile, is_read=False).count()

            if membership:
                recipient = membership.profile
                new_notification = Notification.objects.create(
                    recipient=recipient,
                    notification_type='chat', 
                    message=f"{message.content}"
                )
                if recipient.is_chat_notification and recipient.fcm_token:
                    # Serialize chat room and sender profile data
                    chat_room_serializer = ChatRoomSerializer(chat_room)
                    chat_room_data = chat_room_serializer.data

                    sender_profile_serializer = ProfileSerializer(sender_profile)
                    sender_profile_data = sender_profile_serializer.data

                    plan = {
                        "name": str(sender_profile.plan) if sender_profile.plan else None,
                        "id":  str(sender_profile.plan.id) if sender_profile.plan else None, 
                    }

                    sender_details = {
                        "id": str(sender_profile.id),
                        "plan": json.dumps(plan),
                        "profile_picture": sender_profile.profile_picture.url if sender_profile.profile_picture else None,
                        "first_name": sender_profile.first_name,
                        "last_name": sender_profile.last_name,
                        "email": sender_profile.email,
                        "bio": sender_profile.bio,
                        "date_of_birth": sender_profile.date_of_birth.strftime("%Y-%m-%d")
                    }

                    
                    chat_room_data = self.convert_uuids_to_strings(chat_room_data)
                    sender_profile_data = self.convert_uuids_to_strings(sender_profile_data)

                    fcm_message_data = {
                        "notification_type": "chat",
                        "sender_details": json.dumps(sender_details),
                        "chat_room_data": json.dumps(chat_room_data),
                        # "sender_profile": json.dumps(sender_profile_data)
                    }

                    # Check size of the FCM message payload
                    fcm_payload_size = len(json.dumps(fcm_message_data).encode('utf-8'))
                    max_size = 4096
                    print("FCM payload:", fcm_payload_size)

                    if fcm_payload_size <= max_size:
                        # Prepare FCM message
                        message = messaging.Message(
                            notification=messaging.Notification(
                                title=sender_profile.first_name,
                                body=new_notification.message
                            ),
                            token=recipient.fcm_token,
                            data=fcm_message_data,
                            apns=messaging.APNSConfig(
                                payload=messaging.APNSPayload(
                                    aps=messaging.Aps(
                                        badge=notification_count
                                    )
                                )
                            )
                        )
                        response = messaging.send(message)
                        print("FCM message sent successfully:", response)
                    else:
                        print("Recipient does not have chat notifications enabled or FCM token is missing.")

        except Membership.DoesNotExist:
            print("No recipient found in the chat room.")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, format=None):
        chat_room_id = request.data.get('chat_room_id')
        
        if not chat_room_id:
            return Response({"error": "Missing chat_room_id in request query parameters"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
            messages = Message.objects.filter(room=chat_room)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        except ChatRoom.DoesNotExist:
            raise Response("Chat room not found")

    def put(self, request, format=None):
        message_id = request.data.get('message_id')
        chat_room_id = request.data.get('chat_room')
        new_content = request.data.get('content')
        new_content_type = request.data.get('content_type')
        media_url = request.data.get('media_url')

        if not message_id or not chat_room_id or not new_content:
            return Response({"error": "Missing message_id, chat_room, or content"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            message = Message.objects.get(id=message_id, room_id=chat_room_id)
        except Message.DoesNotExist:
            return Response({"error": "Message or chatroom does not exist"}, status=status.HTTP_404_NOT_FOUND)


        message.content = new_content
        message.content_type = new_content_type
        message.save()

        serializer = MessageSerializer(message)

        # Pusher event for updated message
        pusher_data = {
            'room': str(chat_room_id),
            'message_id': str(message_id),
            'content': new_content,
            'content_type': new_content_type, 
            'media_url': media_url,
            'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }

        pusher_client.trigger(str(chat_room_id), 'message-updated', pusher_data)
        print("Pusher event triggered successfully for message update in chat room:", chat_room_id)

        return Response(serializer.data)

    def convert_uuids_to_strings(self, data):
        """Recursively convert UUID objects to strings in a dictionary."""
        if isinstance(data, dict):
            return {k: self.convert_uuids_to_strings(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.convert_uuids_to_strings(item) for item in data]
        elif isinstance(data, UUID):
            return str(data)
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data


class ActiveChatroomsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_profile = request.user.profile
        
        private_chat_rooms = ChatRoom.objects.filter(membership__profile=user_profile, room_type='private')
        group_chat_rooms = ChatRoom.objects.filter(membership__profile=user_profile, room_type='group')
        
        private_chat_rooms_serializer = ChatRoomSerializer(private_chat_rooms, many=True)
        group_chat_rooms_serializer = ChatRoomSerializer(group_chat_rooms, many=True)
        
        private_chat_rooms_data = []
        for chat_room, serialized_chat_room in zip(private_chat_rooms, private_chat_rooms_serializer.data):
            profiles = Profile.objects.filter(membership__chat_room=chat_room).exclude(id=user_profile.id)
            profiles_serializer = ProfileSerializer(profiles, many=True)
            chat_room_data = {
                'chat_room': serialized_chat_room,
                'profiles': profiles_serializer.data
            }
            private_chat_rooms_data.append(chat_room_data)

        group_chat_rooms_data = []
        for chat_room, serialized_chat_room in zip(group_chat_rooms, group_chat_rooms_serializer.data):
            profiles = Profile.objects.filter(membership__chat_room=chat_room)
            profiles_serializer = ProfileSerializer(profiles, many=True)
            try:
                event = Event.objects.get(event_room=chat_room)
                event_serializer = EventSerializer(event)
                room_display_picture = event_serializer.data.get('room_display_picture')
                start_time = event.start_time
                duration_seconds = event.duration_seconds
                event_id = event.id
            except Event.DoesNotExist:
                room_display_picture = None
                start_time = None
                duration_seconds = None
                event_id = None

            membership = Membership.objects.get(chat_room=chat_room, profile=user_profile)
            is_event_owner = membership.is_event_admin

            chat_room_data = {
                'chat_room': serialized_chat_room,
                'profiles': profiles_serializer.data,
                'room_display_picture': room_display_picture,
                'start_time': start_time,
                'duration_seconds': duration_seconds,
                'event_id': event_id,
                'is_event_owner': is_event_owner
            }

            group_chat_rooms_data.append(chat_room_data)
        
        response_data = {
            'private_chat_rooms': private_chat_rooms_data,
            'group_chat_rooms': group_chat_rooms_data
        }

        return Response(response_data, status=status.HTTP_200_OK)


    

class LeaveChatRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user_profile = request.user.profile
        chatroom_id = request.data.get('chatroom_id')

        if not chatroom_id:
            return Response({"error": "chat_room_id is required in the payload."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            membership = Membership.objects.get(profile=user_profile, chat_room=chatroom_id)
            membership.delete()
            return Response({"detail": "Left the chat room successfully."}, status=status.HTTP_200_OK)
        except Membership.DoesNotExist:
            return Response({"error": "Membership not found."}, status=status.HTTP_404_NOT_FOUND)


class ReportEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        reported_by = request.user.profile
        event_id = request.data.get('event_id')
        reason = request.data.get('reason')

        if not event_id or not reason:
            return Response({"error": "Event ID and reason are required in the payload."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        report_data = {
            'reported_by': reported_by.id,
            'event': event_id,
            'reason': reason
        }

        serializer = ReportEventSerializer(data=report_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MakeCallAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_profile = request.user.profile
        user_uuid = user_profile.id
        uid = user_profile.uid

        chat_room_id = request.data.get('chat_room_id')

        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            user_plan = UserPlan.objects.get(profile=user_profile)
        except UserPlan.DoesNotExist:
            return Response({'error': 'User plan not found'}, status=status.HTTP_404_NOT_FOUND)

        call_duration_record, created = CallDuration.objects.get_or_create(profile=user_profile)

        if call_duration_record.total_minutes >= user_plan.plan.max_minutes:
            return Response({'error': 'You have exceeded your call limit for this month.'}, status=status.HTTP_400_BAD_REQUEST)

        app_id = settings.AGORA_APP_ID
        app_certificate = settings.AGORA_APP_CERT
        channel_name = str(chat_room.id)  
        account = user_uuid
        expire_timestamp = int(time.time()) + timedelta(days=1).total_seconds()
        # privilege_expiration_in_seconds = int(time.time()) + timedelta(days=1).total_seconds()

        token_expiration_in_seconds = expire_timestamp

        token = RtcTokenBuilder.build_token_with_uid(app_id, app_certificate, channel_name, uid, role=1,
                                                 token_expire=token_expiration_in_seconds, privilege_expire=0)

        agora_call = CallRoom.objects.create(caller=user_profile, uid=uid, call_type='outgoing', room=chat_room)
        if not agora_call.start_time:
            agora_call.start_time = timezone.now()
            agora_call.save()
            
        serializer = CallSerializer(agora_call)

        return Response({'rtc_token': token, 'uid':uid, 'call_id': serializer.data['id']})
    


class JoinCallAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_profile = request.user.profile
        uid = user_profile.uid

        chat_room_id = request.data.get('chat_room_id')

        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has a plan and handle accordingly
        try:
            user_plan = UserPlan.objects.get(profile=user_profile)
        except UserPlan.DoesNotExist:
            user_plan = None  # User does not have a plan

        if user_plan and user_plan.is_active:
            # If user has a plan, check the call duration limit
            call_duration_record, created = CallDuration.objects.get_or_create(profile=user_profile)
            if call_duration_record.total_minutes >= user_plan.plan.max_minutes:
                return Response({'error': 'You have exceeded your call limit for this month.'}, status=status.HTTP_400_BAD_REQUEST)
            
        app_id = settings.AGORA_APP_ID
        app_certificate = settings.AGORA_APP_CERT
        expire_time = int(time.time()) + timedelta(days=1).total_seconds()
        channel_name = str(chat_room.id)

        token = RtcTokenBuilder.build_token_with_uid(app_id, app_certificate, channel_name, uid, role=2,
                                                     token_expire=expire_time, privilege_expire=0)

        agora_call = CallRoom.objects.filter(room=chat_room, caller=user_profile).first()
        if not agora_call:
            agora_call = CallRoom.objects.create(caller=user_profile, uid=uid, call_type='incoming', room=chat_room)

        if not agora_call.start_time:
            agora_call.start_time = timezone.now()
            agora_call.save()

        serializer = CallSerializer(agora_call)

        return Response({'rtc_token': token, 'uid': serializer.data['uid'], 'call_id': serializer.data['id']})


class EndCallAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        call_id = request.data.get('call_id')
        try:
            call_room = CallRoom.objects.get(id=call_id)
        except CallRoom.DoesNotExist:
            return Response({'error': 'Call room not found'}, status=status.HTTP_404_NOT_FOUND)

        call_room.end_time = timezone.now()
        call_room.save()

        return Response({'message': 'Call ended successfully', 'duration': call_room.duration}, status=status.HTTP_200_OK)
    

class CallHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = request.user.profile
        chatroom_id = request.data.get('chatroom_id')

        if not chatroom_id:
            return Response({"error": "Chatroom ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chat_room = ChatRoom.objects.get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chatroom not found"}, status=status.HTTP_404_NOT_FOUND)
        
        calls_as_caller = CallRoom.objects.filter(caller=user_profile, room=chat_room)
        calls_in_room = CallRoom.objects.filter(room=chat_room)

        all_calls = list(calls_as_caller) + list(calls_in_room)
        unique_calls = {call.id: call for call in all_calls}

        serializer = CallHistorySerializer(unique_calls.values(), many=True, context={'user_profile': user_profile})

        return Response(serializer.data, status=status.HTTP_200_OK)

