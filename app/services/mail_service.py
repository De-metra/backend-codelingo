from datetime import datetime, timedelta
from fastapi import HTTPException

from app.core.security import verify_password, get_password_hash, create_jwt_token
from app.core.security import get_user_from_token, get_password_hash, generate_reset_code
from app.models.models import Users, Users_Stats, PasswordResetCode
from app.schemas.user import UserRegister, UserReturn, UserLogin
from app.schemas.email import CodeUpdateRequest, EmailRequest
from app.internal.mail import create_message, mail
#from app.internal.mail import send_email  # твой метод отправки
from app.utils.uow import IUnitOfWork
from app.core.exception import *


class MailService():
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    