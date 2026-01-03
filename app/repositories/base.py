from abc import abstractmethod, ABC
from sqlalchemy.future import select
from app.database.db import async_session_maker
from app.models.models import Users
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, and_, insert
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.database.db import async_session_maker

class AbstractRepository(ABC):
    """ @abstractmethod
    async def add(self, data: dict):
        raise NotImplementedError """

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError
    

class Repository(AbstractRepository):  # репозиторий для алхимии 
    model = None 

    def __init__(self, session: AsyncSession):
        self.session = session  

    """ async def add(self, data):
        if isinstance(data, self.model):
            data_dict = {c.name: getattr(data, c.name) for c in self.model.__table__.columns if c.name != "id"}     #что-то сделать
        else:
            data_dict = data

        stmt = insert(self.model).values(**data_dict).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one() """

    async def find_all(self):
        result = await self.session.execute(select(self.model))
        return result.scalars().all()
    
    async def get_by_id(self, id: int):
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().all()

    async def update(self, model, data: dict):
        for field, value in data.items():
            setattr(model, field, value)
        return model