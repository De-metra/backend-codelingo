from abc import abstractmethod, ABC
from typing import TypeVar, Type, Generic, Sequence, Optional

from sqlalchemy.future import select
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")

class AbstractRepository(ABC):
    @abstractmethod
    async def find_all(self):
        raise NotImplementedError
    
    @abstractmethod
    async def find_one_or_none(self, **kwargs):
        raise NotImplementedError
    

class SQLAlchemyRepository(AbstractRepository, Generic[T]):  # репозиторий для алхимии 
    model: Type[T] = None 

    def __init__(self, session: AsyncSession):
        self.session = session  

    # async def add(self, data: dict) -> T:
    #     """Создает объект и добавляет его в сессию."""
    #     instance = self.model(**data)
    #     self.session.add(instance)
    #     return instance
    
    async def find_all(self) -> Sequence[T]:
        """Возвращает все объекты модели."""
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def find_one_or_none(self, **kwargs) -> Optional[T]:
        """Находит один объект по заданным параметрам или возвращает None, если не найдено."""
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Получает объект по его идентификатору или возвращает None, если не найдено."""
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def update(self, obj: T, data: dict) -> T:
        """Обновляет поля существующего объекта (In-place)."""
        for field, value in data.items():
            setattr(obj, field, value)
        return obj

    async def delete(self, **filter_by) -> None:
        """Удаляет записи по фильтру."""
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)