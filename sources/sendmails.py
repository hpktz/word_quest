""" 
This module contains the send_mail function for the application.

Imports:
    - smtplib: SMTP protocol client.
    - MIMEText: Class for generating plain text email messages.
    - MIMEMultipart: Class for generating multipart email messages.
    - MIMEImage: Class for generating image email messages.
    - os: Miscellaneous operating system interfaces.

Functions:
    - send_mail: Send an email.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from root import *
import os

def send_mail(to, subject, body):
    """
    Send an email.

    Args:
        to (string): The recipient's email address.
        subject (string): The subject of the email.
        body (string): The body of the email.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    
    # Create the email message
    mess = MIMEMultipart()
    mess['From'] = 'Word Quest <no-reply@word-quest.com>'
    mess['To'] = to
    mess['Subject'] = subject

    # Attach the body to the message
    mess.attach(MIMEText(body, 'html'))
    
    with open(str(os.getenv("DIRECTORY_PATH")) + 'static/imgs/app-main-logo.png', 'rb') as fp:
        img = MIMEImage(fp.read())
        img.add_header('Content-ID', '<{}>'.format('app-main-logo'))
        mess.attach(img)

    server = None
    try:
        # Send the email
        server = smtplib.SMTP('smtp.ionos.fr', 587)
        server.starttls()
        server.login('no-reply@word-quest.com', os.environ.get('EMAILING_SERVICE_PASSWORD'))
        server.sendmail(mess['From'], mess['To'], mess.as_string())
        return True    
    except Exception as e:
        print(e)
        return False
    finally:
        if server:
            server.quit()

# Example usage
# to_address = 'recipient@example.com'
# email_subject = 'Test Email'
# email_body = '<h1>This is a test email.</h1><p>It contains HTML content.</p>'

# send_mail(to_address, email_subject, email_body)
