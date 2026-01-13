"""Тесты для API endpoints."""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.services.price_service import PriceService
from app.schemas import PriceCreate


@pytest.mark.asyncio
async def test_get_all_prices(client, test_db):
    """Тест получения всех цен."""
    # Создаем тестовые данные
    service = PriceService(test_db)
    for i in range(3):
        price_data = PriceCreate(
            ticker="BTC",
            price=Decimal(f"5000{i}.5"),
            timestamp=1234567890 + i
        )
        await service.create_price(price_data)
    
    response = await client.get("/api/prices?ticker=BTC")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["prices"]) == 3
    assert all(price["ticker"] == "BTC" for price in data["prices"])


@pytest.mark.asyncio
async def test_get_all_prices_invalid_ticker(client):
    """Тест получения всех цен с невалидным тикером."""
    response = await client.get("/api/prices?ticker=INVALID")
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_last_price(client, test_db):
    """Тест получения последней цены."""
    service = PriceService(test_db)
    
    for i in range(3):
        price_data = PriceCreate(
            ticker="ETH",
            price=Decimal(f"300{i}.5"),
            timestamp=1234567890 + i
        )
        await service.create_price(price_data)
    
    response = await client.get("/api/prices/last?ticker=ETH")
    
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "ETH"
    assert data["timestamp"] == 1234567892


@pytest.mark.asyncio
async def test_get_last_price_not_found(client):
    """Тест получения последней цены когда данных нет."""
    response = await client.get("/api/prices/last?ticker=BTC")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_prices_by_date(client, test_db):
    """Тест получения цен с фильтром по дате."""
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
    
    response = await client.get(
        "/api/prices/filter?ticker=BTC&start_date=16-01-2024&end_date=18-01-2024"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_get_prices_by_date_invalid_format(client):
    """Тест получения цен с невалидным форматом даты."""
    response = await client.get(
        "/api/prices/filter?ticker=BTC&start_date=invalid-date"
    )
    
    assert response.status_code == 400
