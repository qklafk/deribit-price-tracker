"""Pydantic схемы для валидации данных."""
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal


class PriceCreate(BaseModel):
    """Схема для создания записи о цене."""
    ticker: str = Field(..., description="Тикер валюты (BTC_USD или ETH_USD)")
    price: Decimal = Field(..., description="Цена валюты")
    timestamp: int = Field(..., description="UNIX timestamp")
    
    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Валидация тикера."""
        allowed_tickers = ['BTC_USD', 'ETH_USD']
        if v not in allowed_tickers:
            raise ValueError(f"Ticker must be one of {allowed_tickers}")
        return v


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
