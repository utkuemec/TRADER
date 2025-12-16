import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Activity, Clock } from 'lucide-react';
import clsx from 'clsx';
import type { Ticker } from '../types';

interface PriceCardProps {
  ticker: Ticker | null;
  loading?: boolean;
}

export default function PriceCard({ ticker, loading }: PriceCardProps) {
  const [priceFlash, setPriceFlash] = useState<'up' | 'down' | null>(null);
  const prevPrice = useRef<number | null>(null);

  useEffect(() => {
    if (ticker && prevPrice.current !== null) {
      if (ticker.last > prevPrice.current) {
        setPriceFlash('up');
      } else if (ticker.last < prevPrice.current) {
        setPriceFlash('down');
      }
      setTimeout(() => setPriceFlash(null), 500);
    }
    prevPrice.current = ticker?.last ?? null;
  }, [ticker?.last]);

  if (loading) {
    return (
      <div className="glass rounded-2xl p-6 border border-neon-cyan/20">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-dark-600 rounded w-24" />
          <div className="h-10 bg-dark-600 rounded w-48" />
          <div className="h-4 bg-dark-600 rounded w-32" />
        </div>
      </div>
    );
  }

  if (!ticker) return null;

  const isPositive = (ticker.percentage ?? 0) >= 0;
  const priceChange = ticker.change ?? 0;
  const percentChange = ticker.percentage ?? 0;

  const formatPrice = (price: number) => {
    if (price >= 1000) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (price >= 1) return price.toFixed(4);
    return price.toFixed(8);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        "glass rounded-2xl p-6 border transition-colors duration-500",
        priceFlash === 'up' && "border-bullish/50 bg-bullish/5",
        priceFlash === 'down' && "border-bearish/50 bg-bearish/5",
        !priceFlash && "border-neon-cyan/20"
      )}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm text-gray-400 mb-1">Current Price</p>
          <div className="flex items-baseline gap-2">
            <span 
              className={clsx(
                "font-display text-4xl font-bold transition-colors",
                priceFlash === 'up' && "text-bullish",
                priceFlash === 'down' && "text-bearish",
                !priceFlash && "text-white"
              )}
            >
              ${formatPrice(ticker.last)}
            </span>
            <span className="text-sm text-gray-500">USD</span>
          </div>
        </div>
        
        <div className={clsx(
          "flex items-center gap-2 px-3 py-2 rounded-xl",
          isPositive ? "bg-bullish/10 text-bullish" : "bg-bearish/10 text-bearish"
        )}>
          {isPositive ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
          <div className="text-right">
            <p className="font-mono font-bold">
              {isPositive ? '+' : ''}{percentChange.toFixed(2)}%
            </p>
            <p className="text-xs opacity-70">
              {isPositive ? '+' : ''}${priceChange.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <StatItem 
          label="24h High" 
          value={ticker.high ? `$${formatPrice(ticker.high)}` : 'N/A'} 
          icon={<TrendingUp className="w-4 h-4 text-bullish" />}
        />
        <StatItem 
          label="24h Low" 
          value={ticker.low ? `$${formatPrice(ticker.low)}` : 'N/A'} 
          icon={<TrendingDown className="w-4 h-4 text-bearish" />}
        />
        <StatItem 
          label="24h Volume" 
          value={ticker.volume ? formatVolume(ticker.volume) : 'N/A'} 
          icon={<Activity className="w-4 h-4 text-neon-cyan" />}
        />
      </div>

      <div className="mt-4 pt-4 border-t border-dark-600 flex items-center gap-2 text-xs text-gray-500">
        <Clock className="w-3 h-3" />
        <span>Updated {new Date(ticker.timestamp).toLocaleTimeString()}</span>
      </div>
    </motion.div>
  );
}

interface StatItemProps {
  label: string;
  value: string;
  icon: React.ReactNode;
}

function StatItem({ label, value, icon }: StatItemProps) {
  return (
    <div className="text-center">
      <div className="flex items-center justify-center gap-1 mb-1">
        {icon}
        <span className="text-xs text-gray-500">{label}</span>
      </div>
      <p className="font-mono text-sm text-white">{value}</p>
    </div>
  );
}

function formatVolume(volume: number): string {
  if (volume >= 1e9) return (volume / 1e9).toFixed(2) + 'B';
  if (volume >= 1e6) return (volume / 1e6).toFixed(2) + 'M';
  if (volume >= 1e3) return (volume / 1e3).toFixed(2) + 'K';
  return volume.toFixed(2);
}

