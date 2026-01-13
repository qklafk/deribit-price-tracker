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
        # Используем правильный формат URL согласно документации Deribit API v2
        # Согласно ответу get_instruments, price_index имеет формат: "btc_usd" или "eth_usd"
        # URL: https://www.deribit.com/api/v2/public/get_index_price?index_name=btc_usd
        url = f"{self.base_url}/public/get_index_price"
        # Преобразуем валюту в формат index_name: валюта в нижнем регистре + "_usd"
        # Например: BTC -> btc_usd, ETH -> eth_usd
        index_name = f"{currency.lower()}_usd"
        params = {"index_name": index_name}
        
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise DeribitClientError(
                        f"Failed to get index price: HTTP {response.status}, {error_text}"
                    )
                
                data = await response.json()
                
                # Проверяем формат ответа Deribit API v2 (может быть JSON-RPC или обычный JSON)
                # Deribit API v2 возвращает ответ в формате JSON-RPC 2.0
                if "error" in data:
                    error_info = data["error"]
                    if isinstance(error_info, dict):
                        error_msg = error_info.get("message", str(error_info))
                        error_code = error_info.get("code", "unknown")
                    else:
                        error_msg = str(error_info)
                        error_code = "unknown"
                    raise DeribitClientError(
                        f"Deribit API error (code {error_code}): {error_msg}"
                    )
                
                # Проверяем наличие результата
                if "result" not in data:
                    raise DeribitClientError(
                        f"Invalid response format from Deribit API: {data}"
                    )
                
                result = data["result"]
                
                # Проверяем наличие index_price в результате
                if "index_price" not in result:
                    raise DeribitClientError(
                        f"Index price not found in response: {result}"
                    )
                
                index_price = result["index_price"]
                return Decimal(str(index_price))
                
        except aiohttp.ClientError as e:
            raise DeribitClientError(f"Network error: {str(e)}") from e
        except Exception as e:
            if isinstance(e, DeribitClientError):
                raise
            raise DeribitClientError(f"Unexpected error: {str(e)}") from e
    
    async def __aenter__(self):
        """Поддержка async context manager."""
        await self._get_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из context manager."""
        await self.close()
