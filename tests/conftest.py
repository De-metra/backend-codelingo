from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
import pytest
import pytest_asyncio

from app.main import app 
from app.core.security import create_jwt_token
from app.database.db import Base
from app.models.models import Courses
from app.utils.dependencies import get_uow
from app.utils.uow import UnitOfWork


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class TestUnitOfWork(UnitOfWork):
    def __init__(self):
        self.session_factory = TestingSessionLocal

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Создает таблицы перед тестами и удаляет после"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():

    def override_get_uow():
        return TestUnitOfWork()

    app.dependency_overrides[get_uow] = override_get_uow

    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user_token():
    user_data = {"sub": "1", "email": "test@example.com"}

    token = create_jwt_token(user_data)
    return token

@pytest.fixture
def auth_header(test_user_token):
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest_asyncio.fixture
async def created_course():
    uow = TestUnitOfWork()

    async with uow:
        course = await uow.course.add(
            Courses(
                title="Pythonяч",
                description="Тестовый курс"
            )
        )
        await uow.commit()

        return course
    

# @pytest_asyncio.fixture
# async def seeded_course():
#     uow = UnitOfWork()

#     async with uow:
#         course = await uow.course.add({
#             "title": "Pythonяч",
#             "description": "Тестовый курс"
#         })

#         await uow.commit()
#         await uow.session.flush()


#         levels = await uow.level.add({

#         })


#         return course