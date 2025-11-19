from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from sqlalchemy.orm import sessionmaker, declarative_base
from collections.abc import AsyncGenerator


from ..core.config import settings


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)

        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.engine, 
            # class_=AsyncSession, 
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    # Зависимость для FastAPI
    # async def get_db(self) -> AsyncSession:
    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.AsyncSessionLocal() as session:
            yield session

# Создание экземпляра помощника
db_helper = DatabaseHelper(url=settings.db.url, echo=settings.db.db_echo)
