import { motion } from 'framer-motion';
import { Layers, Box, GitBranch, Droplets, BarChart3 } from 'lucide-react';
import clsx from 'clsx';
import type { OrderBlock, FairValueGap, LiquidityZone, SupplyDemandZone } from '../types';

interface SmartMoneyPanelProps {
  orderBlocks: OrderBlock[];
  fairValueGaps: FairValueGap[];
  liquidityZones: LiquidityZone[];
  supplyDemandZones: SupplyDemandZone[];
  currentPrice: number;
  loading?: boolean;
}

export default function SmartMoneyPanel({
  orderBlocks,
  fairValueGaps,
  liquidityZones,
  supplyDemandZones,
  currentPrice,
  loading
}: SmartMoneyPanelProps) {
  if (loading) {
    return (
      <div className="glass rounded-2xl p-6 border border-neon-cyan/20">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-dark-600 rounded w-48" />
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 bg-dark-600 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.25 }}
      className="glass rounded-2xl p-6 border border-neon-cyan/20"
    >
      <div className="flex items-center gap-2 mb-6">
        <Layers className="w-5 h-5 text-neon-pink" />
        <h3 className="font-display font-bold text-lg text-white">Smart Money Concepts</h3>
      </div>

      <div className="space-y-6">
        {/* Order Blocks */}
        <Section
          title="Order Blocks"
          icon={<Box className="w-4 h-4" />}
          color="neon-purple"
          items={orderBlocks.slice(0, 4)}
          renderItem={(ob) => (
            <OrderBlockItem key={`${ob.price_high}-${ob.price_low}`} block={ob} currentPrice={currentPrice} />
          )}
          emptyText="No fresh order blocks detected"
        />

        {/* Fair Value Gaps */}
        <Section
          title="Fair Value Gaps"
          icon={<GitBranch className="w-4 h-4" />}
          color="neon-cyan"
          items={fairValueGaps.slice(0, 4)}
          renderItem={(fvg) => (
            <FVGItem key={`${fvg.high}-${fvg.low}`} gap={fvg} currentPrice={currentPrice} />
          )}
          emptyText="No unfilled FVGs detected"
        />

        {/* Liquidity Zones */}
        <Section
          title="Liquidity Zones"
          icon={<Droplets className="w-4 h-4" />}
          color="neon-yellow"
          items={liquidityZones.slice(0, 4)}
          renderItem={(zone) => (
            <LiquidityItem key={`${zone.price_start}-${zone.price_end}`} zone={zone} currentPrice={currentPrice} />
          )}
          emptyText="No significant liquidity pools detected"
        />

        {/* Supply/Demand Zones */}
        <Section
          title="Supply & Demand"
          icon={<BarChart3 className="w-4 h-4" />}
          color="neon-orange"
          items={supplyDemandZones.slice(0, 4)}
          renderItem={(zone) => (
            <SDZoneItem key={`${zone.price_high}-${zone.price_low}`} zone={zone} currentPrice={currentPrice} />
          )}
          emptyText="No fresh S/D zones detected"
        />
      </div>
    </motion.div>
  );
}

interface SectionProps<T> {
  title: string;
  icon: React.ReactNode;
  color: string;
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  emptyText: string;
}

function Section<T>({ title, icon, color, items, renderItem, emptyText }: SectionProps<T>) {
  return (
    <div>
      <div className={clsx("flex items-center gap-2 mb-3", `text-${color}`)}>
        {icon}
        <h4 className="text-sm font-semibold">{title}</h4>
        <span className="ml-auto text-xs text-gray-500">({items.length})</span>
      </div>
      {items.length > 0 ? (
        <div className="space-y-2">
          {items.map(renderItem)}
        </div>
      ) : (
        <p className="text-xs text-gray-500 italic">{emptyText}</p>
      )}
    </div>
  );
}

