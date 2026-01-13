"""Скрипт для инициализации базы данных."""
import asyncio
from app.database import engine, Base
from app.models import Price


async def init_db():
    """Инициализировать базу данных."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
