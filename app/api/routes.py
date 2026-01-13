"""API роуты."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.services.price_service import PriceService
from app.schemas import PriceListResponse, PriceResponse, LastPriceResponse

router = APIRouter(prefix="/api/prices", tags=["prices"])


@router.get("", response_model=PriceListResponse)
async def get_all_prices(
    ticker: str = Query(..., description="Тикер валюты (BTC или ETH). Допускаются также BTC_USD/ETH_USD"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все сохраненные данные по указанной валюте.
    
    Args:
        ticker: Тикер валюты (обязательный параметр)
        db: Сессия базы данных
        
    Returns:
        Список всех цен для указанного тикера
    """
    # Accept both new and legacy ticker formats and normalize to BTC/ETH
    norm = {
        'BTC': 'BTC', 'ETH': 'ETH',
        'BTC_USD': 'BTC', 'ETH_USD': 'ETH'
    }
    if ticker not in norm:
        raise HTTPException(status_code=400, detail="Invalid ticker. Must be BTC or ETH")

    ticker_norm = norm[ticker]
    service = PriceService(db)
    prices = await service.get_prices_by_ticker(ticker_norm)
    
    return PriceListResponse(
        prices=[PriceResponse.model_validate(price) for price in prices],
        total=len(prices)
    )


@router.get("/last", response_model=LastPriceResponse)
async def get_last_price(
    ticker: str = Query(..., description="Тикер валюты (BTC или ETH). Допускаются также BTC_USD/ETH_USD"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить последнюю цену валюты.
    
    Args:
        ticker: Тикер валюты (обязательный параметр)
        db: Сессия базы данных
        
    Returns:
        Последняя цена для указанного тикера
    """
    norm = {
        'BTC': 'BTC', 'ETH': 'ETH',
        'BTC_USD': 'BTC', 'ETH_USD': 'ETH'
    }
    if ticker not in norm:
        raise HTTPException(status_code=400, detail="Invalid ticker. Must be BTC or ETH")

    ticker_norm = norm[ticker]
    service = PriceService(db)
    price = await service.get_last_price(ticker_norm)
    
    if price is None:
        raise HTTPException(
            status_code=404,
            detail=f"No price data found for ticker {ticker}"
        )
    
    return LastPriceResponse(
        ticker=price.ticker,
        price=price.price,
        timestamp=price.timestamp
    )


@router.get("/filter", response_model=PriceListResponse)
async def get_prices_by_date(
    ticker: str = Query(..., description="Тикер валюты (BTC или ETH). Допускаются также BTC_USD/ETH_USD"),
    start_date: Optional[str] = Query(None, description="Начальная дата (DD-MM-YYYY)"),
    end_date: Optional[str] = Query(None, description="Конечная дата (DD-MM-YYYY)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить цену валюты с фильтром по дате.
    
    Args:
        ticker: Тикер валюты (обязательный параметр)
        start_date: Начальная дата в формате DD-MM-YYYY (опционально)
        end_date: Конечная дата в формате DD-MM-YYYY (опционально)
        db: Сессия базы данных
        
    Returns:
        Список цен для указанного тикера в указанном диапазоне дат
    """
    norm = {
        'BTC': 'BTC', 'ETH': 'ETH',
        'BTC_USD': 'BTC', 'ETH_USD': 'ETH'
    }
    if ticker not in norm:
        raise HTTPException(status_code=400, detail="Invalid ticker. Must be BTC or ETH")

    ticker_norm = norm[ticker]
    
    start_datetime = None
    end_datetime = None
    
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%d-%m-%Y")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid start_date format. Use DD-MM-YYYY"
            )
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%d-%m-%Y")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid end_date format. Use DD-MM-YYYY"
            )
    
    service = PriceService(db)
    prices = await service.get_prices_by_date_range(ticker_norm, start_datetime, end_datetime)
    
    return PriceListResponse(
        prices=[PriceResponse.model_validate(price) for price in prices],
        total=len(prices)
    )
