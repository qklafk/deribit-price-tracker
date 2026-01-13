"""Главный файл FastAPI приложения."""
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Deribit Price Tracker API",
    description="API для получения исторических данных о ценах криптовалют с биржи Deribit",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "message": "Deribit Price Tracker API",
        "docs": "/docs"
    }
