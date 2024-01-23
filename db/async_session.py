from contextlib import asynccontextmanager

from dotenv import dotenv_values
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from path_config import ENV_DIR

env = dotenv_values(ENV_DIR)

engine = create_async_engine(
    f"postgresql+asyncpg://{env['USERNAME']}:{env['PASSWORD']}@{env['HOST']}/{env['DATABASE']}",
    echo=True,
)


def async_session_gen():
    return sessionmaker(engine, class_=AsyncSession)


@asynccontextmanager
async def get_session():
    try:
        async_session = async_session_gen()

        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
