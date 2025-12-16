"""
Main Analysis Engine.
Combines all services to produce comprehensive institutional-grade analysis.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from ..config import settings
from ..models import (
    FullAnalysis, MarketContext, MultiTimeframeSummary, TimeframeBias,
    KeyLevels, PredictionOutlook, PriceRangePrediction, BiasType, ConfidenceLevel, TrendState,
    VolatilityState, TechnicalIndicators
)
from .exchange import exchange_service
from .indicators import indicator_service
from .structure import structure_service
from .prediction_cache import prediction_cache
from .advanced_predictor import advanced_predictor, AdvancedPrediction


class AnalysisEngine:
    """Main analysis engine that produces institutional-grade crypto analysis."""
    
    # Timeframe categories
    LOWER_TF = ["1m", "5m", "15m", "30m"]
    MID_TF = ["1h", "2h", "4h", "8h"]
    HIGHER_TF = ["1d", "1w", "1M"]
    
    async def full_analysis(
        self,
        symbol: str,
        exchange_id: str = "binance"
    ) -> FullAnalysis:
        """Generate comprehensive multi-timeframe analysis."""
        
        # Fetch data for all timeframes
        timeframes = ["5m", "15m", "30m", "1h", "4h", "1d"]
        mtf_data = await exchange_service.get_multi_timeframe_data(
            symbol, timeframes, exchange_id
        )
        
        # Get current ticker
        ticker = await exchange_service.get_ticker(symbol, exchange_id)
        current_price = ticker.last
        
        # Calculate indicators for each timeframe
        indicators: Dict[str, TechnicalIndicators] = {}
        structures: Dict[str, any] = {}
        tf_biases: List[TimeframeBias] = []
        
        for tf, df in mtf_data.items():
            # Indicators
            indicators[tf] = indicator_service.calculate_all(df)
            
            # Market structure
            structures[tf] = structure_service.analyze_structure(df)
            
            # Timeframe bias
            bias = self._determine_tf_bias(df, indicators[tf], structures[tf])
            tf_biases.append(TimeframeBias(
                timeframe=tf,
                bias=bias["bias"],
                trend=structures[tf].trend,
                key_level_above=bias.get("resistance"),
                key_level_below=bias.get("support"),
                notes=bias.get("notes", "")
            ))
        
        # Aggregate analysis
        market_context = self._build_market_context(structures, indicators, mtf_data)
        mtf_summary = self._build_mtf_summary(tf_biases)
        key_levels = self._calculate_key_levels(mtf_data, current_price)
        
        # Smart Money Concepts
        primary_df = mtf_data.get("1h", mtf_data.get("4h", list(mtf_data.values())[0]))
        order_blocks = structure_service.find_order_blocks(primary_df, "1h")
        fvgs = structure_service.find_fair_value_gaps(primary_df)
        liquidity_zones = structure_service.find_liquidity_zones(primary_df)
        sd_zones = structure_service.find_supply_demand_zones(primary_df)
        
        # Generate predictions
        next_1h = self._generate_1h_prediction(
            current_price, tf_biases, indicators, key_levels, market_context
        )
        next_1d = self._generate_1d_prediction(
            current_price, tf_biases, indicators, key_levels, market_context
        )
        
        # Generate PRECISE price range predictions (TIME-LOCKED)
        # Check cache first - predictions are locked for their duration
        price_pred_1h = self._get_or_create_prediction(
            symbol, "1h", current_price, indicators, key_levels, market_context, 
            tf_biases, mtf_data, order_blocks, fvgs, liquidity_zones
        )
        price_pred_1d = self._get_or_create_prediction(
            symbol, "1d", current_price, indicators, key_levels, market_context, 
            tf_biases, mtf_data, order_blocks, fvgs, liquidity_zones
        )
        price_pred_1w = self._get_or_create_prediction(
            symbol, "1w", current_price, indicators, key_levels, market_context, 
            tf_biases, mtf_data, order_blocks, fvgs, liquidity_zones
        )
        
        # Confidence assessment
        confidence, confidence_reasoning = self._assess_confidence(
            tf_biases, mtf_summary, market_context
        )
        
        # Generate narrative
        narrative = self._generate_narrative(
            symbol, current_price, market_context, mtf_summary,
            next_1h, next_1d, confidence, key_levels, price_pred_1h, price_pred_1d, price_pred_1w
        )
        
        return FullAnalysis(
            symbol=symbol,
            exchange=exchange_id,
            generated_at=datetime.now().isoformat(),
            current_price=current_price,
            price_change_24h=ticker.percentage,
            market_context=market_context,
            mtf_summary=mtf_summary,
            timeframe_biases=tf_biases,
            indicators=indicators,
            market_structure=structures,
            key_levels=key_levels,
            order_blocks=order_blocks,
            fair_value_gaps=fvgs,
            liquidity_zones=liquidity_zones,
            supply_demand_zones=sd_zones,
            next_1h_outlook=next_1h,
            next_1d_outlook=next_1d,
            price_prediction_1h=price_pred_1h,
            price_prediction_1d=price_pred_1d,
            price_prediction_1w=price_pred_1w,
            confidence=confidence,
            confidence_reasoning=confidence_reasoning,
            analysis_narrative=narrative
        )
    
    def _determine_tf_bias(
        self,
        df: pd.DataFrame,
        indicators: TechnicalIndicators,
        structure: any
    ) -> Dict:
        """Determine bias for a single timeframe."""
        if df.empty:
            return {"bias": BiasType.NEUTRAL, "notes": "Insufficient data"}
        
        bullish_signals = 0
        bearish_signals = 0
        notes = []
        
        current_price = df['close'].iloc[-1]
        
        # Trend structure
        if structure.trend == TrendState.UPTREND:
            bullish_signals += 2
            notes.append("Uptrend structure")
        elif structure.trend == TrendState.DOWNTREND:
            bearish_signals += 2
            notes.append("Downtrend structure")
        
        # EMA alignment
        ma = indicators.moving_averages
        if ma.ema_21 and ma.ema_50:
            if current_price > ma.ema_21 > ma.ema_50:
                bullish_signals += 1
                notes.append("Price above EMAs")
            elif current_price < ma.ema_21 < ma.ema_50:
                bearish_signals += 1
                notes.append("Price below EMAs")
        
        # RSI
        mom = indicators.momentum
        if mom.rsi_14:
            if mom.rsi_14 > 60:
                bullish_signals += 1
            elif mom.rsi_14 < 40:
                bearish_signals += 1
        
        # MACD
        if mom.macd_histogram:
            if mom.macd_histogram > 0:
                bullish_signals += 1
            else:
                bearish_signals += 1
        
        # Determine bias
        if bullish_signals > bearish_signals + 1:
            bias = BiasType.BULLISH
        elif bearish_signals > bullish_signals + 1:
            bias = BiasType.BEARISH
        else:
            bias = BiasType.NEUTRAL
        
        # Find key levels
        swing_highs = structure.higher_highs + structure.lower_highs
        swing_lows = structure.higher_lows + structure.lower_lows
        
        resistance = min([h for h in swing_highs if h > current_price], default=None)
        support = max([l for l in swing_lows if l < current_price], default=None)
        
        return {
            "bias": bias,
            "resistance": resistance,
            "support": support,
            "notes": "; ".join(notes)
        }
    
    def _build_market_context(
        self,
        structures: Dict,
        indicators: Dict[str, TechnicalIndicators],
        mtf_data: Dict[str, pd.DataFrame]
    ) -> MarketContext:
        """Build market context from all data."""
        
        # Determine trends at different levels
        def get_trend(tfs: List[str]) -> TrendState:
            trends = [structures[tf].trend for tf in tfs if tf in structures]
            if not trends:
                return TrendState.RANGING
            # Most common trend
            from collections import Counter
            return Counter(trends).most_common(1)[0][0]
        
        short_trend = get_trend(["5m", "15m", "30m"])
        mid_trend = get_trend(["1h", "4h"])
        high_trend = get_trend(["1d"])
        
        # Volatility assessment
        volatility = VolatilityState.NORMAL
        if "1h" in indicators:
            vol = indicators["1h"].volatility
            if vol.atr_percent:
                if vol.atr_percent > 5:
                    volatility = VolatilityState.EXTREME
                elif vol.atr_percent > 3:
                    volatility = VolatilityState.HIGH
                elif vol.atr_percent < 1:
                    volatility = VolatilityState.LOW
        
        # Liquidity context
        liquidity_context = "Normal liquidity conditions"
        if "1h" in mtf_data:
            df = mtf_data["1h"]
            avg_vol = df['volume'].mean()
            recent_vol = df['volume'].tail(5).mean()
            if recent_vol > avg_vol * 1.5:
                liquidity_context = "Elevated volume - increased liquidity"
            elif recent_vol < avg_vol * 0.5:
                liquidity_context = "Low volume - thin liquidity"
        
        # Market phase (simplified Wyckoff)
        market_phase = self._detect_market_phase(structures, mtf_data)
        
        return MarketContext(
            short_tf_trend=short_trend,
            mid_tf_trend=mid_trend,
            high_tf_trend=high_trend,
            volatility=volatility,
            liquidity_context=liquidity_context,
            market_phase=market_phase
        )
    
    def _detect_market_phase(
        self,
        structures: Dict,
        mtf_data: Dict[str, pd.DataFrame]
    ) -> str:
        """Detect Wyckoff market phase."""
        if "1d" not in mtf_data:
            return "Undetermined"
        
        df = mtf_data["1d"]
        if len(df) < 30:
            return "Undetermined"
        
        # Simple phase detection
        recent = df.tail(20)
        price_change = (recent['close'].iloc[-1] - recent['close'].iloc[0]) / recent['close'].iloc[0]
        volatility = recent['close'].std() / recent['close'].mean()
        
        if price_change > 0.1 and volatility < 0.05:
            return "Markup"
        elif price_change < -0.1 and volatility < 0.05:
            return "Markdown"
        elif volatility < 0.03 and abs(price_change) < 0.05:
            if recent['volume'].iloc[-5:].mean() > recent['volume'].iloc[:5].mean():
                return "Accumulation"
            return "Distribution"
        else:
            return "Transition"
    
    def _build_mtf_summary(self, tf_biases: List[TimeframeBias]) -> MultiTimeframeSummary:
        """Build multi-timeframe summary."""
        
        def summarize(tfs: List[str]) -> str:
            biases = [b for b in tf_biases if b.timeframe in tfs]
            if not biases:
                return "No data"
            
            bullish = sum(1 for b in biases if b.bias == BiasType.BULLISH)
            bearish = sum(1 for b in biases if b.bias == BiasType.BEARISH)
            
            if bullish > bearish:
                return f"Bullish ({bullish}/{len(biases)} timeframes)"
            elif bearish > bullish:
                return f"Bearish ({bearish}/{len(biases)} timeframes)"
            return "Mixed/Neutral"
        
        lower = summarize(["5m", "15m", "30m"])
        mid = summarize(["1h", "4h"])
        higher = summarize(["1d"])
        
        # Overall alignment
        all_bullish = all(b.bias == BiasType.BULLISH for b in tf_biases)
        all_bearish = all(b.bias == BiasType.BEARISH for b in tf_biases)
        
        if all_bullish:
            alignment = "Fully Aligned Bullish"
        elif all_bearish:
            alignment = "Fully Aligned Bearish"
        elif lower.startswith("Bullish") and mid.startswith("Bullish"):
            alignment = "Mostly Aligned Bullish"
        elif lower.startswith("Bearish") and mid.startswith("Bearish"):
            alignment = "Mostly Aligned Bearish"
        else:
            alignment = "Mixed/Conflicting"
        
        return MultiTimeframeSummary(
            lower_tf_bias=lower,
            mid_tf_bias=mid,
            higher_tf_bias=higher,
            alignment=alignment
        )
    
    def _calculate_key_levels(
        self,
        mtf_data: Dict[str, pd.DataFrame],
        current_price: float
    ) -> KeyLevels:
        """Calculate key price levels."""
        
        all_supports = []
        all_resistances = []
        
        for tf, df in mtf_data.items():
            levels = structure_service.find_support_resistance(df)
            for level in levels:
                if level.level_type == "Support":
                    all_supports.append(level.price)
                else:
                    all_resistances.append(level.price)
        
        # Dedupe and sort
        supports = sorted(set(all_supports), reverse=True)
        resistances = sorted(set(all_resistances))
        
        # Filter to relevant levels
        near_supports = [s for s in supports if s < current_price][:5]
        near_resistances = [r for r in resistances if r > current_price][:5]
        
        return KeyLevels(
            immediate_support=near_supports[0] if near_supports else None,
            immediate_resistance=near_resistances[0] if near_resistances else None,
            major_support=near_supports[-1] if len(near_supports) > 1 else near_supports[0] if near_supports else None,
            major_resistance=near_resistances[-1] if len(near_resistances) > 1 else near_resistances[0] if near_resistances else None,
            invalidation_long=near_supports[1] if len(near_supports) > 1 else near_supports[0] if near_supports else current_price * 0.95,
            invalidation_short=near_resistances[1] if len(near_resistances) > 1 else near_resistances[0] if near_resistances else current_price * 1.05,
            targets_long=near_resistances[:3],
            targets_short=near_supports[:3]
        )
    
    def _generate_1h_prediction(
        self,
        current_price: float,
        tf_biases: List[TimeframeBias],
        indicators: Dict[str, TechnicalIndicators],
        key_levels: KeyLevels,
        context: MarketContext
    ) -> PredictionOutlook:
        """Generate 1-hour prediction."""
        
        # Weight lower timeframes more for 1h prediction
        lower_tf = [b for b in tf_biases if b.timeframe in ["5m", "15m", "30m", "1h"]]
        
        bullish = sum(1 for b in lower_tf if b.bias == BiasType.BULLISH)
        bearish = sum(1 for b in lower_tf if b.bias == BiasType.BEARISH)
        
        if bullish > bearish:
            bias = BiasType.BULLISH
            expected = f"Expect continuation higher toward ${key_levels.immediate_resistance:,.2f}" if key_levels.immediate_resistance else "Expect bullish continuation"
            alternative = "Pullback to support before continuation"
            invalidation = f"Break below ${key_levels.immediate_support:,.2f}" if key_levels.immediate_support else "Break of recent swing low"
        elif bearish > bullish:
            bias = BiasType.BEARISH
            expected = f"Expect continuation lower toward ${key_levels.immediate_support:,.2f}" if key_levels.immediate_support else "Expect bearish continuation"
            alternative = "Bounce from support before continuation lower"
            invalidation = f"Break above ${key_levels.immediate_resistance:,.2f}" if key_levels.immediate_resistance else "Break of recent swing high"
        else:
            bias = BiasType.NEUTRAL
            expected = "Range-bound price action expected"
            alternative = "Breakout in either direction possible"
            invalidation = "N/A for neutral outlook"
        
        # Probability based on alignment
        prob = "Medium"
        if context.short_tf_trend == context.mid_tf_trend:
            prob = "High"
        
        return PredictionOutlook(
            bias=bias,
            key_levels=key_levels,
            expected_scenario=expected,
            alternative_scenario=alternative,
            invalidation=invalidation,
            probability=prob
        )
    
    def _generate_1d_prediction(
        self,
        current_price: float,
        tf_biases: List[TimeframeBias],
        indicators: Dict[str, TechnicalIndicators],
        key_levels: KeyLevels,
        context: MarketContext
    ) -> PredictionOutlook:
        """Generate 1-day prediction."""
        
        # Weight higher timeframes more
        higher_tf = [b for b in tf_biases if b.timeframe in ["1h", "4h", "1d"]]
        
        bullish = sum(1 for b in higher_tf if b.bias == BiasType.BULLISH)
        bearish = sum(1 for b in higher_tf if b.bias == BiasType.BEARISH)
        
        if bullish > bearish:
            bias = BiasType.BULLISH
            expected = f"Bullish daily close expected. Target zone: ${key_levels.major_resistance:,.2f}" if key_levels.major_resistance else "Bullish structure continuation"
            alternative = "Consolidation before next leg up"
            invalidation = f"Daily close below ${key_levels.major_support:,.2f}" if key_levels.major_support else "Loss of key support structure"
        elif bearish > bullish:
            bias = BiasType.BEARISH
            expected = f"Bearish daily close expected. Target zone: ${key_levels.major_support:,.2f}" if key_levels.major_support else "Bearish structure continuation"
            alternative = "Dead cat bounce before continuation"
            invalidation = f"Daily close above ${key_levels.major_resistance:,.2f}" if key_levels.major_resistance else "Recovery of key resistance"
        else:
            bias = BiasType.NEUTRAL
            expected = "Consolidation day expected with no clear direction"
            alternative = "Volatility expansion breakout"
            invalidation = "N/A for neutral outlook"
        
        # Probability
        prob = "Medium"
        if context.mid_tf_trend == context.high_tf_trend:
            prob = "High"
        
        return PredictionOutlook(
            bias=bias,
            key_levels=key_levels,
            expected_scenario=expected,
            alternative_scenario=alternative,
            invalidation=invalidation,
            probability=prob
        )
    
    def _calculate_precise_price_range(
        self,
        current_price: float,
        timeframe: str,  # "1h", "1d", or "1w"
        indicators: Dict[str, TechnicalIndicators],
        key_levels: KeyLevels,
        context: MarketContext,
        tf_biases: List[TimeframeBias],
        mtf_data: Dict[str, pd.DataFrame],
        order_blocks: List = None,
        fvgs: List = None,
        liquidity_zones: List = None
    ) -> PriceRangePrediction:
        """
        Calculate PRECISE price range prediction using MULTI-METHOD ANALYSIS.
        Combines 12+ analysis techniques for pinpoint accuracy:
        - Fibonacci Extension/Retracement
        - VWAP Deviation Analysis
        - Order Flow / Order Blocks
        - Liquidity Pool Targeting
        - Mean Reversion / Bollinger Bands
        - Momentum-Based Projection
        - Volume Profile Analysis
        - Pattern Measured Move
        - S/R Confluence Clustering
        - Trend Line Projection
        - Fair Value Gap Analysis
        - ATR-Based Projection
        """
        order_blocks = order_blocks or []
        fvgs = fvgs or []
        liquidity_zones = liquidity_zones or []
        
        # Get primary dataframe for analysis
        if timeframe == "1h":
            primary_tf = "1h" if "1h" in mtf_data else "30m"
        elif timeframe == "1d":
            primary_tf = "4h" if "4h" in mtf_data else "1d"
        else:  # 1w
            primary_tf = "1d" if "1d" in mtf_data else "4h"
        
        df = mtf_data.get(primary_tf, list(mtf_data.values())[0])
        
        # Use ADVANCED predictor - more accurate with heavy current price anchoring
        advanced_result = advanced_predictor.predict(
            timeframe=timeframe,
            current_price=current_price,
            df=df,
            indicators=indicators,
            key_levels=key_levels,
            tf_biases=tf_biases,
            order_blocks=order_blocks,
            fvgs=fvgs,
            liquidity_zones=liquidity_zones,
            context=context
        )
        
        # Map confidence float to ConfidenceLevel
        if advanced_result.confidence >= 0.7:
            confidence = ConfidenceLevel.HIGH
        elif advanced_result.confidence >= 0.5:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW
        
        return PriceRangePrediction(
            timeframe=timeframe,
            current_price=current_price,
            price_at_prediction=current_price,
            predicted_low=advanced_result.predicted_low,
            predicted_high=advanced_result.predicted_high,
            predicted_target=advanced_result.target_price,
            range_size=round(advanced_result.predicted_high - advanced_result.predicted_low, 2),
            range_percent=round(((advanced_result.predicted_high - advanced_result.predicted_low) / current_price) * 100, 3),
            direction=advanced_result.direction,
            confidence=confidence,
            reasoning=advanced_result.reasoning,
            is_locked=False
        )
    
    def _get_or_create_prediction(
        self,
        symbol: str,
        timeframe: str,
        current_price: float,
        indicators: Dict[str, TechnicalIndicators],
        key_levels: KeyLevels,
        context: MarketContext,
        tf_biases: List[TimeframeBias],
        mtf_data: Dict[str, pd.DataFrame],
        order_blocks: List = None,
        fvgs: List = None,
        liquidity_zones: List = None
    ) -> PriceRangePrediction:
        """
        Get cached prediction if valid, or create a new one.
        Predictions are TIME-LOCKED:
        - 1h predictions: locked for 1 hour
        - 1d predictions: locked for 1 day
        - 1w predictions: locked for 1 week
        """
        # Check cache for existing valid prediction
        cached = prediction_cache.get_prediction(symbol, timeframe)
        
        if cached:
            # Return cached prediction with current price updated
            return PriceRangePrediction(
                timeframe=cached['timeframe'],
                current_price=current_price,  # Update to current price
                price_at_prediction=cached['price_at_prediction'],
                predicted_low=cached['predicted_low'],
                predicted_high=cached['predicted_high'],
                predicted_target=cached['predicted_target'],
                range_size=cached['range_size'],
                range_percent=cached['range_percent'],
                direction=BiasType(cached['direction']),
                confidence=ConfidenceLevel(cached['confidence']),
                reasoning=cached['reasoning'],
                created_at=cached.get('created_at'),
                expires_at=cached.get('expires_at'),
                time_remaining=cached.get('time_remaining'),
                is_locked=True
            )
        
        # No valid cache - create new prediction using PRECISION PREDICTOR
        prediction = self._calculate_precise_price_range(
            current_price, timeframe, indicators, key_levels, context, tf_biases, mtf_data,
            order_blocks or [], fvgs or [], liquidity_zones or []
        )
        
        # Save to cache with time lock
        prediction_dict = {
            'timeframe': prediction.timeframe,
            'current_price': prediction.current_price,
            'price_at_prediction': prediction.price_at_prediction,
            'predicted_low': prediction.predicted_low,
            'predicted_high': prediction.predicted_high,
            'predicted_target': prediction.predicted_target,
            'range_size': prediction.range_size,
            'range_percent': prediction.range_percent,
            'direction': prediction.direction.value,
            'confidence': prediction.confidence.value,
            'reasoning': prediction.reasoning,
        }
        
        saved = prediction_cache.save_prediction(symbol, timeframe, prediction_dict)
        
        # Return prediction with timing metadata
        prediction.created_at = saved.get('created_at')
        prediction.expires_at = saved.get('expires_at')
        prediction.time_remaining = saved.get('time_remaining')
        prediction.is_locked = True
        
        return prediction
    
    def _assess_confidence(
        self,
        tf_biases: List[TimeframeBias],
        mtf_summary: MultiTimeframeSummary,
        context: MarketContext
    ) -> tuple[ConfidenceLevel, str]:
        """Assess overall confidence in the analysis."""
        
        reasons = []
        score = 50  # Base score
        
        # Timeframe alignment
        if "Fully Aligned" in mtf_summary.alignment:
            score += 25
            reasons.append("Strong multi-timeframe alignment")
        elif "Mostly Aligned" in mtf_summary.alignment:
            score += 15
            reasons.append("Good timeframe alignment")
        else:
            score -= 10
            reasons.append("Conflicting timeframe signals")
        
        # Volatility impact
        if context.volatility in [VolatilityState.NORMAL, VolatilityState.LOW]:
            score += 10
            reasons.append("Stable volatility environment")
        elif context.volatility == VolatilityState.EXTREME:
            score -= 15
            reasons.append("Extreme volatility reduces predictability")
        
        # Trend clarity
        clear_trends = sum(1 for b in tf_biases if b.trend != TrendState.RANGING)
        if clear_trends >= 4:
            score += 10
            reasons.append("Clear trend structure across timeframes")
        
        # Determine level
        if score >= 75:
            level = ConfidenceLevel.HIGH
        elif score >= 50:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW
        
        reasoning = "; ".join(reasons)
        return level, reasoning
    
    def _generate_narrative(
        self,
        symbol: str,
        current_price: float,
        context: MarketContext,
        mtf_summary: MultiTimeframeSummary,
        next_1h: PredictionOutlook,
        next_1d: PredictionOutlook,
        confidence: ConfidenceLevel,
        key_levels: KeyLevels,
        price_pred_1h: PriceRangePrediction,
        price_pred_1d: PriceRangePrediction,
        price_pred_1w: PriceRangePrediction
    ) -> str:
        """Generate comprehensive analysis narrative."""
        
        def fmt_price(val):
            if val is None:
                return "N/A"
            return f"${val:,.2f}"
        
        def direction_emoji(direction):
            if direction == BiasType.BULLISH:
                return "🟢"
            elif direction == BiasType.BEARISH:
                return "🔴"
            return "⚪"
        
        narrative = f"""
