from typing import Optional

from sqlalchemy import select, and_

from app.repositories.base import SQLAlchemyRepository
from app.models.models import Users_Levels



class UserLevelRepository(SQLAlchemyRepository):
    model = Users_Levels

    async def get_or_create(self, level_id: int, user_id: int) -> Users_Levels:
        """Создание записи о прогрессе пользователя по уровню"""
        stmt = await self.session.execute(
            select(Users_Levels).where(
                Users_Levels.user_id == user_id,
                Users_Levels.level_id == level_id
            )
        )
        user_level = stmt.scalar_one_or_none()

        if not user_level:
            user_level = Users_Levels(
                user_id=user_id,
                level_id=level_id,
                is_complete=False
            )
            self.session.add(user_level)

        return user_level


    async def add(self, data: Users_Levels) -> Users_Levels:
        self.session.add(data)
        return data 

    async def get_completed_levels_ids(self, user_id: int) -> set[int]:
        """Получение всех завершенных уровней пользователя (id)"""
        stmt = await self.session.execute(
            select(Users_Levels.level_id)
            .where(
                and_(
                    Users_Levels.user_id == user_id,
                    Users_Levels.is_complete == True
                )
            )
        )
        completed_ids = {row[0] for row in stmt.all()}
        return completed_ids
    
    async def get_completed_ids_by_course(self, user_id: int, level_ids: list[int]) -> list[int]:
        """Получение завершенных уровней пользователя по списку id уровней"""
        stmt = await self.session.execute(
            select(Users_Levels.level_id)
            .where(
                and_(
                    Users_Levels.user_id == user_id,
                    Users_Levels.is_complete == True,
                    Users_Levels.level_id.in_(level_ids)
                )
            )
        )
        return [row[0] for row in stmt.all()]        

    async def is_completed(self, level_id: int, user_id: int) -> Optional[bool]:
        """Получение статуса уровня у пользователя (True/False)"""
        stmt = await self.session.execute(
            select(Users_Levels.is_complete).where(
                and_(
                    Users_Levels.user_id == user_id,
                    Users_Levels.level_id == level_id
                )
            ))
        return stmt.scalar_one_or_none()

        