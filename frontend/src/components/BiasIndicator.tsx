import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import type { BiasType, ConfidenceLevel } from '../types';

interface BiasIndicatorProps {
  bias: BiasType;
  confidence: ConfidenceLevel;
  timeframe: string;
  probability?: string;
}

export default function BiasIndicator({ bias, confidence, timeframe, probability }: BiasIndicatorProps) {
  const getBiasConfig = () => {
    switch (bias) {
      case 'Bullish':
        return {
          icon: TrendingUp,
          color: 'text-bullish',
          bg: 'bg-bullish/10',
          border: 'border-bullish/30',
          glow: 'shadow-bullish/20',
          label: 'BULLISH',
        };
      case 'Bearish':
        return {
          icon: TrendingDown,
          color: 'text-bearish',
          bg: 'bg-bearish/10',
          border: 'border-bearish/30',
          glow: 'shadow-bearish/20',
          label: 'BEARISH',
        };
      default:
        return {
          icon: Minus,
          color: 'text-neutral',
          bg: 'bg-neutral/10',
          border: 'border-neutral/30',
          glow: 'shadow-neutral/20',
          label: 'NEUTRAL',
        };
    }
  };

  const config = getBiasConfig();
  const Icon = config.icon;

  const confidenceWidth = {
    'Low': '33%',
    'Medium': '66%',
    'High': '100%',
  }[confidence];

  const confidenceColor = {
    'Low': 'bg-gradient-to-r from-bearish to-neon-orange',
    'Medium': 'bg-gradient-to-r from-neon-orange to-neon-yellow',
    'High': 'bg-gradient-to-r from-neon-yellow to-bullish',
  }[confidence];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={clsx(
        "glass rounded-2xl p-5 border",
        config.border,
        `shadow-lg ${config.glow}`
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className={clsx("p-2 rounded-lg", config.bg)}>
            <Icon className={clsx("w-5 h-5", config.color)} />
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider">{timeframe} Outlook</p>
            <h3 className={clsx("font-display font-bold text-lg", config.color)}>
              {config.label}
            </h3>
          </div>
        </div>
        
        {probability && (
          <div className={clsx(
            "px-3 py-1 rounded-full text-xs font-bold uppercase",
            config.bg, config.color, config.border, "border"
          )}>
            {probability}
          </div>
        )}
      </div>

      {/* Confidence Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="text-gray-500">Confidence</span>
          <span className={config.color}>{confidence}</span>
        </div>
        <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: confidenceWidth }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={clsx("h-full rounded-full", confidenceColor)}
          />
        </div>
      </div>

      {/* Visual Bias Meter */}
      <div className="relative h-8 bg-dark-700 rounded-full overflow-hidden">
        <div className="absolute inset-0 flex">
          <div className="w-1/2 bg-gradient-to-r from-bearish/30 to-transparent" />
          <div className="w-1/2 bg-gradient-to-l from-bullish/30 to-transparent" />
        </div>
        
        {/* Center line */}
        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-600" />
        
        {/* Indicator */}
        <motion.div
          initial={{ left: '50%' }}
          animate={{ 
            left: bias === 'Bullish' ? '75%' : bias === 'Bearish' ? '25%' : '50%'
          }}
          transition={{ duration: 0.5, type: 'spring' }}
          className={clsx(
            "absolute top-1/2 -translate-y-1/2 -translate-x-1/2",
            "w-4 h-4 rounded-full",
            config.bg, config.border, "border-2",
            "shadow-lg"
          )}
          style={{
            boxShadow: bias === 'Bullish' 
              ? '0 0 15px rgba(0, 255, 157, 0.5)' 
              : bias === 'Bearish'
              ? '0 0 15px rgba(255, 0, 85, 0.5)'
              : '0 0 15px rgba(0, 245, 255, 0.5)'
          }}
        />
        
        {/* Labels */}
        <div className="absolute inset-0 flex items-center justify-between px-4 text-xs font-mono">
          <span className="text-bearish/70">SELL</span>
          <span className="text-bullish/70">BUY</span>
        </div>
      </div>
    </motion.div>
  );
}

