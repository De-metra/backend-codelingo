from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType

from app.core.config import settings
from pathlib import Path


def get_mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True
    )

def get_mail() -> FastMail:
    return FastMail(get_mail_config())

def create_message(recipients: list[str], subject: str, body: str):

    message = MessageSchema(
       subject=subject,
       recipients=recipients,  # List of recipients, as many as you can pass  
       body=body,
       subtype=MessageType.html
       )
    
    return message
