from datetime import datetime
from fastapi import HTTPException

from app.core.security import verify_password, get_password_hash, create_jwt_token
from app.models.models import Users, Users_Courses, PasswordResetCode
from app.schemas.course import CourseReturn
from app.schemas.email import CodeUpdateRequest
from app.utils.uow import IUnitOfWork
from app.core.exception import *


class CourseService():
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_all_courses(self):
        async with self.uow:
            courses = await self.uow.course.get_all_courses()
            return [
                CourseReturn.model_validate(course)
                for course in courses
            ]
        
    async def get_course_by_id(self, course_id: int):
        async with self.uow:
            course = await self.uow.course.get_by_id(course_id)

            if not course:
                raise NotFoundError()
            
            return CourseReturn.model_validate(course)
        
    async def get_course_with_levels(self, course_id: int):
        async with self.uow:
            course = await self.uow.course.get_with_levels(course_id)

            if not course:
                raise NotFoundError()

            return {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "levels": [ 
                    {
                        "id": level.id,
                        "title": level.title,
                        "xp": level.xp
                    }
                    for level in course.levels
                ] 
            }
        
    
    async def start_course(self, course_id: int, user_id: int):
        async with self.uow:
            course_name = await self.uow.course.get_by_id(course_id)

            if not course_name:
                raise NotFoundError()

            course = await self.uow.user_course.get_user_courses(course_id=course_id, user_id=user_id)

            if course:
                raise AlreadyExistsError()
            
            new_user_course = Users_Courses(
                user_id=user_id,
                course_id=course_id,
                progress=0
            )

            await self.uow.user_stats.add(new_user_course)
            await self.uow.commit()

            return {"message": f"Курс '{course_name}' начат!"}
            


                
