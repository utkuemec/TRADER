"""
Market data API routes.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..config import settings
from ..models import SymbolListResponse, OHLCVResponse, Ticker
from ..services.exchange import exchange_service

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/symbols/{exchange}", response_model=SymbolListResponse)
async def get_symbols(exchange: str = "binance"):
    """Get all available trading symbols from an exchange."""
    try:
        symbols = await exchange_service.get_symbols(exchange)
        return SymbolListResponse(
            exchange=exchange,
            symbols=symbols,
            count=len(symbols)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ticker/{symbol}", response_model=Ticker)
async def get_ticker(
    symbol: str,
    exchange: str = Query(default="binance")
):
    """Get current ticker data for a symbol."""
    try:
        # Convert URL-safe symbol format
        symbol = symbol.replace("-", "/")
        ticker = await exchange_service.get_ticker(symbol, exchange)
        return ticker
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ohlcv/{symbol}", response_model=OHLCVResponse)
async def get_ohlcv(
    symbol: str,
    timeframe: str = Query(default="1h"),
    exchange: str = Query(default="binance"),
    limit: int = Query(default=500, ge=1, le=1000)
):
    """Get OHLCV candlestick data."""
    try:
        symbol = symbol.replace("-", "/")
        candles = await exchange_service.get_ohlcv(symbol, timeframe, exchange, limit)
        return OHLCVResponse(
            symbol=symbol,
            timeframe=timeframe,
            exchange=exchange,
            data=candles,
            count=len(candles)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orderbook/{symbol}")
async def get_orderbook(
    symbol: str,
    exchange: str = Query(default="binance"),
    limit: int = Query(default=50, ge=1, le=100)
):
    """Get order book data."""
    try:
        symbol = symbol.replace("-", "/")
        orderbook = await exchange_service.get_order_book(symbol, exchange, limit)
        return orderbook
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