## {symbol} Technical Analysis Report

**Current Price:** ${current_price:,.2f}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}

---

### Market Context

The market is currently showing **{context.short_tf_trend.value}** structure on lower timeframes, 
**{context.mid_tf_trend.value}** on mid timeframes, and **{context.high_tf_trend.value}** on higher timeframes.
Volatility is **{context.volatility.value}**. {context.liquidity_context}.
Current market phase appears to be **{context.market_phase}**.

### Multi-Timeframe Analysis

- **Lower TF (1m-30m):** {mtf_summary.lower_tf_bias}
- **Mid TF (1h-8h):** {mtf_summary.mid_tf_bias}
- **Higher TF (1d+):** {mtf_summary.higher_tf_bias}
- **Overall Alignment:** {mtf_summary.alignment}

### Key Levels

| Level Type | Price |
|------------|-------|
| Immediate Resistance | {fmt_price(key_levels.immediate_resistance)} |
| Major Resistance | {fmt_price(key_levels.major_resistance)} |
| Immediate Support | {fmt_price(key_levels.immediate_support)} |
| Major Support | {fmt_price(key_levels.major_support)} |

---

## 🎯 PRECISE PRICE PREDICTIONS

### 1 HOUR PRICE PREDICTION {direction_emoji(price_pred_1h.direction)}

