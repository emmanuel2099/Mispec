import requests
from django.conf import settings


def send_contact_email(sender, description):
    html_content = f"""<html><body>
    <p>You have received a new message from the support form on Mispec.</p>
    <p><strong>From:</strong> {sender}</p>
    <p><strong>Message:</strong><br>{description}</p>
    </body></html>"""

    payload = {
        "sender": {"name": "Mispec Support", "email": settings.DEFAULT_FROM_EMAIL},
        "to": [{"email": settings.ADMIN_EMAIL}],
        "subject": f"Support message from {sender}",
        "htmlContent": html_content,
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={
                "api-key": settings.BREVO_API_KEY,
                "Content-Type": "application/json",
            },
        )
        print(f"Support email sent, status: {response.status_code}")
    except Exception as e:
        print(f"Support email error: {e}")
