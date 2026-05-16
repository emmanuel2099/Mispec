import traceback
import requests
from django.conf import settings


def send_otp(email, otp):
    """Send OTP via Brevo HTTP API. Called synchronously so errors are visible."""
    try:
        html_content = f"""
        <html><body>
        <p>Hi,</p>
        <p>Please verify your account using the code below:</p>
        <p><strong style="font-size:28px; letter-spacing:4px;">{otp}</strong></p>
        <p>This code expires in 5 minutes.<br>
        If this wasn't you, contact <a href="mailto:Info@mispec.co.uk">Info@mispec.co.uk</a></p>
        <p>Thanks,<br>Mispec Team</p>
        </body></html>
        """

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json={
                "sender": {"name": "Mispec", "email": settings.DEFAULT_FROM_EMAIL},
                "to": [{"email": email}],
                "subject": "Your Mispec OTP Code",
                "htmlContent": html_content,
                "textContent": f"Your Mispec OTP code is: {otp}. It expires in 5 minutes.",
            },
            headers={
                "api-key": settings.BREVO_API_KEY,
                "Content-Type": "application/json",
            },
            timeout=15,
        )

        if response.status_code in (200, 201):
            print(f"[OTP] Email sent to {email} | messageId: {response.json().get('messageId')}")
        else:
            print(f"[OTP] Brevo error {response.status_code}: {response.text}")
            raise Exception(f"Brevo API error: {response.status_code} {response.text}")

    except Exception as e:
        print(f"[OTP] Failed to send to {email}: {e}")
        traceback.print_exc()
        raise
