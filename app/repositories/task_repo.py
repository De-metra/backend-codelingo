from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.repositories.base import SQLAlchemyRepository
from app.models.models import Tasks, Level_Tasks, Tasks_Options, Tasks_Gap, Tests, Tasks_Code


class TaskRepository(SQLAlchemyRepository):  
    model = Tasks

    async def get_task_by_id(self, id: int) -> Optional[Tasks]:
        stmt = await self.session.execute(
            select(Tasks)
            .where(Tasks.id == id)
            .options(
                selectinload(Tasks.type_rel),
                selectinload(Tasks.tasks_link),
            )
        )
        return stmt.scalar_one_or_none()
    
    async def get_by_level(self, level_id: int):
        stmt = await self.session.execute(
            select(Tasks, Level_Tasks.num_in_order)
            .join(Level_Tasks, Level_Tasks.task_id == Tasks.id)
            .where(Level_Tasks.level_id == level_id)
            .options(
                selectinload(Tasks.type_rel),      # Тип задачи
                selectinload(Tasks.options),        # Задача: выбор ответа из списка
                selectinload(Tasks.gaps),       # Задача: пропуски
                selectinload(Tasks.code).selectinload(Tasks_Code.language)     
            )
            .order_by(Level_Tasks.num_in_order)
        )
        return stmt.all()
    
    async def get_task_hint(self, task_id: int) -> Optional[str]:
        stmt = await self.session.execute(
            select(Tasks.hint)
            .where(Tasks.id == task_id))
        return stmt.scalar_one_or_none()
    
    async def get_task_options_by_id(self, task_id: int) -> Sequence[Tasks_Options]:
        stmt = await self.session.execute(
            select(Tasks_Options)
            .where(Tasks_Options.task_id == task_id))
        return stmt.scalars().all()
    
    async def get_task_gaps_by_id(self, task_id: int) -> Sequence[Tasks_Gap]:
        stmt = await self.session.execute(
            select(Tasks_Gap)
            .where(Tasks_Gap.task_id == task_id))
        return stmt.scalars().all()
    
    async def get_task_code_by_id(self, task_id: int) -> Optional[Tasks_Code]:
        stmt = await self.session.execute(
            select(Tasks_Code)
            .where(Tasks_Code.task_id == task_id)
            .options(selectinload(Tasks_Code.language)))
        return stmt.scalar_one_or_none()
    
    async def get_task_tests_by_code_id(self, code_id: int) -> Sequence[Tests]:
        stmt = await self.session.execute(
            select(Tests)
            .where(Tests.code_id == code_id))
        return stmt.scalars().all()
