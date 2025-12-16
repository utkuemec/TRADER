"""
Market Structure Analysis Service.
Implements Smart Money Concepts (SMC) analysis:
- Market structure (HH, HL, LH, LL)
- Order blocks
- Fair value gaps (imbalances)
- Liquidity zones
- Supply & demand zones
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from scipy.signal import argrelextrema

from ..models import (
    MarketStructure, OrderBlock, FairValueGap, 
    LiquidityZone, SupplyDemandZone, TrendState,
    PriceLevel
)


class StructureService:
    """Service for market structure and Smart Money Concepts analysis."""
    
    def __init__(self):
        self.swing_lookback = 5  # Candles to look back for swing detection
    
    def analyze_structure(self, df: pd.DataFrame) -> MarketStructure:
        """Analyze market structure - HH, HL, LH, LL patterns."""
        if df.empty or len(df) < 20:
            return MarketStructure(trend=TrendState.RANGING)
        
        # Find swing highs and lows
        swing_highs = self._find_swing_highs(df)
        swing_lows = self._find_swing_lows(df)
        
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return MarketStructure(trend=TrendState.RANGING)
        
        # Classify swings
        higher_highs = []
        lower_highs = []
        higher_lows = []
        lower_lows = []
        
        # Analyze highs
        for i in range(1, len(swing_highs)):
            if swing_highs[i] > swing_highs[i-1]:
                higher_highs.append(swing_highs[i])
            else:
                lower_highs.append(swing_highs[i])
        
        # Analyze lows
        for i in range(1, len(swing_lows)):
            if swing_lows[i] > swing_lows[i-1]:
                higher_lows.append(swing_lows[i])
            else:
                lower_lows.append(swing_lows[i])
        
        # Determine trend
        trend = self._determine_trend(higher_highs, higher_lows, lower_highs, lower_lows)
        
        # Check for structure breaks
        structure_break = self._detect_structure_break(df, swing_highs, swing_lows)
        
        return MarketStructure(
            trend=trend,
            higher_highs=higher_highs[-5:] if higher_highs else [],
            higher_lows=higher_lows[-5:] if higher_lows else [],
            lower_highs=lower_highs[-5:] if lower_highs else [],
            lower_lows=lower_lows[-5:] if lower_lows else [],
            last_swing_high=swing_highs[-1] if swing_highs else None,
            last_swing_low=swing_lows[-1] if swing_lows else None,
            structure_break=structure_break
        )
    
    def _find_swing_highs(self, df: pd.DataFrame, order: int = 5) -> List[float]:
        """Find swing high points."""
        highs = df['high'].values
        swing_indices = argrelextrema(highs, np.greater, order=order)[0]
        return [float(highs[i]) for i in swing_indices]
    
    def _find_swing_lows(self, df: pd.DataFrame, order: int = 5) -> List[float]:
        """Find swing low points."""
        lows = df['low'].values
        swing_indices = argrelextrema(lows, np.less, order=order)[0]
        return [float(lows[i]) for i in swing_indices]
    
    def _determine_trend(
        self,
        higher_highs: List[float],
        higher_lows: List[float],
        lower_highs: List[float],
        lower_lows: List[float]
    ) -> TrendState:
        """Determine trend based on swing structure."""
        hh_count = len(higher_highs)
        hl_count = len(higher_lows)
        lh_count = len(lower_highs)
        ll_count = len(lower_lows)
        
        bullish_score = hh_count + hl_count
        bearish_score = lh_count + ll_count
        
        if bullish_score > bearish_score * 1.5:
            return TrendState.UPTREND
        elif bearish_score > bullish_score * 1.5:
            return TrendState.DOWNTREND
        elif abs(bullish_score - bearish_score) <= 2:
            return TrendState.RANGING
        else:
            return TrendState.TRANSITION
    
    def _detect_structure_break(
        self,
        df: pd.DataFrame,
        swing_highs: List[float],
        swing_lows: List[float]
    ) -> Optional[str]:
        """Detect Break of Structure (BOS) or Change of Character (CHoCH)."""
        if len(df) < 10 or not swing_highs or not swing_lows:
            return None
        
        current_price = df['close'].iloc[-1]
        recent_high = swing_highs[-1] if swing_highs else None
        recent_low = swing_lows[-1] if swing_lows else None
        
        # Check for BOS/CHoCH in last few candles
        recent_closes = df['close'].tail(5).values
        
        if recent_high and any(c > recent_high for c in recent_closes):
            return "BOS Bullish - Broke above swing high"
        elif recent_low and any(c < recent_low for c in recent_closes):
            return "BOS Bearish - Broke below swing low"
        
        return None
    
    def find_order_blocks(
        self,
        df: pd.DataFrame,
        timeframe: str = "1h"
    ) -> List[OrderBlock]:
        """Find bullish and bearish order blocks."""
        if df.empty or len(df) < 20:
            return []
        
        order_blocks = []
        
        for i in range(2, len(df) - 1):
            # Bullish Order Block: Down candle before strong up move
            if (df['close'].iloc[i] < df['open'].iloc[i] and  # Down candle
                df['close'].iloc[i+1] > df['high'].iloc[i]):   # Next candle breaks high
                
                # Check if it's been mitigated
                mitigated = any(df['low'].iloc[i+2:] < df['low'].iloc[i])
                
                order_blocks.append(OrderBlock(
                    price_high=float(df['high'].iloc[i]),
                    price_low=float(df['low'].iloc[i]),
                    block_type="Bullish OB",
                    mitigated=mitigated,
                    timeframe=timeframe
                ))
            
            # Bearish Order Block: Up candle before strong down move
            if (df['close'].iloc[i] > df['open'].iloc[i] and  # Up candle
                df['close'].iloc[i+1] < df['low'].iloc[i]):   # Next candle breaks low
                
                mitigated = any(df['high'].iloc[i+2:] > df['high'].iloc[i])
                
                order_blocks.append(OrderBlock(
                    price_high=float(df['high'].iloc[i]),
                    price_low=float(df['low'].iloc[i]),
                    block_type="Bearish OB",
                    mitigated=mitigated,
                    timeframe=timeframe
                ))
        
        # Return only recent unmitigated order blocks
        fresh_obs = [ob for ob in order_blocks if not ob.mitigated]
        return fresh_obs[-10:]  # Last 10 fresh OBs
    
    def find_fair_value_gaps(self, df: pd.DataFrame) -> List[FairValueGap]:
        """Find Fair Value Gaps (imbalances)."""
        if df.empty or len(df) < 5:
            return []
        
        fvgs = []
        current_price = df['close'].iloc[-1]
        
        for i in range(1, len(df) - 1):
            # Bullish FVG: Gap between candle 1's high and candle 3's low
            if df['low'].iloc[i+1] > df['high'].iloc[i-1]:
                gap_high = float(df['low'].iloc[i+1])
                gap_low = float(df['high'].iloc[i-1])
                
                # Check if filled
                filled = current_price < gap_high and current_price > gap_low
                fill_pct = 0.0
                if filled:
                    fill_pct = (gap_high - current_price) / (gap_high - gap_low) * 100
                
                fvgs.append(FairValueGap(
                    high=gap_high,
                    low=gap_low,
                    gap_type="Bullish FVG",
                    filled=fill_pct > 50,
                    fill_percentage=fill_pct
                ))
            
            # Bearish FVG: Gap between candle 1's low and candle 3's high
            if df['high'].iloc[i+1] < df['low'].iloc[i-1]:
                gap_high = float(df['low'].iloc[i-1])
                gap_low = float(df['high'].iloc[i+1])
                
                filled = current_price > gap_low and current_price < gap_high
                fill_pct = 0.0
                if filled:
                    fill_pct = (current_price - gap_low) / (gap_high - gap_low) * 100
                
                fvgs.append(FairValueGap(
                    high=gap_high,
                    low=gap_low,
                    gap_type="Bearish FVG",
                    filled=fill_pct > 50,
                    fill_percentage=fill_pct
                ))
        
        # Return unfilled FVGs near current price
        unfilled = [fvg for fvg in fvgs if not fvg.filled]
        return unfilled[-10:]
    
    def find_liquidity_zones(self, df: pd.DataFrame) -> List[LiquidityZone]:
        """Find liquidity zones (areas where stops likely accumulated)."""
        if df.empty or len(df) < 50:
            return []
        
        zones = []
        
        # Find equal highs (buy-side liquidity)
        highs = df['high'].values
        for i in range(len(highs) - 10):
            window = highs[i:i+10]
            max_val = max(window)
            # Count how many touches near this level
            touches = sum(1 for h in window if abs(h - max_val) / max_val < 0.002)
            
            if touches >= 2:
                zones.append(LiquidityZone(
                    price_start=float(max_val * 0.998),
                    price_end=float(max_val * 1.002),
                    zone_type="Buy-side",
                    strength="Strong" if touches >= 3 else "Moderate",
                    swept=df['high'].iloc[-1] > max_val
                ))
        
        # Find equal lows (sell-side liquidity)
        lows = df['low'].values
        for i in range(len(lows) - 10):
            window = lows[i:i+10]
            min_val = min(window)
            touches = sum(1 for l in window if abs(l - min_val) / min_val < 0.002)
            
            if touches >= 2:
                zones.append(LiquidityZone(
                    price_start=float(min_val * 0.998),
                    price_end=float(min_val * 1.002),
                    zone_type="Sell-side",
                    strength="Strong" if touches >= 3 else "Moderate",
                    swept=df['low'].iloc[-1] < min_val
                ))
        
        # Deduplicate and return most relevant
        return self._dedupe_zones(zones)[-10:]
    
    def find_support_resistance(self, df: pd.DataFrame) -> List[PriceLevel]:
        """Find key support and resistance levels."""
        if df.empty or len(df) < 50:
            return []
        
        levels = []
        current_price = df['close'].iloc[-1]
        
        # Find swing points
        swing_highs = self._find_swing_highs(df, order=10)
        swing_lows = self._find_swing_lows(df, order=10)
        
        # Add swing highs as resistance
        for high in swing_highs[-10:]:
            if high > current_price:
                levels.append(PriceLevel(
                    price=high,
                    strength="Moderate",
                    touches=1,
                    level_type="Resistance"
                ))
        
        # Add swing lows as support
        for low in swing_lows[-10:]:
            if low < current_price:
                levels.append(PriceLevel(
                    price=low,
                    strength="Moderate",
                    touches=1,
                    level_type="Support"
                ))
        
        # Sort by distance to current price
        levels.sort(key=lambda x: abs(x.price - current_price))
        
        return levels[:10]
    
    def find_supply_demand_zones(self, df: pd.DataFrame) -> List[SupplyDemandZone]:
        """Find supply and demand zones based on strong moves."""
        if df.empty or len(df) < 30:
            return []
        
        zones = []
        current_price = df['close'].iloc[-1]
        
        # Calculate average candle size
        avg_body = abs(df['close'] - df['open']).mean()
        
        for i in range(1, len(df) - 2):
            body_size = abs(df['close'].iloc[i] - df['open'].iloc[i])
            
            # Strong bullish candle = potential demand zone at base
            if (df['close'].iloc[i] > df['open'].iloc[i] and 
                body_size > avg_body * 2):
                
                # Zone is the base of the move
                zone_low = min(df['low'].iloc[i-1], df['low'].iloc[i])
                zone_high = df['open'].iloc[i]
                
                # Check if still fresh (price hasn't returned)
                fresh = all(df['low'].iloc[i+1:] > zone_low)
                
                if zone_high < current_price:  # Below current price = demand
                    zones.append(SupplyDemandZone(
                        price_high=float(zone_high),
                        price_low=float(zone_low),
                        zone_type="Demand",
                        strength="Strong" if body_size > avg_body * 3 else "Moderate",
                        fresh=fresh
                    ))
            
            # Strong bearish candle = potential supply zone at top
            if (df['close'].iloc[i] < df['open'].iloc[i] and 
                body_size > avg_body * 2):
                
                zone_high = max(df['high'].iloc[i-1], df['high'].iloc[i])
                zone_low = df['open'].iloc[i]
                
                fresh = all(df['high'].iloc[i+1:] < zone_high)
                
                if zone_low > current_price:  # Above current price = supply
                    zones.append(SupplyDemandZone(
                        price_high=float(zone_high),
                        price_low=float(zone_low),
                        zone_type="Supply",
                        strength="Strong" if body_size > avg_body * 3 else "Moderate",
                        fresh=fresh
                    ))
        
        # Return fresh zones only
        fresh_zones = [z for z in zones if z.fresh]
        return fresh_zones[-10:]
    
    def _dedupe_zones(self, zones: List[LiquidityZone]) -> List[LiquidityZone]:
        """Remove duplicate/overlapping zones."""
        if not zones:
            return []
        
        # Sort by price
        zones.sort(key=lambda z: z.price_start)
        
        deduped = [zones[0]]
        for zone in zones[1:]:
            last = deduped[-1]
            # If zones overlap significantly, keep the stronger one
            if zone.price_start < last.price_end:
                if zone.strength == "Strong" and last.strength != "Strong":
                    deduped[-1] = zone
            else:
                deduped.append(zone)
        
        return deduped


# Singleton instance
structure_service = StructureService()

