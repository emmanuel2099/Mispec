from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)
from .views import *
from . import views

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth_provider/', ProviderAuthView.as_view(), name="auth_provider" ),
    path('send_otp/', OtpSendView.as_view(), name='send_otp'),
    path('verify_otp/', VerifyOtpView.as_view(), name='verify_otp'),
    path('register/', RegistrationView.as_view(), name='user_registration'),
    path('login/', LoginAPIView.as_view(), name="login" ),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('create_referral/', CreateReferralView.as_view(), name='create_referral'),
    path('change_password/', ChangePasswordView.as_view(), name='change-password'),
    path('reset_password_request/', ResetPasswordRequest.as_view(), name='reset_password_request'),
    path('reset_password_verify/', ResetPasswordVerify.as_view(), name='reset_password_verify'),
    path('delete_account/', DeleteAccountView.as_view(), name='delete-account'),
]