| Metric | Value |
|--------|-------|
| **Direction** | {price_pred_1h.direction.value} |
| **Predicted Range** | ${price_pred_1h.predicted_low:,.2f} - ${price_pred_1h.predicted_high:,.2f} |
| **Target Price** | ${price_pred_1h.predicted_target:,.2f} |
| **Range Size** | ${price_pred_1h.range_size:,.2f} ({price_pred_1h.range_percent:.2f}%) |
| **Confidence** | {price_pred_1h.confidence.value} |

*{price_pred_1h.reasoning}*

### 1 DAY PRICE PREDICTION {direction_emoji(price_pred_1d.direction)}

| Metric | Value |
|--------|-------|
| **Direction** | {price_pred_1d.direction.value} |
| **Predicted Range** | ${price_pred_1d.predicted_low:,.2f} - ${price_pred_1d.predicted_high:,.2f} |
| **Target Price** | ${price_pred_1d.predicted_target:,.2f} |
| **Range Size** | ${price_pred_1d.range_size:,.2f} ({price_pred_1d.range_percent:.2f}%) |
| **Confidence** | {price_pred_1d.confidence.value} |

*{price_pred_1d.reasoning}*

### 1 WEEK PRICE PREDICTION {direction_emoji(price_pred_1w.direction)}

