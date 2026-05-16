import traceback
import requests
from django.conf import settings


def send_otp(email, otp):
    """Send OTP via Gmail SMTP using app password - free and reliable."""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your Mispec OTP Code'
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = email

        text = f"Your Mispec OTP code is: {otp}. It expires in 5 minutes."
        html = f"""
        <html><body>
        <p>Hi,</p>
        <p>Please verify your account using the code below:</p>
        <p><strong style="font-size:28px; letter-spacing:4px;">{otp}</strong></p>
        <p>This code expires in 5 minutes.<br>
        If this wasn't you, contact <a href="mailto:Info@mispec.co.uk">Info@mispec.co.uk</a></p>
        <p>Thanks,<br>Mispec Team</p>
        </body></html>
        """
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP(settings.EMAIL_HOST, int(settings.EMAIL_PORT), timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.EMAIL_HOST_USER, [email], msg.as_string())

        print(f"[OTP] Email sent successfully to {email}")

    except Exception as e:
        print(f"[OTP] Email failed to {email}: {e}")
        traceback.print_exc()
        raise
