import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(to, subject, body):
    mess = MIMEMultipart()
    mess['From'] = 'developement@glacka.dev'
    mess['To'] = to
    mess['Subject'] = subject

    mess.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.hostinger.com', 587)
        server.starttls()
        server.login('developement@glacka.dev', 'q!YSc*-YQM7.zFt')
        server.sendmail(mess['From'], mess['To'], mess.as_string())
        return True    
    except Exception as e:
        return False
    finally:
        server.quit()