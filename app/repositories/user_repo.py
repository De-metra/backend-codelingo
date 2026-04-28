from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.repositories.base import SQLAlchemyRepository
from app.models.models import Users, Users_Levels


class UserRepository(SQLAlchemyRepository):  
    model = Users

    async def get_by_email(self, email: str) -> Optional[Users]:
        stmt = await self.session.execute(
            select(Users).where(
                Users.email == email,
                Users.is_active == True
            )
        )
        return stmt.scalar_one_or_none()
    
    async def get_by_id(self, id: int) -> Optional[Users]:
        stmt = await self.session.execute(
            select(Users).where(
                Users.google_id == id,
                Users.is_active == True
            )
        )
        return stmt.scalar_one_or_none()
    
    async def get_by_google_id(self, google_id: str):
        stmt = await self.session.execute(
            select(Users).where(
                Users.google_id == google_id,
                Users.is_active == True
            )
        )
        return stmt.scalar_one_or_none()
    
    async def add(self, user_data: Users) -> Users:
        self.session.add(user_data)
        return user_data

    async def get_user_with_stats(self, user_id: int) -> Optional[Users]:
        stmt = await self.session.execute(
            select(Users)
            .options(selectinload(Users.stats))    
            .where(Users.id == user_id))
        return stmt.scalar_one_or_none()
    
    async def get_user_with_stats_and_levels(self, user_id: int) -> Optional[Users]:
        stmt = await self.session.execute(
            select(Users)
            .options(
                selectinload(Users.levels).selectinload(Users_Levels.level),
                selectinload(Users.stats)
            )
            .where(Users.id == user_id)
        )
        return stmt.scalar_one_or_none()


    

