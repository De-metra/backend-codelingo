from abc import ABC, abstractmethod

from app.database.db import async_session_maker
from app.repositories.user_repo import UserRepository
from app.repositories.user_stats_repo import UserStatsRepository
from app.repositories.level_repo import LevelRepository
from app.repositories.user_levels_repo import UserLevelRepository
from app.repositories.course_repo import CourseRepository
from app.repositories.user_courses_repo import UserCourseRepository
from app.repositories.task_repo import TaskRepository
from app.repositories.reset_code_repo import ResetCodeRepository
from app.repositories.achievment_repo import AchievmentRepository
from app.repositories.user_achievment_repo import UserAchievmentRepository

class IUnitOfWork(ABC):
    user: UserRepository
    user_stats: UserStatsRepository
    level: LevelRepository 
    user_levels: UserLevelRepository
    course: CourseRepository
    user_course: UserCourseRepository
    task: TaskRepository
    reset_code: ResetCodeRepository
    achievment: AchievmentRepository
    user_achievments: UserAchievmentRepository

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...

class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()

        self.user = UserRepository(self.session)
        self.user_stats = UserStatsRepository(self.session)
        self.level = LevelRepository(self.session)
        self.user_levels = UserLevelRepository(self.session)
        self.course = CourseRepository(self.session)
        self.user_course = UserCourseRepository(self.session)
        self.task = TaskRepository(self.session)
        self.reset_code = ResetCodeRepository(self.session)
        self.achievment = AchievmentRepository(self.session)
        self.user_achievments = UserAchievmentRepository(self.session)
        return self
    
    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()
        self.session = None

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()