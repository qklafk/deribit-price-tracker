"""Celery задачи."""
import time
import logging
import asyncio
from app.celery_app import celery_app
from app.services.deribit_client import DeribitClient
from app.services.price_service import PriceService
from app.schemas import PriceCreate
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


def _create_db_session():
    """
    Создать engine и sessionmaker для работы с БД в текущем event loop.
    Важно: создаем engine заново для каждого event loop.
    """
    database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
    )
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    return async_session, engine


async def _fetch_and_save_price(ticker: str, currency: str):
    """
    Получить индексную цену валюты с биржи Deribit и сохранить в БД.
    
    Args:
        ticker: Тикер для сохранения (BTC или ETH)
        currency: Валюта для запроса к API (BTC or ETH)
    """
    async with DeribitClient() as client:
        try:
            # Получаем текущее время в формате UNIX timestamp ПЕРЕД запросом к API
            # Это гарантирует точный интервал ровно 60 секунд между записями
            timestamp = int(time.time())
            
            # Получаем индексную цену с биржи Deribit
            price = await client.get_index_price(currency)
            
            logger.info(f"Получена цена {ticker}: {price} (timestamp: {timestamp})")
            
            # Создаем engine и сессию БД в текущем event loop
            # Это важно для работы с Celery prefork pool
            async_session, engine = _create_db_session()
            
            try:
                async with async_session() as session:
                    service = PriceService(session)
                    price_data = PriceCreate(
                        ticker=ticker,
                        price=price,
                        timestamp=timestamp
                    )
                    saved_price = await service.create_price(price_data)
                    logger.info(f"Сохранена цена {ticker} в БД: ID={saved_price.id}, цена={saved_price.price}, timestamp={saved_price.timestamp}")
            finally:
                # Закрываем engine после использования
                await engine.dispose()
        except Exception as e:
            # Логируем ошибку, но не прерываем выполнение задачи
            logger.error(f"Ошибка при получении цены для {ticker}: {str(e)}", exc_info=True)


@celery_app.task(name="app.tasks.fetch_prices")
def fetch_prices():
    """
    Задача для получения индексных цен BTC_USD и ETH_USD с биржи Deribit.
    Выполняется каждую минуту через Celery Beat.
    
    Получает текущие индексные цены (index price) для обеих валют
    и сохраняет их в базу данных с тикером, ценой и UNIX timestamp.
    """
    import asyncio
    
    logger.info("Запуск задачи получения цен BTC и ETH")
    
    # Создаем новый event loop для задачи
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Запускаем обе задачи параллельно (получение цен для BTC и ETH одновременно)
        loop.run_until_complete(
            asyncio.gather(
                _fetch_and_save_price("BTC", "BTC"),
                _fetch_and_save_price("ETH", "ETH")
            )
        )
        logger.info("Задача получения цен успешно завершена")
    except Exception as e:
        logger.error(f"Ошибка при выполнении задачи получения цен: {str(e)}", exc_info=True)
    finally:
        loop.close()
