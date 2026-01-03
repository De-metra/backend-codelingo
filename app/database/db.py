from datetime import datetime
from typing import Annotated

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession

from app.core.config import get_db_url 


DATABASE_URL = get_db_url()

# Главный объект для работы с базой данных - используется во всех запросах
#database = Database(DATABASE_URL)
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# настройка аннотаций
int_pk = Annotated[int, mapped_column(primary_key=True)]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}"

    updated_at: Mapped[updated_at]

async def get_async_session():
    async with async_session_maker() as session:
        yield session

