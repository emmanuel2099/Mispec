from rest_framework import serializers
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomUser, OtpCheck
from django.shortcuts import get_object_or_404
from profiles.models import Profile, Referral
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password


class ProviderAuthSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=250, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=250, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=250, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    provider = serializers.CharField(max_length=200)
    provider_id = serializers.CharField(max_length=1500)
    referral_code = serializers.CharField(max_length=100, allow_blank=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'provider', 'provider_id', 'referral_code']

    def validate(self, data):
        provider = data.get('provider')
        provider_id = data.get('provider_id')
        email = data.get('email')

        try:
            existing_user = CustomUser.objects.get(provider_id=provider_id, provider=provider)
        except CustomUser.DoesNotExist:
            existing_user = None

        # Migrate older clients that used email as provider_id
        if existing_user is None and email:
            existing_user = CustomUser.objects.filter(
                provider=provider, email=email
            ).first()
            if existing_user is not None:
                existing_user.provider_id = provider_id
                existing_user.save(update_fields=['provider_id'])

        if existing_user:
            if not existing_user.is_active:
                raise AuthenticationFailed("Your account has been disabled, contact admin.")

            existing_user.is_new_user = False
            existing_user.save()

            return {
                'email': existing_user.email,
                'tokens': existing_user.tokens(),
                'is_verified': existing_user.is_verified,
                'is_new_user': existing_user.is_new_user
            }
        else:
            # Handle first-time sign-in
            phone_number = data.pop('phone_number', None)

            if not phone_number:
                raise serializers.ValidationError("Phone number is required for new users.")

            data['is_verified'] = True
            data['is_new_user'] = True

            email = data.get('email')
            if email and CustomUser.objects.filter(email=email).exists():
                raise AuthenticationFailed("A user with this email already exists.")

            try:
                user = CustomUser.objects.create_user(phone_number=phone_number, **data)
            except IntegrityError:
                raise AuthenticationFailed("A user with this email already exists.")

            referral_code = data.get('referral_code')
            if referral_code:
                handle_referral(self.context['request'], referral_code, user)

            return {
                'email': user.email,
                'tokens': user.tokens(),
                'is_verified': user.is_verified,
                'is_new_user': user.is_new_user
            }

def handle_referral(request, referral_code, referred_user):
    
    referrer = get_object_or_404(Profile, referral_code=referral_code)

    
    referral = Referral.objects.create(referred_by=referrer, referred_user=referred_user.profile, is_redeemed=False)

    
    referred_user.profile.referred_by = referrer
    referred_user.profile.save()


class CreateReferralSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(max_length=250, allow_blank=True, allow_null=True)

    class Meta:
        model = Referral
        fields = ['referral_code']


class OtpSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OtpCheck
        fields = ['email', 'phone_number', 'otp_code']


class VerifyOtpSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=100)
    otp_code = serializers.CharField(max_length=100)

    class Meta:
        model = OtpCheck
        fields = ['email', 'otp_code']

    def validate(self, validated_data):
        email = validated_data.get('email')
        otp_code = validated_data.get('otp_code')

        if OtpCheck.objects.filter(email=email, otp_code=otp_code).exists():
            return {
                'email': email,
                'otp_code': otp_code
            }
        else:
            raise serializers.ValidationError({'detail': 'Invalid email or OTP code'})



class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=250)
    phone_number = serializers.CharField(max_length=100)
    otp = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    referral_code = serializers.CharField(max_length=100, allow_blank=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'otp', 'referral_code', 'password']

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        phone_number = data.get('phone_number')
        if phone_number:
            data['phone_number'] = phone_number.replace(' ', '')
        return data

    def validate(self, args):
        email = args.get('email', None)
        phone_number = args.get('phone_number', None)
        otp = args.get('otp', None)
        referral_code = args.get('referral_code', None)

        if CustomUser.objects.filter(email=email).exists():
            raise AuthenticationFailed('Email already exists')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise AuthenticationFailed('This phone number already exists')

        otp_match = OtpCheck.objects.filter(email=email, otp_code=otp).first()
        if otp_match is None:
            # Also allow match by email + phone when both were stored together
            otp_match = OtpCheck.objects.filter(
                email=email, phone_number=phone_number, otp_code=otp
            ).first()
        if otp_match is None:
            raise AuthenticationFailed('Invalid or expired OTP. Please request a new code.')

        return super().validate(args)
    

    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', None)
        otp_code = validated_data.get('otp')
        email = validated_data.get('email')
        
        validated_data['is_verified'] = True
        validated_data['is_new_user'] = True

        user = CustomUser.objects.create_user(**validated_data)

        # Consume OTP so it cannot be reused
        OtpCheck.objects.filter(email=email, otp_code=otp_code).delete()

        if referral_code:
            handle_referral(self.context['request'], referral_code, user)
            
        return {
            'email': user.email,
            'tokens': user.tokens(),
            'is_new_user': user.is_new_user,
            'is_verified': user.is_verified,
            'referral_code': user.referral_code
        }
            
 


class LoginSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    is_new_user = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password', 'is_verified', 'is_new_user']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        phone_number = attrs.get('phone_number', '')
        password = attrs.get('password', '')

        # user = auth.authenticate(phone_number=phone_number, password=password)

        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('This is not a valid account')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')
        
        # if not user:
        #     raise AuthenticationFailed('This is not a valid account')
        if not user.is_active:
            raise AuthenticationFailed('Your account has been disabled, contact admin')
        
        user.is_new_user = False
        user.save()
        
        self.user = user
        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['tokens'] = self.user.tokens()
        ret['is_verified'] = self.user.is_verified
        ret['is_new_user'] = self.user.is_new_user
        return ret



class ResetPasswordRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    email = serializers.CharField()


class ResetPasswordVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    new_password = serializers.CharField()
    otp = serializers.CharField(required=False, allow_blank=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class DeleteAccountSerializer(serializers.Serializer):
    model = CustomUser


    




