from fastapi import Depends
from app.services.auth_service import AuthService
from app.services.level_service import LevelService
from app.services.course_service import CourseService
from app.services.user_service import UserService
from app.services.task_service import TaskService
from app.services.achievment_service import AchievmentsService
from app.utils.uow import IUnitOfWork, UnitOfWork
from app.executors import base, wandbox_executor


def get_uow():
    return UnitOfWork()

async def get_executor_registry():
    registy = base.ExecutorRegistry()
    registy.register("python", wandbox_executor.WandboxExecutor())
    registy.register("javascript", wandbox_executor.WandboxExecutor())
    return registy

async def get_achievment_service(uow: IUnitOfWork = Depends(get_uow)) -> AchievmentsService:
    return AchievmentsService(uow)

async def get_auth_service(uow: IUnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow)

async def get_level_service(uow: IUnitOfWork = Depends(get_uow)) -> LevelService:
    return LevelService(uow)

async def get_course_service(uow: IUnitOfWork = Depends(get_uow)) -> CourseService:
    return CourseService(uow)

async def get_user_service(uow: IUnitOfWork = Depends(get_uow)) -> UserService:
    return UserService(uow)

async def get_task_service(uow: IUnitOfWork = Depends(get_uow)) -> TaskService:
    return TaskService(uow)

async def get_task_service(
    uow: IUnitOfWork = Depends(get_uow),
    executor_registry = Depends(get_executor_registry)
) -> TaskService:
    return TaskService(uow, executor_registry)

