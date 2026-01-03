from app.repositories.base import Repository
from app.models.models import Users, Users_Levels
from sqlalchemy import select, update, and_, insert
from sqlalchemy.orm import selectinload
from app.core.security import verify_password, get_password_hash


class UserRepository(Repository):  
    model = Users

    async def get_by_email(self, email: str):
        stmt = await self.session.execute(
            select(Users).where(Users.email == email)
        )
        return stmt.scalar_one_or_none()
    
    async def get_by_id(self, id: int):
        stmt = await self.session.execute(
            select(Users).where(Users.id == id)
        )
        return stmt.scalar_one_or_none()
    
    async def add(self, user_data: Users):
        self.session.add(user_data)
        return user_data
    
    async def update(self, user: Users, data: dict):
        for field, value in data.items():
            setattr(user, field, value)
        return user
    
    async def change_password(self, user: Users, new_pass: str):
        user.hashed_password = get_password_hash(new_pass)

    async def delete(self, user: Users):
        await self.session.delete(user)

    async def get_user_with_stats(self, user_id: int):
        stmt = await self.session.execute(
            select(Users)
            .options(selectinload(Users.stats))    
            .where(Users.id == user_id))
        return stmt.scalar_one_or_none()
    
    async def get_user_with_stats_and_levels(self, user_id: int):
        stmt = await self.session.execute(
            select(Users)
            .options(
                selectinload(Users.levels).selectinload(Users_Levels.level),
                selectinload(Users.stats)
            )
            .where(Users.id == user_id)
        )
        return stmt.scalars().first()


    

