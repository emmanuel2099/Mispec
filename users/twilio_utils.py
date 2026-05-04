from django.conf import settings
from django.core.mail import send_mail


def send_otp(email, otp):
    subject = "Your OTP Code"
    html_message = f"""<html><body>
    <p>Hi,<br>We're excited to have you get started.</p>
    <br><p>First, you need to verify your account. Just copy the code below:<br>
    <strong style="font-size:24px;">{otp}</strong></p><br>
    <p>Note: This code expires in 5 minutes.
    If this wasn't done by you, please contact <a href="mailto:Info@mispec.co.uk">Info@mispec.co.uk</a></p><br>
    <p>Thanks for choosing Mispec.</p>
    </body></html>"""

    send_mail(
        subject=subject,
        message=f"Your OTP code is: {otp}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )
    print(f"OTP email sent to {email}")
