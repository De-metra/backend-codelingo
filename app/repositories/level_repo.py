from typing import Sequence, Optional

from app.repositories.base import SQLAlchemyRepository
from app.models.models import Levels, Theories
from sqlalchemy import select


class LevelRepository(SQLAlchemyRepository):
    model = Levels

    async def get_by_course(self, course_id: int) -> Sequence[Levels]:
        '''Получение уровней из курса по id курса и их сортировка по num_in_order'''
        stmt = await self.session.execute(
            select(Levels)
            .where(Levels.course_id == course_id)
            .order_by(Levels.num_in_order)
        )
        return stmt.scalars().all()
        
    async def get_level_ids_by_course(self, course_id : int) -> Sequence[int]:
        '''Получение всех ids уровня из конкретного курса'''
        stmt = await self.session.execute(
            select(Levels.id)
            .where(Levels.course_id == course_id)
            .order_by(Levels.num_in_order)
        )
        return [row[0] for row in stmt.all()]       

    async def get_level_theory(self, level_id: int) -> Optional[Theories]:
        """Получение теории конкретного уровня"""
        stmt = await self.session.execute(
            select(Theories)
            .join(Levels, Levels.theory_id == Theories.id)
            .where(Levels.id == level_id)
        )
        return stmt.scalar_one_or_none()

    async def get_level_xp(self, level_id: int) -> Optional[int]:
        """Получение количества xp за уровень"""
        stmt = await self.session.execute(select(Levels.xp).where(Levels.id == level_id))
        return stmt.scalar_one_or_none()
    
    async def add(self, data: Levels) -> Levels:
        self.session.add(data)
        return data
    