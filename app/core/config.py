import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    DB_HOST: str
    DB_PORT: int 
    DB_NAME: str 
    DB_USER: str 
    DB_PASSWORD: str 
    SECRET_KEY: str
    ADMIN_SECRET_KEY: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ALGORITHM: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: str
    MAIL_SERVER: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    RESEND_API_KEY: str
    RESEND_FROM: str

    MOBILE_APP_REDIRECT_URL: str

    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
    )


settings = Settings()


def get_db_url():
    return settings.DATABASE_URL


def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}


def get_admin_key():
    return {"secret_key": settings.ADMIN_SECRET_KEY}

def get_google_data():
    return {'google_id': settings.GOOGLE_CLIENT_ID, 'google_secret': settings.GOOGLE_CLIENT_SECRET}