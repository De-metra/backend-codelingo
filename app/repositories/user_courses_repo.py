from typing import Optional, Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload

from app.repositories.base import SQLAlchemyRepository
from app.models.models import Users_Courses


class UserCourseRepository(SQLAlchemyRepository):
    model = Users_Courses
    
    async def get_or_create(self, course_id: int, user_id: int) -> Users_Courses:
        stmt = await self.session.execute(
            select(Users_Courses).where(
                Users_Courses.user_id == user_id, 
                Users_Courses.course_id == course_id
            )
        )
        user_course = stmt.scalars().first()

        if not user_course:
            user_course = Users_Courses(
                user_id=user_id,
                course_id=course_id,
                progress=0,
                is_complete=False
            )
            self.session.add(user_course)

        return user_course

    async def add(self, data: Users_Courses) -> Users_Courses:
        self.session.add(data)
        return data

    async def any_course_completed(self, user_id: int) -> bool:
        stmt = await self.session.execute(
            select(Users_Courses)
            .where(Users_Courses.user_id == user_id, 
                   Users_Courses.progress >= 100)
        )
        return stmt.scalar_one_or_none() is not None
    
    async def get_last_active_course(self, user_id: int) -> Optional[Users_Courses]:
        stmt = await self.session.execute(
            select(Users_Courses)
            .where(Users_Courses.user_id == user_id)
            .options(selectinload(Users_Courses.course))
            .order_by(desc(Users_Courses.updated_at))
            .limit(1)
        )
        return stmt.scalar_one_or_none()

    async def get_progress_of_courses(self, user_id: int) -> Sequence[Users_Courses]:
        stmt = await self.session.execute(
            select(Users_Courses)
            .where(Users_Courses.user_id == user_id)
            .options(selectinload(Users_Courses.course))
        )
        return stmt.scalars().all()
