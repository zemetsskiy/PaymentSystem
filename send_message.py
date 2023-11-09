import asyncio

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import GMAIL_USER, GMAIL_PASSWORD


async def send_message_coroutine(recipient_email, subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    gmail_user = GMAIL_USER
    gmail_password = GMAIL_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_server,
            port=smtp_port,
            start_tls=True,
            username=gmail_user,
            password=gmail_password,
        )
        print("Message was sent")
    except aiosmtplib.SMTPException as e:
        print("Message not sent", e)
