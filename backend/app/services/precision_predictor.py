"""
Precision Price Predictor.
Uses multiple advanced analysis methods to generate pinpoint price predictions.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..models import (
    BiasType, ConfidenceLevel, TechnicalIndicators, KeyLevels,
    TimeframeBias, MarketContext, OrderBlock, FairValueGap, LiquidityZone
)


class PredictionMethod(Enum):
    FIBONACCI = "Fibonacci Extension/Retracement"
    VWAP_DEVIATION = "VWAP Standard Deviation"
    ORDER_FLOW = "Order Flow / Order Blocks"
    LIQUIDITY_TARGET = "Liquidity Pool Targeting"
    MEAN_REVERSION = "Mean Reversion / Bollinger"
    MOMENTUM_PROJECTION = "Momentum-Based Projection"
    VOLUME_PROFILE = "Volume Profile Analysis"
    PATTERN_MEASURED_MOVE = "Pattern Measured Move"
    CONFLUENCE_CLUSTER = "S/R Confluence Cluster"
    TREND_PROJECTION = "Trend Line Projection"


@dataclass
class PredictionSignal:
    """A single prediction signal from one method."""
    method: PredictionMethod
    target_price: float
    confidence: float  # 0-1
    direction: BiasType
    reasoning: str
    weight: float  # How much this signal should count


@dataclass
class PrecisionPrediction:
    """Final precision prediction combining all methods."""
    target_price: float
    predicted_low: float
    predicted_high: float
    direction: BiasType
    confidence: float
    signals: List[PredictionSignal]
    weighted_average: float
    standard_deviation: float
    method_breakdown: Dict[str, float]


class PrecisionPredictor:
    """
    Advanced price predictor using multiple analysis methods.
    Combines signals from various techniques to produce a precise target.
    """
    
    def __init__(self):
        # Method weights (can be adjusted based on backtesting)
        self.method_weights = {
            PredictionMethod.FIBONACCI: 1.5,
            PredictionMethod.VWAP_DEVIATION: 1.2,
            PredictionMethod.ORDER_FLOW: 1.4,
            PredictionMethod.LIQUIDITY_TARGET: 1.6,
            PredictionMethod.MEAN_REVERSION: 1.0,
            PredictionMethod.MOMENTUM_PROJECTION: 1.3,
            PredictionMethod.VOLUME_PROFILE: 1.1,
            PredictionMethod.PATTERN_MEASURED_MOVE: 1.2,
            PredictionMethod.CONFLUENCE_CLUSTER: 1.5,
            PredictionMethod.TREND_PROJECTION: 1.0,
        }
    
    def predict(
        self,
        timeframe: str,
        current_price: float,
        df: pd.DataFrame,
        indicators: Dict[str, TechnicalIndicators],
        key_levels: KeyLevels,
        tf_biases: List[TimeframeBias],
        order_blocks: List[OrderBlock],
        fvgs: List[FairValueGap],
        liquidity_zones: List[LiquidityZone],
        context: MarketContext
    ) -> PrecisionPrediction:
        """
        Generate precision prediction using all available methods.
        """
        signals: List[PredictionSignal] = []
        
        # Determine primary timeframe for analysis
        analysis_tf = self._get_analysis_timeframe(timeframe)
        tf_indicators = indicators.get(analysis_tf) or indicators.get("1h")
        
        if tf_indicators is None:
            # Fallback if no indicators available
            return self._create_fallback_prediction(current_price, timeframe)
        
        # Determine overall bias from timeframe biases
        overall_bias = self._determine_overall_bias(tf_biases, timeframe)
        
        # 1. Fibonacci Analysis
        fib_signal = self._fibonacci_analysis(
            df, current_price, overall_bias, timeframe
        )
        if fib_signal:
            signals.append(fib_signal)
        
        # 2. VWAP Deviation Analysis
        vwap_signal = self._vwap_analysis(
            current_price, tf_indicators, overall_bias, timeframe
        )
        if vwap_signal:
            signals.append(vwap_signal)
        
        # 3. Order Flow / Order Block Analysis
        ob_signal = self._order_block_analysis(
            current_price, order_blocks, overall_bias, timeframe
        )
        if ob_signal:
            signals.append(ob_signal)
        
        # 4. Liquidity Target Analysis
        liq_signal = self._liquidity_analysis(
            current_price, liquidity_zones, overall_bias, timeframe
        )
        if liq_signal:
            signals.append(liq_signal)
        
        # 5. Mean Reversion / Bollinger Analysis
        bb_signal = self._bollinger_analysis(
            current_price, tf_indicators, overall_bias, timeframe
        )
        if bb_signal:
            signals.append(bb_signal)
        
        # 6. Momentum Projection
        momentum_signal = self._momentum_projection(
            df, current_price, tf_indicators, overall_bias, timeframe
        )
        if momentum_signal:
            signals.append(momentum_signal)
        
        # 7. Volume Profile Analysis
        vol_signal = self._volume_profile_analysis(
            df, current_price, overall_bias, timeframe
        )
        if vol_signal:
            signals.append(vol_signal)
        
        # 8. Pattern Measured Move
        pattern_signal = self._pattern_analysis(
            df, current_price, key_levels, overall_bias, timeframe
        )
        if pattern_signal:
            signals.append(pattern_signal)
        
        # 9. S/R Confluence Cluster
        confluence_signal = self._confluence_analysis(
            current_price, key_levels, order_blocks, fvgs, overall_bias, timeframe
        )
        if confluence_signal:
            signals.append(confluence_signal)
        
        # 10. Trend Projection
        trend_signal = self._trend_projection(
            df, current_price, tf_indicators, overall_bias, timeframe
        )
        if trend_signal:
            signals.append(trend_signal)
        
        # 11. FVG (Fair Value Gap) Target
        fvg_signal = self._fvg_analysis(
            current_price, fvgs, overall_bias, timeframe
        )
        if fvg_signal:
            signals.append(fvg_signal)
        
        # 12. ATR-Based Projection
        atr_signal = self._atr_projection(
            current_price, tf_indicators, overall_bias, timeframe
        )
        if atr_signal:
            signals.append(atr_signal)
        
        # Combine all signals into final prediction
        return self._combine_signals(signals, current_price, overall_bias, timeframe)
    
    def _get_analysis_timeframe(self, timeframe: str) -> str:
        """Get the primary analysis timeframe."""
        if timeframe == "1h":
            return "1h"
        elif timeframe == "1d":
            return "4h"
        else:  # 1w
            return "1d"
    
    def _determine_overall_bias(
        self, tf_biases: List[TimeframeBias], timeframe: str
    ) -> BiasType:
        """Determine overall bias based on timeframe biases."""
        if timeframe == "1h":
            relevant = [b for b in tf_biases if b.timeframe in ["5m", "15m", "30m", "1h"]]
        elif timeframe == "1d":
            relevant = [b for b in tf_biases if b.timeframe in ["1h", "4h", "1d"]]
        else:
            relevant = [b for b in tf_biases if b.timeframe in ["4h", "1d"]]
        
        bullish = sum(1 for b in relevant if b.bias == BiasType.BULLISH)
        bearish = sum(1 for b in relevant if b.bias == BiasType.BEARISH)
        
        if bullish > bearish:
            return BiasType.BULLISH
        elif bearish > bullish:
            return BiasType.BEARISH
        return BiasType.NEUTRAL
    
    def _fibonacci_analysis(
        self, df: pd.DataFrame, current_price: float, 
        bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        Calculate Fibonacci extension/retracement targets.
        """
        try:
            # Find recent swing high and low
            lookback = {"1h": 50, "1d": 100, "1w": 200}.get(timeframe, 100)
            recent = df.tail(lookback)
            
            swing_high = recent['high'].max()
            swing_low = recent['low'].min()
            swing_range = swing_high - swing_low
            
            if swing_range == 0:
                return None
            
            # Fibonacci levels
            fib_levels = {
                0.236: swing_low + swing_range * 0.236,
                0.382: swing_low + swing_range * 0.382,
                0.5: swing_low + swing_range * 0.5,
                0.618: swing_low + swing_range * 0.618,
                0.786: swing_low + swing_range * 0.786,
                1.0: swing_high,
                1.272: swing_low + swing_range * 1.272,
                1.618: swing_low + swing_range * 1.618,
            }
            
            # Find nearest Fibonacci target based on bias
            if bias == BiasType.BULLISH:
                # Look for levels above current price
                targets = [(lvl, price) for lvl, price in fib_levels.items() 
                          if price > current_price]
                if targets:
                    target_level, target_price = min(targets, key=lambda x: x[1])
                else:
                    target_price = swing_high
            elif bias == BiasType.BEARISH:
                # Look for levels below current price
                targets = [(lvl, price) for lvl, price in fib_levels.items() 
                          if price < current_price]
                if targets:
                    target_level, target_price = max(targets, key=lambda x: x[1])
                else:
                    target_price = swing_low
            else:
                # Neutral - target middle
                target_price = fib_levels[0.5]
            
            # Confidence based on how close current price is to a fib level
            distances = [abs(current_price - p) / current_price for p in fib_levels.values()]
            min_distance = min(distances)
            confidence = max(0.5, 1 - min_distance * 10)  # Higher confidence if near fib level
            
            return PredictionSignal(
                method=PredictionMethod.FIBONACCI,
                target_price=target_price,
                confidence=confidence,
                direction=bias,
                reasoning=f"Fib target at ${target_price:,.2f} (swing range ${swing_range:,.2f})",
                weight=self.method_weights[PredictionMethod.FIBONACCI]
            )
        except Exception:
            return None
    
    def _vwap_analysis(
        self, current_price: float, indicators: TechnicalIndicators,
        bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        VWAP deviation analysis for mean reversion targets.
        """
        try:
            vwap = indicators.moving_averages.vwap
            if not vwap:
                return None
            
            # Calculate deviation from VWAP
            deviation = current_price - vwap
            deviation_pct = (deviation / vwap) * 100
            
            # VWAP bands (approximate standard deviations)
            atr = indicators.volatility.atr_14 or (current_price * 0.01)
            vwap_upper = vwap + atr * 2
            vwap_lower = vwap - atr * 2
            
            if bias == BiasType.BULLISH:
                if current_price < vwap:
                    # Below VWAP - target VWAP or upper band
                    target_price = vwap
                else:
                    # Above VWAP - target upper band
                    target_price = vwap_upper
            elif bias == BiasType.BEARISH:
                if current_price > vwap:
                    # Above VWAP - target VWAP or lower band
                    target_price = vwap
                else:
                    # Below VWAP - target lower band
                    target_price = vwap_lower
            else:
                # Neutral - target VWAP
                target_price = vwap
            
            # Confidence based on deviation
            confidence = max(0.4, min(0.9, 1 - abs(deviation_pct) / 5))
            
            return PredictionSignal(
                method=PredictionMethod.VWAP_DEVIATION,
                target_price=target_price,
                confidence=confidence,
                direction=bias,
                reasoning=f"VWAP ${vwap:,.2f}, deviation {deviation_pct:.2f}%",
                weight=self.method_weights[PredictionMethod.VWAP_DEVIATION]
            )
        except Exception:
            return None
    
    def _order_block_analysis(
        self, current_price: float, order_blocks: List[OrderBlock],
        bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        Analyze order blocks for price targets.
        """
        try:
            if not order_blocks:
                return None
            
            # Filter unmitigated order blocks
            active_obs = [ob for ob in order_blocks if not ob.mitigated]
            if not active_obs:
                return None
            
            if bias == BiasType.BULLISH:
                # Look for bullish OBs below price (support)
                bullish_obs = [ob for ob in active_obs 
                              if ob.block_type == "Bullish OB" and ob.price_high < current_price]
                if bullish_obs:
                    # Target the highest bullish OB
                    target_ob = max(bullish_obs, key=lambda x: x.price_high)
                    target_price = target_ob.price_high
                else:
                    # Look for bearish OBs above price (target)
                    bearish_obs = [ob for ob in active_obs 
                                  if ob.block_type == "Bearish OB" and ob.price_low > current_price]
                    if bearish_obs:
                        target_ob = min(bearish_obs, key=lambda x: x.price_low)
                        target_price = target_ob.price_low
                    else:
                        return None
            elif bias == BiasType.BEARISH:
                # Look for bearish OBs above price (resistance)
                bearish_obs = [ob for ob in active_obs 
                              if ob.block_type == "Bearish OB" and ob.price_low > current_price]
                if bearish_obs:
                    target_ob = min(bearish_obs, key=lambda x: x.price_low)
                    target_price = target_ob.price_low
                else:
                    # Look for bullish OBs below price (target)
                    bullish_obs = [ob for ob in active_obs 
                                  if ob.block_type == "Bullish OB" and ob.price_high < current_price]
                    if bullish_obs:
                        target_ob = max(bullish_obs, key=lambda x: x.price_high)
                        target_price = target_ob.price_high
                    else:
                        return None
            else:
                # Neutral - find nearest OB
                all_obs = [(ob, abs(current_price - (ob.price_high + ob.price_low) / 2)) 
                          for ob in active_obs]
                if all_obs:
                    nearest = min(all_obs, key=lambda x: x[1])
                    target_price = (nearest[0].price_high + nearest[0].price_low) / 2
                else:
                    return None
            
            return PredictionSignal(
                method=PredictionMethod.ORDER_FLOW,
                target_price=target_price,
                confidence=0.75,
                direction=bias,
                reasoning=f"Order block target at ${target_price:,.2f}",
                weight=self.method_weights[PredictionMethod.ORDER_FLOW]
            )
        except Exception:
            return None
    
    def _liquidity_analysis(
        self, current_price: float, liquidity_zones: List[LiquidityZone],
        bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        Identify liquidity pool targets.
        """
        try:
            if not liquidity_zones:
                return None
            
            # Filter unswept liquidity
            active_liq = [lz for lz in liquidity_zones if not lz.swept]
            if not active_liq:
                return None
            
            if bias == BiasType.BULLISH:
                # Target buy-side liquidity above
                buy_side = [lz for lz in active_liq 
                           if lz.zone_type == "Buy-side" and lz.price_start > current_price]
                if buy_side:
                    target = min(buy_side, key=lambda x: x.price_start)
                    target_price = target.price_start
                else:
                    return None
            elif bias == BiasType.BEARISH:
                # Target sell-side liquidity below
                sell_side = [lz for lz in active_liq 
                            if lz.zone_type == "Sell-side" and lz.price_end < current_price]
                if sell_side:
                    target = max(sell_side, key=lambda x: x.price_end)
                    target_price = target.price_end
                else:
                    return None
            else:
                return None
            
            # Higher confidence for strong liquidity zones
            confidence = 0.8 if target.strength == "Strong" else 0.6
            
            return PredictionSignal(
                method=PredictionMethod.LIQUIDITY_TARGET,
                target_price=target_price,
                confidence=confidence,
                direction=bias,
                reasoning=f"Liquidity pool target at ${target_price:,.2f} ({target.strength})",
                weight=self.method_weights[PredictionMethod.LIQUIDITY_TARGET]
            )
        except Exception:
            return None
    
    def _bollinger_analysis(
        self, current_price: float, indicators: TechnicalIndicators,
        bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        Bollinger Band analysis for mean reversion.
        """
        try:
            bb = indicators.volatility
            if not bb.bb_upper or not bb.bb_lower:
                return None
            
            bb_upper = bb.bb_upper
            bb_middle = bb.bb_middle
            bb_lower = bb.bb_lower
            bb_position = bb.bb_position  # 0 = lower, 0.5 = middle, 1 = upper
            
            if bias == BiasType.BULLISH:
                if bb_position < 0.3:
                    # Near lower band - target middle
                    target_price = bb_middle
                    confidence = 0.7
                elif bb_position < 0.7:
                    # Middle - target upper
                    target_price = bb_upper
                    confidence = 0.6
                else:
                    # Near upper - slight pullback then higher
                    target_price = bb_upper + (bb_upper - bb_middle) * 0.5
                    confidence = 0.5
            elif bias == BiasType.BEARISH:
                if bb_position > 0.7:
                    # Near upper band - target middle
                    target_price = bb_middle
                    confidence = 0.7
                elif bb_position > 0.3:
                    # Middle - target lower
                    target_price = bb_lower
                    confidence = 0.6
                else:
                    # Near lower - slight bounce then lower
                    target_price = bb_lower - (bb_middle - bb_lower) * 0.5
                    confidence = 0.5
            else:
                # Neutral - target middle
                target_price = bb_middle
                confidence = 0.5
            
            return PredictionSignal(
                method=PredictionMethod.MEAN_REVERSION,
                target_price=target_price,
                confidence=confidence,
                direction=bias,
                reasoning=f"BB position {bb_position:.2f}, target ${target_price:,.2f}",
                weight=self.method_weights[PredictionMethod.MEAN_REVERSION]
            )
        except Exception:
            return None
    
    def _momentum_projection(
        self, df: pd.DataFrame, current_price: float, 
        indicators: TechnicalIndicators, bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        Project price based on momentum indicators.
        """
        try:
            rsi = indicators.momentum.rsi_14
            macd_hist = indicators.momentum.macd_histogram
            
            if rsi is None:
                return None
            
            # Calculate recent price velocity
            lookback = {"1h": 10, "1d": 20, "1w": 50}.get(timeframe, 20)
            recent = df.tail(lookback)
            price_change = (recent['close'].iloc[-1] - recent['close'].iloc[0])
            velocity = price_change / lookback
            
            # Project based on momentum
            projection_periods = {"1h": 1, "1d": 24, "1w": 168}.get(timeframe, 24)
            
            # Adjust velocity based on RSI (overbought/oversold)
            if rsi > 70:
                velocity *= 0.5 if bias == BiasType.BULLISH else 1.5
            elif rsi < 30:
                velocity *= 1.5 if bias == BiasType.BULLISH else 0.5
            
            # MACD confirmation
            if macd_hist:
                if macd_hist > 0 and bias == BiasType.BULLISH:
                    velocity *= 1.2
                elif macd_hist < 0 and bias == BiasType.BEARISH:
                    velocity *= 1.2
            
            target_price = current_price + (velocity * projection_periods * 0.5)
            
            # Confidence based on RSI extremes and MACD alignment
            confidence = 0.6
            if (rsi > 60 and bias == BiasType.BULLISH) or (rsi < 40 and bias == BiasType.BEARISH):
                confidence = 0.7
            
            return PredictionSignal(
                method=PredictionMethod.MOMENTUM_PROJECTION,
                target_price=target_price,
                confidence=confidence,
                direction=bias,
                reasoning=f"RSI {rsi:.1f}, velocity ${velocity:.2f}/period",
                weight=self.method_weights[PredictionMethod.MOMENTUM_PROJECTION]
            )
        except Exception:
            return None
    
    def _volume_profile_analysis(
        self, df: pd.DataFrame, current_price: float,
        bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        Identify high volume nodes as price targets.
        """
        try:
            lookback = {"1h": 50, "1d": 100, "1w": 200}.get(timeframe, 100)
            recent = df.tail(lookback)
            
            # Create simple volume profile
            price_bins = 50
            price_range = recent['high'].max() - recent['low'].min()
            bin_size = price_range / price_bins
            
            volume_profile = {}
            for _, row in recent.iterrows():
                price_level = round(row['close'] / bin_size) * bin_size
                volume_profile[price_level] = volume_profile.get(price_level, 0) + row['volume']
            
            if not volume_profile:
                return None
            
            # Find high volume nodes (HVN)
            sorted_nodes = sorted(volume_profile.items(), key=lambda x: x[1], reverse=True)
            top_nodes = sorted_nodes[:5]
            
            # Find nearest HVN in direction of bias
            if bias == BiasType.BULLISH:
                targets = [(p, v) for p, v in top_nodes if p > current_price]
                if targets:
                    target_price = min(targets, key=lambda x: x[0])[0]
                else:
                    target_price = max(p for p, v in top_nodes)
            elif bias == BiasType.BEARISH:
                targets = [(p, v) for p, v in top_nodes if p < current_price]
                if targets:
                    target_price = max(targets, key=lambda x: x[0])[0]
                else:
                    target_price = min(p for p, v in top_nodes)
            else:
                # Find POC (Point of Control)
                target_price = sorted_nodes[0][0]
            
            return PredictionSignal(
                method=PredictionMethod.VOLUME_PROFILE,
                target_price=target_price,
                confidence=0.65,
                direction=bias,
                reasoning=f"High volume node at ${target_price:,.2f}",
                weight=self.method_weights[PredictionMethod.VOLUME_PROFILE]
            )
        except Exception:
            return None
    
    def _pattern_analysis(
        self, df: pd.DataFrame, current_price: float, key_levels: KeyLevels,
        bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        Measure move based on recent pattern range.
        """
        try:
            lookback = {"1h": 30, "1d": 50, "1w": 100}.get(timeframe, 50)
            recent = df.tail(lookback)
            
            # Calculate recent range as potential measured move
            recent_high = recent['high'].max()
            recent_low = recent['low'].min()
            pattern_range = recent_high - recent_low
            
            if bias == BiasType.BULLISH:
                # Measured move up from support
                if key_levels.immediate_support:
                    target_price = key_levels.immediate_support + pattern_range
                else:
                    target_price = recent_low + pattern_range
            elif bias == BiasType.BEARISH:
                # Measured move down from resistance
                if key_levels.immediate_resistance:
                    target_price = key_levels.immediate_resistance - pattern_range
                else:
                    target_price = recent_high - pattern_range
            else:
                target_price = (recent_high + recent_low) / 2
            
            return PredictionSignal(
                method=PredictionMethod.PATTERN_MEASURED_MOVE,
                target_price=target_price,
                confidence=0.6,
                direction=bias,
                reasoning=f"Measured move ${pattern_range:,.2f} from range",
                weight=self.method_weights[PredictionMethod.PATTERN_MEASURED_MOVE]
            )
        except Exception:
            return None
    
    def _confluence_analysis(
        self, current_price: float, key_levels: KeyLevels,
        order_blocks: List[OrderBlock], fvgs: List[FairValueGap],
        bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        Find confluence zones where multiple levels cluster.
        """
        try:
            # Collect all potential levels
            levels = []
            
            if key_levels.immediate_support:
                levels.append(("S/R", key_levels.immediate_support))
            if key_levels.immediate_resistance:
                levels.append(("S/R", key_levels.immediate_resistance))
            if key_levels.major_support:
                levels.append(("Major S", key_levels.major_support))
            if key_levels.major_resistance:
                levels.append(("Major R", key_levels.major_resistance))
            
            for ob in order_blocks[:5]:
                mid = (ob.price_high + ob.price_low) / 2
                levels.append(("OB", mid))
            
            for fvg in fvgs[:5]:
                mid = (fvg.high + fvg.low) / 2
                levels.append(("FVG", mid))
            
            if not levels:
                return None
            
            # Cluster levels within 0.5% of each other
            tolerance = current_price * 0.005
            clusters = []
            
            for label, level in levels:
                found_cluster = False
                for cluster in clusters:
                    if abs(cluster['center'] - level) < tolerance:
                        cluster['levels'].append((label, level))
                        cluster['center'] = np.mean([l[1] for l in cluster['levels']])
                        found_cluster = True
                        break
                if not found_cluster:
                    clusters.append({'center': level, 'levels': [(label, level)]})
            
            # Find strongest confluence cluster in direction of bias
            if bias == BiasType.BULLISH:
                valid_clusters = [c for c in clusters if c['center'] > current_price]
            elif bias == BiasType.BEARISH:
                valid_clusters = [c for c in clusters if c['center'] < current_price]
            else:
                valid_clusters = clusters
            
            if not valid_clusters:
                return None
            
            # Sort by cluster strength (number of levels) and proximity
            best_cluster = max(valid_clusters, key=lambda c: len(c['levels']))
            target_price = best_cluster['center']
            confluence_count = len(best_cluster['levels'])
            
            confidence = min(0.9, 0.5 + confluence_count * 0.1)
            
            return PredictionSignal(
                method=PredictionMethod.CONFLUENCE_CLUSTER,
                target_price=target_price,
                confidence=confidence,
                direction=bias,
                reasoning=f"Confluence zone with {confluence_count} levels at ${target_price:,.2f}",
                weight=self.method_weights[PredictionMethod.CONFLUENCE_CLUSTER]
            )
        except Exception:
            return None
    
    def _trend_projection(
        self, df: pd.DataFrame, current_price: float,
        indicators: TechnicalIndicators, bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        Project price along trend line.
        """
        try:
            lookback = {"1h": 20, "1d": 50, "1w": 100}.get(timeframe, 50)
            recent = df.tail(lookback)
            
            # Calculate linear regression
            x = np.arange(len(recent))
            y = recent['close'].values
            
            # Simple linear regression
            slope = np.polyfit(x, y, 1)[0]
            
            # Project forward
            projection_periods = {"1h": 1, "1d": 24, "1w": 168}.get(timeframe, 24)
            target_price = current_price + (slope * projection_periods * 0.3)
            
            # Adjust based on bias
            if bias == BiasType.BULLISH and slope < 0:
                # Trend reversal expected
                target_price = current_price + abs(slope) * projection_periods * 0.2
            elif bias == BiasType.BEARISH and slope > 0:
                # Trend reversal expected
                target_price = current_price - abs(slope) * projection_periods * 0.2
            
            # Confidence based on trend strength
            r_squared = np.corrcoef(x, y)[0, 1] ** 2
            confidence = 0.4 + r_squared * 0.4
            
            return PredictionSignal(
                method=PredictionMethod.TREND_PROJECTION,
                target_price=target_price,
                confidence=confidence,
                direction=bias,
                reasoning=f"Trend slope ${slope:.2f}/period, R²={r_squared:.2f}",
                weight=self.method_weights[PredictionMethod.TREND_PROJECTION]
            )
        except Exception:
            return None
    
    def _fvg_analysis(
        self, current_price: float, fvgs: List[FairValueGap],
        bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        Target unfilled Fair Value Gaps.
        """
        try:
            # Filter unfilled FVGs
            unfilled = [fvg for fvg in fvgs if not fvg.filled]
            if not unfilled:
                return None
            
            if bias == BiasType.BULLISH:
                # Look for bullish FVGs to fill (above price)
                targets = [fvg for fvg in unfilled 
                          if fvg.gap_type == "Bullish FVG" and fvg.low > current_price]
                if not targets:
                    # Or bearish FVGs below to fill
                    targets = [fvg for fvg in unfilled 
                              if fvg.gap_type == "Bearish FVG" and fvg.high > current_price]
                
                if targets:
                    target_fvg = min(targets, key=lambda x: x.low)
                    target_price = (target_fvg.high + target_fvg.low) / 2
                else:
                    return None
            elif bias == BiasType.BEARISH:
                # Look for bearish FVGs to fill (below price)
                targets = [fvg for fvg in unfilled 
                          if fvg.gap_type == "Bearish FVG" and fvg.high < current_price]
                if not targets:
                    # Or bullish FVGs above to fill
                    targets = [fvg for fvg in unfilled 
                              if fvg.gap_type == "Bullish FVG" and fvg.low < current_price]
                
                if targets:
                    target_fvg = max(targets, key=lambda x: x.high)
                    target_price = (target_fvg.high + target_fvg.low) / 2
                else:
                    return None
            else:
                # Neutral - find nearest unfilled FVG
                nearest = min(unfilled, key=lambda x: abs((x.high + x.low) / 2 - current_price))
                target_price = (nearest.high + nearest.low) / 2
            
            return PredictionSignal(
                method=PredictionMethod.CONFLUENCE_CLUSTER,
                target_price=target_price,
                confidence=0.7,
                direction=bias,
                reasoning=f"FVG fill target at ${target_price:,.2f}",
                weight=1.3
            )
        except Exception:
            return None
    
    def _atr_projection(
        self, current_price: float, indicators: TechnicalIndicators,
        bias: BiasType, timeframe: str
    ) -> Optional[PredictionSignal]:
        """
        ATR-based price projection.
        """
        try:
            atr = indicators.volatility.atr_14
            if not atr:
                return None
            
            # Multipliers based on timeframe
            multiplier = {"1h": 0.5, "1d": 1.2, "1w": 3.5}.get(timeframe, 1.0)
            
            if bias == BiasType.BULLISH:
                target_price = current_price + (atr * multiplier)
            elif bias == BiasType.BEARISH:
                target_price = current_price - (atr * multiplier)
            else:
                target_price = current_price
            
            return PredictionSignal(
                method=PredictionMethod.MOMENTUM_PROJECTION,
                target_price=target_price,
                confidence=0.65,
                direction=bias,
                reasoning=f"ATR ${atr:.2f} x {multiplier} = ${atr * multiplier:.2f} move",
                weight=1.2
            )
        except Exception:
            return None
    
    def _combine_signals(
        self, signals: List[PredictionSignal], current_price: float,
        overall_bias: BiasType, timeframe: str
    ) -> PrecisionPrediction:
        """
        Combine all signals into a final prediction.
        """
        if not signals:
            return self._create_fallback_prediction(current_price, timeframe)
        
        # Calculate weighted average
        total_weight = sum(s.weight * s.confidence for s in signals)
        if total_weight == 0:
            return self._create_fallback_prediction(current_price, timeframe)
        
        weighted_sum = sum(s.target_price * s.weight * s.confidence for s in signals)
        weighted_average = weighted_sum / total_weight
        
        # Calculate standard deviation of predictions
        targets = [s.target_price for s in signals]
        std_dev = np.std(targets) if len(targets) > 1 else 0
        
        # Final target - use weighted average
        target_price = weighted_average
        
        # Calculate prediction range based on signal agreement
        agreement_factor = 1 - (std_dev / current_price)  # Lower std = higher agreement
        agreement_factor = max(0.3, min(0.9, agreement_factor))
        
        # Range based on timeframe and agreement
        base_range = {"1h": 0.003, "1d": 0.015, "1w": 0.05}.get(timeframe, 0.01)
        range_factor = base_range * (2 - agreement_factor)  # Tighter range with more agreement
        
        # Calculate range ensuring low < high always
        range_amount = current_price * range_factor
        
        if overall_bias == BiasType.BULLISH:
            # Bullish: target above current, range skewed upward
            predicted_low = min(current_price, target_price) - (range_amount * 0.3)
            predicted_high = max(current_price, target_price) + (range_amount * 0.7)
        elif overall_bias == BiasType.BEARISH:
            # Bearish: target below current, range skewed downward
            predicted_low = min(current_price, target_price) - (range_amount * 0.7)
            predicted_high = max(current_price, target_price) + (range_amount * 0.3)
        else:
            # Neutral: symmetric range around target
            range_half = range_amount * 0.5
            predicted_low = target_price - range_half
            predicted_high = target_price + range_half
        
        # Ensure low < high
        if predicted_low > predicted_high:
            predicted_low, predicted_high = predicted_high, predicted_low
        
        # Calculate overall confidence
        avg_confidence = np.mean([s.confidence for s in signals])
        method_count_bonus = min(0.2, len(signals) * 0.02)  # More methods = higher confidence
        overall_confidence = min(0.95, avg_confidence + method_count_bonus)
        
        # Method breakdown
        method_breakdown = {}
        for s in signals:
            method_name = s.method.value
            method_breakdown[method_name] = s.target_price
        
        return PrecisionPrediction(
            target_price=round(target_price, 2),
            predicted_low=round(predicted_low, 2),
            predicted_high=round(predicted_high, 2),
            direction=overall_bias,
            confidence=overall_confidence,
            signals=signals,
            weighted_average=round(weighted_average, 2),
            standard_deviation=round(std_dev, 2),
            method_breakdown=method_breakdown
        )
    
    def _create_fallback_prediction(
        self, current_price: float, timeframe: str
    ) -> PrecisionPrediction:
        """Create fallback prediction when no signals available."""
        range_pct = {"1h": 0.005, "1d": 0.02, "1w": 0.06}.get(timeframe, 0.01)
        return PrecisionPrediction(
            target_price=current_price,
            predicted_low=current_price * (1 - range_pct),
            predicted_high=current_price * (1 + range_pct),
            direction=BiasType.NEUTRAL,
            confidence=0.3,
            signals=[],
            weighted_average=current_price,
            standard_deviation=0,
            method_breakdown={}
        )


# Singleton instance
precision_predictor = PrecisionPredictor()

