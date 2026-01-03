from app.repositories.base import Repository
from app.models.models import Courses, Users_Courses, Levels
from sqlalchemy import select, update, and_, insert
from sqlalchemy.orm import selectinload


class CourseRepository(Repository):
    model = Courses

    async def get_all_courses(self):
        '''Получение всех курсов'''
        stmt = await self.session.execute(select(Courses))
        return stmt.scalars().all()
    
    async def get_by_id(self, id: int):
        '''Получение курса по id'''
        stmt = await self.session.execute(select(Courses).where(Courses.id == id))
        return stmt.scalar_one_or_none()
    
    async def get_with_levels(self, course_id: int):
        '''Получение курса со всеми уровнями'''
        stmt = await self.session.execute(
            select(Courses)
            .options(selectinload(Courses.levels))
            .where(Courses.id == course_id)
            )
        return stmt.scalars().first()
    
    