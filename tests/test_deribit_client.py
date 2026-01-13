"""Тесты для клиента Deribit."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
from aiohttp import ClientResponse
from app.services.deribit_client import DeribitClient, DeribitClientError


@pytest.mark.asyncio
async def test_get_index_price_success():
    """Тест успешного получения цены."""
    mock_response_data = {
        "jsonrpc": "2.0",
        "result": {
            "index_price": "50000.5",
            "index_name": "BTC_USD"
        },
        "usIn": 1234567890,
        "usOut": 1234567891,
        "usDiff": 1,
        "testnet": False
    }
    
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_response_data)
    
    mock_session = AsyncMock()
    mock_session.get = AsyncMock()
    mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
    mock_session.get.return_value.__aexit__ = AsyncMock(return_value=False)
    mock_session.close = AsyncMock()
    
    client = DeribitClient(session=mock_session)
    
    price = await client.get_index_price("BTC")
    
    assert price == Decimal("50000.5")
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_index_price_api_error():
    """Тест обработки ошибки API."""
    mock_response_data = {
        "jsonrpc": "2.0",
        "error": {
            "code": 10001,
            "message": "Invalid index name"
        }
    }
    
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_response_data)
    
    mock_session = AsyncMock()
    mock_session.get = AsyncMock()
    mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
    mock_session.get.return_value.__aexit__ = AsyncMock(return_value=False)
    mock_session.close = AsyncMock()
    
    client = DeribitClient(session=mock_session)
    
    with pytest.raises(DeribitClientError):
        await client.get_index_price("INVALID")


@pytest.mark.asyncio
async def test_get_index_price_http_error():
    """Тест обработки HTTP ошибки."""
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 500
    
    mock_session = AsyncMock()
    mock_session.get = AsyncMock()
    mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
    mock_session.get.return_value.__aexit__ = AsyncMock(return_value=False)
    mock_session.close = AsyncMock()
    
    client = DeribitClient(session=mock_session)
    
    with pytest.raises(DeribitClientError):
        await client.get_index_price("BTC")


@pytest.mark.asyncio
async def test_context_manager():
    """Тест использования клиента как context manager."""
    mock_session = AsyncMock()
    mock_session.close = AsyncMock()
    
    async with DeribitClient(session=mock_session) as client:
        assert client is not None
    
    # Сессия не должна закрываться, так как она была передана извне
    mock_session.close.assert_not_called()
