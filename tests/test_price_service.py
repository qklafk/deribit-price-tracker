"""Тесты для сервиса работы с ценами."""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.services.price_service import PriceService
from app.models import Price
from app.schemas import PriceCreate


@pytest.mark.asyncio
async def test_create_price(test_db):
    """Тест создания записи о цене."""
    service = PriceService(test_db)
    
    price_data = PriceCreate(
           ticker="BTC",
        price=Decimal("50000.5"),
        timestamp=1234567890
    )
    
    price = await service.create_price(price_data)
    
    assert price.id is not None
    assert price.ticker == "BTC"
    assert price.price == Decimal("50000.5")
    assert price.timestamp == 1234567890


@pytest.mark.asyncio
async def test_get_prices_by_ticker(test_db):
    """Тест получения всех цен по тикеру."""
    service = PriceService(test_db)
    
    # Создаем несколько записей
    for i in range(3):
        price_data = PriceCreate(
                ticker="BTC",
            price=Decimal(f"5000{i}.5"),
            timestamp=1234567890 + i
        )
        await service.create_price(price_data)
    
    # Создаем запись с другим тикером
    eth_price_data = PriceCreate(
            ticker="ETH",
        price=Decimal("3000.5"),
        timestamp=1234567890
    )
    await service.create_price(eth_price_data)
    
    prices = await service.get_prices_by_ticker("BTC")
    
    assert len(prices) == 3
    assert all(price.ticker == "BTC" for price in prices)
    # Проверяем сортировку по убыванию timestamp
    assert prices[0].timestamp >= prices[1].timestamp >= prices[2].timestamp


@pytest.mark.asyncio
async def test_get_last_price(test_db):
    """Тест получения последней цены."""
    service = PriceService(test_db)
    
    # Создаем несколько записей
    for i in range(3):
        price_data = PriceCreate(
            ticker="BTC",
            price=Decimal(f"5000{i}.5"),
            timestamp=1234567890 + i
        )
        await service.create_price(price_data)
    
    last_price = await service.get_last_price("BTC")
    
    assert last_price is not None
    assert last_price.ticker == "BTC"
    assert last_price.timestamp == 1234567892  # Последний timestamp


@pytest.mark.asyncio
async def test_get_last_price_not_found(test_db):
    """Тест получения последней цены когда данных нет."""
    service = PriceService(test_db)
    
    last_price = await service.get_last_price("BTC")
    
    assert last_price is None


@pytest.mark.asyncio
async def test_get_prices_by_date_range(test_db):
    """Тест получения цен с фильтром по дате."""
    service = PriceService(test_db)
    
    base_time = datetime(2024, 1, 15, 12, 0, 0)
    
    # Создаем записи в разных датах
    for i in range(5):
        date = base_time + timedelta(days=i)
        price_data = PriceCreate(
            ticker="BTC",
            price=Decimal(f"5000{i}.5"),
            timestamp=int(date.timestamp())
        )
        await service.create_price(price_data)
    
    start_date = datetime(2024, 1, 16)
    end_date = datetime(2024, 1, 18)
    
    prices = await service.get_prices_by_date_range(
            "BTC",
        start_date=start_date,
        end_date=end_date
    )
    
    assert len(prices) == 3
    for price in prices:
        price_date = datetime.fromtimestamp(price.timestamp)
        assert start_date.date() <= price_date.date() <= end_date.date()


@pytest.mark.asyncio
async def test_get_prices_by_date_range_start_only(test_db):
    """Тест получения цен с фильтром только по начальной дате."""
    service = PriceService(test_db)
    
    base_time = datetime(2024, 1, 15, 12, 0, 0)
    
    for i in range(5):
        date = base_time + timedelta(days=i)
        price_data = PriceCreate(
            ticker="BTC",
            price=Decimal(f"5000{i}.5"),
            timestamp=int(date.timestamp())
        )
        await service.create_price(price_data)
    
    start_date = datetime(2024, 1, 17)
    
    prices = await service.get_prices_by_date_range(
            "BTC",
        start_date=start_date
    )
    
    assert len(prices) == 3
    for price in prices:
        price_date = datetime.fromtimestamp(price.timestamp)
        assert price_date.date() >= start_date.date()
