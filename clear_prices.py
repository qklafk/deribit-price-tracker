"""Скрипт для очистки таблицы prices."""
import asyncio
from app.database import engine, Base
from app.models import Price
from sqlalchemy import text


async def clear_prices_table():
    """Очистить таблицу prices."""
    async with engine.begin() as conn:
        # Удаляем все записи из таблицы
        await conn.execute(text("DELETE FROM prices"))
        # Сбрасываем счетчик последовательности (опционально)
        await conn.execute(text("ALTER SEQUENCE prices_id_seq RESTART WITH 1"))
    print("Таблица prices очищена успешно!")


if __name__ == "__main__":
    asyncio.run(clear_prices_table())
