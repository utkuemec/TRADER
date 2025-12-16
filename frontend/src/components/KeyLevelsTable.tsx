import { motion } from 'framer-motion';
import { Target, ArrowUp, ArrowDown, AlertTriangle, Shield } from 'lucide-react';
import clsx from 'clsx';
import type { KeyLevels } from '../types';

interface KeyLevelsTableProps {
  levels: KeyLevels;
  currentPrice: number;
  loading?: boolean;
}

export default function KeyLevelsTable({ levels, currentPrice, loading }: KeyLevelsTableProps) {
  if (loading) {
    return (
      <div className="glass rounded-2xl p-6 border border-neon-cyan/20">
        <div className="animate-pulse space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-12 bg-dark-600 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  const formatPrice = (price: number | null) => {
    if (!price) return 'N/A';
    return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const getDistancePercent = (price: number | null) => {
    if (!price || !currentPrice) return null;
    return ((price - currentPrice) / currentPrice * 100).toFixed(2);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 }}
      className="glass rounded-2xl p-6 border border-neon-cyan/20"
    >
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-5 h-5 text-neon-cyan" />
        <h3 className="font-display font-bold text-lg text-white">Key Price Levels</h3>
      </div>

      <div className="space-y-3">
        {/* Resistance Levels */}
        <LevelRow
          label="Major Resistance"
          price={levels.major_resistance}
          currentPrice={currentPrice}
          type="resistance"
          icon={<ArrowUp className="w-4 h-4" />}
        />
        <LevelRow
          label="Immediate Resistance"
          price={levels.immediate_resistance}
          currentPrice={currentPrice}
          type="resistance"
          icon={<ArrowUp className="w-4 h-4" />}
        />

        {/* Current Price Marker */}
        <div className="relative py-3">
          <div className="absolute inset-x-0 top-1/2 h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent" />
          <div className="relative flex items-center justify-center">
            <span className="px-4 py-1 bg-dark-800 rounded-full text-xs font-mono text-neon-cyan border border-neon-cyan/30">
              Current: {formatPrice(currentPrice)}
            </span>
          </div>
        </div>

        {/* Support Levels */}
        <LevelRow
          label="Immediate Support"
          price={levels.immediate_support}
          currentPrice={currentPrice}
          type="support"
          icon={<Shield className="w-4 h-4" />}
        />
        <LevelRow
          label="Major Support"
          price={levels.major_support}
          currentPrice={currentPrice}
          type="support"
          icon={<Shield className="w-4 h-4" />}
        />

        {/* Invalidation Levels */}
        <div className="pt-3 mt-3 border-t border-dark-600">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <AlertTriangle className="w-3 h-3 text-neon-orange" />
            Invalidation Levels
          </p>
          <div className="grid grid-cols-2 gap-3">
            <InvalidationLevel
              label="Long Invalid"
              price={levels.invalidation_long}
              currentPrice={currentPrice}
            />
            <InvalidationLevel
              label="Short Invalid"
              price={levels.invalidation_short}
              currentPrice={currentPrice}
            />
          </div>
        </div>

        {/* Targets */}
        {(levels.targets_long.length > 0 || levels.targets_short.length > 0) && (
          <div className="pt-3 mt-3 border-t border-dark-600">
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">
              Price Targets
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-bullish mb-2">Long Targets</p>
                <div className="space-y-1">
                  {levels.targets_long.slice(0, 3).map((target, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">T{i + 1}</span>
                      <span className="font-mono text-white">{formatPrice(target)}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs text-bearish mb-2">Short Targets</p>
                <div className="space-y-1">
                  {levels.targets_short.slice(0, 3).map((target, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">T{i + 1}</span>
                      <span className="font-mono text-white">{formatPrice(target)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

interface LevelRowProps {
  label: string;
  price: number | null;
  currentPrice: number;
  type: 'resistance' | 'support';
  icon: React.ReactNode;
}

function LevelRow({ label, price, currentPrice, type, icon }: LevelRowProps) {
  const formatPrice = (p: number | null) => {
    if (!p) return 'N/A';
    return `$${p.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const getDistance = () => {
    if (!price) return null;
    const dist = ((price - currentPrice) / currentPrice * 100);
    return dist > 0 ? `+${dist.toFixed(2)}%` : `${dist.toFixed(2)}%`;
  };

  const isResistance = type === 'resistance';
  const colorClass = isResistance ? 'text-bearish' : 'text-bullish';
  const bgClass = isResistance ? 'bg-bearish/10' : 'bg-bullish/10';
  const borderClass = isResistance ? 'border-bearish/20' : 'border-bullish/20';

  return (
    <div className={clsx(
      "flex items-center justify-between p-3 rounded-lg border",
      bgClass, borderClass
    )}>
      <div className="flex items-center gap-3">
        <div className={clsx("p-1.5 rounded-lg", bgClass, colorClass)}>
          {icon}
        </div>
        <div>
          <p className="text-sm font-medium text-white">{label}</p>
          <p className="text-xs text-gray-500">{type === 'resistance' ? 'Sell Zone' : 'Buy Zone'}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-mono font-bold text-white">{formatPrice(price)}</p>
        {price && (
          <p className={clsx("text-xs font-mono", colorClass)}>{getDistance()}</p>
        )}
      </div>
    </div>
  );
}

function InvalidationLevel({ label, price, currentPrice }: { 
  label: string; 
  price: number | null;
  currentPrice: number;
}) {
  const formatPrice = (p: number | null) => {
    if (!p) return 'N/A';
    return `$${p.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  return (
    <div className="bg-neon-orange/10 border border-neon-orange/20 rounded-lg p-3">
      <p className="text-xs text-neon-orange mb-1">{label}</p>
      <p className="font-mono font-bold text-white">{formatPrice(price)}</p>
    </div>
  );
}

