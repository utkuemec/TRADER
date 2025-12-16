"""
Advanced Price Predictor - Focused on ACCURACY.
Uses real price action, momentum, and statistical methods for precise predictions.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy import stats
from scipy.signal import find_peaks

from ..models import (
    BiasType, ConfidenceLevel, TechnicalIndicators, KeyLevels,
    TimeframeBias, MarketContext, OrderBlock, FairValueGap, LiquidityZone
)


@dataclass
class PriceTarget:
    """A price target from one analysis method."""
    method: str
    target: float
    confidence: float
    weight: float
    reasoning: str


@dataclass
class AdvancedPrediction:
    """Final prediction with full breakdown."""
    target_price: float
    predicted_low: float
    predicted_high: float
    direction: BiasType
    confidence: float
    targets: List[PriceTarget]
    method_breakdown: Dict[str, float]
    reasoning: str


class AdvancedPredictor:
    """
    Advanced predictor using price action, statistical analysis, and machine learning concepts.
    Focused on ACCURACY over complexity.
    """
    
    def predict(
        self,
        timeframe: str,  # "1h", "1d", "1w"
        current_price: float,
        df: pd.DataFrame,
        indicators: Dict[str, TechnicalIndicators],
        key_levels: KeyLevels,
        tf_biases: List[TimeframeBias],
        order_blocks: List[OrderBlock],
        fvgs: List[FairValueGap],
        liquidity_zones: List[LiquidityZone],
        context: MarketContext
    ) -> AdvancedPrediction:
        """Generate advanced prediction using multiple methods."""
        
        targets: List[PriceTarget] = []
        
        # Get timeframe-specific parameters
        if timeframe == "1h":
            lookback = 60  # Last 60 candles
            projection_weight = 0.3  # How much to project vs current
            primary_tf = "5m" if "5m" in indicators else "15m"
        elif timeframe == "1d":
            lookback = 100
            projection_weight = 0.5
            primary_tf = "1h" if "1h" in indicators else "4h"
        else:  # 1w
            lookback = 200
            projection_weight = 0.7
            primary_tf = "4h" if "4h" in indicators else "1d"
        
        tf_ind = indicators.get(primary_tf) or list(indicators.values())[0]
        recent_df = df.tail(lookback).copy()
        
        # ===== METHOD 1: WEIGHTED PRICE MOMENTUM =====
        # Recent price action is weighted exponentially
        momentum_target = self._weighted_momentum(recent_df, current_price, timeframe)
        if momentum_target:
            targets.append(momentum_target)
        
        # ===== METHOD 2: LINEAR REGRESSION CHANNEL =====
        # Project price along regression line
        regression_target = self._regression_projection(recent_df, current_price, timeframe)
        if regression_target:
            targets.append(regression_target)
        
        # ===== METHOD 3: SUPPORT/RESISTANCE MAGNET =====
        # Price tends to move toward nearest S/R
        sr_target = self._sr_magnet(current_price, key_levels, tf_biases, timeframe)
        if sr_target:
            targets.append(sr_target)
        
        # ===== METHOD 4: MEAN REVERSION =====
        # Price reverts to moving averages
        mean_target = self._mean_reversion(current_price, tf_ind, timeframe)
        if mean_target:
            targets.append(mean_target)
        
        # ===== METHOD 5: VOLATILITY-BASED RANGE =====
        # ATR-based expected move
        vol_target = self._volatility_projection(current_price, tf_ind, recent_df, timeframe)
        if vol_target:
            targets.append(vol_target)
        
        # ===== METHOD 6: RECENT SWING PROJECTION =====
        # Project based on recent swing high/low
        swing_target = self._swing_projection(recent_df, current_price, timeframe)
        if swing_target:
            targets.append(swing_target)
        
        # ===== METHOD 7: PRICE VELOCITY =====
        # Rate of change projection
        velocity_target = self._price_velocity(recent_df, current_price, timeframe)
        if velocity_target:
            targets.append(velocity_target)
        
        # ===== METHOD 8: CANDLE PATTERN PROJECTION =====
        # Recent candle patterns
        pattern_target = self._candle_pattern(recent_df, current_price, timeframe)
        if pattern_target:
            targets.append(pattern_target)
        
        # ===== METHOD 9: ORDER BLOCK ATTRACTION =====
        # Price attracted to unmitigated order blocks
        ob_target = self._order_block_target(current_price, order_blocks, timeframe)
        if ob_target:
            targets.append(ob_target)
        
        # ===== METHOD 10: LIQUIDITY HUNT =====
        # Price moves to sweep liquidity
        liq_target = self._liquidity_target(current_price, liquidity_zones, timeframe)
        if liq_target:
            targets.append(liq_target)
        
        # ===== METHOD 11: FVG FILL =====
        # Price fills fair value gaps
        fvg_target = self._fvg_fill_target(current_price, fvgs, timeframe)
        if fvg_target:
            targets.append(fvg_target)
        
        # ===== METHOD 12: STATISTICAL PROJECTION =====
        # Based on historical moves
        stat_target = self._statistical_projection(recent_df, current_price, timeframe)
        if stat_target:
            targets.append(stat_target)
        
        # ===== METHOD 13: MOMENTUM DIVERGENCE =====
        # RSI/Price divergence detection
        div_target = self._divergence_target(recent_df, current_price, tf_ind, timeframe)
        if div_target:
            targets.append(div_target)
        
        # ===== METHOD 14: CURRENT PRICE ANCHOR =====
        # Heavy weight on current price for short timeframes
        anchor_target = self._current_anchor(current_price, timeframe)
        targets.append(anchor_target)
        
        # Combine all targets
        return self._combine_targets(targets, current_price, timeframe)
    
    def _weighted_momentum(
        self, df: pd.DataFrame, current_price: float, timeframe: str
    ) -> Optional[PriceTarget]:
        """Calculate momentum-weighted price projection."""
        try:
            # Calculate returns
            df['returns'] = df['close'].pct_change()
            
            # Exponential weights - recent data matters more
            n = len(df)
            weights = np.exp(np.linspace(0, 2, n))
            weights = weights / weights.sum()
            
            # Weighted average return
            avg_return = (df['returns'].fillna(0) * weights).sum()
            
            # Project based on timeframe
            if timeframe == "1h":
                periods = 1  # 1 period ahead
                multiplier = 0.5  # Conservative for short term
            elif timeframe == "1d":
                periods = 24
                multiplier = 0.7
            else:
                periods = 168
                multiplier = 0.9
            
            projected_return = avg_return * periods * multiplier
            target = current_price * (1 + projected_return)
            
            # Confidence based on return consistency
            return_std = df['returns'].std()
            confidence = max(0.3, min(0.8, 1 - return_std * 10))
            
            return PriceTarget(
                method="Weighted Momentum",
                target=target,
                confidence=confidence,
                weight=2.0 if timeframe == "1h" else 1.5,
                reasoning=f"Avg return {avg_return*100:.3f}%"
            )
        except:
            return None
    
    def _regression_projection(
        self, df: pd.DataFrame, current_price: float, timeframe: str
    ) -> Optional[PriceTarget]:
        """Linear regression channel projection."""
        try:
            y = df['close'].values
            x = np.arange(len(y))
            
            # Linear regression
            slope, intercept, r_value, _, _ = stats.linregress(x, y)
            
            # Project forward
            if timeframe == "1h":
                forward = 1
            elif timeframe == "1d":
                forward = 24
            else:
                forward = 168
            
            # Regression prediction
            predicted = intercept + slope * (len(y) + forward * 0.3)
            
            # Blend with current price (regression can drift)
            target = predicted * 0.4 + current_price * 0.6
            
            # Confidence based on R-squared
            confidence = abs(r_value) ** 2
            confidence = max(0.3, min(0.85, confidence))
            
            return PriceTarget(
                method="Regression Projection",
                target=target,
                confidence=confidence,
                weight=1.5,
                reasoning=f"Slope ${slope:.2f}, R²={r_value**2:.2f}"
            )
        except:
            return None
    
    def _sr_magnet(
        self, current_price: float, key_levels: KeyLevels, 
        tf_biases: List[TimeframeBias], timeframe: str
    ) -> Optional[PriceTarget]:
        """Price attracted to nearest support/resistance."""
        try:
            # Determine bias direction
            bullish = sum(1 for b in tf_biases if b.bias == BiasType.BULLISH)
            bearish = sum(1 for b in tf_biases if b.bias == BiasType.BEARISH)
            
            if bullish > bearish:
                # Target resistance
                if key_levels.immediate_resistance:
                    target = key_levels.immediate_resistance
                    # Don't overshoot - stay slightly below
                    target = current_price + (target - current_price) * 0.7
                else:
                    return None
            elif bearish > bullish:
                # Target support
                if key_levels.immediate_support:
                    target = key_levels.immediate_support
                    # Don't undershoot - stay slightly above
                    target = current_price - (current_price - target) * 0.7
                else:
                    return None
            else:
                # Neutral - closest level
                levels = []
                if key_levels.immediate_support:
                    levels.append(key_levels.immediate_support)
                if key_levels.immediate_resistance:
                    levels.append(key_levels.immediate_resistance)
                if not levels:
                    return None
                target = min(levels, key=lambda x: abs(x - current_price))
                target = current_price + (target - current_price) * 0.5
            
            distance = abs(target - current_price) / current_price
            # Higher confidence if target is close
            confidence = max(0.4, 0.9 - distance * 10)
            
            return PriceTarget(
                method="S/R Magnet",
                target=target,
                confidence=confidence,
                weight=2.5 if timeframe == "1h" else 2.0,
                reasoning=f"Nearest level attraction"
            )
        except:
            return None
    
    def _mean_reversion(
        self, current_price: float, indicators: TechnicalIndicators, timeframe: str
    ) -> Optional[PriceTarget]:
        """Mean reversion to moving averages."""
        try:
            ma = indicators.moving_averages
            
            # Get relevant MAs
            targets = []
            if ma.ema_21:
                targets.append(("EMA21", ma.ema_21, 1.5))
            if ma.sma_20:
                targets.append(("SMA20", ma.sma_20, 1.2))
            if ma.vwap:
                targets.append(("VWAP", ma.vwap, 2.0))
            
            if not targets:
                return None
            
            # Weighted average of MAs
            total_weight = sum(t[2] for t in targets)
            target = sum(t[1] * t[2] for t in targets) / total_weight
            
            # Blend with current price
            if timeframe == "1h":
                blend = 0.3  # For 1h, don't expect full reversion
            elif timeframe == "1d":
                blend = 0.5
            else:
                blend = 0.7
            
            target = target * blend + current_price * (1 - blend)
            
            # Confidence based on distance
            distance = abs(target - current_price) / current_price
            confidence = max(0.4, 0.85 - distance * 5)
            
            return PriceTarget(
                method="Mean Reversion",
                target=target,
                confidence=confidence,
                weight=1.8,
                reasoning=f"Reversion to MAs"
            )
        except:
            return None
    
    def _volatility_projection(
        self, current_price: float, indicators: TechnicalIndicators,
        df: pd.DataFrame, timeframe: str
    ) -> Optional[PriceTarget]:
        """ATR and Bollinger-based projection."""
        try:
            vol = indicators.volatility
            
            if not vol.atr_14:
                return None
            
            atr = vol.atr_14
            
            # Recent trend direction
            recent_returns = df['close'].pct_change().tail(10).mean()
            
            if recent_returns > 0:
                direction = 1
            elif recent_returns < 0:
                direction = -1
            else:
                direction = 0
            
            # Expected move based on timeframe
            if timeframe == "1h":
                multiplier = 0.2  # Small move for 1h
            elif timeframe == "1d":
                multiplier = 0.8
            else:
                multiplier = 2.5
            
            expected_move = atr * multiplier * direction
            target = current_price + expected_move
            
            return PriceTarget(
                method="Volatility Projection",
                target=target,
                confidence=0.6,
                weight=1.5,
                reasoning=f"ATR ${atr:.2f} x {multiplier}"
            )
        except:
            return None
    
    def _swing_projection(
        self, df: pd.DataFrame, current_price: float, timeframe: str
    ) -> Optional[PriceTarget]:
        """Project based on recent swing structure."""
        try:
            highs = df['high'].values
            lows = df['low'].values
            
            # Find swing points
            high_peaks, _ = find_peaks(highs, distance=5)
            low_peaks, _ = find_peaks(-lows, distance=5)
            
            if len(high_peaks) < 2 or len(low_peaks) < 2:
                return None
            
            # Recent swing high and low
            recent_high = highs[high_peaks[-1]]
            recent_low = lows[low_peaks[-1]]
            
            # Current position in range
            range_size = recent_high - recent_low
            position = (current_price - recent_low) / range_size if range_size > 0 else 0.5
            
            # Project based on position
            if position > 0.7:
                # Near top - expect pullback or breakout
                target = recent_high * 0.6 + recent_low * 0.4  # Slight pullback
            elif position < 0.3:
                # Near bottom - expect bounce or breakdown
                target = recent_low * 0.6 + recent_high * 0.4  # Slight bounce
            else:
                # Middle - project based on recent momentum
                target = current_price  # Stay neutral
            
            return PriceTarget(
                method="Swing Projection",
                target=target,
                confidence=0.55,
                weight=1.3,
                reasoning=f"Position {position:.0%} in range"
            )
        except:
            return None
    
    def _price_velocity(
        self, df: pd.DataFrame, current_price: float, timeframe: str
    ) -> Optional[PriceTarget]:
        """Price rate of change projection."""
        try:
            # Calculate velocity (rate of change)
            df['velocity'] = df['close'].diff()
            df['acceleration'] = df['velocity'].diff()
            
            # Recent velocity and acceleration
            recent_velocity = df['velocity'].tail(5).mean()
            recent_accel = df['acceleration'].tail(5).mean()
            
            # Project with deceleration factor
            if timeframe == "1h":
                periods = 1
                decel = 0.3
            elif timeframe == "1d":
                periods = 24
                decel = 0.5
            else:
                periods = 168
                decel = 0.7
            
            # Projected move considering acceleration
            projected_move = recent_velocity * periods * decel
            if recent_accel < 0 and recent_velocity > 0:
                projected_move *= 0.7  # Momentum slowing
            elif recent_accel > 0 and recent_velocity < 0:
                projected_move *= 0.7  # Momentum slowing
            
            target = current_price + projected_move
            
            return PriceTarget(
                method="Price Velocity",
                target=target,
                confidence=0.5,
                weight=2.0 if timeframe == "1h" else 1.5,
                reasoning=f"Velocity ${recent_velocity:.2f}/period"
            )
        except:
            return None
    
    def _candle_pattern(
        self, df: pd.DataFrame, current_price: float, timeframe: str
    ) -> Optional[PriceTarget]:
        """Recent candle pattern analysis."""
        try:
            last_candles = df.tail(5)
            
            # Calculate candle characteristics
            bodies = last_candles['close'] - last_candles['open']
            wicks_up = last_candles['high'] - last_candles[['open', 'close']].max(axis=1)
            wicks_down = last_candles[['open', 'close']].min(axis=1) - last_candles['low']
            
            # Bullish or bearish bias
            avg_body = bodies.mean()
            avg_range = (last_candles['high'] - last_candles['low']).mean()
            
            if avg_body > 0:
                # Bullish candles
                target = current_price + avg_range * 0.3
            elif avg_body < 0:
                # Bearish candles
                target = current_price - avg_range * 0.3
            else:
                target = current_price
            
            return PriceTarget(
                method="Candle Pattern",
                target=target,
                confidence=0.45,
                weight=1.5 if timeframe == "1h" else 1.0,
                reasoning=f"Avg body ${avg_body:.2f}"
            )
        except:
            return None
    
    def _order_block_target(
        self, current_price: float, order_blocks: List[OrderBlock], timeframe: str
    ) -> Optional[PriceTarget]:
        """Nearest unmitigated order block as target."""
        try:
            active = [ob for ob in order_blocks if not ob.mitigated]
            if not active:
                return None
            
            # Find nearest OB
            nearest = min(active, key=lambda ob: abs((ob.price_high + ob.price_low)/2 - current_price))
            ob_mid = (nearest.price_high + nearest.price_low) / 2
            
            # Blend with current price
            blend = 0.3 if timeframe == "1h" else 0.5
            target = ob_mid * blend + current_price * (1 - blend)
            
            return PriceTarget(
                method="Order Block",
                target=target,
                confidence=0.6,
                weight=1.5,
                reasoning=f"{nearest.block_type} at ${ob_mid:,.2f}"
            )
        except:
            return None
    
    def _liquidity_target(
        self, current_price: float, liquidity_zones: List[LiquidityZone], timeframe: str
    ) -> Optional[PriceTarget]:
        """Nearest liquidity pool as target."""
        try:
            active = [lz for lz in liquidity_zones if not lz.swept]
            if not active:
                return None
            
            # Find nearest unswept liquidity
            nearest = min(active, key=lambda lz: abs((lz.price_start + lz.price_end)/2 - current_price))
            liq_mid = (nearest.price_start + nearest.price_end) / 2
            
            # Blend with current price
            blend = 0.25 if timeframe == "1h" else 0.4
            target = liq_mid * blend + current_price * (1 - blend)
            
            return PriceTarget(
                method="Liquidity Hunt",
                target=target,
                confidence=0.5,
                weight=1.2,
                reasoning=f"{nearest.zone_type} liquidity"
            )
        except:
            return None
    
    def _fvg_fill_target(
        self, current_price: float, fvgs: List[FairValueGap], timeframe: str
    ) -> Optional[PriceTarget]:
        """Nearest unfilled FVG as target."""
        try:
            unfilled = [fvg for fvg in fvgs if not fvg.filled]
            if not unfilled:
                return None
            
            # Find nearest FVG
            nearest = min(unfilled, key=lambda fvg: abs((fvg.high + fvg.low)/2 - current_price))
            fvg_mid = (nearest.high + nearest.low) / 2
            
            # Blend with current price
            blend = 0.2 if timeframe == "1h" else 0.35
            target = fvg_mid * blend + current_price * (1 - blend)
            
            return PriceTarget(
                method="FVG Fill",
                target=target,
                confidence=0.55,
                weight=1.3,
                reasoning=f"{nearest.gap_type}"
            )
        except:
            return None
    
    def _statistical_projection(
        self, df: pd.DataFrame, current_price: float, timeframe: str
    ) -> Optional[PriceTarget]:
        """Statistical analysis of historical moves."""
        try:
            returns = df['close'].pct_change().dropna()
            
            # Mean and std of returns
            mean_return = returns.mean()
            std_return = returns.std()
            
            # Expected return based on timeframe
            if timeframe == "1h":
                periods = 1
            elif timeframe == "1d":
                periods = 24
            else:
                periods = 168
            
            # Use mean + small portion of std for directional bias
            expected = mean_return * periods
            
            # Conservative projection
            target = current_price * (1 + expected * 0.5)
            
            # Confidence based on return distribution
            skew = stats.skew(returns)
            confidence = max(0.4, 0.7 - abs(skew) * 0.1)
            
            return PriceTarget(
                method="Statistical",
                target=target,
                confidence=confidence,
                weight=1.2,
                reasoning=f"Mean return {mean_return*100:.3f}%"
            )
        except:
            return None
    
    def _divergence_target(
        self, df: pd.DataFrame, current_price: float, 
        indicators: TechnicalIndicators, timeframe: str
    ) -> Optional[PriceTarget]:
        """RSI divergence detection."""
        try:
            if not indicators.momentum.rsi_14:
                return None
            
            rsi = indicators.momentum.rsi_14
            
            # Recent price and RSI trends
            recent_prices = df['close'].tail(10)
            price_trend = recent_prices.iloc[-1] - recent_prices.iloc[0]
            
            # Simplified divergence check
            if price_trend > 0 and rsi < 50:
                # Bearish divergence - price up but RSI weak
                target = current_price * 0.997
            elif price_trend < 0 and rsi > 50:
                # Bullish divergence - price down but RSI strong
                target = current_price * 1.003
            else:
                target = current_price
            
            return PriceTarget(
                method="Divergence",
                target=target,
                confidence=0.45,
                weight=1.0,
                reasoning=f"RSI {rsi:.1f}"
            )
        except:
            return None
    
    def _current_anchor(self, current_price: float, timeframe: str) -> PriceTarget:
        """
        Heavy anchor on current price - CRITICAL for short-term accuracy.
        The closer the timeframe, the more we anchor to current price.
        """
        if timeframe == "1h":
            weight = 5.0  # Very high weight for 1h
            confidence = 0.9
        elif timeframe == "1d":
            weight = 3.0
            confidence = 0.7
        else:
            weight = 2.0
            confidence = 0.5
        
        return PriceTarget(
            method="Current Price Anchor",
            target=current_price,
            confidence=confidence,
            weight=weight,
            reasoning="Anchored to current price"
        )
    
    def _combine_targets(
        self, targets: List[PriceTarget], current_price: float, timeframe: str
    ) -> AdvancedPrediction:
        """Combine all targets into final prediction."""
        
        if not targets:
            return self._fallback(current_price, timeframe)
        
        # Weighted average
        total_weight = sum(t.weight * t.confidence for t in targets)
        if total_weight == 0:
            return self._fallback(current_price, timeframe)
        
        weighted_target = sum(t.target * t.weight * t.confidence for t in targets) / total_weight
        
        # Calculate standard deviation of targets
        target_values = [t.target for t in targets]
        std_dev = np.std(target_values) if len(target_values) > 1 else 0
        
        # Determine direction
        if weighted_target > current_price * 1.001:
            direction = BiasType.BULLISH
        elif weighted_target < current_price * 0.999:
            direction = BiasType.BEARISH
        else:
            direction = BiasType.NEUTRAL
        
        # Calculate range based on timeframe and agreement
        if timeframe == "1h":
            base_range_pct = 0.003  # 0.3% range for 1h
        elif timeframe == "1d":
            base_range_pct = 0.015
        else:
            base_range_pct = 0.05
        
        # Adjust range based on target agreement
        agreement = 1 - (std_dev / current_price) if current_price > 0 else 1
        range_pct = base_range_pct * (2 - agreement)
        range_pct = max(base_range_pct, min(range_pct, base_range_pct * 3))
        
        range_amount = current_price * range_pct
        
        # Calculate bounds
        predicted_low = min(current_price, weighted_target) - range_amount * 0.5
        predicted_high = max(current_price, weighted_target) + range_amount * 0.5
        
        # Ensure low < high
        if predicted_low > predicted_high:
            predicted_low, predicted_high = predicted_high, predicted_low
        
        # Overall confidence
        avg_confidence = np.mean([t.confidence for t in targets])
        method_bonus = min(0.15, len(targets) * 0.01)
        overall_confidence = min(0.95, avg_confidence + method_bonus)
        
        # Method breakdown
        breakdown = {t.method: t.target for t in targets}
        
        # Top 3 methods for reasoning
        sorted_targets = sorted(targets, key=lambda t: t.weight * t.confidence, reverse=True)[:3]
        reasoning_parts = [f"Combined {len(targets)} methods"]
        for t in sorted_targets:
            reasoning_parts.append(f"{t.method}: ${t.target:,.2f}")
        
        return AdvancedPrediction(
            target_price=round(weighted_target, 2),
            predicted_low=round(predicted_low, 2),
            predicted_high=round(predicted_high, 2),
            direction=direction,
            confidence=overall_confidence,
            targets=targets,
            method_breakdown=breakdown,
            reasoning="; ".join(reasoning_parts)
        )
    
    def _fallback(self, current_price: float, timeframe: str) -> AdvancedPrediction:
        """Fallback prediction."""
        range_pct = {"1h": 0.002, "1d": 0.01, "1w": 0.03}.get(timeframe, 0.01)
        return AdvancedPrediction(
            target_price=current_price,
            predicted_low=current_price * (1 - range_pct),
            predicted_high=current_price * (1 + range_pct),
            direction=BiasType.NEUTRAL,
            confidence=0.5,
            targets=[],
            method_breakdown={},
            reasoning="Fallback - insufficient data"
        )


# Singleton
advanced_predictor = AdvancedPredictor()

