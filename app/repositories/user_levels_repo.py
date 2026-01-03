from app.repositories.base import Repository
from app.models.models import Users_Levels
from sqlalchemy import select, update, and_, insert
from app.core.security import verify_password, get_password_hash


class UserLevelRepository(Repository):
    model = Users_Levels

    async def get_or_create(self, level_id: int, user_id: int):
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


    async def add(self, data: Users_Levels):
        self.session.add(data)



    async def get_completed_levels_ids(self, user_id: int):
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
    
    async def get_completed_ids_by_course(self, user_id: int, level_ids: list[int]):
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
    
    async def get_user_level(self, user_id: int, level_id: int):
        stmt = await self.session.execute(
            select(Users_Levels).where(
                Users_Levels.user_id == user_id,
                Users_Levels.level_id == level_id
            )
        )
        return stmt.scalar_one_or_none()
        

    async def is_completed(self, level_id: int, user_id: int):
        """Получение статуса уровня у пользователя (True/False)"""
        stmt = await self.session.execute(
            select(Users_Levels.is_complete).where(
                and_(
                    Users_Levels.user_id == user_id,
                    Users_Levels.level_id == level_id
                )
            ))
        return stmt.scalar_one_or_none()
        

    async def mark_level_complete(self, level_id: int, user_id: int):
        """Отметка уровня пройденным"""
        is_completed = await self.is_completed(level_id, user_id)

        if is_completed:
            raise ValueError("Уровень уже завершён")
        else:
            user_level = Users_Levels(
            user_id = user_id,
            level_id = level_id,
            is_complete = True
        )
        self.session.add(user_level)


        stmt = await self.session.execute(
            select(Users_Levels).where(
                and_(
                    Users_Levels.user_id == user_id,
                    Users_Levels.level_id == level_id
                )
            ))
        return stmt.scalar_one_or_none()

        