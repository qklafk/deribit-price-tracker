"""Клиент для работы с API Deribit."""
import aiohttp
from typing import Optional
from decimal import Decimal
from app.config import settings


class DeribitClientError(Exception):
    """Исключение для ошибок клиента Deribit."""
    pass


class DeribitClient:
    """Клиент для получения данных с биржи Deribit."""
    
    def __init__(self, base_url: str = None, session: Optional[aiohttp.ClientSession] = None):
        """
        Инициализация клиента.
        
        Args:
            base_url: Базовый URL API Deribit
            session: Опциональная сессия aiohttp для переиспользования
        """
        self.base_url = base_url or settings.deribit_api_url
        self._session = session
        self._own_session = session is None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать сессию aiohttp."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Закрыть сессию, если она была создана клиентом."""
        if self._own_session and self._session:
            await self._session.close()
            self._session = None
    
    async def get_index_price(self, currency: str) -> Decimal:
        """
        Получить индексную цену валюты.
        
        Args:
            currency: Валюта (BTC или ETH)
            
        Returns:
            Индексная цена валюты
            
        Raises:
            DeribitClientError: При ошибке получения данных
        """
        session = await self._get_session()
        url = f"{self.base_url}/public/get_index_price"
        params = {"index_name": f"{currency}_USD"}
        
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise DeribitClientError(
                        f"Failed to get index price: HTTP {response.status}"
                    )
                
                data = await response.json()
                
                if "error" in data and data["error"]:
                    raise DeribitClientError(
                        f"Deribit API error: {data['error']}"
                    )
                
                if "result" not in data or "index_price" not in data["result"]:
                    raise DeribitClientError("Invalid response format from Deribit API")
                
                return Decimal(str(data["result"]["index_price"]))
                
        except aiohttp.ClientError as e:
            raise DeribitClientError(f"Network error: {str(e)}") from e
        except Exception as e:
            if isinstance(e, DeribitClientError):
                raise
            raise DeribitClientError(f"Unexpected error: {str(e)}") from e
    
    async def __aenter__(self):
        """Поддержка async context manager."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из context manager."""
        await self.close()
