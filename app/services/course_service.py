from app.models.models import Users_Courses
from app.schemas.course import CourseReturn, CourseWithLevels, LevelBase
from app.schemas.schemas import MessageReturn
from app.utils.uow import IUnitOfWork
from app.core.exception import NotFoundError, AlreadyExistsError


class CourseService():
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_all_courses(self) -> list[CourseReturn]:
        async with self.uow:
            courses = await self.uow.course.find_all()
            return [
                CourseReturn.model_validate(course)
                for course in courses
            ]
        
    async def get_course_by_id(self, course_id: int) -> CourseReturn:
        async with self.uow:
            course = await self.uow.course.get_by_id(course_id)

            if not course:
                raise NotFoundError()
            
            return CourseReturn.model_validate(course)
        
    async def get_course_with_levels(self, course_id: int) -> CourseWithLevels:
        async with self.uow:
            course = await self.uow.course.get_with_levels(course_id)

            if not course:
                raise NotFoundError()

            return CourseWithLevels(
                id=course.id,
                title=course.title,
                description=course.description,
                icon=course.icon,
                levels=[
                        LevelBase(
                            id=level.id,
                            title=level.title,
                            xp=level.xp
                        )
                    for level in course.levels
                ] 
            )
        
    
    async def start_course(self, course_id: int, user_id: int) -> MessageReturn:
        async with self.uow:
            course_name = await self.uow.course.get_by_id(course_id)

            if not course_name:
                raise NotFoundError()

            course = await self.uow.user_course.find_one_or_none(course_id=course_id, user_id=user_id)

            if course:
                raise AlreadyExistsError()
            
            new_user_course = Users_Courses(
                user_id=user_id,
                course_id=course_id,
                progress=0
            )

            await self.uow.user_course.add(new_user_course)
            await self.uow.commit()

            return MessageReturn(message=f"Курс '{course_name}' начат!")
            


                
