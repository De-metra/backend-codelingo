from app.repositories.base import Repository
from app.models.models import Users_Achievments
from sqlalchemy import select, update, and_, insert
from sqlalchemy.orm import selectinload
from app.core.security import verify_password, get_password_hash


class UserAchievmentRepository(Repository):  
    model = Users_Achievments

    async def get_by_user(self, user_id: int):
        stmt = await self.session.execute(
            select(Users_Achievments).where(Users_Achievments.user_id == user_id)
        )
        return stmt.scalars().all()
    
    async def add(self, data: Users_Achievments):
        self.session.add(data)

    async def has_achievment(self, user_id: int, achievment_id: int):
        stmt = await self.session.execute(
            select(Users_Achievments)
            .where(
                Users_Achievments.user_id == user_id,
                Users_Achievments.achievment_id == achievment_id
            ))
        return stmt.scalar_one_or_none()