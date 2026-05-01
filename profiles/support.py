from mailbit import Mailbit
from django.conf import settings

def send_contact_email(sender, description):
    api_key = settings.MAILBIT_API_KEY
      
    email_data = {
        'toAddress': settings.ADMIN_EMAIL,
        'subject': f'Message from {sender}',
        'template': f'''<html><body>
        <p>You have received a new message from the support form on mispec.</p>
        <p><strong>Message:</strong><br>{description}</p>
        </body></html>''',
        'from': settings.DEFAULT_FROM_EMAIL,
        'senderName':'Mispec Support',
        'replyTo': 'no reply',
        'attachments': []
    }
    
    mailbit = Mailbit(api_key)
    
    try:
        mailbit.send_email(email_data)
        print('Contact form email successfully sent.')
    except ValueError as e:
        print('An error occurred:', e)