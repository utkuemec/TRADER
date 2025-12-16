"""
Exchange data service using CCXT.
Handles fetching OHLCV, tickers, and order book data from multiple exchanges.
"""
import ccxt.async_support as ccxt
from typing import List, Dict, Optional, Any
from datetime import datetime
import asyncio
from cachetools import TTLCache
import pandas as pd

from ..config import settings
from ..models import OHLCV, Ticker


class ExchangeService:
    """Service for fetching data from cryptocurrency exchanges."""
    
    def __init__(self):
        self._exchanges: Dict[str, ccxt.Exchange] = {}
        self._ticker_cache = TTLCache(maxsize=100, ttl=settings.CACHE_TTL_TICKER)
        self._ohlcv_cache = TTLCache(maxsize=500, ttl=settings.CACHE_TTL_OHLCV)
    
    async def get_exchange(self, exchange_id: str) -> ccxt.Exchange:
        """Get or create an exchange instance."""
        if exchange_id not in self._exchanges:
            exchange_class = getattr(ccxt, exchange_id, None)
            if exchange_class is None:
                raise ValueError(f"Exchange '{exchange_id}' not supported")
            
            self._exchanges[exchange_id] = exchange_class({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
        
        return self._exchanges[exchange_id]
    
    async def close_all(self):
        """Close all exchange connections."""
        for exchange in self._exchanges.values():
            await exchange.close()
        self._exchanges.clear()
    
    async def get_symbols(self, exchange_id: str) -> List[str]:
        """Get all available trading symbols from an exchange."""
        exchange = await self.get_exchange(exchange_id)
        await exchange.load_markets()
        
        # Filter for USDT pairs and sort by volume
        usdt_symbols = [
            symbol for symbol in exchange.symbols 
            if symbol.endswith('/USDT') and ':' not in symbol
        ]
        return sorted(usdt_symbols)
    
    async def get_ticker(self, symbol: str, exchange_id: str = "binance") -> Ticker:
        """Get current ticker data for a symbol."""
        cache_key = f"{exchange_id}:{symbol}"
        
        if cache_key in self._ticker_cache:
            return self._ticker_cache[cache_key]
        
        exchange = await self.get_exchange(exchange_id)
        await exchange.load_markets()
        
        ticker_data = await exchange.fetch_ticker(symbol)
        
        ticker = Ticker(
            symbol=symbol,
            last=ticker_data.get('last', 0),
            bid=ticker_data.get('bid'),
            ask=ticker_data.get('ask'),
            high=ticker_data.get('high'),
            low=ticker_data.get('low'),
            volume=ticker_data.get('baseVolume'),
            change=ticker_data.get('change'),
            percentage=ticker_data.get('percentage'),
            timestamp=ticker_data.get('timestamp', int(datetime.now().timestamp() * 1000))
        )
        
        self._ticker_cache[cache_key] = ticker
        return ticker
    
    async def get_ohlcv(
        self, 
        symbol: str, 
        timeframe: str = "1h",
        exchange_id: str = "binance",
        limit: int = 500
    ) -> List[OHLCV]:
        """Fetch OHLCV (candlestick) data."""
        cache_key = f"{exchange_id}:{symbol}:{timeframe}:{limit}"
        
        if cache_key in self._ohlcv_cache:
            return self._ohlcv_cache[cache_key]
        
        exchange = await self.get_exchange(exchange_id)
        await exchange.load_markets()
        
        ohlcv_data = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        candles = []
        for candle in ohlcv_data:
            candles.append(OHLCV(
                timestamp=candle[0],
                datetime=datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                open=candle[1],
                high=candle[2],
                low=candle[3],
                close=candle[4],
                volume=candle[5]
            ))
        
        self._ohlcv_cache[cache_key] = candles
        return candles
    
    async def get_ohlcv_dataframe(
        self,
        symbol: str,
        timeframe: str = "1h",
        exchange_id: str = "binance",
        limit: int = 500
    ) -> pd.DataFrame:
        """Fetch OHLCV data as a pandas DataFrame for analysis."""
        candles = await self.get_ohlcv(symbol, timeframe, exchange_id, limit)
        
        df = pd.DataFrame([c.model_dump() for c in candles])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('datetime', inplace=True)
        
        return df
    
    async def get_multi_timeframe_data(
        self,
        symbol: str,
        timeframes: List[str],
        exchange_id: str = "binance",
        limit: int = 500
    ) -> Dict[str, pd.DataFrame]:
        """Fetch OHLCV data for multiple timeframes concurrently."""
        tasks = [
            self.get_ohlcv_dataframe(symbol, tf, exchange_id, limit)
            for tf in timeframes
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data = {}
        for tf, result in zip(timeframes, results):
            if not isinstance(result, Exception):
                data[tf] = result
        
        return data
    
    async def get_order_book(
        self,
        symbol: str,
        exchange_id: str = "binance",
        limit: int = 50
    ) -> Dict[str, Any]:
        """Fetch order book data."""
        exchange = await self.get_exchange(exchange_id)
        await exchange.load_markets()
        
        order_book = await exchange.fetch_order_book(symbol, limit)
        
        return {
            'bids': order_book['bids'][:limit],
            'asks': order_book['asks'][:limit],
            'timestamp': order_book.get('timestamp'),
            'spread': order_book['asks'][0][0] - order_book['bids'][0][0] if order_book['asks'] and order_book['bids'] else 0
        }


# Singleton instance
exchange_service = ExchangeService()

