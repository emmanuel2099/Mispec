from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Profile, Like, Block, Report, Referral, Entertainment, Sport, Notification
from chat.models import Membership
from .serializers import *
from django.shortcuts import get_object_or_404
import uuid
import math
from django.utils import timezone
from .utils import calculate_distance
from geopy.geocoders import Nominatim
from geopy.distance import distance as geopy_distance
from datetime import datetime, timedelta, date
from django.db.models import ExpressionWrapper, F, fields
from django.db.models.functions import Now, Cast, Extract, TruncYear, TruncDate
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from firebase_admin import messaging
from django.db.models import Q
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import json
from .support import send_contact_email
from chat.models import MessageAllowance
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.core.cache import cache
from .tasks import process_geocoding



class EntertainmentView(generics.ListAPIView):
    queryset = Entertainment.objects.all()
    serializer_class = EntertainmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class SportView(generics.ListAPIView):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_object(self):
        return self.queryset.get(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        user_id = request.data.get('user')
        if user_id:
            user_instance = get_object_or_404(CustomUser, id=user_id)
            instance.user = user_instance

        for field in Profile._meta.fields:
            field_name = field.name
            if field_name == 'user':
                continue
            if field_name not in request.data:
                continue
            field_value = request.data.get(field_name)
            if field_name in ['longitude', 'latitude'] and field_value == '':
                field_value = None
            setattr(instance, field_name, field_value)

        # Handle M2M — works for both multipart (getlist) and JSON (list value)
        entertainment_ids = (
            request.data.getlist('entertainment')
            if hasattr(request.data, 'getlist')
            else request.data.get('entertainment', [])
        )
        if entertainment_ids:
            instance.entertainment.set(entertainment_ids)

        sport_ids = (
            request.data.getlist('sport')
            if hasattr(request.data, 'getlist')
            else request.data.get('sport', [])
        )
        if sport_ids:
            instance.sport.set(sport_ids)

        # Handle media uploads (multipart only)
        uploaded_medias = (
            request.data.getlist('uploaded_medias')
            if hasattr(request.data, 'getlist')
            else []
        )
        for uploaded_media in uploaded_medias:
            media_data = {'files': uploaded_media, 'profile': instance.id}
            media_serializer = ProfileMediaSerializer(data=media_data)
            if media_serializer.is_valid():
                media_serializer.save()
            else:
                print(media_serializer.errors)

        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ProfileMediaDeleteView(generics.DestroyAPIView):
    queryset = ProfileMedia.objects.all()
    serializer_class = ProfileMediaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    

    def get_object(self):
        queryset = self.queryset.filter(profile__user=self.request.user)
        pk = self.request.data.get('pk')
        instance = get_object_or_404(queryset, id=pk)
        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileFilterView(generics.ListAPIView):
    serializer_class = ProfileFilterSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        profile = user.profile
        
        # Ensure location is provided
        if not profile or profile.latitude is None or profile.longitude is None:
            raise ValidationError("You must provide your location coordinates.")

        user_coords = (profile.latitude, profile.longitude)
        geolocator = Nominatim(user_agent="profile_locator")
        
        # Get query params
        latitude = float(self.request.query_params.get('latitude', user_coords[0]))
        longitude = float(self.request.query_params.get('longitude', user_coords[1]))
        distance_param = self.request.query_params.get('distance')
        max_distance = float(distance_param.split('km')[0]) if distance_param else 10.0  # Default to 10 km

        min_age = self.request.query_params.get('min_age')
        max_age = self.request.query_params.get('max_age')

        sexual_orientation = profile.sexual_orientation
        
        # Bounding box calculation
        lat_offset = max_distance / 111.0  
        lon_offset = max_distance / (111.0 * abs(math.cos(math.radians(latitude))))
        min_lat = latitude - lat_offset
        max_lat = latitude + lat_offset
        min_lon = longitude - lon_offset
        max_lon = longitude + lon_offset

        # Get matched profile IDs to exclude
        matched_profiles = Match.objects.filter(
            Q(profile_a=profile) | Q(profile_b=profile)
        ).values_list('profile_a', 'profile_b')

        matched_profiles_ids = set(
            profile_id for match in matched_profiles for profile_id in match
        )
        matched_profiles_ids.discard(profile.id)

        # Get blocked profile IDs
        blocked_profiles = Block.objects.filter(blocked_by=profile).values_list('blocked_user__id', flat=True)

        # Filter queryset
        queryset = Profile.objects.annotate(
            age=ExpressionWrapper(Now() - F('date_of_birth'), output_field=fields.DurationField())
        ).filter(
            latitude__range=(min_lat, max_lat),
            longitude__range=(min_lon, max_lon),
            user__is_active=True, 
            is_incognito=False,
            is_verified=True
        ).exclude(
            id__in=matched_profiles_ids
        ).exclude(
            id__in=blocked_profiles
        ).exclude(
            user=user
        ).exclude(
            bio__isnull=True
        ).exclude(
            bio=''
        )

        # Filter by age
        if min_age and max_age:
            queryset = queryset.filter(
                age__range=(f"{min_age} years", f"{max_age} years")
            )

        # Filter by sexual orientation
        if sexual_orientation != 'both':
            queryset = queryset.filter(gender=sexual_orientation)

        # Process distance and location asynchronously (potential Celery integration)
        for profile in queryset:
            try:
                # Caching to reduce geocoding API calls
                cache_key = f"geocode_{profile.latitude}_{profile.longitude}"
                cached_location = cache.get(cache_key)
                if not cached_location:
                    profile_distance = geopy_distance(user_coords, (profile.latitude, profile.longitude)).kilometers
                    setattr(profile, 'distance', int(profile_distance))

                    location = geolocator.reverse((profile.latitude, profile.longitude), language="en")
                    setattr(profile, 'location_name', location.address if location else None)
                    
                    # Cache the location
                    cache.set(cache_key, location.address if location else None, timeout=86400)  # Cache for 1 day
                else:
                    setattr(profile, 'location_name', cached_location)

            except Exception as e:
                # Handle failure gracefully (e.g., API failure)
                setattr(profile, 'distance', None)
                setattr(profile, 'location_name', None)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        serializer = self.get_serializer(paginated_queryset, many=True)
        response_data = serializer.data

        # Add reported accounts data
        reported_accounts = self.get_reported_accounts_data()

        response = paginator.get_paginated_response(response_data)
        response.data['reported_accounts'] = reported_accounts

        return response

    def get_reported_accounts_data(self):
        profile = self.request.user.profile
        reported_accounts = Report.objects.filter(reported_by=profile)
        reported_accounts_serializer = ReportSerializer(reported_accounts, many=True)
        return reported_accounts_serializer.data


class BothProfileFilterView(ProfileFilterView):
    serializer_class = ProfileFilterSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 5

    def get_queryset(self):
        user = self.request.user
        profile = user.profile

        # Ensure location is provided
        if not profile or profile.latitude is None or profile.longitude is None:
            raise ValidationError("You must provide your location coordinates.")

        user_coords = (profile.latitude, profile.longitude)

        # Get query params
        latitude = float(self.request.query_params.get('latitude', user_coords[0]))
        longitude = float(self.request.query_params.get('longitude', user_coords[1]))
        distance_param = self.request.query_params.get('distance')
        max_distance = float(distance_param.split('km')[0]) if distance_param else 10.0

        min_age = self.request.query_params.get('min_age')
        max_age = self.request.query_params.get('max_age')

        # Bounding box calculation
        lat_offset = max_distance / 111.0  
        lon_offset = max_distance / (111.0 * abs(math.cos(math.radians(latitude))))
        min_lat = latitude - lat_offset
        max_lat = latitude + lat_offset
        min_lon = longitude - lon_offset
        max_lon = longitude + lon_offset

        # Get matched and blocked profile IDs to exclude
        matched_profiles = Match.objects.filter(
            Q(profile_a=profile) | Q(profile_b=profile)
        ).values_list('profile_a', 'profile_b')
        
        matched_profiles_ids = set(
            profile_id for match in matched_profiles for profile_id in match
        )
        matched_profiles_ids.discard(profile.id)

        blocked_profiles = Block.objects.filter(blocked_by=profile).values_list('blocked_user__id', flat=True)

        # Filter queryset
        queryset = Profile.objects.annotate(
            age=ExpressionWrapper(Now() - F('date_of_birth'), output_field=fields.DurationField())
        ).filter(
            latitude__range=(min_lat, max_lat),
            longitude__range=(min_lon, max_lon),
            user__is_active=True,
            is_incognito=False
        ).exclude(
            id__in=matched_profiles_ids
        ).exclude(
            id__in=blocked_profiles
        ).exclude(
            user=user
        ).exclude(
            bio__isnull=True
        ).exclude(
            bio=''
        )

        # Filter by age
        if min_age and max_age:
            queryset = queryset.filter(
                age__range=(f"{min_age} years", f"{max_age} years")
            )

        # Process distance synchronously, using Celery
        for profile in queryset:
            try:
                profile_distance = geopy_distance(user_coords, (profile.latitude, profile.longitude)).kilometers
                setattr(profile, 'distance', int(profile_distance))
                
                # Use Celery to process geocoding asynchronously
                process_geocoding.delay(profile.id, profile.latitude, profile.longitude)

            except Exception as e:
                setattr(profile, 'distance', None)

        return queryset


# class ProfileFilterView(generics.ListAPIView):
#     serializer_class = ProfileFilterSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = PageNumberPagination


#     def get_queryset(self):
#         user = self.request.user
#         profile = user.profile
#         if not profile or profile.latitude is None or profile.longitude is None:
#             raise ValidationError("You cannot search for a profile without providing your own location coordinates.")

#         user_coords = (profile.latitude, profile.longitude)
#         # user_coords = (profile.latitude, profile.longitude) if profile else (0.0, 0.0)
#         geolocator = Nominatim(user_agent="profile_locator")

#         latitude = float(self.request.query_params.get('latitude', user_coords[0]))
#         longitude = float(self.request.query_params.get('longitude', user_coords[1]))
#         distance_param = self.request.query_params.get('distance')
#         max_distance = float(distance_param.split('km')[0]) if distance_param else 0.00

#         min_age = self.request.query_params.get('min_age')
#         max_age = self.request.query_params.get('max_age')

#         sexual_orientation = profile.sexual_orientation
#         print('sexual_orientation:', sexual_orientation)

#         # Calculate bounding box coordinates
#         # 1 degree of latitude is approximately 111 kilometers
#         lat_offset = max_distance / 111.0  
#         lon_offset = max_distance / (111.0 * abs(math.cos(math.radians(latitude))))
#         # Adjust for longitude offset
#         min_lat = latitude - lat_offset
#         max_lat = latitude + lat_offset
#         min_lon = longitude - lon_offset
#         max_lon = longitude + lon_offset

#         # Get matched profiles
#         matched_profiles = Match.objects.filter(
#             Q(profile_a=profile) | Q(profile_b=profile)
#         ).values_list('profile_a', 'profile_b')

#         matched_profiles_ids = set(
#             profile_id for match in matched_profiles for profile_id in match
#         )
#         # Remove current user's profile id
#         matched_profiles_ids.discard(profile.id)

#         blocked_profiles = Block.objects.filter(blocked_by=profile).values_list('blocked_user__id', flat=True)
        
#         queryset = Profile.objects.annotate(
#             age=ExpressionWrapper(
#                 Now() - F('date_of_birth'),
#                 output_field=fields.DurationField()

#                 # make DurationField for live server
#             ),
#         ).exclude(user=user, date_of_birth__isnull=True).filter(
#             latitude__range=(min_lat, max_lat),
#             longitude__range=(min_lon, max_lon),
#             age__range=(f"{min_age} years", f"{max_age} years"),
#             is_incognito=False
#         ).exclude(id__in=matched_profiles_ids).exclude(id__in=blocked_profiles).exclude(user=user).exclude(bio__isnull=True).exclude(bio='')

#         if sexual_orientation != 'both':
#             queryset = queryset.filter(gender=sexual_orientation)
        

#         for profile in queryset:
#             profile_distance = int(geopy_distance(user_coords, (profile.latitude, profile.longitude)).kilometers)
#             setattr(profile, 'distance', profile_distance)

#             location = geolocator.reverse((profile.latitude, profile.longitude), language="en")
#             setattr(profile, 'location_name', location.address if location else None)

#             if not isinstance(profile_distance, int):
#                 print(f"Warning: profile_distance is not an integer. Value: {profile_distance}")
        
#         print(min_age, max_age, max_distance)
#         print('prof:', queryset)
#         return queryset
#     # (f"{min_age} years", f"{max_age} years")

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
        
#         paginator = self.pagination_class()
#         paginated_queryset = paginator.paginate_queryset(queryset, request)
        
#         serializer = self.get_serializer(paginated_queryset, many=True)
#         response_data = serializer.data

#         reported_accounts = self.get_reported_accounts_data()

#         response = paginator.get_paginated_response(response_data)
#         response.data['reported_accounts'] = reported_accounts

#         return response

#     def get_reported_accounts_data(self):
#         user = self.request.user
#         profile = user.profile
#         reported_accounts = Report.objects.filter(reported_by=profile)
#         reported_accounts_serializer = ReportSerializer(reported_accounts, many=True)
#         return reported_accounts_serializer.data
    


# class BothProfileFilterView(generics.ListAPIView):
#     serializer_class = ProfileFilterSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = PageNumberPagination


#     def get_queryset(self):
#         user = self.request.user
#         profile = user.profile
#         if not profile or profile.latitude is None or profile.longitude is None:
#             raise ValidationError("You cannot search for a profile without providing your own location coordinates.")

#         user_coords = (profile.latitude, profile.longitude)
#         geolocator = Nominatim(user_agent="profile_locator")

#         latitude = float(self.request.query_params.get('latitude', user_coords[0]))
#         longitude = float(self.request.query_params.get('longitude', user_coords[1]))
#         distance_param = self.request.query_params.get('distance')
#         max_distance = float(distance_param.split('km')[0]) if distance_param else 0.00

#         min_age = self.request.query_params.get('min_age')
#         max_age = self.request.query_params.get('max_age')

#         # sexual_orientation = profile.sexual_orientation
#         # print('sexual_orientation:', sexual_orientation)

#         # Calculate bounding box coordinates
#         # 1 degree of latitude is approximately 111 kilometers
#         lat_offset = max_distance / 111.0  
#         lon_offset = max_distance / (111.0 * abs(math.cos(math.radians(latitude))))
#         # Adjust for longitude offset
#         min_lat = latitude - lat_offset
#         max_lat = latitude + lat_offset
#         min_lon = longitude - lon_offset
#         max_lon = longitude + lon_offset


#         # Get matched profiles
#         matched_profiles = Match.objects.filter(
#             Q(profile_a=profile) | Q(profile_b=profile)
#         ).values_list('profile_a', 'profile_b')

#         matched_profiles_ids = set(
#             profile_id for match in matched_profiles for profile_id in match
#         )
#         # Remove current user's profile id
#         matched_profiles_ids.discard(profile.id) 

#         blocked_profiles = Block.objects.filter(blocked_by=profile).values_list('blocked_user__id', flat=True) 
        
#         queryset = Profile.objects.annotate(
#             age=ExpressionWrapper(
#                 Now() - F('date_of_birth'),
#                 output_field=fields.DurationField()

#                 # make DurationField for live server
#             ),
#         ).exclude(user=user, date_of_birth__isnull=True).filter(
#             latitude__range=(min_lat, max_lat),
#             longitude__range=(min_lon, max_lon),
#             age__range=(f"{min_age} years", f"{max_age} years"),
#             is_incognito=False
#         ).exclude(id__in=matched_profiles_ids).exclude(id__in=blocked_profiles).exclude(user=user).exclude(bio__isnull=True).exclude(bio='')


#         for profile in queryset:
#             profile_distance = int(geopy_distance(user_coords, (profile.latitude, profile.longitude)).kilometers)
#             setattr(profile, 'distance', int(profile_distance))

#             location = geolocator.reverse((profile.latitude, profile.longitude), language="en")
#             setattr(profile, 'location_name', location.address if location else None)
        
#         print(min_age, max_age, max_distance)
#         print('prof:', queryset)
#         return queryset
#     # (f"{min_age} years", f"{max_age} years")

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
        
#         paginator = self.pagination_class()
#         paginated_queryset = paginator.paginate_queryset(queryset, request)
        
#         serializer = self.get_serializer(paginated_queryset, many=True)
#         response_data = serializer.data

#         reported_accounts = self.get_reported_accounts_data()

#         response = paginator.get_paginated_response(response_data)
#         response.data['reported_accounts'] = reported_accounts

#         return response

#     def get_reported_accounts_data(self):
#         user = self.request.user
#         profile = user.profile
#         reported_accounts = Report.objects.filter(reported_by=profile)
#         reported_accounts_serializer = ReportSerializer(reported_accounts, many=True)
#         return reported_accounts_serializer.data



class LikeCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        sender_profile = Profile.objects.get(user=request.user)
        data = request.data.copy()
        data['sender'] = str(sender_profile.id)
        serializer = LikeSerializer(data=data)

        if serializer.is_valid():
            receiver_profile = serializer.validated_data.get('receiver')

            if not isinstance(receiver_profile, Profile):
                raise serializers.ValidationError("Invalid receiver profile.")
            
            if Like.objects.filter(sender=sender_profile, receiver=receiver_profile).exists():
                return Response({"error": "You have already liked this profile."}, status=status.HTTP_400_BAD_REQUEST)

            has_been_liked = Like.objects.filter(sender=receiver_profile, receiver=sender_profile).exists()

            with transaction.atomic():
                serializer.save()

                if has_been_liked:
                    match, created = Match.objects.get_or_create(profile_a=sender_profile, profile_b=receiver_profile)
                    
                    if created:
                        # Delete the likes only if a new match is created
                        Like.objects.filter(sender=sender_profile, receiver=receiver_profile).delete()
                        Like.objects.filter(sender=receiver_profile, receiver=sender_profile).delete()

                        # Send match notifications to both sender and receiver
                        receiver_notification_count = Notification.objects.filter(recipient=receiver_profile, is_read=False).count()
                        sender_notification_count = Notification.objects.filter(recipient=sender_profile, is_read=False).count()

                        if receiver_profile.is_match_notification and receiver_profile.fcm_token:
                            new_notification = Notification.objects.create(
                                recipient=receiver_profile,
                                notification_type='match', 
                                message=f"You are now a match with {sender_profile.first_name}"
                            )
                            message = messaging.Message(
                                notification=messaging.Notification(
                                    title="New Match!",
                                    body=new_notification.message
                                ),
                                token=receiver_profile.fcm_token,
                                data={"notification_type": "match"},
                                apns=messaging.APNSConfig(
                                    payload=messaging.APNSPayload(
                                        aps=messaging.Aps(
                                            badge=receiver_notification_count
                                        )
                                    )
                                )
                            )
                            messaging.send(message)

                        if sender_profile.is_match_notification and sender_profile.fcm_token:
                            new_notification = Notification.objects.create(
                                recipient=sender_profile,
                                notification_type='match', 
                                message=f"You are now a match with {receiver_profile.first_name}"
                            )
                            message = messaging.Message(
                                notification=messaging.Notification(
                                    title="New Match!",
                                    body=new_notification.message
                                ),
                                token=sender_profile.fcm_token,
                                data={"notification_type": "match"},
                                apns=messaging.APNSConfig(
                                    payload=messaging.APNSPayload(
                                        aps=messaging.Aps(
                                            badge=sender_notification_count
                                        )
                                    )
                                )
                            )
                            messaging.send(message)
                else:
                    # Send like notification only if no match is created
                    receiver_notification_count = Notification.objects.filter(recipient=receiver_profile, is_read=False).count()

                    if receiver_profile.is_like_notification and receiver_profile.fcm_token:
                        new_notification = Notification.objects.create(
                            recipient=receiver_profile,
                            notification_type='like', 
                            message=f"{sender_profile.first_name} liked your profile!"
                        )
                        message = messaging.Message(
                            notification=messaging.Notification(
                                title="New Like!",
                                body=new_notification.message
                            ),
                            token=receiver_profile.fcm_token,
                            data={"notification_type": "like"},
                            apns=messaging.APNSConfig(
                                payload=messaging.APNSPayload(
                                    aps=messaging.Aps(
                                        badge=receiver_notification_count
                                    )
                                )
                            )
                        )
                        messaging.send(message)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  

class LikedProfilesView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request, format=None):
        user_profile = Profile.objects.get(user=request.user)
        likes = Like.objects.filter(receiver=user_profile)
        liked_profiles = Profile.objects.filter(id__in=likes.values_list('sender__id', flat=True))

        blocked_profiles = Block.objects.filter(blocked_by=user_profile)
        blocked_profile_ids = blocked_profiles.values_list('blocked_user__id', flat=True)
        liked_profiles = liked_profiles.exclude(id__in=blocked_profile_ids)

        reported_profiles = Report.objects.filter(reported_by=user_profile)
        reported_profiles_serializer = ReportSerializer(reported_profiles, many=True)

        user_coords = (user_profile.latitude, user_profile.longitude) if user_profile else (0.0, 0.0)
        geolocator = Nominatim(user_agent="profile_locator")

        for profile in liked_profiles:
            profile_distance = geopy_distance(user_coords, (profile.latitude, profile.longitude)).kilometers
            setattr(profile, 'distance', profile_distance)

            location = geolocator.reverse((profile.latitude, profile.longitude), language="en")
            setattr(profile, 'location_name', location.address if location else None)

            distance_in_km = int(profile_distance)

            setattr(profile, 'distance', distance_in_km)
            print('dis:', distance_in_km)


            if not isinstance(distance_in_km, int):
                print(f"Warning: profile_distance is not an integer. Value: {distance_in_km}")

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(liked_profiles, request)
        serializer = ProfileSerializer(result_page, many=True, context={'request': request})

        response_data = {
            'liked_profiles': serializer.data,
            'reported_profiles': reported_profiles_serializer.data,
            'total_likes': likes.count(),
        }

        return Response(response_data, status=status.HTTP_200_OK)

    

class ProfileDislikeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None):
        sender_profile = Profile.objects.get(user=request.user)
        receiver_profile = request.data.get('receiver')

        like_instance = get_object_or_404(Like, sender=sender_profile, receiver=receiver_profile)
        like_instance.delete()

        return Response("Profile disliked successfully.", status=status.HTTP_204_NO_CONTENT)


    

class CreateReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        reported_by_profile = Profile.objects.get(user=request.user)
        data = request.data.copy()
        data['reported_by'] = str(reported_by_profile.id)
        serializer = ReportSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportProfilesView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_calss = PageNumberPagination

    def get(self, request, format=None):
        user_profile = Profile.objects.get(user=request.user)
        reports = Report.objects.filter(reported_by=user_profile)
        reported_profiles = Profile.objects.filter(id__in=reports.values_list('reported_user__id', flat=True))
        serializer = ProfileSerializer(reported_profiles, many=True)

        blocked_profiles = Block.objects.filter(blocked_by=user_profile)
        blocked_profiles_serializer = BlockSerializer(blocked_profiles, many=True)

        
        response_data = {
            'reported_profiles': serializer.data,
            'total_reports': reports.count(),
            'blocked_profiles': blocked_profiles_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    


class ReferralView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_calss = PageNumberPagination

    def get(self, request, format=None):
        user_profile = Profile.objects.get(user=request.user)
        referrals = Referral.objects.filter(referred_by=user_profile, is_redeemed=False)
        serializer = ReferralSerializer(referrals, many=True)

        
        response_data = {
            'referred_profiles': serializer.data,
            'total_referrals': referrals.count(),
        }

        return Response(response_data, status=status.HTTP_200_OK)

class CreateBlockView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        blocked_by_profile = Profile.objects.get(user=request.user)
        data = request.data.copy()
        data['blocked_by'] = str(blocked_by_profile.id)
        serializer = BlockSerializer(data=data)
        blocked_user = data.get('blocked_user')
        
        if serializer.is_valid():
            if Block.objects.filter(blocked_by=blocked_by_profile, blocked_user=blocked_user).exists():
                return Response({"error": "You have already blocked this account."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            
            

            membership = Membership.objects.filter(
                profile=blocked_user,
                chat_room__membership__profile=blocked_by_profile
            ).first()

            if membership:
                membership.blocked = True
                membership.save()

            matches_to_delete = Match.objects.filter(
                profile_a__id__in=[blocked_by_profile.id, blocked_user],
                profile_b__id__in=[blocked_by_profile.id, blocked_user]
            )
            if matches_to_delete.exists():
                matches_to_delete.delete()

            

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileUnblockView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None):
        blocked_by_profile = Profile.objects.get(user=request.user)
        blocked_user_profile = request.data.get('blocked_user')

        block_instance = get_object_or_404(Block, blocked_by=blocked_by_profile, blocked_user=blocked_user_profile)
        block_instance.delete()

        membership = Membership.objects.filter(
            profile=blocked_user_profile,
            chat_room__membership__profile=blocked_by_profile
        ).first()

        if membership:
            membership.blocked = False
            membership.save()

        return Response("Profile unblocked successfully.", status=status.HTTP_204_NO_CONTENT)


class BlockedProfilesView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_calss = PageNumberPagination

    def get(self, request, format=None):
        user_profile = Profile.objects.get(user=request.user)
        blocks = Block.objects.filter(blocked_by=user_profile)
        blocked_profiles = Profile.objects.filter(id__in=blocks.values_list('blocked_user__id', flat=True))
        serializer = ProfileSerializer(blocked_profiles, many=True)

        
        response_data = {
            'blocked_profiles': serializer.data,
            'total_blocks': blocks.count(),
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
    

class MatchListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        current_user_profile = Profile.objects.get(user=request.user)
        matches = Match.objects.filter(profile_a=current_user_profile) | Match.objects.filter(profile_b=current_user_profile)

        reported_profiles = Report.objects.filter(reported_by=current_user_profile)
        reported_profiles_serializer = ReportSerializer(reported_profiles, many=True)
        
        matched_profiles = []
        for match in matches:
            if match.profile_a == current_user_profile:
                matched_profiles.append(match.profile_b)
            else:
                matched_profiles.append(match.profile_a)
        
        user_coords = (current_user_profile.latitude, current_user_profile.longitude) if current_user_profile else (0.0, 0.0)
        geolocator = Nominatim(user_agent="profile_locator")

        for profile in matched_profiles:
            profile_distance = geopy_distance(user_coords, (profile.latitude, profile.longitude)).kilometers
            setattr(profile, 'distance', profile_distance)

            location = geolocator.reverse((profile.latitude, profile.longitude), language="en")
            setattr(profile, 'location_name', location.address if location else None)

        serializer = ProfileSerializer(matched_profiles, many=True)
        response_data = {
            'matches': serializer.data,
            'reported_profiles': reported_profiles_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class GiftListView(generics.ListAPIView):
    queryset = Gift.objects.all()
    serializer_class = GiftSerializer
    permission_classes = [IsAuthenticated]


class CreateProfileGiftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        owner_profile = Profile.objects.get(user=request.user)
        data = request.data
        data['owner'] = str(owner_profile.id)

        serializer = ProfileGiftSerializer(data=data)

        if serializer.is_valid():
            existing_gift = ProfileGift.objects.filter(owner=owner_profile, gift=data['gift'], gift_type=data['gift_type']).first()

            if existing_gift:
                existing_gift.quantity += data['quantity']
                existing_gift.save()
                serializer = ProfileGiftSerializer(existing_gift)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedeemGiftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        owner_profile = Profile.objects.get(user=request.user)
        
        # Check if the user currently has an active plan
        active_user_plan = UserPlan.objects.filter(profile=owner_profile, is_active=True, expiry_date__gte=timezone.now()).first()
        if active_user_plan:
            return Response({'error': 'You are currently on a plan. Try again when your current plan expires.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total received gifts
        received_gifts = ProfileGift.objects.filter(owner=owner_profile, gift_type='received', is_redeemed=False)
        total_received_gifts = received_gifts.aggregate(total_quantity=models.Sum('quantity'))['total_quantity']
        
        if total_received_gifts is None or total_received_gifts < 50:
            return Response({'error': 'You need 50 received gifts to redeem'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Deduct 50 gifts
        remaining_to_deduct = 50
        for gift in received_gifts:
            if gift.quantity <= remaining_to_deduct:
                remaining_to_deduct -= gift.quantity
                gift.quantity = 0
                gift.is_redeemed = True
                gift.save()
            else:
                gift.quantity -= remaining_to_deduct
                remaining_to_deduct = 0
                gift.save()
            if remaining_to_deduct == 0:
                break

        one_month_plan = get_object_or_404(Plan, name='Classic')
        one_month_from_now = timezone.now() + timedelta(days=30)

        # Create a new UserPlan
        UserPlan.objects.create(
            profile=owner_profile,
            plan=one_month_plan,
            expiry_date=one_month_from_now,
            is_active=True
        )

        owner_profile.plan = one_month_plan
        owner_profile.save()

        return Response({'message': 'You have successfully redeemed 50 gifts and received a one-month subscription plan'}, status=status.HTTP_201_CREATED)

class RedeemReferralView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user_profile = Profile.objects.get(user=request.user)

        # Check if the user currently has an active plan
        active_user_plan = UserPlan.objects.filter(profile=user_profile, is_active=True, expiry_date__gte=timezone.now()).first()
        if active_user_plan:
            return Response({'error': 'You are currently on a plan. Try again when your current plan expires.'}, status=status.HTTP_400_BAD_REQUEST)

        referrals = Referral.objects.filter(referred_by=user_profile, is_redeemed=False)
        total_referrals = referrals.count()

        if total_referrals < 30:
            return Response({'error': 'You need 30 referrals to redeem'}, status=status.HTTP_400_BAD_REQUEST)

        # Deduct 30 referrals
        referrals_to_redeem = referrals[:30]
        for referral in referrals_to_redeem:
            referral.is_redeemed = True
            referral.save()

        one_month_plan = get_object_or_404(Plan, name='Classic')

        one_month_from_now = timezone.now() + timedelta(days=30)
        UserPlan.objects.create(
            profile=user_profile,
            plan=one_month_plan,
            expiry_date=one_month_from_now,
            is_active=True
        )

        user_profile.plan = one_month_plan
        user_profile.save()

        return Response({'message': 'You have successfully redeemed 30 referrals and received a one-month subscription plan'}, status=status.HTTP_201_CREATED)

class OwnedGiftView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request, format=None):
        user_profile = Profile.objects.get(user=request.user)
        owned_gifts = ProfileGift.objects.filter(owner=user_profile, gift_type='bought')
        total_owned_gifts = owned_gifts.aggregate(total_quantity=models.Sum('quantity'))['total_quantity']

        serializer = GetProfileGiftSerializer(owned_gifts, many=True)

        response_data = {
            'owned_gifts': serializer.data,
            'total_owned_gifts': total_owned_gifts,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class ReceivedGiftView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request, format=None):
        user_profile = Profile.objects.get(user=request.user)
        received_gifts = ProfileGift.objects.filter(owner=user_profile, gift_type='received', is_reedemed=False)
        total_received_gifts = received_gifts.aggregate(total_quantity=models.Sum('quantity'))['total_quantity']
        
        serializer = GetProfileGiftSerializer(received_gifts, many=True)

        response_data = {
            'received_gifts': serializer.data,
            'total_received_gifts': total_received_gifts,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    


class SendGiftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        sender_profile = Profile.objects.get(user=request.user)
        receiver_id = request.data.get('receiver_id')
        gift_id = request.data.get('gift_id')
        quantity = request.data.get('quantity')

        if not receiver_id or not gift_id:
            return Response({'error': 'Receiver ID and Gift ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        receiver_profile = get_object_or_404(Profile, pk=receiver_id)
        gift = get_object_or_404(Gift, pk=gift_id)

        if sender_profile == receiver_profile:
            return Response({'error': 'Cannot send a gift to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        sender_gift = ProfileGift.objects.filter(owner=sender_profile, gift=gift, gift_type=ProfileGift.BOUGHT).first()

        if not sender_gift or sender_gift.quantity < quantity:
            return Response({'error': 'Insufficient quantity of the gift to send'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            sender_gift.quantity -= quantity
            sender_gift.save()

            receiver_gift, created = ProfileGift.objects.get_or_create(owner=receiver_profile, gift=gift, gift_type=ProfileGift.RECEIVED)
            if not created:
                receiver_gift.quantity += quantity
                receiver_gift.save()


            new_notification = Notification.objects.create(
                recipient=receiver_profile,
                notification_type='gift',
                message=f"{sender_profile.first_name} has sent you a gift!"
            )


            if receiver_profile.is_gift_notification and receiver_profile.fcm_token:
                notification_count = Notification.objects.filter(recipient=receiver_profile, is_read=False).count()
                message = messaging.Message(
                    notification=messaging.Notification(
                        title="New Gift!",
                        body=new_notification.message
                    ),
                    token=receiver_profile.fcm_token,
                    data={"notification_type": "gift"},
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                badge=notification_count
                            )
                        )
                    )
                )
                messaging.send(message)
          
            sender_to_receiver_allowance, created = MessageAllowance.objects.get_or_create(sender=sender_profile, receiver=receiver_profile)
            sender_to_receiver_allowance.remaining_messages += quantity * 200
            sender_to_receiver_allowance.save()

            receiver_to_sender_allowance, created = MessageAllowance.objects.get_or_create(sender=receiver_profile, receiver=sender_profile)
            receiver_to_sender_allowance.remaining_messages += quantity * 200
            receiver_to_sender_allowance.save()

        serializer = ProfileGiftSerializer(receiver_gift)
        return Response(serializer.data, status=status.HTTP_200_OK)


    

class ChatNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_profile = Profile.objects.get(user=request.user)
        chat_notifications = Notification.objects.filter(recipient=user_profile, notification_type='chat')

        chat_serializer = NotificationSerializer(chat_notifications, many=True)

        response_data = {
            'chat_notifications': chat_serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_profile = Profile.objects.get(user=request.user)
        like_notifications = Notification.objects.filter(recipient=user_profile, notification_type='like')
        match_notifications = Notification.objects.filter(recipient=user_profile, notification_type='match')
        gift_notification = Notification.objects.filter(recipient=user_profile, notification_type='gift')


        like_match_gift_notifications = list(like_notifications) + list(match_notifications) + list(gift_notification)

        like_match_gift_serializer = NotificationSerializer(like_match_gift_notifications, many=True)

        response_data = {
            'like_match_gift_notifications': like_match_gift_serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class NotificationsReadAndDelete(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user_profile = Profile.objects.get(user=request.user)
        
        notifications = Notification.objects.filter(recipient=user_profile)
        notifications.update(is_read=True)
        
        notifications.delete()
        
        return Response({'message': 'notifications marked as read and deleted successfully.'}, status=status.HTTP_200_OK)
    



class VerifyPurchaseView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyPurchaseSerializer  

    def post(self, request, *args, **kwargs):
        print("Received POST request")
        purchase_data = request.data
        print(f"Purchase data: {purchase_data}")
        
        platform = purchase_data.get('platform')
        print(f"Platform: {platform}")
        
        purchase_type = purchase_data.get('purchase_type')  # New field to specify purchase type
        print(f"Purchase type: {purchase_type}")

        if purchase_type == 'subscription':
            valid = self.verify_subscription_purchase(purchase_data, platform)
            print(f"Subscription validation result: {valid}")
        elif purchase_type == 'gift':
            valid = self.verify_gift_purchase(purchase_data, platform)
            print(f"Gift validation result: {valid}")
        else:
            print("Invalid purchase type provided.")
            return Response({'detail': 'Invalid purchase type.'}, status=status.HTTP_400_BAD_REQUEST)

        if valid:
            user = request.user  # Assuming user is authenticated
            print(f"Authenticated user: {user}")
            
            if purchase_type == 'subscription':
                user_plan = self.update_user_subscription(purchase_data, user)
                print(f"Updated user subscription: {user_plan}")
                return Response({
                    'detail': 'Purchase verified successfully.',
                    'subscription': {
                        'plan': user_plan.plan.name,
                        'expiry_date': user_plan.expiry_date.isoformat()
                    }
                }, status=status.HTTP_200_OK)
            elif purchase_type == 'gift':
                self.update_user_gifts(purchase_data, user)
                print("Gift purchase updated successfully.")
                return Response({'detail': 'Gift purchase verified successfully.'}, status=status.HTTP_200_OK)
        else:
            print("Purchase verification failed.")
            return Response({'detail': 'Invalid purchase.'}, status=status.HTTP_400_BAD_REQUEST)

    def verify_subscription_purchase(self, purchase_data, platform):
        print(f"Verifying subscription purchase for platform: {platform}")
        
        if platform == 'google':
            return self.verify_google_purchase(purchase_data)
        elif platform == 'apple':
            return self.verify_apple_purchase(purchase_data)
        else:
            print("Invalid platform provided for subscription.")
            return False

        
    def verify_google_purchase(self, purchase_data):
        package_name = "co.weprototype.mispec"  # Ensure this is your correct package name
        product_id = purchase_data['productId']
        purchase_token = purchase_data['purchaseToken']

        # Print full API URL
        api_url = f"https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{package_name}/purchases/subscriptions/{product_id}/tokens/{purchase_token}"
        print(f"API URL: {api_url}")

        if not purchase_token or not product_id:
            print("Missing purchase token or product ID.")
            return False

        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE
        )

        service = build('androidpublisher', 'v3', credentials=credentials)

        try:
            request = service.purchases().subscriptions().get(
                packageName=package_name,
                subscriptionId=product_id,
                token=purchase_token
            )
            response = request.execute()
            print(f"Google purchase response: {response}")

            # Check the purchase state
            payment_state = response.get('paymentState')
            acknowledgement_state = response.get('acknowledgementState')

            # Valid payment state (1 means payment received)
            if payment_state == 1:
                if acknowledgement_state == 0:
                    print("Purchase needs to be acknowledged.")
                    self.acknowledge_google_purchase(package_name, product_id, purchase_token, service)
                return True
            else:
                print(f"Invalid payment state: {payment_state}")
                return False
        except Exception as e:
            print(f"Google purchase verification error: {e}")
            return False

    def acknowledge_google_purchase(self, package_name, product_id, purchase_token, service):
        try:
            service.purchases().subscriptions().acknowledge(
                packageName=package_name,
                subscriptionId=product_id,
                token=purchase_token,
                body={}
            ).execute()
            print("Purchase acknowledged successfully.")
        except Exception as e:
            print(f"Error acknowledging purchase: {e}")
                
    def verify_apple_purchase(self, purchase_data):
        print("Verifying Apple subscription purchase")
        
        receipt_data = purchase_data.get('receiptData')
        production_url = 'https://buy.itunes.apple.com/verifyReceipt'
        sandbox_url = 'https://sandbox.itunes.apple.com/verifyReceipt'

        print(f"Apple receipt data: {receipt_data}")

        if not receipt_data:
            print("Missing Apple receipt data.")
            return False

        payload = {
            'receipt-data': receipt_data,
            'password': settings.APPLE_SHARED_SECRET
        }

        # Attempt to verify with the production URL first
        try:
            response = requests.post(production_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            result = response.json()
            print(f"Apple production verification response: {result}")

            # Check if the receipt is from the sandbox environment
            if result.get('status') == 21007:
                print("Receipt is from sandbox environment, retrying with sandbox URL.")
                response = requests.post(sandbox_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
                result = response.json()
                print(f"Apple sandbox verification response: {result}")

            if result.get('status') == 0:  # 0 means valid receipt
                return True
            else:
                print(f"Apple verification failed with status: {result.get('status')}")
                return False
        except Exception as e:
            print(f"Apple verification error: {e}")
            return False

    def verify_gift_purchase(self, purchase_data, platform):
        print(f"Verifying gift purchase for platform: {platform}")
        
        if platform == 'google':
            return self.verify_google_gift_purchase(purchase_data)
        elif platform == 'apple':
            return self.verify_apple_gift_purchase(purchase_data)
        else:
            print("Invalid platform provided for gift.")
            return False

    def verify_google_gift_purchase(self, purchase_data):
        print("Verifying Google gift purchase")
        
        purchase_token = purchase_data.get('purchaseToken')
        product_id = purchase_data.get('productId')
        package_name = 'co.weprototype.mispec'

        print(f"Google purchase token: {purchase_token}")
        print(f"Google product ID: {product_id}")

        if not purchase_token or not product_id:
            print("Missing purchase token or product ID.")
            return False

        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE
        )

        service = build('androidpublisher', 'v3', credentials=credentials)

        try:
            request = service.purchases().products().get(
                packageName=package_name,
                productId=product_id,
                token=purchase_token
            )
            response = request.execute()
            print(f"Google gift purchase response: {response}")
            return response.get('purchaseState') == 0  # 0 means purchased
        except Exception as e:
            print(f"Google gift purchase verification error: {e}")
            return False


    def verify_apple_gift_purchase(self, purchase_data):
        print("Verifying Apple gift purchase")
        
        receipt_data = purchase_data.get('receiptData')
        production_url = 'https://buy.itunes.apple.com/verifyReceipt'
        sandbox_url = 'https://sandbox.itunes.apple.com/verifyReceipt'

        print(f"Apple receipt data: {receipt_data}")

        if not receipt_data:
            print("Missing Apple receipt data.")
            return False

        payload = {
            'receipt-data': receipt_data,
            'password': settings.APPLE_SHARED_SECRET  # App-specific shared secret
        }

        try:
            # Attempt to verify with the production URL first
            response = requests.post(production_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            result = response.json()
            print(f"Apple production verification response: {result}")

            # Check if the receipt is from the sandbox environment
            if result.get('status') == 21007:
                print("Receipt is from sandbox environment, retrying with sandbox URL.")
                response = requests.post(sandbox_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
                result = response.json()
                print(f"Apple sandbox verification response: {result}")

            # Check if the status is 0, meaning the receipt is valid
            if result.get('status') == 0:  # 0 means valid receipt
                return True
            else:
                print(f"Apple gift verification failed with status: {result.get('status')}")
                return False
        except Exception as e:
            print(f"Apple gift verification error: {e}")
            return False

    def update_user_subscription(self, purchase_data, user):
        print("Updating user subscription")
        
        product_id = purchase_data.get('productId')
        expiry_date = purchase_data.get('expiry_date')
        print(f"Product ID: {product_id}, Expiry Date: {expiry_date}")

        if not product_id or not expiry_date:
            print("Missing product ID or expiry date.")
            return None

        # Convert expiry_date string to datetime object
        try:
            expiry_date = datetime.fromisoformat(expiry_date)
        except Exception as e:
            print(f"Error parsing expiry date: {e}")
            return None

        # Retrieve the plan and user's profile
        plan = Plan.objects.get(product_id=product_id)
        profile = Profile.objects.get(user=user)

        # Update or create the user's subscription
        user_plan, created = UserPlan.objects.update_or_create(
            profile=profile,
            defaults={
                'plan': plan,
                'expiry_date': expiry_date,
                'is_active': True
            }
        )

        # Update the profile's plan
        profile.plan = plan
        profile.save()
        return user_plan

    def update_user_gifts(self, purchase_data, user):
        print("Updating user gifts")
        
        product_id = purchase_data.get('productId')
        quantity = purchase_data.get('quantity')
        print(f"Product ID: {product_id}, Quantity: {quantity}")

        if not product_id or quantity is None:
            print("Missing product ID or quantity.")
            return Response({'detail': 'Invalid purchase data.'}, status=status.HTTP_400_BAD_REQUEST)

        gift = get_object_or_404(Gift, id=purchase_data.get('gift_id'))
        profile = Profile.objects.get(user=user)

        try:
            profile_gift = ProfileGift.objects.get(owner=profile, gift=gift)
            profile_gift.quantity += quantity
            profile_gift.save()
            print(f"Updated existing profile gift: {profile_gift}")
        except ProfileGift.DoesNotExist:
            profile_gift = ProfileGift.objects.create(
                owner=profile,
                gift=gift,
                quantity=quantity,
                gift_type=ProfileGift.BOUGHT
            )
            print(f"Created new profile gift: {profile_gift}")

        return profile_gift



class SupportView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupportSerializer

    def post(self, request, *args, **kwargs):
        sender_user = request.user
        # Accept either 'description' or 'message' as the body field
        data = request.data.copy()
        if 'message' in data and 'description' not in data:
            data['description'] = data['message']

        try:
            sender_profile = sender_user.profile
            data['sender'] = str(sender_profile.id)
        except Exception:
            pass

        serializer = SupportSerializer(data=data)
        if serializer.is_valid():
            description = serializer.validated_data['description']
            send_contact_email(sender_user, description)
            serializer.save()
            return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
