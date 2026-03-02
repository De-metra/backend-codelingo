from datetime import datetime, timedelta
from fastapi import HTTPException

import aiohttp

from app.core.security import verify_password, get_password_hash, create_jwt_token, generate_reset_code
from app.models.models import Users, Users_Stats, PasswordResetCode
from app.schemas.user import UserRegister, UserReturn, UserLogin
from app.schemas.email import CodeUpdateRequest, EmailSchema, EmailRequest, CodeRequest
from app.core.config import settings
from app.core.resend import send_reset_mail
from app.internal.mail import create_message, get_mail
#from app.internal.mail import send_email  # твой метод отправки
from app.utils.uow import IUnitOfWork
from app.core.exception import *


class AuthService():
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow


    async def register(self, user_data: UserRegister) -> UserReturn: 
        async with self.uow:
            existing_user = await self.uow.user.get_by_email(user_data.email)
            if existing_user and existing_user.is_active:
                raise UserAlreadyExistsError()

            new_user = Users(
                username = user_data.username,
                email = user_data.email,
                hashed_password=get_password_hash(user_data.password),
                picture_link=None
            )
            await self._create_user_with_stats(new_user)
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
                return {"message": "Сообщение с кодом отправлено на вашу почту!"}
            
            # если есть ранее запрошенный не просроченный код
            code_obj = await self.uow.reset_code.get_existing_code(user.id)
            
            if code_obj:
                code = code_obj.code 
            else:
                code = generate_reset_code()

                reset_code = PasswordResetCode(
                    user_id = user.id,
                    code = code,
                    expires_at = datetime.now() + timedelta(minutes=5)
                )

                await self.uow.reset_code.add(reset_code) 
                await self.uow.commit()

        await send_reset_mail(user_mail.email, code)

        return {"message": "Сообщение с кодом отправлено на вашу почту!"}
        
    
    async def verify_code(self, data: CodeRequest):
        async with self.uow:
            user = await self.uow.user.get_by_email(data.email)

            if not user:
                raise InvalidCodeError()
            
            reset_token = await self.uow.reset_code.get_valid_code(user.id, data.code)

            if not reset_token:
                raise InvalidCodeError()
            
            return {"message": "Код подтвержден", "code": data.code}


    async def reset_password(self, data: CodeUpdateRequest):     
        async with self.uow:
            user = await self.uow.user.get_by_email(data.email)
            if not user:
                raise UserNotFoundError()
            
            reset_code = await self.uow.reset_code.get_valid_code(user.id, data.code)
            if not reset_code:
                raise InvalidCodeError()

            await self.uow.user.change_password(user, data.new_password)

            await self.uow.reset_code.delete(reset_code)

            await self.uow.commit()

        return {"message": "Пароль успешно обновлён"} 


    async def google_callback(self, code: str):
        access_token = await self._exchange_code(code)
        user_info = await self._get_user_info(access_token)
        async with self.uow:
            user = await self._get_or_create_google_user(user_info)
            await self.uow.commit()

            token = create_jwt_token({"sub": str(user.id)}) 
            return token
            

#---------------------------------Вспомогательные-----------------------------------------------------

    
    async def _get_or_create_google_user(self, user_info: dict):
        # ищем по google id
        user = await self.uow.user.get_by_google_id(user_info["sub"])
        if user: return user
        
        # если регистрировался с гугл-почты без привязки
        user = await self.uow.user.get_by_email(user_info["email"])
        if user:
            user.google_id = user_info["sub"]
            if not user.picture_link:
                user.picture_link = user_info.get("picture")
            return user

        # если новый пользователь
        new_user = Users(
            username=user_info["name"],
            email=user_info["email"],
            google_id=user_info["sub"],
            picture_link=user_info.get("picture"),
            auth_provider="google"
        ) 
        
        return await self._create_user_with_stats(new_user)
    
    
    async def _create_user_with_stats(self, user_model: Users):
        await self.uow.user.add(user_model)
        await self.uow.session.flush()

        new_stats = Users_Stats(
                user_id = user_model.id,
                total_xp = 0,
                streak = 0,
                last_activity = None
            )
        await self.uow.user_stats.add(new_stats)    
        
        return user_model


    async def _exchange_code(self, code: str):
        async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "grant_type": "authorization_code",
                        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                        "code": code, 
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                ) as resp:

                    if resp.status != 200:
                        error_text = await resp.json()
                        print(f"Google Auth Error: {error_text}")
                        raise GoogleAuthError()     # нет обработки
                    
                    #print(f"{resp=}")
                    data = await resp.json()
                    return data["access_token"]
    

    async def _get_user_info(self, access_token: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",  
                headers={"Authorization": f"Bearer {access_token}"}  
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.json()
                    print(f"Google Auth Error: {error_text}")
                    raise GoogleAuthError()

                #print(f"{resp=}")
                return await resp.json() 

    