function OrderBlockItem({ block, currentPrice }: { block: OrderBlock; currentPrice: number }) {
  const isBullish = block.block_type.includes('Bullish');
  const midPrice = (block.price_high + block.price_low) / 2;
  const distance = ((midPrice - currentPrice) / currentPrice * 100).toFixed(2);
  const isAbove = midPrice > currentPrice;

  return (
    <div className={clsx(
      "flex items-center justify-between p-3 rounded-lg border",
      isBullish ? "bg-bullish/5 border-bullish/20" : "bg-bearish/5 border-bearish/20"
    )}>
      <div className="flex items-center gap-3">
        <div className={clsx(
          "w-2 h-8 rounded-full",
          isBullish ? "bg-bullish" : "bg-bearish"
        )} />
        <div>
          <p className="text-sm font-medium text-white">{block.block_type}</p>
          <p className="text-xs text-gray-500">{block.timeframe}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-mono text-sm text-white">
          ${block.price_low.toFixed(2)} - ${block.price_high.toFixed(2)}
        </p>
        <p className={clsx("text-xs font-mono", isAbove ? "text-bearish" : "text-bullish")}>
          {isAbove ? '+' : ''}{distance}%
        </p>
      </div>
    </div>
  );
}

function FVGItem({ gap, currentPrice }: { gap: FairValueGap; currentPrice: number }) {
  const isBullish = gap.gap_type.includes('Bullish');
  const midPrice = (gap.high + gap.low) / 2;
  const distance = ((midPrice - currentPrice) / currentPrice * 100).toFixed(2);

  return (
    <div className={clsx(
      "flex items-center justify-between p-3 rounded-lg border",
      isBullish ? "bg-bullish/5 border-bullish/20" : "bg-bearish/5 border-bearish/20"
    )}>
      <div className="flex items-center gap-3">
        <div className={clsx(
          "w-8 h-4 rounded flex items-center justify-center text-[10px] font-bold",
          isBullish ? "bg-bullish/20 text-bullish" : "bg-bearish/20 text-bearish"
        )}>
          FVG
        </div>
        <div>
          <p className="text-sm font-medium text-white">{gap.gap_type}</p>
          <p className="text-xs text-gray-500">
            {gap.filled ? `${gap.fill_percentage.toFixed(0)}% filled` : 'Unfilled'}
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-mono text-sm text-white">
          ${gap.low.toFixed(2)} - ${gap.high.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500 font-mono">{distance}%</p>
      </div>
    </div>
  );
}

function LiquidityItem({ zone, currentPrice }: { zone: LiquidityZone; currentPrice: number }) {
  const isBuySide = zone.zone_type.includes('Buy');
  const midPrice = (zone.price_start + zone.price_end) / 2;
  const distance = ((midPrice - currentPrice) / currentPrice * 100).toFixed(2);

  return (
    <div className={clsx(
      "flex items-center justify-between p-3 rounded-lg border",
      zone.swept ? "opacity-50" : "",
      "bg-neon-yellow/5 border-neon-yellow/20"
    )}>
      <div className="flex items-center gap-3">
        <Droplets className={clsx(
          "w-4 h-4",
          zone.swept ? "text-gray-500" : "text-neon-yellow"
        )} />
        <div>
          <p className="text-sm font-medium text-white">{zone.zone_type}</p>
          <p className="text-xs text-gray-500">
            {zone.strength} • {zone.swept ? 'Swept' : 'Active'}
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-mono text-sm text-white">
          ${zone.price_start.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500 font-mono">{distance}%</p>
      </div>
    </div>
  );
}

function SDZoneItem({ zone, currentPrice }: { zone: SupplyDemandZone; currentPrice: number }) {
  const isSupply = zone.zone_type === 'Supply';
  const midPrice = (zone.price_high + zone.price_low) / 2;
  const distance = ((midPrice - currentPrice) / currentPrice * 100).toFixed(2);

  return (
    <div className={clsx(
      "flex items-center justify-between p-3 rounded-lg border",
      !zone.fresh && "opacity-50",
      isSupply ? "bg-bearish/5 border-bearish/20" : "bg-bullish/5 border-bullish/20"
    )}>
      <div className="flex items-center gap-3">
        <div className={clsx(
          "px-2 py-1 rounded text-[10px] font-bold",
          isSupply ? "bg-bearish/20 text-bearish" : "bg-bullish/20 text-bullish"
        )}>
          {isSupply ? 'S' : 'D'}
        </div>
        <div>
          <p className="text-sm font-medium text-white">{zone.zone_type} Zone</p>
          <p className="text-xs text-gray-500">
            {zone.strength} • {zone.fresh ? 'Fresh' : 'Tested'}
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-mono text-sm text-white">
          ${zone.price_low.toFixed(2)} - ${zone.price_high.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500 font-mono">{distance}%</p>
      </div>
    </div>
  );
}

