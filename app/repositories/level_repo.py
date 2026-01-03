from app.repositories.base import Repository
from app.models.models import Levels, Users_Levels, Theories
from sqlalchemy import select, update, and_, insert

class LevelRepository(Repository):
    model = Levels

    async def get_by_course(self, course_id: int):
        '''Получение уровней из курса по id курса'''
        stmt = await self.session.execute(select(Levels).where(Levels.course_id == course_id))
        return stmt.scalars().all()
        
    async def get_level_ids_by_course(self, course_id : int):
        '''Получение всех ids уровня из конкретного курса'''
        stmt = await self.session.execute(
            select(Levels.id)
            .where(Levels.course_id == course_id))
        return [row[0] for row in stmt.all()]

    async def get_by_id(self, id: int):
        '''Получение уровня по id'''
        stmt = await self.session.execute(select(Levels).where(Levels.id == id))
        return stmt.scalar_one()
       

    async def get_level_theory(self, level_id: int):
        """Получение теории конкретного уровня"""
        stmt = await self.session.execute(select(Theories)
                                            .join(Levels, Levels.theory_id == Theories.id)
                                            .where(Levels.id == level_id))
        return stmt.scalar_one_or_none()
        

    async def get_level_xp(self, level_id: int):
        """Получение количества xp за уровень"""
        stmt = await self.session.execute(select(Levels.xp).where(Levels.id == level_id))
        return stmt.scalar_one_or_none()
    
       

    

    