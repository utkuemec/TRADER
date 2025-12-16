import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, AlertCircle, Zap } from 'lucide-react';
import clsx from 'clsx';

import Layout from './components/Layout';
import SymbolSelector from './components/SymbolSelector';
import PriceCard from './components/PriceCard';
import PriceChart from './components/PriceChart';
import BiasIndicator from './components/BiasIndicator';
import MarketContextCard from './components/MarketContextCard';
import TimeframeBiasGrid from './components/TimeframeBiasGrid';
import KeyLevelsTable from './components/KeyLevelsTable';
import IndicatorPanel from './components/IndicatorPanel';
import SmartMoneyPanel from './components/SmartMoneyPanel';
import AnalysisNarrative from './components/AnalysisNarrative';
import PricePrediction from './components/PricePrediction';

import { marketApi, analysisApi } from './api/client';
import type { FullAnalysis, Ticker, OHLCV } from './types';

export default function App() {
  // State
  const [symbols, setSymbols] = useState<string[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [chartTimeframe, setChartTimeframe] = useState('1h');
  
  const [ticker, setTicker] = useState<Ticker | null>(null);
  const [ohlcv, setOhlcv] = useState<OHLCV[]>([]);
  const [analysis, setAnalysis] = useState<FullAnalysis | null>(null);
  
  const [loading, setLoading] = useState({
    symbols: false,
    ticker: false,
    chart: false,
    analysis: false,
  });
  
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Fetch symbols on mount
  useEffect(() => {
    const fetchSymbols = async () => {
      setLoading(l => ({ ...l, symbols: true }));
      try {
        const data = await marketApi.getSymbols('binance');
        setSymbols(data);
      } catch (err) {
        console.error('Failed to fetch symbols:', err);
      } finally {
        setLoading(l => ({ ...l, symbols: false }));
      }
    };
    fetchSymbols();
  }, []);

  // Fetch data when symbol changes
  const fetchData = useCallback(async () => {
    setError(null);
    
    // Fetch ticker
    setLoading(l => ({ ...l, ticker: true }));
    try {
      const tickerData = await marketApi.getTicker(selectedSymbol);
      setTicker(tickerData);
    } catch (err) {
      console.error('Ticker error:', err);
    } finally {
      setLoading(l => ({ ...l, ticker: false }));
    }

    // Fetch OHLCV
    setLoading(l => ({ ...l, chart: true }));
    try {
      const ohlcvData = await marketApi.getOHLCV(selectedSymbol, chartTimeframe);
      setOhlcv(ohlcvData);
    } catch (err) {
      console.error('OHLCV error:', err);
    } finally {
      setLoading(l => ({ ...l, chart: false }));
    }

    // Fetch full analysis
    setLoading(l => ({ ...l, analysis: true }));
    try {
      const analysisData = await analysisApi.getFullAnalysis(selectedSymbol);
      setAnalysis(analysisData);
      setLastUpdate(new Date());
    } catch (err: any) {
      console.error('Analysis error:', err);
      setError(err.message || 'Failed to fetch analysis');
    } finally {
      setLoading(l => ({ ...l, analysis: false }));
    }
  }, [selectedSymbol, chartTimeframe]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Refresh ticker periodically
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const tickerData = await marketApi.getTicker(selectedSymbol);
        setTicker(tickerData);
      } catch (err) {
        // Silent fail for ticker refresh
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [selectedSymbol]);

  const handleSymbolChange = (symbol: string) => {
    setSelectedSymbol(symbol);
    setAnalysis(null);
    setTicker(null);
  };

  const handleTimeframeChange = (tf: string) => {
    setChartTimeframe(tf);
  };

  const isLoading = loading.analysis || loading.ticker;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Top Bar */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-center md:justify-between gap-4"
        >
          <div className="flex items-center gap-4">
            <SymbolSelector
              symbols={symbols}
              selected={selectedSymbol}
              onSelect={handleSymbolChange}
              loading={loading.symbols}
            />
            
            <button
              onClick={fetchData}
              disabled={isLoading}
              className={clsx(
                "flex items-center gap-2 px-4 py-3 rounded-xl transition-all",
                "glass border border-neon-pink/20 hover:border-neon-pink/40",
                "text-neon-pink hover:bg-neon-pink/10",
                isLoading && "opacity-50 cursor-not-allowed"
              )}
            >
              <RefreshCw className={clsx("w-4 h-4", isLoading && "animate-spin")} />
              <span className="font-medium">Refresh</span>
            </button>
          </div>

          {lastUpdate && (
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <Zap className="w-3 h-3 text-neon-cyan" />
              <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
            </div>
          )}
        </motion.div>

        {/* Error Display */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-bearish/10 border border-bearish/30 rounded-xl p-4 flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-bearish" />
              <div>
                <p className="text-bearish font-medium">Analysis Error</p>
                <p className="text-sm text-gray-400">{error}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Price Prediction - Featured Section */}
        {analysis && (
          <PricePrediction
            prediction1h={analysis.price_prediction_1h}
            prediction1d={analysis.price_prediction_1d}
            prediction1w={analysis.price_prediction_1w}
            loading={loading.analysis}
          />
        )}

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Price & Chart */}
          <div className="lg:col-span-2 space-y-6">
            <PriceCard ticker={ticker} loading={loading.ticker} />
            
            <PriceChart
              data={ohlcv}
              symbol={selectedSymbol}
              timeframe={chartTimeframe}
              loading={loading.chart}
              onTimeframeChange={handleTimeframeChange}
            />

            <TimeframeBiasGrid
              biases={analysis?.timeframe_biases || []}
              loading={loading.analysis}
            />

            <IndicatorPanel
              indicators={analysis?.indicators?.[chartTimeframe] || null}
              timeframe={chartTimeframe}
              loading={loading.analysis}
            />
          </div>

          {/* Right Column - Analysis */}
          <div className="space-y-6">
            {/* 1H Outlook */}
            {analysis && (
              <BiasIndicator
                bias={analysis.next_1h_outlook.bias}
                confidence={analysis.confidence}
                timeframe="Next 1 Hour"
                probability={analysis.next_1h_outlook.probability}
              />
            )}

            {/* 1D Outlook */}
            {analysis && (
              <BiasIndicator
                bias={analysis.next_1d_outlook.bias}
                confidence={analysis.confidence}
                timeframe="Next 1 Day"
                probability={analysis.next_1d_outlook.probability}
              />
            )}

            {analysis && (
              <MarketContextCard
                context={analysis.market_context}
                mtfSummary={analysis.mtf_summary}
                loading={loading.analysis}
              />
            )}

            {analysis && (
              <KeyLevelsTable
                levels={analysis.key_levels}
                currentPrice={analysis.current_price}
                loading={loading.analysis}
              />
            )}
          </div>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {analysis && (
            <SmartMoneyPanel
              orderBlocks={analysis.order_blocks}
              fairValueGaps={analysis.fair_value_gaps}
              liquidityZones={analysis.liquidity_zones}
              supplyDemandZones={analysis.supply_demand_zones}
              currentPrice={analysis.current_price}
              loading={loading.analysis}
            />
          )}

          {analysis && (
            <AnalysisNarrative
              narrative={analysis.analysis_narrative}
              loading={loading.analysis}
            />
          )}
        </div>

        {/* Loading Overlay for initial load */}
        <AnimatePresence>
          {!analysis && loading.analysis && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-dark-950/90 flex items-center justify-center z-50"
            >
              <div className="text-center">
                <div className="relative w-24 h-24 mx-auto mb-6">
                  <div className="absolute inset-0 border-4 border-neon-cyan/20 rounded-full" />
                  <div className="absolute inset-0 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin" />
                  <div className="absolute inset-4 border-4 border-neon-pink/20 rounded-full" />
                  <div className="absolute inset-4 border-4 border-neon-pink border-b-transparent rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }} />
                </div>
                <h2 className="font-display text-xl font-bold text-white mb-2">
                  Analyzing {selectedSymbol.replace('/USDT', '')}
                </h2>
                <p className="text-gray-400 text-sm">
                  Running multi-timeframe analysis...
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </Layout>
  );
}

