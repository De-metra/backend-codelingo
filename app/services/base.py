from sqlalchemy.future import select
from app.database.db import async_session_maker
from app.models.models import Users


class BaseService:
    model = None

    @classmethod
    async def find_all_students(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            students = await session.execute(query)
            return students.scalars().all()
        
    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()