import { motion } from 'framer-motion';
import { Activity, BarChart2, Waves, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';
import type { TechnicalIndicators } from '../types';

interface IndicatorPanelProps {
  indicators: TechnicalIndicators | null;
  timeframe: string;
  loading?: boolean;
}

export default function IndicatorPanel({ indicators, timeframe, loading }: IndicatorPanelProps) {
  if (loading) {
    return (
      <div className="glass rounded-2xl p-6 border border-neon-cyan/20">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-dark-600 rounded w-32" />
          <div className="grid grid-cols-2 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-20 bg-dark-600 rounded-xl" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!indicators) return null;

  const { moving_averages, momentum, volatility } = indicators;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="glass rounded-2xl p-6 border border-neon-cyan/20"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-neon-cyan" />
          <h3 className="font-display font-bold text-lg text-white">Technical Indicators</h3>
        </div>
        <span className="text-xs text-gray-500 font-mono">{timeframe}</span>
      </div>

      <div className="space-y-6">
        {/* Momentum Section */}
        <div>
          <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <TrendingUp className="w-3 h-3" /> Momentum
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <RSIGauge value={momentum.rsi_14} state={momentum.rsi_state} />
            <MACDIndicator 
              line={momentum.macd_line}
              signal={momentum.macd_signal}
              histogram={momentum.macd_histogram}
              state={momentum.macd_state}
            />
            <StochIndicator k={momentum.stoch_k} d={momentum.stoch_d} state={momentum.stoch_state} />
            <CCIIndicator value={momentum.cci} />
          </div>
        </div>

        {/* Moving Averages */}
        <div>
          <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Waves className="w-3 h-3" /> Moving Averages
          </h4>
          <div className="grid grid-cols-4 gap-2">
            <MAValue label="EMA 9" value={moving_averages.ema_9} />
            <MAValue label="EMA 21" value={moving_averages.ema_21} />
            <MAValue label="EMA 50" value={moving_averages.ema_50} />
            <MAValue label="EMA 200" value={moving_averages.ema_200} />
          </div>
          {moving_averages.vwap && (
            <div className="mt-3 p-3 rounded-lg bg-dark-700/50 flex items-center justify-between">
              <span className="text-xs text-gray-400">VWAP</span>
              <span className="font-mono text-sm text-neon-cyan">
                ${moving_averages.vwap.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </span>
            </div>
          )}
        </div>

        {/* Volatility */}
        <div>
          <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <BarChart2 className="w-3 h-3" /> Volatility
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <ATRIndicator value={volatility.atr_14} percent={volatility.atr_percent} />
            <BollingerBands 
              upper={volatility.bb_upper}
              middle={volatility.bb_middle}
              lower={volatility.bb_lower}
              position={volatility.bb_position}
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// RSI Gauge Component
function RSIGauge({ value, state }: { value: number | null; state: string | null }) {
  if (value === null) return <EmptyIndicator label="RSI" />;

  const getColor = () => {
    if (value < 30) return 'text-bullish';
    if (value > 70) return 'text-bearish';
    return 'text-neutral';
  };

  const rotation = ((value - 50) / 50) * 90; // -90 to 90 degrees

  return (
    <div className="bg-dark-700/50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400">RSI (14)</span>
        <span className={clsx("text-xs font-medium", getColor())}>{state}</span>
      </div>
      <div className="flex items-center gap-3">
        <div className="relative w-16 h-8">
          {/* Semi-circle gauge */}
          <svg viewBox="0 0 100 50" className="w-full h-full">
            <path
              d="M 5 50 A 45 45 0 0 1 95 50"
              fill="none"
              stroke="#2f2f3d"
              strokeWidth="8"
            />
            <path
              d="M 5 50 A 45 45 0 0 1 95 50"
              fill="none"
              stroke="url(#rsi-gradient)"
              strokeWidth="8"
              strokeDasharray={`${(value / 100) * 141} 141`}
            />
            <defs>
              <linearGradient id="rsi-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#00ff9d" />
                <stop offset="50%" stopColor="#00f5ff" />
                <stop offset="100%" stopColor="#ff0055" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <span className={clsx("font-display text-2xl font-bold", getColor())}>
          {value.toFixed(1)}
        </span>
      </div>
    </div>
  );
}

// MACD Component
function MACDIndicator({ 
  line, signal, histogram, state 
}: { 
  line: number | null; 
  signal: number | null;
  histogram: number | null;
  state: string | null;
}) {
  if (line === null) return <EmptyIndicator label="MACD" />;

  const isBullish = histogram && histogram > 0;

  return (
    <div className="bg-dark-700/50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400">MACD</span>
        <span className={clsx(
          "text-xs font-medium",
          isBullish ? "text-bullish" : "text-bearish"
        )}>{state}</span>
      </div>
      <div className="space-y-1">
        <div className="flex justify-between text-xs">
          <span className="text-gray-500">Line</span>
          <span className="font-mono text-white">{line.toFixed(4)}</span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-gray-500">Signal</span>
          <span className="font-mono text-white">{signal?.toFixed(4) ?? 'N/A'}</span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-gray-500">Histogram</span>
          <span className={clsx(
            "font-mono font-bold",
            isBullish ? "text-bullish" : "text-bearish"
          )}>{histogram?.toFixed(4) ?? 'N/A'}</span>
        </div>
      </div>
    </div>
  );
}

// Stochastic Component
function StochIndicator({ k, d, state }: { k: number | null; d: number | null; state: string | null }) {
  if (k === null) return <EmptyIndicator label="Stochastic" />;

  const getColor = () => {
    if (k < 20) return 'text-bullish';
    if (k > 80) return 'text-bearish';
    return 'text-neutral';
  };

  return (
    <div className="bg-dark-700/50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400">Stochastic</span>
        <span className={clsx("text-xs font-medium", getColor())}>{state}</span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className={clsx("font-display text-xl font-bold", getColor())}>
          {k.toFixed(1)}
        </span>
        <span className="text-xs text-gray-500">/ {d?.toFixed(1) ?? 'N/A'}</span>
      </div>
      <div className="mt-2 h-1.5 bg-dark-600 rounded-full overflow-hidden">
        <div 
          className={clsx(
            "h-full rounded-full",
            k < 20 ? "bg-bullish" : k > 80 ? "bg-bearish" : "bg-neutral"
          )}
          style={{ width: `${k}%` }}
        />
      </div>
    </div>
  );
}

// CCI Component
function CCIIndicator({ value }: { value: number | null }) {
  if (value === null) return <EmptyIndicator label="CCI" />;

  const getColor = () => {
    if (value < -100) return 'text-bullish';
    if (value > 100) return 'text-bearish';
    return 'text-neutral';
  };

  return (
    <div className="bg-dark-700/50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400">CCI (20)</span>
        <span className={clsx("text-xs font-medium", getColor())}>
          {value < -100 ? 'Oversold' : value > 100 ? 'Overbought' : 'Neutral'}
        </span>
      </div>
      <span className={clsx("font-display text-xl font-bold", getColor())}>
        {value.toFixed(1)}
      </span>
    </div>
  );
}

// ATR Component
function ATRIndicator({ value, percent }: { value: number | null; percent: number | null }) {
  if (value === null) return <EmptyIndicator label="ATR" />;

  const getVolatilityLevel = () => {
    if (!percent) return 'Normal';
    if (percent > 5) return 'Extreme';
    if (percent > 3) return 'High';
    if (percent < 1) return 'Low';
    return 'Normal';
  };

  return (
    <div className="bg-dark-700/50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400">ATR (14)</span>
        <span className="text-xs font-medium text-neon-orange">{getVolatilityLevel()}</span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="font-display text-xl font-bold text-white">
          ${value.toFixed(2)}
        </span>
        {percent && (
          <span className="text-xs text-gray-500">({percent.toFixed(2)}%)</span>
        )}
      </div>
    </div>
  );
}

// Bollinger Bands Component
function BollingerBands({ 
  upper, middle, lower, position 
}: { 
  upper: number | null;
  middle: number | null;
  lower: number | null;
  position: number | null;
}) {
  if (upper === null) return <EmptyIndicator label="Bollinger" />;

  const positionPercent = position ? position * 100 : 50;

  return (
    <div className="bg-dark-700/50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400">Bollinger Bands</span>
        <span className="text-xs font-medium text-neon-purple">
          {positionPercent > 80 ? 'Upper' : positionPercent < 20 ? 'Lower' : 'Middle'}
        </span>
      </div>
      <div className="space-y-1 text-xs">
        <div className="flex justify-between">
          <span className="text-bearish">Upper</span>
          <span className="font-mono">${upper.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-neutral">Mid</span>
          <span className="font-mono">${middle?.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-bullish">Lower</span>
          <span className="font-mono">${lower?.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}

// MA Value Display
function MAValue({ label, value }: { label: string; value: number | null }) {
  return (
    <div className="bg-dark-700/50 rounded-lg p-2 text-center">
      <span className="text-[10px] text-gray-500 block">{label}</span>
      <span className="font-mono text-xs text-white">
        {value ? `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : 'N/A'}
      </span>
    </div>
  );
}

// Empty Indicator Placeholder
function EmptyIndicator({ label }: { label: string }) {
  return (
    <div className="bg-dark-700/50 rounded-xl p-4 flex items-center justify-center">
      <span className="text-xs text-gray-500">{label}: N/A</span>
    </div>
  );
}

