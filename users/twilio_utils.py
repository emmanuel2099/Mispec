import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.conf import settings


def send_otp(email, otp):
    sg = sendgrid.SendGridAPIClient(api_key=settings.EMAIL_HOST_PASSWORD)

    html_content = f"""<html><body>
    <p>Hi,<br>We're excited to have you get started.</p>
    <br><p>Please verify your account using the code below:<br>
    <strong style="font-size:24px;">{otp}</strong></p><br>
    <p>Note: This code expires in 5 minutes.
    If this wasn't done by you, contact <a href="mailto:Info@mispec.co.uk">Info@mispec.co.uk</a></p><br>
    <p>Thanks for choosing Mispec.</p>
    </body></html>"""

    message = Mail(
        from_email=Email(settings.DEFAULT_FROM_EMAIL, "Mispec"),
        to_emails=To(email),
        subject="Your OTP Code",
        html_content=Content("text/html", html_content),
    )

    response = sg.client.mail.send.post(request_body=message.get())
    print(f"OTP email sent to {email}, status: {response.status_code}")
