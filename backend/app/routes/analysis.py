"""
Analysis API routes.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..models import FullAnalysis, IndicatorResponse, AnalysisRequest
from ..services.exchange import exchange_service
from ..services.indicators import indicator_service
from ..services.structure import structure_service
from ..services.analyzer import analysis_engine
from ..services.prediction_cache import prediction_cache

router = APIRouter(prefix="/analysis", tags=["Technical Analysis"])


@router.get("/full/{symbol}", response_model=FullAnalysis)
async def get_full_analysis(
    symbol: str,
    exchange: str = Query(default="binance")
):
    """
    Get comprehensive multi-timeframe institutional-grade analysis.
    
    This endpoint provides:
    - Multi-timeframe bias analysis
    - Technical indicators across all timeframes
    - Market structure (HH, HL, LH, LL)
    - Smart Money Concepts (Order Blocks, FVGs, Liquidity)
    - 1 Hour and 1 Day predictions
    - Professional narrative analysis
    """
    try:
        symbol = symbol.replace("-", "/")
        analysis = await analysis_engine.full_analysis(symbol, exchange)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full", response_model=FullAnalysis)
async def post_full_analysis(request: AnalysisRequest):
    """Get full analysis via POST request."""
    try:
        analysis = await analysis_engine.full_analysis(request.symbol, request.exchange)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators/{symbol}", response_model=IndicatorResponse)
async def get_indicators(
    symbol: str,
    timeframe: str = Query(default="1h"),
    exchange: str = Query(default="binance")
):
    """Get technical indicators for a specific timeframe."""
    try:
        symbol = symbol.replace("-", "/")
        df = await exchange_service.get_ohlcv_dataframe(symbol, timeframe, exchange)
        indicators = indicator_service.calculate_all(df)
        return IndicatorResponse(
            symbol=symbol,
            timeframe=timeframe,
            indicators=indicators
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structure/{symbol}")
async def get_structure(
    symbol: str,
    timeframe: str = Query(default="1h"),
    exchange: str = Query(default="binance")
):
    """Get market structure analysis."""
    try:
        symbol = symbol.replace("-", "/")
        df = await exchange_service.get_ohlcv_dataframe(symbol, timeframe, exchange)
        
        structure = structure_service.analyze_structure(df)
        order_blocks = structure_service.find_order_blocks(df, timeframe)
        fvgs = structure_service.find_fair_value_gaps(df)
        liquidity = structure_service.find_liquidity_zones(df)
        sr_levels = structure_service.find_support_resistance(df)
        sd_zones = structure_service.find_supply_demand_zones(df)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "structure": structure,
            "order_blocks": order_blocks,
            "fair_value_gaps": fvgs,
            "liquidity_zones": liquidity,
            "support_resistance": sr_levels,
            "supply_demand_zones": sd_zones
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fibonacci/{symbol}")
async def get_fibonacci(
    symbol: str,
    timeframe: str = Query(default="4h"),
    exchange: str = Query(default="binance"),
    lookback: int = Query(default=100, ge=20, le=500)
):
    """Get Fibonacci retracement levels."""
    try:
        symbol = symbol.replace("-", "/")
        df = await exchange_service.get_ohlcv_dataframe(symbol, timeframe, exchange)
        fib_levels = indicator_service.calculate_fibonacci_levels(df, lookback)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "levels": fib_levels
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/predictions/{symbol}")
async def clear_predictions(
    symbol: str,
    timeframe: str = Query(default=None, description="1h or 1d - leave empty to clear both")
):
    """
    Clear cached predictions for a symbol.
    Use this to force new predictions before the lock expires.
    """
    try:
        symbol = symbol.replace("-", "/")
        prediction_cache.clear_cache(symbol, timeframe)
        return {
            "status": "success",
            "message": f"Predictions cleared for {symbol}" + (f" ({timeframe})" if timeframe else " (all timeframes)")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{symbol}")
async def get_predictions_status(symbol: str):
    """
    Get status of cached predictions for a symbol.
    Shows when predictions were created and when they expire.
    """
    try:
        symbol = symbol.replace("-", "/")
        predictions = prediction_cache.get_all_predictions(symbol)
        
        return {
            "symbol": symbol,
            "predictions": {
                "1h": predictions.get("1h"),
                "1d": predictions.get("1d")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

