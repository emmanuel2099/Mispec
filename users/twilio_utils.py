import requests
from django.conf import settings


def send_otp(email, otp):
    html_content = f"""<html><body>
    <p>Hi,<br>We're excited to have you get started.</p>
    <br><p>Please verify your account using the code below:<br>
    <strong style="font-size:24px;">{otp}</strong></p><br>
    <p>Note: This code expires in 5 minutes.
    If this wasn't done by you, contact <a href="mailto:Info@mispec.co.uk">Info@mispec.co.uk</a></p><br>
    <p>Thanks for choosing Mispec.</p>
    </body></html>"""

    payload = {
        "recipients": [{"address": {"email": email}}],
        "body": {
            "type": "html",
            "html": {"data": html_content},
        },
        "from": {
            "address": {
                "email": settings.DEFAULT_FROM_EMAIL,
                "name": "Mispec",
            }
        },
        "subject": "Your OTP Code",
    }

    response = requests.post(
        "https://api.bird.com/workspaces/me/channels/me/messages",
        json=payload,
        headers={
            "Authorization": f"AccessKey {settings.BIRD_EMAIL_API_KEY}",
            "Content-Type": "application/json",
        },
    )

    if response.status_code not in (200, 201):
        raise Exception(f"Bird error {response.status_code}: {response.text}")

    print(f"OTP email sent to {email} via Bird")
