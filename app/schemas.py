"""Pydantic схемы для валидации данных."""
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal


class PriceCreate(BaseModel):
    """Схема для создания записи о цене."""
    ticker: str = Field(..., description="Тикер валюты (BTC или ETH). Допускаются также BTC_USD/ETH_USD - будут нормализованы")
    price: Decimal = Field(..., description="Цена валюты")
    timestamp: int = Field(..., description="UNIX timestamp")
    
    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Валидация и нормализация тикера: возвращает 'BTC' или 'ETH'."""
        allowed = {
            'BTC': 'BTC',
            'ETH': 'ETH',
            'BTC_USD': 'BTC',
            'ETH_USD': 'ETH'
        }
        if v not in allowed:
            raise ValueError(f"Ticker must be one of {list(allowed.keys())}")
        return allowed[v]


class PriceResponse(BaseModel):
    """Схема для ответа API."""
    id: int
    ticker: str
    price: Decimal
    timestamp: int
    
    class Config:
        from_attributes = True


class PriceListResponse(BaseModel):
    """Схема для списка цен."""
    prices: list[PriceResponse]
    total: int


class LastPriceResponse(BaseModel):
    """Схема для последней цены."""
    ticker: str
    price: Decimal
    timestamp: int
