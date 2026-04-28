from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.repositories.base import SQLAlchemyRepository
from app.models.models import Courses


class CourseRepository(SQLAlchemyRepository):
    model = Courses
    
    async def get_with_levels(self, course_id: int) -> Optional[Courses]:
        '''Получение курса со всеми уровнями'''
        stmt = await self.session.execute(
            select(Courses)
            .options(selectinload(Courses.levels))
            .where(Courses.id == course_id)
            )
        return stmt.scalar_one_or_none()
    
    async def add(self, data: Courses) -> Courses:
        self.session.add(data)
        return data
    
    