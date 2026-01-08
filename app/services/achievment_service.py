from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.database.db import async_session_maker
from app.schemas.user import UserRegister, UserReturn, Stats, UserChangeProfile, UserUpdatedInfo
from app.services.base import BaseService
from app.models.models import Users, Users_Stats, Users_Achievments, Achievments
from app.utils.uow import IUnitOfWork
from app.core.exception import *


class AchievementType(str, Enum):
    FIRST_LEVEL = "FIRST_LEVEL"
    COMPLETE_COURSE = "COMPLETE_COURSE"
    XP_100 = "XP_100"
    XP_500 = "XP_500"
    STREAK_3 = "STREAK_3"
    STREAK_7 = "STREAK_7"
    TASKS_5 = "TASKS_5"     #нет отслеживания кол-ва решенных задач
    TASKS_15 = "TASKS_15"       #нет отслеживания кол-ва решенных задач
    PERFECT_LEVEL = "PERFECT_LEVEL"     #нет отслеживания кол-ва ошибок

class AchievmentsService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        self.uow : IUnitOfWork = uow

    async def check_after_level_complete(self, user_id: int):
        earned = []
        async with self.uow:
            for checker in (
                self._first_level,
                self._complete_course,
                self._xp_achivments,
                self._streak_achivments
            ):
                res = await checker(user_id)
                if res:
                    earned.append(res)
            
            await self.uow.commit()

            return {
                "earned": [
                    {"id": a.id, "title": a.title, "icon": a.icon}
                    for a in earned
                ]
            }

    async def give_achievment(self, user_id: int, code: str):
        achievment = await self.uow.achievment.get_by_code(code)
        if not achievment:
            raise AchievmentNotFoundError()
        
        already = await self.uow.user_achievments.has_achievment(user_id=user_id, achievment_id=achievment.id)
        if already: 
            return None
        
        achievment_to_add = Users_Achievments(
            user_id = user_id,
            achievment_id = achievment.id
        )
        await self.uow.user_achievments.add(achievment_to_add)

        return achievment
            

    async def get_all_with_status(self, user_id: int):
        async with self.uow:
            user_achiv = await self.uow.user_achievments.get_by_user(user_id)

            all_achiv = await self.uow.achievment.get_all()

            received_ids = {ua.achievment_id for ua in user_achiv}

            return [
                {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "icon": a.icon,
                    "received": a.id in received_ids
                }
                for a in all_achiv
            ]
        

    async def _first_level(self, user_id: int):
        completed_levels = await self.uow.user_levels.get_completed_levels_ids(user_id)
        
        if len(completed_levels) == 1:
            return await self.give_achievment(user_id=user_id, code=AchievementType.FIRST_LEVEL)
        
        return None

    async def _complete_course(self, user_id: int):
        user_progress = await self.uow.user_course.get_progress(user_id)
        
        if user_progress and user_progress >= 100:
            return await self.give_achievment(user_id=user_id, code=AchievementType.COMPLETE_COURSE)
        
        return None

    async def _xp_achivments(self, user_id: int):
        user_stats = await self.uow.user_stats.get_user_stats(user_id)

        if 100 <= user_stats.total_xp < 500:
            return await self.give_achievment(user_id=user_id, code=AchievementType.XP_100)

        if user_stats.total_xp >= 500:
            return await self.give_achievment(user_id=user_id, code=AchievementType.XP_500) 
        
        return None

    async def _streak_achivments(self, user_id: int):
        user_stats = await self.uow.user_stats.get_user_stats(user_id)

        if 3 <= user_stats.streak < 7:
            return await self.give_achievment(user_id=user_id, code=AchievementType.STREAK_3)

        if user_stats.streak >= 7:
            return await self.give_achievment(user_id=user_id, code=AchievementType.STREAK_7)
        
        return None

                
    async def _tasks_achivments(self, user_id: int):    #нет отслеживания кол-ва решенных задач
        async with self.uow:
            pass

    