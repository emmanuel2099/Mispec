import threading
import traceback
import requests
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

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json={
                "sender": {"name": "Mispec", "email": settings.DEFAULT_FROM_EMAIL},
                "to": [{"email": email}],
                "subject": "Your OTP Code",
                "htmlContent": html_content,
                "textContent": f"Your OTP code is: {otp}. It expires in 5 minutes.",
            },
            headers={
                "api-key": settings.BREVO_API_KEY,
                "Content-Type": "application/json",
            },
            timeout=15,
        )

        if response.status_code in (200, 201):
            print(f"[OTP] Email sent successfully to {email}")
        else:
            print(f"[OTP] Brevo error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"[OTP] Email failed to {email}: {e}")
        traceback.print_exc()


def send_otp(email, otp):
    t = threading.Thread(target=_send_email, args=(email, otp), daemon=True)
    t.start()
