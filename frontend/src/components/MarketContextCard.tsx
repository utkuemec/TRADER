import { motion } from 'framer-motion';
import { Compass, TrendingUp, TrendingDown, Minus, Zap, Droplets, Layers } from 'lucide-react';
import clsx from 'clsx';
import type { MarketContext, MultiTimeframeSummary } from '../types';

interface MarketContextCardProps {
  context: MarketContext;
  mtfSummary: MultiTimeframeSummary;
  loading?: boolean;
}

export default function MarketContextCard({ context, mtfSummary, loading }: MarketContextCardProps) {
  if (loading) {
    return (
      <div className="glass rounded-2xl p-6 border border-neon-cyan/20">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-dark-600 rounded w-32" />
          <div className="grid grid-cols-3 gap-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-20 bg-dark-600 rounded-xl" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const getTrendIcon = (trend: string) => {
    if (trend.includes('Uptrend')) return <TrendingUp className="w-4 h-4 text-bullish" />;
    if (trend.includes('Downtrend')) return <TrendingDown className="w-4 h-4 text-bearish" />;
    return <Minus className="w-4 h-4 text-neutral" />;
  };

  const getVolatilityColor = (vol: string) => {
    switch (vol) {
      case 'Extreme': return 'text-bearish';
      case 'High': return 'text-neon-orange';
      case 'Low': return 'text-bullish';
      default: return 'text-neon-cyan';
    }
  };

  const getAlignmentColor = (alignment: string) => {
    if (alignment.includes('Bullish')) return 'text-bullish bg-bullish/10 border-bullish/30';
    if (alignment.includes('Bearish')) return 'text-bearish bg-bearish/10 border-bearish/30';
    return 'text-neutral bg-neutral/10 border-neutral/30';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6 border border-neon-cyan/20"
    >
      <div className="flex items-center gap-2 mb-4">
        <Compass className="w-5 h-5 text-neon-cyan" />
        <h3 className="font-display font-bold text-lg text-white">Market Context</h3>
      </div>

      {/* Trend Overview */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <TrendCard
          label="Short TF"
          trend={context.short_tf_trend}
          sublabel="1m - 30m"
        />
        <TrendCard
          label="Mid TF"
          trend={context.mid_tf_trend}
          sublabel="1h - 4h"
        />
        <TrendCard
          label="High TF"
          trend={context.high_tf_trend}
          sublabel="1d+"
        />
      </div>

      {/* MTF Alignment Badge */}
      <div className={clsx(
        "p-4 rounded-xl border mb-4",
        getAlignmentColor(mtfSummary.alignment)
      )}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4" />
            <span className="font-medium">MTF Alignment</span>
          </div>
          <span className="font-display font-bold">{mtfSummary.alignment}</span>
        </div>
      </div>

      {/* Additional Context */}
      <div className="grid grid-cols-2 gap-4">
        {/* Volatility */}
        <div className="bg-dark-700/50 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Zap className={clsx("w-4 h-4", getVolatilityColor(context.volatility))} />
            <span className="text-xs text-gray-400">Volatility</span>
          </div>
          <p className={clsx("font-display font-bold", getVolatilityColor(context.volatility))}>
            {context.volatility}
          </p>
        </div>

        {/* Market Phase */}
        <div className="bg-dark-700/50 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Droplets className="w-4 h-4 text-neon-purple" />
            <span className="text-xs text-gray-400">Market Phase</span>
          </div>
          <p className="font-display font-bold text-neon-purple">
            {context.market_phase}
          </p>
        </div>
      </div>

      {/* Liquidity Context */}
      <div className="mt-4 p-3 rounded-lg bg-dark-700/30 border border-dark-600">
        <p className="text-xs text-gray-400 mb-1">Liquidity Context</p>
        <p className="text-sm text-white">{context.liquidity_context}</p>
      </div>
    </motion.div>
  );
}

interface TrendCardProps {
  label: string;
  trend: string;
  sublabel: string;
}

function TrendCard({ label, trend, sublabel }: TrendCardProps) {
  const getConfig = () => {
    if (trend.includes('Uptrend')) {
      return {
        icon: TrendingUp,
        color: 'text-bullish',
        bg: 'bg-bullish/10',
        border: 'border-bullish/20',
      };
    }
    if (trend.includes('Downtrend')) {
      return {
        icon: TrendingDown,
        color: 'text-bearish',
        bg: 'bg-bearish/10',
        border: 'border-bearish/20',
      };
    }
    return {
      icon: Minus,
      color: 'text-neutral',
      bg: 'bg-neutral/10',
      border: 'border-neutral/20',
    };
  };

  const config = getConfig();
  const Icon = config.icon;

  return (
    <div className={clsx(
      "rounded-xl p-4 border text-center",
      config.bg, config.border
    )}>
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <div className="flex items-center justify-center gap-2 mb-1">
        <Icon className={clsx("w-5 h-5", config.color)} />
        <span className={clsx("font-display font-bold", config.color)}>{trend}</span>
      </div>
      <p className="text-[10px] text-gray-600">{sublabel}</p>
    </div>
  );
}

