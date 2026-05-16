from rest_framework import serializers
from .models import *

class EntertainmentSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import Entertainment
        model = Entertainment
        fields = '__all__'

class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class GiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gift
        fields = '__all__'


class ProfileMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileMedia
        fields = ['id', 'profile', 'files']


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    entertainment = EntertainmentSerializer(many=True, read_only=True)
    sport = SportSerializer(many=True, read_only=True)
    plan = PlanSerializer(required=False)
    date_of_birth = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'], allow_null=True, required=False)
    medias = ProfileMediaSerializer(many=True, read_only=True)
    uploaded_medias = serializers.ListField(
        child = serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only = True,
        required = False
    )
    is_reported = serializers.SerializerMethodField()
    distance = serializers.IntegerField(required=False, allow_null=True)
    

    class Meta:
        model = Profile
        fields = ['id', 'user', 'email', 'first_name', 'last_name', 'profile_picture', 'gender', 'date_of_birth',
                  'sexual_orientation', 'zodiac_sign', 'entertainment', 'sport', 'why_are_you_here',
                  'relationship_status', 'longitude', 'latitude', 'bio', 'plan', 'referral_code',
                  'occupation', 'height', 'is_reported', 'is_location', 'is_incognito', 'medias', 'uploaded_medias', 'location_name', 'distance']
    
    def validate_longitude(self, value):
        return None if value == '' else value

    def validate_latitude(self, value):
        return None if value == '' else value
    
    def get_is_reported(self, obj):
        return obj.reports_received.exists()
   
class ProfileFilterSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(required=False)
    min_age = serializers.IntegerField(required=False)
    max_age = serializers.IntegerField(required=False)
    plan = PlanSerializer(required=False)
    medias = ProfileMediaSerializer(many=True, read_only=True)
    entertainment = EntertainmentSerializer(many=True, read_only=True)
    sport = SportSerializer(many=True, read_only=True)
    is_reported = serializers.SerializerMethodField()
    location_name = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = ['id', 'email', 'profile_picture', 'first_name', 'last_name', 'distance', 'plan', 'date_of_birth',
                   'bio', 'gender', 'longitude', 'latitude', 'location_name', 'is_location', 'entertainment', 'sport', 'occupation', 'height', 'zodiac_sign', 'medias', 'min_age', 'max_age', 'is_reported']

    def get_is_reported(self, obj):
        return obj.reports_received.exists()

class ProfileUUIDField(serializers.UUIDField):
    def to_internal_value(self, data):
        try:
            profile = Profile.objects.get(id=data)
            return profile
        except Profile.DoesNotExist:
            raise serializers.ValidationError("Profile not found.")

class LikeSerializer(serializers.ModelSerializer):
    receiver = ProfileUUIDField()

    class Meta:
        model = Like
        fields = '__all__'

class BlockSerializer(serializers.ModelSerializer):
    blocked_user = ProfileUUIDField()

    class Meta:
        model = Block
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    reported_user = ProfileUUIDField()
    reason = serializers.CharField(max_length=250)

    class Meta:
        model = Report
        fields = '__all__'

class ReferralSerializer(serializers.ModelSerializer):
    referred_user_first_name = serializers.CharField(source='referred_user.first_name', read_only=True)
    referred_user_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Referral
        fields = ['id', 'referred_by', 'referred_user', 'is_redeemed', 'timestamp', 'referred_user_first_name', 'referred_user_profile_picture']

    def get_referred_user_profile_picture(self, obj):
        try:
            pic = obj.referred_user.profile_picture
            if pic:
                request = self.context.get('request')
                return request.build_absolute_uri(pic.url) if request else pic.url
        except Exception:
            pass
        return None

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class ProfileGiftSerializer(serializers.ModelSerializer):
    gift = serializers.PrimaryKeyRelatedField(queryset=Gift.objects.all())
    gift_type = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = ProfileGift
        fields = '__all__'

class GetProfileGiftSerializer(serializers.ModelSerializer):
    gift = GiftSerializer()
    gift_type = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = ProfileGift
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'


class SupportSerializer(serializers.ModelSerializer):
    description = serializers.CharField(max_length=1000)

    class Meta:
        model = Support
        fields = '__all__'


class VerifyPurchaseSerializer(serializers.Serializer):
    platform = serializers.CharField()
    purchase_type = serializers.CharField()
    purchaseToken = serializers.CharField(required=False)  # Required for Google purchases
    productId = serializers.CharField(required=False)     # Required for Google purchases
    receiptData = serializers.CharField(required=False)   # Required for Apple purchases
    expiry_date = serializers.DateTimeField(required=False)  # Required for subscriptions
    gift_id = serializers.IntegerField(required=False)       # Required for gift purchases
    quantity = serializers.IntegerField(required=False)      # Required for gift purchases