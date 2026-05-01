from django.contrib import admin
from .models import *

# Register your models here.


class MatchAdmin(admin.ModelAdmin):
    search_fields = ['profile_a__email', 'profile_b__email']
    list_display = ('profile_a', 'profile_b', 'timestamp')

class LikeAdmin(admin.ModelAdmin):
    search_fields = ['sender__email', 'receiver__email']
    list_display = ('sender', 'receiver', 'timestamp')

class BlockAdmin(admin.ModelAdmin):
    list_display = ('blocked_by', 'blocked_user', 'timestamp')

class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referred_by', 'referred_user', 'timestamp')


class ReportAdmin(admin.ModelAdmin):
    list_display = ('reported_by', 'reported_user', 'timestamp')


class NotficationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'notification_type', 'created_at')

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'first_name', 'last_name', 'email', 'referral_code', 'occupation', 'bio', 'location_name']


class ProfileMediaAdmin(admin.ModelAdmin):
    search_fields = ['profile__first_name', 'profile__last_name']

admin.site.register(Plan)
admin.site.register(Gift)
admin.site.register(ProfileGift)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Referral, ReferralAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(Sport)
admin.site.register(Entertainment)
admin.site.register(ProfileMedia, ProfileMediaAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Notification, NotficationAdmin)
admin.site.register(UserPlan)
admin.site.register(Support)
