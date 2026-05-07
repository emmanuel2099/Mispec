import threading
import traceback
from django.core.mail import send_mail
from django.conf import settings


def _send_email(email, otp):
    try:
        html_content = f"""
        Hi,<br>We're excited to have you get started.<br><br>
        Please verify your account using the code below:<br>
        <strong style="font-size:24px;">{otp}</strong><br><br>
        Note: This code expires in 5 minutes.
        If this wasn't done by you, contact <a href="mailto:Info@mispec.co.uk">Info@mispec.co.uk</a><br><br>
        Thanks for choosing Mispec.
        """
        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP code is: {otp}. It expires in 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False,
        )
        print(f"[OTP] Email sent successfully to {email}")
    except Exception as e:
        print(f"[OTP] Email failed to {email}: {e}")
        traceback.print_exc()


def send_otp(email, otp):
    t = threading.Thread(target=_send_email, args=(email, otp), daemon=True)
    t.start()
