"""
Configuration settings for the TRADER platform.
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_TITLE: str = "TRADER - Institutional Crypto Analysis API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
    
    # Exchange Settings
    DEFAULT_EXCHANGE: str = "binance"
    SUPPORTED_EXCHANGES: List[str] = ["binance", "bybit", "coinbase", "kraken", "okx"]
    
    # Default Trading Pairs
    DEFAULT_SYMBOLS: List[str] = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT"]
    
    # Timeframes for analysis
    TIMEFRAMES: List[str] = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "8h", "1d", "1w", "1M"]
    
    # Cache settings (seconds)
    CACHE_TTL_TICKER: int = 5
    CACHE_TTL_OHLCV: int = 30
    CACHE_TTL_ANALYSIS: int = 60
    
    # Analysis settings
    ANALYSIS_LOOKBACK_PERIODS: int = 500
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

