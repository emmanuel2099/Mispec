from django.conf import settings
import requests
import messagebird
from django.core.mail import send_mail
from mailbit import Mailbit
    

def send_otp(email, otp):
    api_key = settings.MAILBIT_API_KEY
      
    email_data = {
        'toAddress': email,
        'subject': 'Your OTP Code',
        'template': f'''<html><body>
        <p>Hi<br>We’re excited to have you get started.</p>
        <br><p>First, you need to verify your account. Just copy the code below<br>
        {otp}</p><br>
        <p>Note: This code expires in 5mins.
        If this wasn’t done by you, please contact <a href="mailto:Info@mispec.co.uk">Info@mispec.co.uk</a></p><br>
        <p>Thanks for choosing Mispec.</p></body></html>''',
        'from': settings.DEFAULT_FROM_EMAIL,
        'senderName': 'Mispec',
        'replyTo': 'no reply',
        'attachments': []
    }
    mailbit = Mailbit(api_key)
      
    try:
        mailbit.send_email(email_data)
        print('Email successfully sent.')
    except ValueError as e:
        print('An error occurred:', e)

