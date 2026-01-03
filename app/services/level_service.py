from datetime import datetime, timedelta
from fastapi import HTTPException

from app.core.security import verify_password, get_password_hash, create_jwt_token
from app.models.models import Users, Users_Stats, PasswordResetCode, Users_Levels, Users_Courses
from app.schemas.level import LevelBaseReturn, LevelStatusReturn, LevelReturn, TheoryReturn
from app.schemas.email import CodeUpdateRequest
from app.utils.uow import IUnitOfWork
from app.services.achievment_service import AchievmentsService
from app.core.exception import *


class LevelService():
    def __init__(self, uow: IUnitOfWork, achivment_service: AchievmentsService):
        self.uow = uow
        self.achivment_service = AchievmentsService

    async def get_levels_with_progress(self, course_id: int, user_id: int):
        async with self.uow:
            levels = await self.uow.level.get_by_course(course_id)
            
            if not levels:
                raise LevelNotFoundError()

            completed_ids = await self.uow.user_levels.get_completed_levels_ids(user_id)

            return [
                LevelStatusReturn(
                    id=level.id,
                    title=level.title,
                    is_complete=level.id in completed_ids
                )
                for level in levels
            ]
        
    async def get_level_info(self, level_id: int, user_id: int):
        async with self.uow:
            level = await self.uow.level.get_by_id(level_id)

            if not level:
                raise LevelNotFoundError()
            
            is_complited = await self.uow.user_levels.is_completed(level_id, user_id)

            return LevelBaseReturn(
                id=level_id,
                title=level.title,
                description=level.description or None,
                is_complete=is_complited,
            ) 

    async def get_level_theory(self, level_id: int):
        async with self.uow:
            theory = await self.uow.level.get_level_theory(level_id)
            print(theory)

            if not theory:
                raise TheoryNotFoundError()

            return TheoryReturn(
                theory=theory.description
            )   
        
    async def get_level_xp(self, level_id: int):
        async with self.uow:
            xp = await self.uow.level.get_level_xp(level_id)

            if not xp:
                raise XpNotFoundError()

            return {"xp": xp}
        
    async def complete_level(self, level_id: int, user_id: int):
        async with self.uow:
            user_with_info = await self.uow.user.get_user_with_stats_and_levels(user_id)

            if not user_with_info:
                raise UserNotFoundError()
            
            level = await self.uow.level.get_by_id(level_id)

            if not level:
                raise LevelNotFoundError()    
            
            user_level = await self.uow.user_levels.get_or_create(level_id=level_id, user_id=user_id)

            if user_level.is_complete:
                 raise LevelAlreadyCompletedError()
            
            user_level.is_complete = True
            
            stats = await self.uow.user_stats.get_or_create(user_id)
            stats.total_xp += level.xp

            #streak
            now = datetime.now().date()
            last_activity = stats.last_activity.date() if stats.last_activity else None

            if last_activity == now - timedelta(days=1):
                stats.streak += 1
            elif last_activity == now:
                pass
            else:
                stats.streak = 1

            stats.last_activity = datetime.now()

            #прогресс курса
            course_id = level.course_id
            level_ids = await self.uow.level.get_level_ids_by_course(course_id)
            completed_ids = await self.uow.user_levels.get_completed_ids_by_course(user_id=user_id, level_ids=level_ids)
            progress_percent = round(len(completed_ids) / len(level_ids) * 100, 2)

            users_course = await self.uow.user_course.get_or_create(course_id=course_id, user_id=user_id)

            users_course.progress = progress_percent
            if progress_percent >= 100:
                users_course.is_complete = True

            await self.uow.commit()
            
            #проверка на ачивки
            await self.achivment_service.check_after_level_complete(user_id=user_id)

            return {
                "message": f"Урок id:{level_id} завершён",
                "xp_added": level.xp,
                "total_xp": stats.total_xp,
                "streak": stats.streak,
                "course_progress": progress_percent
            }