import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { createChart, ColorType, IChartApi, ISeriesApi, CandlestickData } from 'lightweight-charts';
import { RefreshCw, Maximize2, Settings } from 'lucide-react';
import clsx from 'clsx';
import type { OHLCV } from '../types';

interface PriceChartProps {
  data: OHLCV[];
  symbol: string;
  timeframe: string;
  loading?: boolean;
  onTimeframeChange?: (tf: string) => void;
}

const TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'];

export default function PriceChart({ 
  data, 
  symbol, 
  timeframe, 
  loading,
  onTimeframeChange 
}: PriceChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#9ca3af',
        fontFamily: 'JetBrains Mono, monospace',
      },
      grid: {
        vertLines: { color: 'rgba(0, 245, 255, 0.05)' },
        horzLines: { color: 'rgba(0, 245, 255, 0.05)' },
      },
      crosshair: {
        mode: 1,
        vertLine: {
          width: 1,
          color: 'rgba(0, 245, 255, 0.3)',
          style: 2,
        },
        horzLine: {
          width: 1,
          color: 'rgba(0, 245, 255, 0.3)',
          style: 2,
        },
      },
      rightPriceScale: {
        borderColor: 'rgba(0, 245, 255, 0.1)',
        scaleMargins: {
          top: 0.1,
          bottom: 0.2,
        },
      },
      timeScale: {
        borderColor: 'rgba(0, 245, 255, 0.1)',
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    });

    // Candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#00ff9d',
      downColor: '#ff0055',
      borderUpColor: '#00ff9d',
      borderDownColor: '#ff0055',
      wickUpColor: '#00ff9d',
      wickDownColor: '#ff0055',
    });

    // Volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#00f5ff',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.85,
        bottom: 0,
      },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // Update data
  useEffect(() => {
    if (!candleSeriesRef.current || !volumeSeriesRef.current || !data.length) return;

    const candleData: CandlestickData[] = data.map(d => ({
      time: (d.timestamp / 1000) as any,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    const volumeData = data.map(d => ({
      time: (d.timestamp / 1000) as any,
      value: d.volume,
      color: d.close >= d.open ? 'rgba(0, 255, 157, 0.3)' : 'rgba(255, 0, 85, 0.3)',
    }));

    candleSeriesRef.current.setData(candleData);
    volumeSeriesRef.current.setData(volumeData);

    // Fit content
    chartRef.current?.timeScale().fitContent();
  }, [data]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl border border-neon-cyan/20 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-dark-600">
        <div className="flex items-center gap-4">
          <h3 className="font-display font-bold text-white">{symbol}</h3>
          
          {/* Timeframe selector */}
          <div className="flex items-center gap-1 bg-dark-700 rounded-lg p-1">
            {TIMEFRAMES.map(tf => (
              <button
                key={tf}
                onClick={() => onTimeframeChange?.(tf)}
                className={clsx(
                  "px-3 py-1 rounded-md text-xs font-mono transition-all",
                  timeframe === tf
                    ? "bg-neon-cyan/20 text-neon-cyan"
                    : "text-gray-400 hover:text-white hover:bg-dark-600"
                )}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-600 transition-all">
            <RefreshCw className={clsx("w-4 h-4", loading && "animate-spin")} />
          </button>
          <button className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-600 transition-all">
            <Maximize2 className="w-4 h-4" />
          </button>
          <button className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-600 transition-all">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="relative">
        {loading && (
          <div className="absolute inset-0 bg-dark-900/80 flex items-center justify-center z-10">
            <div className="w-8 h-8 border-2 border-neon-cyan border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        <div 
          ref={chartContainerRef} 
          className="w-full h-[400px]"
        />
      </div>

      {/* Footer with price info */}
      {data.length > 0 && (
        <div className="flex items-center justify-between px-4 py-2 border-t border-dark-600 text-xs">
          <div className="flex items-center gap-4">
            <span className="text-gray-500">O: <span className="text-white font-mono">{data[data.length - 1]?.open.toFixed(2)}</span></span>
            <span className="text-gray-500">H: <span className="text-bullish font-mono">{data[data.length - 1]?.high.toFixed(2)}</span></span>
            <span className="text-gray-500">L: <span className="text-bearish font-mono">{data[data.length - 1]?.low.toFixed(2)}</span></span>
            <span className="text-gray-500">C: <span className="text-white font-mono">{data[data.length - 1]?.close.toFixed(2)}</span></span>
          </div>
          <span className="text-gray-500">
            Vol: <span className="text-neon-cyan font-mono">{formatVolume(data[data.length - 1]?.volume || 0)}</span>
          </span>
        </div>
      )}
    </motion.div>
  );
}

function formatVolume(volume: number): string {
  if (volume >= 1e9) return (volume / 1e9).toFixed(2) + 'B';
  if (volume >= 1e6) return (volume / 1e6).toFixed(2) + 'M';
  if (volume >= 1e3) return (volume / 1e3).toFixed(2) + 'K';
  return volume.toFixed(2);
}

