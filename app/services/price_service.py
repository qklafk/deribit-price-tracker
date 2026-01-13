"""Сервис для работы с ценами в базе данных."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from app.models import Price
from app.schemas import PriceCreate


class PriceService:
    """Сервис для работы с ценами."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_price(self, price_data: PriceCreate) -> Price:
        """
        Создать запись о цене.
        
        Args:
            price_data: Данные о цене
            
        Returns:
            Созданная запись
        """
        price = Price(
            ticker=price_data.ticker,
            price=price_data.price,
            timestamp=price_data.timestamp
        )
        self.db.add(price)
        await self.db.commit()
        await self.db.refresh(price)
        return price
    
    async def get_prices_by_ticker(self, ticker: str) -> List[Price]:
        """
        Получить все цены по тикеру.
        
        Args:
            ticker: Тикер валюты
            
        Returns:
            Список цен
        """
        result = await self.db.execute(
            select(Price).where(Price.ticker == ticker).order_by(Price.timestamp.desc())
        )
        return list(result.scalars().all())
    
    async def get_last_price(self, ticker: str) -> Optional[Price]:
        """
        Получить последнюю цену по тикеру.
        
        Args:
            ticker: Тикер валюты
            
        Returns:
            Последняя цена или None
        """
        result = await self.db.execute(
            select(Price)
            .where(Price.ticker == ticker)
            .order_by(Price.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_prices_by_date_range(
        self,
        ticker: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Price]:
        """
        Получить цены по тикеру с фильтром по дате.
        
        Args:
            ticker: Тикер валюты
            start_date: Начальная дата (опционально)
            end_date: Конечная дата (опционально)
            
        Returns:
            Список цен
        """
        query = select(Price).where(Price.ticker == ticker)
        
        conditions = []
        if start_date:
            start_timestamp = int(start_date.timestamp())
            conditions.append(Price.timestamp >= start_timestamp)
        
        if end_date:
            end_timestamp = int(end_date.timestamp())
            conditions.append(Price.timestamp <= end_timestamp)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Price.timestamp.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
