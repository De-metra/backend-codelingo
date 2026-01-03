from app.repositories.base import Repository
from app.models.models import Tasks, Level_Tasks, Tasks_Options, Tasks_Gap, Tests
from sqlalchemy import select, update, and_, insert
from sqlalchemy.orm import selectinload
from app.core.security import verify_password, get_password_hash


class TaskRepository(Repository):  
    model = Tasks

    async def get_by_id(self, id: int):
        stmt = await self.session.execute(
            select(Tasks)
            .where(Tasks.id == id)
            .options(selectinload(Tasks.type_rel))
        )
        return stmt.scalar_one_or_none()
    
    async def get_by_level(self, level_id: int):
        stmt = await self.session.execute(
            select(Tasks)
            .join(Level_Tasks, Level_Tasks.task_id == Tasks.id)
            .where(Level_Tasks.level_id == level_id)
            .options(
                selectinload(Tasks.type_rel),      # Тип задачи
                selectinload(Tasks.options),        # Задача: выбор ответа из списка
                selectinload(Tasks.gaps)       # Задача: пропуски
            )
        )
        return stmt.scalars().all()
    
    async def get_task_hint(self, task_id: int):
        stmt = await self.session.execute(
            select(Tasks.hint)
            .where(Tasks.id == task_id))
        return stmt.scalar_one_or_none()
    
    async def get_task_options_by_id(self, task_id: int):
        stmt = await self.session.execute(
            select(Tasks_Options)
            .where(Tasks_Options.task_id == task_id))
        return stmt.scalars().all()
    
    async def get_task_gaps_by_id(self, task_id: int):
        stmt = await self.session.execute(
            select(Tasks_Gap)
            .where(Tasks_Gap.task_id == task_id))
        return stmt.scalars().all()
    
    async def get_task_tests_by_id(self, task_id: int):
        stmt = await self.session.execute(
             select(Tests)
             .where(Tests.task_id == task_id))
        return stmt.scalars().all()
