import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(message_body: str) -> None:
    sender_email = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_SENDER_PASSWORD"]
    recipient_email = os.environ["EMAIL_RECEIVER"]
    subject = "Message from script"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    thread_id = os.environ["EMAIL_THREAD_ID"]
    message["In-Reply-To"] = thread_id
    message["References"] = thread_id

    part1 = MIMEText(message_body, "plain")
    message.attach(part1)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("mail.privateemail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, message.as_string())