| Metric | Value |
|--------|-------|
| **Direction** | {price_pred_1w.direction.value} |
| **Predicted Range** | ${price_pred_1w.predicted_low:,.2f} - ${price_pred_1w.predicted_high:,.2f} |
| **Target Price** | ${price_pred_1w.predicted_target:,.2f} |
| **Range Size** | ${price_pred_1w.range_size:,.2f} ({price_pred_1w.range_percent:.2f}%) |
| **Confidence** | {price_pred_1w.confidence.value} |

*{price_pred_1w.reasoning}*

---

### Next 1 Hour Outlook

**Bias:** {next_1h.bias.value}
**Probability:** {next_1h.probability}

{next_1h.expected_scenario}

*Alternative:* {next_1h.alternative_scenario}
*Invalidation:* {next_1h.invalidation}

### Next 1 Day Outlook

**Bias:** {next_1d.bias.value}
**Probability:** {next_1d.probability}

{next_1d.expected_scenario}

*Alternative:* {next_1d.alternative_scenario}
*Invalidation:* {next_1d.invalidation}

### Confidence Assessment

**Level:** {confidence.value}

This analysis is based on multi-timeframe confluence, market structure analysis, 
and technical indicator alignment. Always use proper risk management.

---
*Analysis generated by TRADER Institutional Analysis Engine*
"""
        return narrative.strip()


# Singleton instance
analysis_engine = AnalysisEngine()

