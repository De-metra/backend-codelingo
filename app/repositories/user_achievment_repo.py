from typing import Sequence

from app.repositories.base import SQLAlchemyRepository
from app.models.models import Users_Achievments
from sqlalchemy import select


class UserAchievmentRepository(SQLAlchemyRepository):  
    model = Users_Achievments

    async def get_by_user(self, user_id: int) -> Sequence[Users_Achievments]:
        stmt = await self.session.execute(
            select(Users_Achievments).where(Users_Achievments.user_id == user_id)
        )
        return stmt.scalars().all()
    
    async def add(self, data: Users_Achievments) -> Users_Achievments:
        self.session.add(data)
        return data
