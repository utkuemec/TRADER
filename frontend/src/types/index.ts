// API Response Types

export type BiasType = 'Bullish' | 'Bearish' | 'Neutral';
export type ConfidenceLevel = 'Low' | 'Medium' | 'High';
export type TrendState = 'Uptrend' | 'Downtrend' | 'Ranging' | 'Transition';
export type VolatilityState = 'Low' | 'Normal' | 'High' | 'Extreme';

export interface OHLCV {
  timestamp: number;
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Ticker {
  symbol: string;
  last: number;
  bid: number | null;
  ask: number | null;
  high: number | null;
  low: number | null;
  volume: number | null;
  change: number | null;
  percentage: number | null;
  timestamp: number;
}

export interface MovingAverages {
  ema_9: number | null;
  ema_21: number | null;
  ema_50: number | null;
  ema_100: number | null;
  ema_200: number | null;
  sma_20: number | null;
  sma_50: number | null;
  sma_200: number | null;
  vwap: number | null;
}

export interface MomentumIndicators {
  rsi_14: number | null;
  rsi_state: string | null;
  macd_line: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  macd_state: string | null;
  stoch_k: number | null;
  stoch_d: number | null;
  stoch_state: string | null;
  cci: number | null;
}

export interface VolatilityIndicators {
  atr_14: number | null;
  atr_percent: number | null;
  bb_upper: number | null;
  bb_middle: number | null;
  bb_lower: number | null;
  bb_width: number | null;
  bb_position: number | null;
}

export interface TechnicalIndicators {
  moving_averages: MovingAverages;
  momentum: MomentumIndicators;
  volatility: VolatilityIndicators;
}

export interface MarketStructure {
  trend: TrendState;
  higher_highs: number[];
  higher_lows: number[];
  lower_highs: number[];
  lower_lows: number[];
  last_swing_high: number | null;
  last_swing_low: number | null;
  structure_break: string | null;
}

export interface OrderBlock {
  price_high: number;
  price_low: number;
  block_type: string;
  mitigated: boolean;
  timeframe: string;
}

export interface FairValueGap {
  high: number;
  low: number;
  gap_type: string;
  filled: boolean;
  fill_percentage: number;
}

export interface LiquidityZone {
  price_start: number;
  price_end: number;
  zone_type: string;
  strength: string;
  swept: boolean;
}

export interface SupplyDemandZone {
  price_high: number;
  price_low: number;
  zone_type: string;
  strength: string;
  fresh: boolean;
}

export interface KeyLevels {
  immediate_support: number | null;
  immediate_resistance: number | null;
  major_support: number | null;
  major_resistance: number | null;
  invalidation_long: number | null;
  invalidation_short: number | null;
  targets_long: number[];
  targets_short: number[];
}

export interface TimeframeBias {
  timeframe: string;
  bias: BiasType;
  trend: TrendState;
  key_level_above: number | null;
  key_level_below: number | null;
  notes: string;
}

export interface MarketContext {
  short_tf_trend: TrendState;
  mid_tf_trend: TrendState;
  high_tf_trend: TrendState;
  volatility: VolatilityState;
  liquidity_context: string;
  market_phase: string;
}

export interface MultiTimeframeSummary {
  lower_tf_bias: string;
  mid_tf_bias: string;
  higher_tf_bias: string;
  alignment: string;
}

export interface PredictionOutlook {
  bias: BiasType;
  key_levels: KeyLevels;
  expected_scenario: string;
  alternative_scenario: string;
  invalidation: string;
  probability: string;
}

export interface PriceRangePrediction {
  timeframe: string;
  current_price: number;
  price_at_prediction: number;
  predicted_low: number;
  predicted_high: number;
  predicted_target: number;
  range_size: number;
  range_percent: number;
  direction: BiasType;
  confidence: ConfidenceLevel;
  reasoning: string;
  created_at: string | null;
  expires_at: string | null;
  time_remaining: string | null;
  is_locked: boolean;
}

export interface FullAnalysis {
  symbol: string;
  exchange: string;
  generated_at: string;
  current_price: number;
  price_change_24h: number | null;
  market_context: MarketContext;
  mtf_summary: MultiTimeframeSummary;
  timeframe_biases: TimeframeBias[];
  indicators: Record<string, TechnicalIndicators>;
  market_structure: Record<string, MarketStructure>;
  key_levels: KeyLevels;
  order_blocks: OrderBlock[];
  fair_value_gaps: FairValueGap[];
  liquidity_zones: LiquidityZone[];
  supply_demand_zones: SupplyDemandZone[];
  next_1h_outlook: PredictionOutlook;
  next_1d_outlook: PredictionOutlook;
  price_prediction_1h: PriceRangePrediction;
  price_prediction_1d: PriceRangePrediction;
  price_prediction_1w: PriceRangePrediction;
  confidence: ConfidenceLevel;
  confidence_reasoning: string;
  analysis_narrative: string;
}

export interface SymbolInfo {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
}

