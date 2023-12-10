from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.configs import DATABASE_FILE


BaseModel = declarative_base()


def get_async_session():
    engine = create_async_engine(f"sqlite+aiosqlite:///{DATABASE_FILE}")
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return async_session


async def execute_command(command, commit_after_execute=False):
    async_session = get_async_session()

    async with async_session() as session:
        result = await session.execute(command)

        if commit_after_execute:
            await session.commit()

    return result
