from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser, OtpCheck
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from rest_framework.views import APIView
from rest_framework import generics, status
from django.contrib.auth import update_session_auth_hash
from profiles.models import Profile, Referral
from rest_framework.permissions import IsAuthenticated
from .utils import generate_otp
from .twilio_utils import send_otp


class ProviderAuthView(generics.CreateAPIView):
    serializer_class = ProviderAuthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        response_data = serializer.validated_data
        return Response(response_data, status=status.HTTP_200_OK)
    

class OtpSendView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')

        if not phone_number:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        otp_instance, created = OtpCheck.objects.get_or_create(email=email, phone_number=phone_number)

        generated_otp = generate_otp()

        otp_instance.otp_code = generated_otp
        otp_instance.save()

        try:
            send_otp(email, generated_otp)
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Email failed but OTP is saved — return it so testing isn't blocked
            # TODO: remove otp from response once email service is working
            return Response({
                "success": "OTP generated (email delivery failed)",
                "otp": generated_otp
            }, status=status.HTTP_200_OK)

        response_data = {
            "success": "OTP sent successfully"
        }
        return Response(response_data, status=status.HTTP_200_OK)
    

class VerifyOtpView(APIView):
    serializer_class = VerifyOtpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']


        response_data = {
            'email': email,
            'otp_code': otp_code,
            'message': 'OTP verified successfully'
        }

        return Response(response_data, status=status.HTTP_200_OK)

    

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response_data = serializer.create(validated_data=serializer.validated_data)

        return Response(response_data, status=status.HTTP_201_CREATED)

    
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetPasswordRequest(APIView):
    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        email = serializer.validated_data['email']
        user = CustomUser.objects.filter(phone_number=phone_number, email=email).first()

        if user is None:
            return Response({'error': 'User not found with the provided phone number'}, status=status.HTTP_404_NOT_FOUND)

        otp = generate_otp()

        send_otp(email, otp)

        return Response({'message': 'OTP sent successfully', 'otp': otp}, status=status.HTTP_200_OK)
    



class ResetPasswordVerify(APIView):
    def post(self, request):
        serializer = ResetPasswordVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        new_password = serializer.validated_data['new_password']

        user = get_object_or_404(CustomUser, phone_number=phone_number)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)


class CreateReferralView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        referred_user = Profile.objects.get(user=request.user)
        serializer = CreateReferralSerializer(data=request.data)
        if serializer.is_valid():
            referral_code = serializer.validated_data['referral_code']
            referrer = get_object_or_404(Profile, referral_code=referral_code)
            referral = Referral.objects.create(referred_by=referrer, referred_user=referred_user)

    
            referred_user.referred_by = referrer
            referred_user.save()
            return Response({"message": "Referral created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.validated_data.get('old_password')):
                user.set_password(serializer.validated_data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)  # To update session after password change
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = DeleteAccountSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.is_authenticated and user.is_active:
                user.is_active = False
                user.save()
                return Response({'message': 'Account deleted'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User account not found or already suspended'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']

            token = RefreshToken(refresh_token)
            token.blacklist()


            return Response({"detail": "Successfully logged out."})

        except Exception as e:
            return Response({"detail": "Invalid or missing refresh token."}, status=400)

