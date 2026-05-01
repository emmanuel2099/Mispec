from django.urls import path
from .views import *

urlpatterns = [
    path('profiles_update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profiles_filter/', ProfileFilterView.as_view(), name='profile-filter'),
    path('both_profiles_filter/', BothProfileFilterView.as_view(), name='both-profile-filter'),
    path('entertainment/', EntertainmentView.as_view(), name='entertainment'),
    path('sport/', SportView.as_view(), name='sport'),
    path('media_delete/', ProfileMediaDeleteView.as_view(), name='media_delete'),
    path('like_create/', LikeCreateView.as_view(), name='like-create'),
    path('liked_profiles/', LikedProfilesView.as_view(), name='liked-profiles'),
    path('report_create/', CreateReportView.as_view(), name='report-create'),
    path('reported_profiles/', ReportProfilesView.as_view(), name='reported-profiles'),
    path('block_create/', CreateBlockView.as_view(), name='block-create'),
    path('blocked_profiles/', BlockedProfilesView.as_view(), name='reported-profiles'),
    path('matches/', MatchListView.as_view(), name='match'),
    path('profile_gift/', CreateProfileGiftView.as_view(), name='profile-gift'),
    path('owned_gift/', OwnedGiftView.as_view(), name='owned-gift'),
    path('received_gift/', ReceivedGiftView.as_view(), name='received-gift'),
    path('profile_unblock/', ProfileUnblockView.as_view(), name='unblock-profile'),
    path('referrals/', ReferralView.as_view(), name='referrals'),
    path('redeem_gift/', RedeemGiftView.as_view(), name='redeem-gift'),
    path('redeem_referral/', RedeemReferralView.as_view(), name='redeem-referral'),
    path('dislike/', ProfileDislikeView.as_view(), name='dislike'),
    path('chat_notifications/', ChatNotificationView.as_view(), name='chat-notifications'),
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('read_notification/', NotificationsReadAndDelete.as_view(), name='read_notification'),
    path('send_gift/', SendGiftView.as_view(), name='send-gift'),
    path('gifts/', GiftListView.as_view(), name='gift-list'),
    path('verify_purchase/', VerifyPurchaseView.as_view(), name='verify_purchase'),
    path('support/', SupportView.as_view(), name='support'),

]
