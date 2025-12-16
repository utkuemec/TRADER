"""
Pydantic models for request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class BiasType(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"


class ConfidenceLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TrendState(str, Enum):
    UPTREND = "Uptrend"
    DOWNTREND = "Downtrend"
    RANGING = "Ranging"
    TRANSITION = "Transition"


class VolatilityState(str, Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    EXTREME = "Extreme"


# ============ Price & OHLCV Models ============

class OHLCV(BaseModel):
    timestamp: int
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class Ticker(BaseModel):
    symbol: str
    last: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[float] = None
    change: Optional[float] = None
    percentage: Optional[float] = None
    timestamp: int


# ============ Technical Indicator Models ============

class MovingAverages(BaseModel):
    ema_9: Optional[float] = None
    ema_21: Optional[float] = None
    ema_50: Optional[float] = None
    ema_100: Optional[float] = None
    ema_200: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    vwap: Optional[float] = None


class MomentumIndicators(BaseModel):
    rsi_14: Optional[float] = None
    rsi_state: Optional[str] = None  # Oversold, Neutral, Overbought
    macd_line: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    macd_state: Optional[str] = None  # Bullish, Bearish, Crossover
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None
    stoch_state: Optional[str] = None
    cci: Optional[float] = None


class VolatilityIndicators(BaseModel):
    atr_14: Optional[float] = None
    atr_percent: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_width: Optional[float] = None
    bb_position: Optional[float] = None  # 0-1 position within bands


class TechnicalIndicators(BaseModel):
    moving_averages: MovingAverages
    momentum: MomentumIndicators
    volatility: VolatilityIndicators


# ============ Market Structure Models ============

class PriceLevel(BaseModel):
    price: float
    strength: str  # Weak, Moderate, Strong
    touches: int = 1
    level_type: str  # Support, Resistance


class MarketStructure(BaseModel):
    trend: TrendState
    higher_highs: List[float] = []
    higher_lows: List[float] = []
    lower_highs: List[float] = []
    lower_lows: List[float] = []
    last_swing_high: Optional[float] = None
    last_swing_low: Optional[float] = None
    structure_break: Optional[str] = None  # BOS (Break of Structure), CHoCH (Change of Character)


class LiquidityZone(BaseModel):
    price_start: float
    price_end: float
    zone_type: str  # Buy-side, Sell-side
    strength: str
    swept: bool = False


class OrderBlock(BaseModel):
    price_high: float
    price_low: float
    block_type: str  # Bullish OB, Bearish OB
    mitigated: bool = False
    timeframe: str


class FairValueGap(BaseModel):
    high: float
    low: float
    gap_type: str  # Bullish FVG, Bearish FVG
    filled: bool = False
    fill_percentage: float = 0.0


class SupplyDemandZone(BaseModel):
    price_high: float
    price_low: float
    zone_type: str  # Supply, Demand
    strength: str
    fresh: bool = True


# ============ Analysis Models ============

class TimeframeBias(BaseModel):
    timeframe: str
    bias: BiasType
    trend: TrendState
    key_level_above: Optional[float] = None
    key_level_below: Optional[float] = None
    notes: str = ""


class KeyLevels(BaseModel):
    immediate_support: Optional[float] = None
    immediate_resistance: Optional[float] = None
    major_support: Optional[float] = None
    major_resistance: Optional[float] = None
    invalidation_long: Optional[float] = None
    invalidation_short: Optional[float] = None
    targets_long: List[float] = []
    targets_short: List[float] = []


class PredictionOutlook(BaseModel):
    bias: BiasType
    key_levels: KeyLevels
    expected_scenario: str
    alternative_scenario: str
    invalidation: str
    probability: str


class PriceRangePrediction(BaseModel):
    """Precise price range prediction with max $1000 range for BTC-level assets."""
    timeframe: str  # "1h" or "1d"
    current_price: float
    price_at_prediction: float  # Price when prediction was made
    predicted_low: float
    predicted_high: float
    predicted_target: float  # Most likely price point
    range_size: float  # Size of the range in dollars
    range_percent: float  # Range as percentage of current price
    direction: BiasType  # Expected direction
    confidence: ConfidenceLevel
    reasoning: str
    # Time-lock fields
    created_at: Optional[str] = None  # When prediction was created
    expires_at: Optional[str] = None  # When prediction expires
    time_remaining: Optional[str] = None  # Time until new prediction
    is_locked: bool = False  # Whether this is a locked prediction


class MarketContext(BaseModel):
    short_tf_trend: TrendState
    mid_tf_trend: TrendState
    high_tf_trend: TrendState
    volatility: VolatilityState
    liquidity_context: str
    market_phase: str  # Accumulation, Markup, Distribution, Markdown


class MultiTimeframeSummary(BaseModel):
    lower_tf_bias: str  # 1m-30m analysis
    mid_tf_bias: str    # 1h-8h analysis  
    higher_tf_bias: str # 1d+ analysis
    alignment: str      # Aligned Bullish, Aligned Bearish, Mixed/Conflicting


class FullAnalysis(BaseModel):
    symbol: str
    exchange: str
    generated_at: str
    current_price: float
    price_change_24h: Optional[float] = None
    
    # Context
    market_context: MarketContext
    
    # Multi-TF Summary
    mtf_summary: MultiTimeframeSummary
    
    # Timeframe Biases
    timeframe_biases: List[TimeframeBias]
    
    # Technical Indicators (multiple timeframes)
    indicators: Dict[str, TechnicalIndicators]
    
    # Structure
    market_structure: Dict[str, MarketStructure]
    
    # Key Levels
    key_levels: KeyLevels
    
    # Smart Money Concepts
    order_blocks: List[OrderBlock] = []
    fair_value_gaps: List[FairValueGap] = []
    liquidity_zones: List[LiquidityZone] = []
    supply_demand_zones: List[SupplyDemandZone] = []
    
    # Predictions
    next_1h_outlook: PredictionOutlook
    next_1d_outlook: PredictionOutlook
    
    # Precise Price Range Predictions
    price_prediction_1h: PriceRangePrediction
    price_prediction_1d: PriceRangePrediction
    price_prediction_1w: PriceRangePrediction
    
    # Confidence
    confidence: ConfidenceLevel
    confidence_reasoning: str
    
    # Full narrative analysis
    analysis_narrative: str


# ============ API Response Models ============

class SymbolListResponse(BaseModel):
    exchange: str
    symbols: List[str]
    count: int


class OHLCVResponse(BaseModel):
    symbol: str
    timeframe: str
    exchange: str
    data: List[OHLCV]
    count: int


class IndicatorResponse(BaseModel):
    symbol: str
    timeframe: str
    indicators: TechnicalIndicators


class AnalysisRequest(BaseModel):
    symbol: str = "BTC/USDT"
    exchange: str = "binance"

