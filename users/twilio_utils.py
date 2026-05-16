import threading
import traceback
from django.core.mail import send_mail
from django.conf import settings


def _send_email(email, otp):
    try:
        html_content = f"""
        <html><body>
        <p>Hi,</p>
        <p>We're excited to have you get started.</p>
        <p>Please verify your account using the code below:</p>
        <p><strong style="font-size:24px;">{otp}</strong></p>
        <p>Note: This code expires in 5 minutes.<br>
        If this wasn't done by you, contact
        <a href="mailto:Info@mispec.co.uk">Info@mispec.co.uk</a></p>
        <p>Thanks for choosing Mispec.</p>
        </body></html>
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
