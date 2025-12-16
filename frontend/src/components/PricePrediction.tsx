import { motion } from 'framer-motion';
import { Target, TrendingUp, TrendingDown, Minus, Clock, Calendar, CalendarDays, Zap, Lock, Timer } from 'lucide-react';
import clsx from 'clsx';

interface PriceRangePrediction {
  timeframe: string;
  current_price: number;
  price_at_prediction: number;
  predicted_low: number;
  predicted_high: number;
  predicted_target: number;
  range_size: number;
  range_percent: number;
  direction: 'Bullish' | 'Bearish' | 'Neutral';
  confidence: 'Low' | 'Medium' | 'High';
  reasoning: string;
  created_at: string | null;
  expires_at: string | null;
  time_remaining: string | null;
  is_locked: boolean;
}

interface PricePredictionProps {
  prediction1h: PriceRangePrediction | null;
  prediction1d: PriceRangePrediction | null;
  prediction1w: PriceRangePrediction | null;
  loading?: boolean;
}

export default function PricePrediction({ prediction1h, prediction1d, prediction1w, loading }: PricePredictionProps) {
  if (loading) {
    return (
      <div className="glass rounded-2xl p-6 border border-neon-cyan/20">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-dark-600 rounded w-48" />
          <div className="grid grid-cols-2 gap-4">
            <div className="h-48 bg-dark-600 rounded-xl" />
            <div className="h-48 bg-dark-600 rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6 border border-neon-pink/30 shadow-lg shadow-neon-pink/10"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-lg bg-neon-pink/20">
          <Target className="w-6 h-6 text-neon-pink" />
        </div>
        <div>
          <h3 className="font-display font-bold text-xl text-white">Precise Price Predictions</h3>
          <p className="text-xs text-gray-500">Time-locked targets • Updates when timer expires</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {prediction1h && (
          <PredictionCard
            prediction={prediction1h}
            icon={<Clock className="w-5 h-5" />}
            label="1 Hour Target"
            accentColor="cyan"
          />
        )}
        {prediction1d && (
          <PredictionCard
            prediction={prediction1d}
            icon={<Calendar className="w-5 h-5" />}
            label="1 Day Target"
            accentColor="pink"
          />
        )}
        {prediction1w && (
          <PredictionCard
            prediction={prediction1w}
            icon={<CalendarDays className="w-5 h-5" />}
            label="1 Week Target"
            accentColor="purple"
          />
        )}
      </div>
    </motion.div>
  );
}

interface PredictionCardProps {
  prediction: PriceRangePrediction;
  icon: React.ReactNode;
  label: string;
  accentColor: 'cyan' | 'pink' | 'purple';
}

function PredictionCard({ prediction, icon, label, accentColor }: PredictionCardProps) {
  const getDirectionConfig = () => {
    switch (prediction.direction) {
      case 'Bullish':
        return {
          icon: TrendingUp,
          color: 'text-bullish',
          bg: 'bg-bullish/10',
          border: 'border-bullish/30',
        };
      case 'Bearish':
        return {
          icon: TrendingDown,
          color: 'text-bearish',
          bg: 'bg-bearish/10',
          border: 'border-bearish/30',
        };
      default:
        return {
          icon: Minus,
          color: 'text-neutral',
          bg: 'bg-neutral/10',
          border: 'border-neutral/30',
        };
    }
  };

  const config = getDirectionConfig();
  const DirectionIcon = config.icon;

  const confidenceWidth = {
    'Low': '33%',
    'Medium': '66%',
    'High': '100%',
  }[prediction.confidence];

  const confidenceColor = {
    'Low': 'bg-bearish',
    'Medium': 'bg-neon-yellow',
    'High': 'bg-bullish',
  }[prediction.confidence];

  const accentClasses = {
    cyan: 'border-neon-cyan/30 hover:border-neon-cyan/50',
    pink: 'border-neon-pink/30 hover:border-neon-pink/50',
    purple: 'border-neon-purple/30 hover:border-neon-purple/50',
  };

  // Calculate position of current price and target within range
  const rangeStart = prediction.predicted_low;
  const rangeEnd = prediction.predicted_high;
  const rangeTotal = rangeEnd - rangeStart;
  const currentPos = ((prediction.current_price - rangeStart) / rangeTotal) * 100;
  const targetPos = ((prediction.predicted_target - rangeStart) / rangeTotal) * 100;
  const predictionPricePos = ((prediction.price_at_prediction - rangeStart) / rangeTotal) * 100;

  // Format time remaining
  const formatTimeRemaining = (timeStr: string | null) => {
    if (!timeStr) return 'Unknown';
    return timeStr;
  };

  // Calculate price change since prediction
  const priceChange = prediction.current_price - prediction.price_at_prediction;
  const priceChangePercent = (priceChange / prediction.price_at_prediction) * 100;

  return (
    <div className={clsx(
      "rounded-xl p-4 border transition-all",
      "bg-dark-800/50",
      accentClasses[accentColor]
    )}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={clsx("p-1.5 rounded-lg", `bg-neon-${accentColor}/20`, `text-neon-${accentColor}`)}>
            {icon}
          </div>
          <span className="font-display font-bold text-white">{label}</span>
        </div>
        <div className={clsx("flex items-center gap-1 px-2 py-1 rounded-lg", config.bg, config.border, "border")}>
          <DirectionIcon className={clsx("w-4 h-4", config.color)} />
          <span className={clsx("text-xs font-bold", config.color)}>{prediction.direction}</span>
        </div>
      </div>

      {/* Time Lock Status */}
      {prediction.is_locked && prediction.time_remaining && (
        <div className="mb-3 p-2 rounded-lg bg-neon-purple/10 border border-neon-purple/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Lock className="w-3 h-3 text-neon-purple" />
              <span className="text-xs text-neon-purple font-medium">LOCKED PREDICTION</span>
            </div>
            <div className="flex items-center gap-1">
              <Timer className="w-3 h-3 text-neon-yellow" />
              <span className="text-xs text-neon-yellow font-mono">{formatTimeRemaining(prediction.time_remaining)}</span>
            </div>
          </div>
          <p className="text-[10px] text-gray-500 mt-1">
            Prediction made at ${prediction.price_at_prediction.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
        </div>
      )}

      {/* Target Price - Big Display */}
      <div className="text-center mb-3">
        <p className="text-xs text-gray-500 mb-1">Target Price</p>
        <p className={clsx("font-display text-3xl font-bold", config.color)}>
          ${prediction.predicted_target.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
        {/* Show price change since prediction */}
        <p className={clsx(
          "text-xs mt-1",
          priceChange >= 0 ? "text-bullish" : "text-bearish"
        )}>
          Current: ${prediction.current_price.toLocaleString()} ({priceChange >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}% since prediction)
        </p>
      </div>

      {/* Range Visualization */}
      <div className="mb-3">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>${prediction.predicted_low.toLocaleString()}</span>
          <span>${prediction.predicted_high.toLocaleString()}</span>
        </div>
        <div className="relative h-8 bg-dark-700 rounded-full overflow-hidden">
          {/* Range gradient */}
          <div className={clsx(
            "absolute inset-0",
            prediction.direction === 'Bullish' 
              ? "bg-gradient-to-r from-bearish/30 via-neutral/30 to-bullish/50"
              : prediction.direction === 'Bearish'
              ? "bg-gradient-to-r from-bearish/50 via-neutral/30 to-bullish/30"
              : "bg-gradient-to-r from-neutral/30 via-neutral/50 to-neutral/30"
          )} />
          
          {/* Prediction price marker (where prediction was made) */}
          <div 
            className="absolute top-0 bottom-0 w-0.5 bg-neon-purple/50"
            style={{ left: `${Math.max(0, Math.min(100, predictionPricePos))}%` }}
          />
          
          {/* Current price marker */}
          <div 
            className="absolute top-0 bottom-0 w-0.5 bg-white/70"
            style={{ left: `${Math.max(0, Math.min(100, currentPos))}%` }}
          >
            <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-white" />
          </div>
          
          {/* Target marker */}
          <motion.div 
            initial={{ left: `${predictionPricePos}%` }}
            animate={{ left: `${Math.max(0, Math.min(100, targetPos))}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={clsx("absolute top-0 bottom-0 w-1", config.color === 'text-bullish' ? 'bg-bullish' : config.color === 'text-bearish' ? 'bg-bearish' : 'bg-neutral')}
            style={{ boxShadow: `0 0 10px ${config.color === 'text-bullish' ? '#00ff9d' : config.color === 'text-bearish' ? '#ff0055' : '#00f5ff'}` }}
          >
            <div className={clsx("absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full", config.bg, "border-2", config.border)} />
          </motion.div>
        </div>
        <div className="flex justify-center mt-1">
          <span className="text-xs text-gray-500">
            Range: ${prediction.range_size.toLocaleString()} ({prediction.range_percent.toFixed(2)}%)
          </span>
        </div>
      </div>

      {/* Confidence */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-gray-500">Confidence</span>
          <span className={clsx(
            prediction.confidence === 'High' ? 'text-bullish' :
            prediction.confidence === 'Medium' ? 'text-neon-yellow' : 'text-bearish'
          )}>{prediction.confidence}</span>
        </div>
        <div className="h-1.5 bg-dark-600 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: confidenceWidth }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={clsx("h-full rounded-full", confidenceColor)}
          />
        </div>
      </div>

      {/* Reasoning */}
      <div className="p-2 rounded-lg bg-dark-700/50">
        <div className="flex items-start gap-2">
          <Zap className="w-3 h-3 text-neon-yellow mt-0.5 flex-shrink-0" />
          <p className="text-xs text-gray-400 leading-relaxed">{prediction.reasoning}</p>
        </div>
      </div>
    </div>
  );
}
