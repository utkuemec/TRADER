"""
Technical Indicators Service.
Calculates all major technical indicators using ta library.
"""
import pandas as pd
import numpy as np
from ta import momentum, trend, volatility
from typing import Optional, Dict, Any

from ..models import (
    TechnicalIndicators, MovingAverages, MomentumIndicators, 
    VolatilityIndicators
)


class IndicatorService:
    """Service for calculating technical indicators."""
    
    def calculate_all(self, df: pd.DataFrame) -> TechnicalIndicators:
        """Calculate all technical indicators for a dataframe."""
        if df.empty or len(df) < 20:
            return self._empty_indicators()
        
        ma = self._calculate_moving_averages(df)
        mom = self._calculate_momentum(df)
        vol = self._calculate_volatility(df)
        
        return TechnicalIndicators(
            moving_averages=ma,
            momentum=mom,
            volatility=vol
        )
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> MovingAverages:
        """Calculate moving averages and VWAP."""
        close = df['close']
        
        # EMAs
        ema_9 = trend.ema_indicator(close, window=9)
        ema_21 = trend.ema_indicator(close, window=21)
        ema_50 = trend.ema_indicator(close, window=50)
        ema_100 = trend.ema_indicator(close, window=100) if len(df) >= 100 else pd.Series([None] * len(df))
        ema_200 = trend.ema_indicator(close, window=200) if len(df) >= 200 else pd.Series([None] * len(df))
        
        # SMAs
        sma_20 = trend.sma_indicator(close, window=20)
        sma_50 = trend.sma_indicator(close, window=50)
        sma_200 = trend.sma_indicator(close, window=200) if len(df) >= 200 else pd.Series([None] * len(df))
        
        # VWAP (simplified)
        vwap = self._calculate_vwap(df)
        
        return MovingAverages(
            ema_9=self._safe_last(ema_9),
            ema_21=self._safe_last(ema_21),
            ema_50=self._safe_last(ema_50),
            ema_100=self._safe_last(ema_100),
            ema_200=self._safe_last(ema_200),
            sma_20=self._safe_last(sma_20),
            sma_50=self._safe_last(sma_50),
            sma_200=self._safe_last(sma_200),
            vwap=vwap
        )
    
    def _calculate_vwap(self, df: pd.DataFrame) -> Optional[float]:
        """Calculate Volume Weighted Average Price."""
        try:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            return float(vwap.iloc[-1]) if not pd.isna(vwap.iloc[-1]) else None
        except:
            return None
    
    def _calculate_momentum(self, df: pd.DataFrame) -> MomentumIndicators:
        """Calculate momentum indicators."""
        close = df['close']
        high = df['high']
        low = df['low']
        
        # RSI
        rsi = momentum.rsi(close, window=14)
        rsi_value = self._safe_last(rsi)
        rsi_state = self._get_rsi_state(rsi_value)
        
        # MACD
        macd_obj = trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
        macd_line = self._safe_last(macd_obj.macd())
        macd_signal = self._safe_last(macd_obj.macd_signal())
        macd_histogram = self._safe_last(macd_obj.macd_diff())
        macd_state = self._get_macd_state(macd_line, macd_signal, macd_histogram)
        
        # Stochastic
        stoch = momentum.stoch(high, low, close, window=14, smooth_window=3)
        stoch_signal = momentum.stoch_signal(high, low, close, window=14, smooth_window=3)
        stoch_k = self._safe_last(stoch)
        stoch_d = self._safe_last(stoch_signal)
        stoch_state = self._get_stoch_state(stoch_k, stoch_d)
        
        # CCI
        cci_indicator = trend.cci(high, low, close, window=20)
        
        return MomentumIndicators(
            rsi_14=rsi_value,
            rsi_state=rsi_state,
            macd_line=macd_line,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            macd_state=macd_state,
            stoch_k=stoch_k,
            stoch_d=stoch_d,
            stoch_state=stoch_state,
            cci=self._safe_last(cci_indicator)
        )
    
    def _calculate_volatility(self, df: pd.DataFrame) -> VolatilityIndicators:
        """Calculate volatility indicators."""
        close = df['close']
        high = df['high']
        low = df['low']
        
        # ATR
        atr = volatility.average_true_range(high, low, close, window=14)
        atr_value = self._safe_last(atr)
        atr_percent = (atr_value / close.iloc[-1] * 100) if atr_value and close.iloc[-1] else None
        
        # Bollinger Bands
        bb = volatility.BollingerBands(close, window=20, window_dev=2)
        bb_upper = self._safe_last(bb.bollinger_hband())
        bb_middle = self._safe_last(bb.bollinger_mavg())
        bb_lower = self._safe_last(bb.bollinger_lband())
        
        bb_width = None
        bb_position = None
        
        if bb_upper and bb_lower and bb_middle:
            bb_width = (bb_upper - bb_lower) / bb_middle * 100
            current_price = close.iloc[-1]
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        
        return VolatilityIndicators(
            atr_14=atr_value,
            atr_percent=atr_percent,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            bb_lower=bb_lower,
            bb_width=bb_width,
            bb_position=bb_position
        )
    
    def _get_rsi_state(self, rsi: Optional[float]) -> Optional[str]:
        """Determine RSI state."""
        if rsi is None:
            return None
        if rsi < 30:
            return "Oversold"
        elif rsi > 70:
            return "Overbought"
        elif rsi < 40:
            return "Weakening"
        elif rsi > 60:
            return "Strengthening"
        return "Neutral"
    
    def _get_macd_state(
        self, 
        macd_line: Optional[float], 
        signal: Optional[float],
        histogram: Optional[float]
    ) -> Optional[str]:
        """Determine MACD state."""
        if macd_line is None or signal is None:
            return None
        
        if histogram and histogram > 0:
            if macd_line > 0:
                return "Bullish Momentum"
            return "Bullish Crossover"
        elif histogram and histogram < 0:
            if macd_line < 0:
                return "Bearish Momentum"
            return "Bearish Crossover"
        return "Neutral"
    
    def _get_stoch_state(
        self,
        stoch_k: Optional[float],
        stoch_d: Optional[float]
    ) -> Optional[str]:
        """Determine Stochastic state."""
        if stoch_k is None:
            return None
        
        if stoch_k < 20:
            return "Oversold"
        elif stoch_k > 80:
            return "Overbought"
        elif stoch_k > stoch_d if stoch_d else False:
            return "Bullish"
        elif stoch_k < stoch_d if stoch_d else False:
            return "Bearish"
        return "Neutral"
    
    def _safe_last(self, series: Optional[pd.Series]) -> Optional[float]:
        """Safely get the last value from a series."""
        if series is None or len(series) == 0:
            return None
        try:
            val = series.iloc[-1]
            if pd.isna(val):
                return None
            return round(float(val), 8)
        except:
            return None
    
    def _empty_indicators(self) -> TechnicalIndicators:
        """Return empty indicators structure."""
        return TechnicalIndicators(
            moving_averages=MovingAverages(),
            momentum=MomentumIndicators(),
            volatility=VolatilityIndicators()
        )
    
    def get_ema_alignment(self, ma: MovingAverages) -> str:
        """Determine EMA alignment (Golden/Death cross status)."""
        if not all([ma.ema_9, ma.ema_21, ma.ema_50, ma.ema_200]):
            return "Insufficient data"
        
        # Perfect bullish alignment
        if ma.ema_9 > ma.ema_21 > ma.ema_50 > ma.ema_200:
            return "Perfect Bullish Alignment"
        
        # Perfect bearish alignment
        if ma.ema_9 < ma.ema_21 < ma.ema_50 < ma.ema_200:
            return "Perfect Bearish Alignment"
        
        # Check for golden/death cross
        if ma.ema_50 > ma.ema_200:
            return "Bullish (Above 200 EMA)"
        else:
            return "Bearish (Below 200 EMA)"
    
    def calculate_fibonacci_levels(
        self, 
        df: pd.DataFrame, 
        lookback: int = 100
    ) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels from recent swing."""
        recent = df.tail(lookback)
        high = recent['high'].max()
        low = recent['low'].min()
        diff = high - low
        
        return {
            "high": high,
            "low": low,
            "0.236": high - (diff * 0.236),
            "0.382": high - (diff * 0.382),
            "0.5": high - (diff * 0.5),
            "0.618": high - (diff * 0.618),
            "0.786": high - (diff * 0.786),
            "1.0": low,
            # Extensions
            "1.272": high + (diff * 0.272),
            "1.618": high + (diff * 0.618),
        }


# Singleton instance
indicator_service = IndicatorService()
