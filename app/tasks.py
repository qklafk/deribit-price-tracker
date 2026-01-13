"""Celery задачи."""
import time
from app.celery_app import celery_app
from app.services.deribit_client import DeribitClient
from app.services.price_service import PriceService
from app.schemas import PriceCreate
from app.database import AsyncSessionLocal


async def _fetch_and_save_price(ticker: str, currency: str):
    """
    Получить цену с Deribit и сохранить в БД.
    
    Args:
        ticker: Тикер для сохранения (BTC_USD или ETH_USD)
        currency: Валюта для запроса к API (BTC или ETH)
    """
    async with DeribitClient() as client:
        try:
            price = await client.get_index_price(currency)
            timestamp = int(time.time())
            
            async with AsyncSessionLocal() as session:
                service = PriceService(session)
                price_data = PriceCreate(
                    ticker=ticker,
                    price=price,
                    timestamp=timestamp
                )
                await service.create_price(price_data)
        except Exception as e:
            # Логируем ошибку, но не прерываем выполнение задачи
            print(f"Error fetching price for {ticker}: {str(e)}")


@celery_app.task(name="app.tasks.fetch_prices")
def fetch_prices():
    """
    Задача для получения цен BTC_USD и ETH_USD с биржи Deribit.
    Выполняется каждую минуту.
    """
    import asyncio
    
    # Создаем новый event loop для задачи
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Запускаем обе задачи параллельно
        loop.run_until_complete(
            asyncio.gather(
                _fetch_and_save_price("BTC_USD", "BTC"),
                _fetch_and_save_price("ETH_USD", "ETH")
            )
        )
    finally:
        loop.close()
