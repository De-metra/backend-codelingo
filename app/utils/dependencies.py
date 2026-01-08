from fastapi import Depends
from app.services.auth_service import AuthService
from app.services.level_service import LevelService
from app.services.course_service import CourseService
from app.services.user_service import UserService
from app.services.task_service import TaskService
from app.services.achievment_service import AchievmentsService
from app.utils.uow import IUnitOfWork, UnitOfWork
from app.executors.python_executor import PythonExexcutor


async def get_python_executor():
    return PythonExexcutor(timeout=2)

async def get_achievment_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> AchievmentsService:
    return AchievmentsService(uow)

async def get_auth_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> AuthService:
    return AuthService(uow)

async def get_level_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> LevelService:
    return LevelService(uow)

async def get_course_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> CourseService:
    return CourseService(uow)

async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)

async def get_task_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> TaskService:
    return TaskService(uow)

async def get_task_service(
    uow: IUnitOfWork = Depends(UnitOfWork),
    executor: PythonExexcutor = Depends(get_python_executor)
) -> TaskService:
    return TaskService(uow, executor)

