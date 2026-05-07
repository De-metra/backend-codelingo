from datetime import datetime, timedelta
from typing import Optional

from app.models.models import Users_Stats, Users_Achievments, Achievments
from app.schemas.achiev import AchievmentReturn
from app.schemas.level import LevelBaseReturn, LevelStatusReturn, TheoryReturn, XpReturn, LevelCompleteReturn
from app.services.achievment_service import AchievementType
from app.utils.uow import IUnitOfWork
from app.core.exception import (
    AchievmentNotFoundError, LevelAlreadyCompletedError, NotFoundError,
    TheoryNotFoundError, XpNotFoundError, UserNotFoundError,
    LevelNotFoundError
)


class LevelService():
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_levels_with_progress(self, course_id: int, user_id: int) -> list[LevelStatusReturn]:
        async with self.uow:
            levels = await self.uow.level.get_by_course(course_id)
            
            if not levels:
                raise LevelNotFoundError()

            completed_ids = await self.uow.user_levels.get_completed_levels_ids(user_id)

            return [
                LevelStatusReturn(
                    id=level.id,
                    title=level.title,
                    num_in_order=level.num_in_order,
                    is_complete=level.id in completed_ids
                )
                for level in levels
            ]
        
    async def get_level_info(self, level_id: int, user_id: int) -> LevelBaseReturn:
        async with self.uow:
            level = await self.uow.level.get_by_id(level_id)

            if not level:
                raise NotFoundError()
            
            is_complited = await self.uow.user_levels.is_completed(level_id, user_id)

            return LevelBaseReturn(
                id=level_id,
                title=level.title,
                description=level.description or None,
                num_in_order=level.num_in_order,
                is_complete=is_complited or False,
            ) 

    async def get_level_theory(self, level_id: int) -> TheoryReturn:
        async with self.uow:
            theory = await self.uow.level.get_level_theory(level_id)

            if not theory:
                raise TheoryNotFoundError()

            return TheoryReturn(
                theory=theory.description
            )   
        
    async def get_level_xp(self, level_id: int) -> XpReturn:
        async with self.uow:
            xp = await self.uow.level.get_level_xp(level_id)

            if not xp:
                raise XpNotFoundError()

            return XpReturn(xp=xp)
        
    async def complete_level(self, level_id: int, user_id: int) -> LevelCompleteReturn:
        async with self.uow:
            user_with_info = await self.uow.user.get_user_with_stats_and_levels(user_id)

            if not user_with_info:
                raise UserNotFoundError()
            
            level = await self.uow.level.get_by_id(level_id)

            if not level:
                raise NotFoundError()    
            
            user_level = await self.uow.user_levels.get_or_create(level_id=level_id, user_id=user_id)
            stats = await self.uow.user_stats.get_or_create(user_id)

            is_first_time = not user_level.is_complete
            xp_to_add = 0

            if is_first_time:
                user_level.is_complete = True
                stats.total_xp += level.xp
                xp_to_add = level.xp
            
            new_stats = self._update_user_streak(stats)

            progress_percent = await self._calculate_course_progress(user_id=user_id, course_id=level.course_id)

            new_achievments = await self._check_after_level_complete(user_id)

            await self.uow.commit()

            return LevelCompleteReturn(
                message=f"Урок id:{level_id} завершён",
                xp_added=level.xp,
                total_xp=new_stats.total_xp,
                streak=new_stats.streak, 
                course_progress=progress_percent,
                new_achievments=new_achievments or None
            )
    

    def _update_user_streak(self, stats: Users_Stats) -> Users_Stats:
        now = datetime.now().date()
        last_activity = stats.last_activity.date() if stats.last_activity else None

        if last_activity == now - timedelta(days=1):
            stats.streak += 1
        elif last_activity == now:
            pass
        else:
            stats.streak = 1

        stats.last_activity = datetime.now()

        return stats
    

    async def _calculate_course_progress(self, user_id, course_id) -> float:
        level_ids = await self.uow.level.get_level_ids_by_course(course_id)

        if not level_ids:
            return 0.0
        completed_ids = await self.uow.user_levels.get_completed_ids_by_course(user_id=user_id, level_ids=level_ids)
        progress_percent = round(len(completed_ids) / len(level_ids) * 100, 2)

        users_course = await self.uow.user_course.get_or_create(course_id=course_id, user_id=user_id)

        users_course.progress = progress_percent
        if progress_percent >= 100:
            users_course.is_complete = True

        return progress_percent

    async def _check_after_level_complete(self, user_id: int) -> list:
        earned = []
        
        for checker in (
            self._first_level,
            self._complete_course,
            self._xp_achivments,
            self._streak_achivments
        ):
            res = await checker(user_id)
            if res:
                earned.append(res)

        return [
            AchievmentReturn(id=a.id, title=a.title, icon=a.icon)
            for a in earned
        ]
        
    async def _first_level(self, user_id: int):
        completed_levels = await self.uow.user_levels.get_completed_levels_ids(user_id)
        
        if len(completed_levels) == 1:
            return await self._give_achievment(user_id=user_id, code=AchievementType.FIRST_LEVEL)
        
        return None

    async def _complete_course(self, user_id: int):
        user_progress = await self.uow.user_course.any_course_completed(user_id)
        
        if user_progress:
            return await self._give_achievment(user_id=user_id, code=AchievementType.COMPLETE_COURSE)
        
        return None

    async def _xp_achivments(self, user_id: int):
        user_stats = await self.uow.user_stats.find_one_or_none(user_id=user_id)

        if not user_stats:
            return None

        if 100 <= user_stats.total_xp < 500:
            return await self._give_achievment(user_id=user_id, code=AchievementType.XP_100)

        if user_stats.total_xp >= 500:
            return await self._give_achievment(user_id=user_id, code=AchievementType.XP_500) 
        
        return None

    async def _streak_achivments(self, user_id: int):
        user_stats = await self.uow.user_stats.find_one_or_none(user_id=user_id)

        if not user_stats:
            return None

        if 3 <= user_stats.streak < 7:
            return await self._give_achievment(user_id=user_id, code=AchievementType.STREAK_3)

        if user_stats.streak >= 7:
            return await self._give_achievment(user_id=user_id, code=AchievementType.STREAK_7)
        
        return None
    
    async def _give_achievment(self, user_id: int, code: str) -> Optional[Achievments]:
        achievment = await self.uow.achievment.find_one_or_none(code=code)
        if not achievment:
            raise AchievmentNotFoundError()
        
        already = await self.uow.user_achievments.find_one_or_none(user_id=user_id, achievment_id=achievment.id)
        if already: 
            return None
        
        achievment_to_add = Users_Achievments(
            user_id = user_id,
            achievment_id = achievment.id
        )
        await self.uow.user_achievments.add(achievment_to_add)

        return achievment
        