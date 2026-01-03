from datetime import datetime, timedelta
from fastapi import HTTPException

from app.core.security import verify_password, get_password_hash, create_jwt_token
from app.models.models import Users, Users_Stats, PasswordResetCode
from app.schemas.user import UserRegister, UserReturn, UserLogin
from app.schemas.email import CodeUpdateRequest, EmailSchema, EmailRequest, CodeRequest
from app.core.security import get_user_from_token, get_password_hash, generate_reset_code
from app.internal.mail import create_message, get_mail
#from app.internal.mail import send_email  # твой метод отправки
from app.utils.uow import IUnitOfWork
from app.core.exception import *


class AuthService():
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def register(self, user_data: UserRegister) -> UserReturn: 
        async with self.uow:
            is_email_exist = await self.uow.user.get_by_email(user_data.email)
            if is_email_exist:
                raise UserAlreadyExistsError()

            new_user = Users(
                username = user_data.username,
                email = user_data.email,
                hashed_password=get_password_hash(user_data.password),
                picture_link=None,
                created_at=datetime.now()
            )
            
            await self.uow.user.add(new_user)
            await self.uow.session.flush()

            new_stats = Users_Stats(
                user_id = new_user.id,
                total_xp = 0,
                streak = 0,
                last_activity = None
            )
            await self.uow.user_stats.add(new_stats)     #это не должно быть
            await self.uow.commit()

            token = create_jwt_token({"sub": str(new_user.id)}) #заменить на репозиторий или что-то другое
            
            return {"access_token": token, "token_type": "bearer"}  #возвращать пользователя????
        

    async def login(self, user_data: UserLogin):
        async with self.uow:
            user = await self.uow.user.get_by_email(user_data.email)

            if not user or not verify_password(user_data.password, user.hashed_password):
                raise UnauthorizedError()

            token = create_jwt_token({"sub": str(user.id)})
            return {"access_token": token, "token_type": "bearer"}   
    

    async def forgot_password(self, user_mail: EmailRequest): 
        async with self.uow:
            user = await self.uow.user.get_by_email(user_mail.email)

            if not user:
                raise UserNotFoundError()
            
            code = generate_reset_code()

            #To do: обновление существующей записи в таблице

            reset_code = PasswordResetCode(
                user_id = user.id,
                code = code,
                expires_at = datetime.now() + timedelta(minutes=60)
            )

            await self.uow.reset_code.add(reset_code) 
            await self.uow.commit()

            html = f"""
                Приветствуем!<br>
                
                Чтобы восстановить доступ к своему аккаунту, введите, пожалуйста, код:<br>

                <h1>{code}</h1>

                Если вы получили это письмо по ошибке, просто проигнорируйте его.
            """
            
            message = create_message(
                recipients=[user_mail.email],
                subject="Codelingo | Восстановление пароля",
                body=html
            )

            mail = get_mail()
            await mail.send_message(message)

            return {"message": "Сообщение с кодом отправлено на вашу почту!"}
        
    
    async def verify_code(self, data: CodeRequest):
        async with self.uow:
            user = await self.uow.user.get_by_email(data.email)

            if not user:
                raise UserNotFoundError()
            
            reset_token = await self.uow.reset_code.get_valid_code(user.id, data.code)

            if not reset_token:
                raise InvalidCodeError()
            
            await self.uow.reset_code.mark_used(reset_code=reset_token)
            await self.uow.commit()
            
            return {"verified": True}


    async def reset_password(self, data: CodeUpdateRequest):       #не проверено
        async with self.uow:
            user = await self.uow.user.get_by_email(data.email)
            if not user:
                raise UserNotFoundError()
            
            await self.uow.user.change_password(user, data.new_password)

            await self.uow.commit()

        return {"message": "Пароль успешно обновлён"} 
