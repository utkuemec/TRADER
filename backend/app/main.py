"""
TRADER - Institutional Crypto Analysis Platform
Main FastAPI Application
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json

from .config import settings
from .routes import market, analysis
from .services.exchange import exchange_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 TRADER Platform Starting...")
    print(f"📊 Default Exchange: {settings.DEFAULT_EXCHANGE}")
    print(f"💹 Default Symbols: {', '.join(settings.DEFAULT_SYMBOLS)}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down TRADER Platform...")
    await exchange_service.close_all()


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="""
# TRADER - Institutional Crypto Analysis Platform

Elite, institutional-grade cryptocurrency trading analysis API providing:

## Features

- **Multi-Timeframe Analysis**: Analysis across 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w timeframes
- **Technical Indicators**: RSI, MACD, Stochastic, Bollinger Bands, ATR, EMAs, VWAP
- **Market Structure**: HH, HL, LH, LL pattern detection, trend identification
- **Smart Money Concepts**: Order Blocks, Fair Value Gaps, Liquidity Zones
- **Price Predictions**: 1 Hour and 1 Day outlooks with confidence levels
- **Professional Reports**: Institutional-grade analysis narratives

## Exchanges Supported

- Binance
- Bybit
- Coinbase
- Kraken
- OKX

""",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(market.router, prefix=settings.API_PREFIX)
app.include_router(analysis.router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "symbols": f"{settings.API_PREFIX}/market/symbols/binance",
            "ticker": f"{settings.API_PREFIX}/market/ticker/BTC-USDT",
            "ohlcv": f"{settings.API_PREFIX}/market/ohlcv/BTC-USDT?timeframe=1h",
            "full_analysis": f"{settings.API_PREFIX}/analysis/full/BTC-USDT",
            "indicators": f"{settings.API_PREFIX}/analysis/indicators/BTC-USDT",
            "structure": f"{settings.API_PREFIX}/analysis/structure/BTC-USDT",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "TRADER API"}


# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@app.websocket("/ws/ticker/{symbol}")
async def websocket_ticker(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time ticker updates."""
    await manager.connect(websocket)
    symbol = symbol.replace("-", "/")
    
    try:
        while True:
            # Send ticker update every 2 seconds
            try:
                ticker = await exchange_service.get_ticker(symbol, "binance")
                await websocket.send_json({
                    "type": "ticker",
                    "data": ticker.model_dump()
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
            
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

