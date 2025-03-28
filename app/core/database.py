from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import config

Base = declarative_base()

DEBUG = config.ENVIRONMENT == "development"

engine = create_async_engine(
    config.DATABASE_URL,
    pool_size=30,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_session() -> AsyncSession:
    session = AsyncSessionLocal()
    try:
        yield session
    except SQLAlchemyError as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
