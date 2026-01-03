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
        async with self.uow:
            await self._first_level(user_id)
            await self._complete_course(user_id)
            await self._xp_achivments(user_id)
            await self._streak_achivments(user_id)
            await self.uow.commit()


    async def give_achievment(self, user_id: int, code: str):
        async with self.uow:
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
            await self.uow.commit()

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
        async with self.uow:
            completed_levels = await self.uow.user_levels.get_completed_levels_ids(user_id)
            count = len(completed_levels) 
            if count >= 1:
                await self.give_achievment(user_id=user_id, code=AchievementType.FIRST_LEVEL)

    async def _complete_course(self, user_id: int):
        async with self.uow:
            user_progress = await self.uow.user_course.get_progress(user_id)

            if not user_progress:
                return
            
            if user_progress >= 100:
                await self.give_achievment(user_id=user_id, code=AchievementType.COMPLETE_COURSE)

    async def _xp_achivments(self, user_id: int):
        async with self.uow:
            user_stats = await self.uow.user_stats.get_user_stats(user_id)

            if user_stats.total_xp >= 100:
                await self.give_achievment(user_id=user_id, code=AchievementType.XP_100)

            if user_stats.total_xp >= 500:
                await self.give_achievment(user_id=user_id, code=AchievementType.XP_500) 

    async def _streak_achivments(self, user_id: int):
        async with self.uow:
            user_stats = await self.uow.user_stats.get_user_stats(user_id)

            if user_stats.streak >= 3:
                await self.give_achievment(user_id=user_id, code=AchievementType.STREAK_3)

            if user_stats.streak >= 7:
                await self.give_achievment(user_id=user_id, code=AchievementType.STREAK_7)

                
    async def _tasks_achivments(self, user_id: int):    #нет отслеживания кол-ва решенных задач
        async with self.uow:
            pass

    