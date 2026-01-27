from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.database.db import async_session_maker
from app.core.cloudinary import upload_image
from app.schemas.user import UserRegister, UserReturn, Stats, UserChangeProfile, UserUpdatedInfo
from app.services.base import BaseService
from app.models.models import Users, Users_Stats
from app.utils.uow import IUnitOfWork
from app.core.exception import *

class UserService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        self.uow : IUnitOfWork = uow

    async def add_user(self, user: UserRegister):
        user_dict: dict = user.model_dump()

        async with self.uow:     # вход в контекст (если выбьет с ошибкой, то изменения откатятся) 
            user_from_db = await self.uow.user.add_one(user_dict)
            user_to_return = UserReturn.model_validate(user_from_db)

            await self.uow.commit()

            return user_to_return
        

    async def get_users(self):
        async with self.uow:
            users = await self.uow.user.find_all()
            return [UserReturn.model_validate(user) for user in users]


    async def get_user_stats(self, user_id: int):
        async with self.uow:
            stats = await self.uow.user_stats.get_user_stats(user_id=user_id)

            if not stats:
                raise StatsNotFoundError()
            
            return Stats.model_validate(stats)
        
    async def get_user_with_stats(self, user_id: int):
        async with self.uow:
            user = await self.uow.user.get_user_with_stats(user_id=user_id)

            if not user:
                raise UserNotFoundError()
            
            if not user.stats:
                stats = Users_Stats(user_id=user.id, total_xp=0, streak=0)
                await self.uow.user_stats.add(stats)
                await self.uow.commit()
            else:
                stats = user.stats

            return UserReturn(
                id=user.id,
                username=user.username,
                email=user.email,
                picture_link=user.picture_link,
                xp=stats.total_xp,
                streak=stats.streak
            )
        
    async def change_avatar(self, user_id: int, file: UploadFile):
        async with self.uow:
            user = await self.uow.user.get_by_id(user_id)

            if not user:
                raise UserNotFoundError()

            avatar_url = upload_image(file=file.file, user_id=user_id) 

            user.picture_link = avatar_url
            await self.uow.commit()

            return {"avatar_url": avatar_url}
        
    
    async def change_me(self, user_id: int, username: str | None, file: UploadFile | None):
        async with self.uow:
            user = await self.uow.user.get_by_id(user_id)

            if not user:
                raise UserNotFoundError()
            
            update_data = {}

            if username:
                update_data["username"] = username

            if file:
                picture_link = upload_image(file=file.file, user_id=user_id) 
                update_data["picture_link"] = picture_link   

            if not update_data:
                raise NoneDataToUpdate()

            await self.uow.user.update(user=user, data=update_data)
            await self.uow.commit()

            return UserUpdatedInfo(
                id=user_id,
                username=user.username,
                email=user.email, 
                picture_link=user.picture_link
            )

        
    """ async def change_me(self, user_id: int, data: UserChangeProfile):
        async with self.uow:
            user = await self.uow.user.get_by_id(user_id)

            if not user:
                raise UserNotFoundError()
            
            update_data = data.model_dump(exclude_unset=True)

            if not update_data:
                raise NoneDataToUpdate()

            await self.uow.user.update(user=user, data=update_data)
            await self.uow.commit()

            return UserUpdatedInfo(
                id=user_id,
                username=user.username,
                email=user.email, 
                picture_link=user.picture_link
            ) """
        
    async def soft_delete_account(self, user_id: int):
        async with self.uow:
            user = await self.uow.user.get_by_id(user_id)

            if not user:
                raise UserNotFoundError()
            
            user.is_active = False
            user.deleted_at = datetime.now()

            await self.uow.commit()

            return {"message": f"Аккаунт {user.username} успешно удалён"}
        



#model_config = ConfigDict(from_attributes=True)