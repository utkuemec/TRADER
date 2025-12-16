import { motion } from 'framer-motion';
import { Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import clsx from 'clsx';
import type { TimeframeBias } from '../types';

interface TimeframeBiasGridProps {
  biases: TimeframeBias[];
  loading?: boolean;
}

export default function TimeframeBiasGrid({ biases, loading }: TimeframeBiasGridProps) {
  if (loading) {
    return (
      <div className="glass rounded-2xl p-6 border border-neon-cyan/20">
        <div className="animate-pulse">
          <div className="h-6 bg-dark-600 rounded w-48 mb-4" />
          <div className="grid grid-cols-3 gap-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-24 bg-dark-600 rounded-xl" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const timeframeOrder = ['5m', '15m', '30m', '1h', '4h', '1d'];
  const sortedBiases = [...biases].sort(
    (a, b) => timeframeOrder.indexOf(a.timeframe) - timeframeOrder.indexOf(b.timeframe)
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="glass rounded-2xl p-6 border border-neon-cyan/20"
    >
      <div className="flex items-center gap-2 mb-4">
        <Clock className="w-5 h-5 text-neon-cyan" />
        <h3 className="font-display font-bold text-lg text-white">Multi-Timeframe Bias</h3>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {sortedBiases.map((bias, index) => (
          <TimeframeCard key={bias.timeframe} bias={bias} index={index} />
        ))}
      </div>

      {/* Legend */}
      <div className="mt-4 pt-4 border-t border-dark-600 flex items-center justify-center gap-6">
        <LegendItem color="bullish" label="Bullish" />
        <LegendItem color="bearish" label="Bearish" />
        <LegendItem color="neutral" label="Neutral" />
      </div>
    </motion.div>
  );
}

interface TimeframeCardProps {
  bias: TimeframeBias;
  index: number;
}

function TimeframeCard({ bias, index }: TimeframeCardProps) {
  const getConfig = () => {
    switch (bias.bias) {
      case 'Bullish':
        return {
          icon: TrendingUp,
          color: 'text-bullish',
          bg: 'bg-bullish/10',
          border: 'border-bullish/30',
          glow: 'hover:shadow-bullish/20',
        };
      case 'Bearish':
        return {
          icon: TrendingDown,
          color: 'text-bearish',
          bg: 'bg-bearish/10',
          border: 'border-bearish/30',
          glow: 'hover:shadow-bearish/20',
        };
      default:
        return {
          icon: Minus,
          color: 'text-neutral',
          bg: 'bg-neutral/10',
          border: 'border-neutral/30',
          glow: 'hover:shadow-neutral/20',
        };
    }
  };

  const config = getConfig();
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.05 }}
      className={clsx(
        "rounded-xl p-4 border transition-all cursor-default",
        "hover:shadow-lg",
        config.bg,
        config.border,
        config.glow
      )}
    >
      <div className="text-center">
        <span className="text-xs text-gray-500 font-mono block mb-2">{bias.timeframe}</span>
        <div className={clsx("inline-flex p-2 rounded-lg mb-2", config.bg)}>
          <Icon className={clsx("w-5 h-5", config.color)} />
        </div>
        <p className={clsx("font-display font-bold text-sm", config.color)}>
          {bias.bias}
        </p>
        <p className="text-[10px] text-gray-500 mt-1 truncate" title={bias.notes}>
          {bias.trend}
        </p>
      </div>
    </motion.div>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  const colorClass = {
    bullish: 'bg-bullish',
    bearish: 'bg-bearish',
    neutral: 'bg-neutral',
  }[color];

  return (
    <div className="flex items-center gap-2">
      <div className={clsx("w-3 h-3 rounded-full", colorClass)} />
      <span className="text-xs text-gray-400">{label}</span>
    </div>
  );
}

