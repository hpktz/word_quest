""" 
This module contains the send_mail function for the application.

Imports:
    - smtplib: SMTP protocol client.
    - MIMEText: Class for generating plain text email messages.
    - MIMEMultipart: Class for generating multipart email messages.

Functions:
    - send_mail: Send an email.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    mess['From'] = 'developement@glacka.dev'
    mess['To'] = to
    mess['Subject'] = subject

    # Attach the body to the message
    mess.attach(MIMEText(body, 'plain'))

    try:
        # Send the email
        server = smtplib.SMTP('smtp.hostinger.com', 587)
        server.starttls()
        server.login('developement@glacka.dev', 'q!YSc*-YQM7.zFt')
        server.sendmail(mess['From'], mess['To'], mess.as_string())
        return True    
    except Exception as e:
        return False
    finally:
        server.quit()