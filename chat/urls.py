from django.urls import path
from .views import *

urlpatterns = [
    path('messages/', MessageAPIView.as_view(), name='messages'),
    path('active_chatrooms/', ActiveChatroomsAPIView.as_view(), name='active-chatrooms'),
    path('make_call/', MakeCallAPIView.as_view(), name='make-call'),
    path('join_call/', JoinCallAPIView.as_view(), name='join-call'),
    path('call_history/', CallHistoryAPIView.as_view(), name='call-history'),
    path('create_room/', CreateRoom.as_view(), name='create-room'),
    path('create_event/', CreateEventView.as_view(), name='create-event'),
    path('edit_event/', EditEventView.as_view(), name='edit-event'),
    path('event_detail/', EventDetailView.as_view(), name='event-detail'),
    path('add_member/', AddToEventView.as_view(), name='add-member'),
    path('stop_event/', StopEventView.as_view(), name='stop-event'),
    path('leave_event/', LeaveChatRoomView.as_view(), name='leave-event'),
    path('report_event/', ReportEventView.as_view(), name='report-event'),
    path('end_call/', EndCallAPIView.as_view(), name='end-call'),
]