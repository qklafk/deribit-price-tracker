"""Модели базы данных."""
from sqlalchemy import Column, String, Numeric, BigInteger, Index
from app.database import Base


class Price(Base):
    """Модель для хранения цен валют."""
    
    __tablename__ = "prices"
    
    id = Column(BigInteger, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    price = Column(Numeric(20, 8), nullable=False)
    timestamp = Column(BigInteger, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_ticker_timestamp', 'ticker', 'timestamp'),
    )
