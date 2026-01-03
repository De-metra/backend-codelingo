from app.repositories.base import Repository
from app.models.models import Achievments
from sqlalchemy import select, update, and_, insert
from sqlalchemy.orm import selectinload
from app.core.security import verify_password, get_password_hash


class AchievmentRepository(Repository):  
    model = Achievments

    async def get_by_id(self, id: int):
        stmt = await self.session.execute(
            select(Achievments).where(Achievments.id == id)
        )
        return stmt.scalars().all()
    
    async def get_by_code(self, code: str):
        stmt = await self.session.execute(
            select(Achievments).where(Achievments.code == code)
        )
        return stmt.scalar_one_or_none()
    
    async def get_all(self):
        stmt = await self.session.execute(
            select(Achievments)
        )
        return stmt.scalars().all()