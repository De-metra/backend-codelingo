from app.repositories.base import Repository
from app.models.models import Courses, Users_Courses, Levels
from sqlalchemy import select, update, and_, insert
from sqlalchemy.orm import selectinload


class UserCourseRepository(Repository):
    model = Users_Courses

    async def get_user_courses(self, course_id: int, user_id: int):
        stmt = await self.session.execute(
            select(Users_Courses).where(
                Users_Courses.user_id == user_id, 
                Users_Courses.course_id == course_id
            )
        )
        return stmt.scalars().first()
    
    async def get_or_create(self, course_id: int, user_id: int):
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
    

    async def add(self, users_courses: Users_Courses):
        self.session.add(users_courses)


    async def update_progress(self, course_id: int, user_id: int, progress):
        pass

    async def get_progress(self, user_id: int):
        stmt = await self.session.execute(
            select(Users_Courses.progress)
            .where(Users_Courses.user_id == user_id)
        )
        return stmt.scalar_one_or_none()
