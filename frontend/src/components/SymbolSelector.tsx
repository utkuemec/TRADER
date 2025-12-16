import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ChevronDown, Star, TrendingUp, TrendingDown } from 'lucide-react';
import clsx from 'clsx';

interface SymbolSelectorProps {
  symbols: string[];
  selected: string;
  onSelect: (symbol: string) => void;
  loading?: boolean;
}

const POPULAR_SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'ADA/USDT'];

export default function SymbolSelector({ symbols, selected, onSelect, loading }: SymbolSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [favorites, setFavorites] = useState<string[]>(() => {
    const saved = localStorage.getItem('trader_favorites');
    return saved ? JSON.parse(saved) : POPULAR_SYMBOLS;
  });

  useEffect(() => {
    localStorage.setItem('trader_favorites', JSON.stringify(favorites));
  }, [favorites]);

  const filteredSymbols = symbols.filter(s => 
    s.toLowerCase().includes(search.toLowerCase())
  );

  const toggleFavorite = (symbol: string) => {
    setFavorites(prev => 
      prev.includes(symbol) 
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    );
  };

  const displaySymbol = selected.replace('/USDT', '');

  return (
    <div className="relative">
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          "flex items-center gap-3 px-4 py-3 rounded-xl transition-all",
          "glass border border-neon-cyan/20 hover:border-neon-cyan/40",
          isOpen && "border-neon-cyan/50"
        )}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-neon-cyan/20 to-neon-pink/20 flex items-center justify-center">
          <span className="font-display font-bold text-neon-cyan">
            {displaySymbol.charAt(0)}
          </span>
        </div>
        <div className="text-left">
          <h3 className="font-display font-bold text-lg text-white">{displaySymbol}</h3>
          <p className="text-xs text-gray-500">{selected}</p>
        </div>
        <ChevronDown className={clsx(
          "w-5 h-5 text-gray-400 transition-transform ml-auto",
          isOpen && "rotate-180"
        )} />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 right-0 mt-2 z-50"
          >
            <div className="glass rounded-xl border border-neon-cyan/20 overflow-hidden shadow-2xl shadow-black/50">
              {/* Search */}
              <div className="p-3 border-b border-dark-600">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Search symbols..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full bg-dark-800 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:ring-1 focus:ring-neon-cyan/50"
                  />
                </div>
              </div>

              {/* Favorites */}
              {!search && favorites.length > 0 && (
                <div className="p-3 border-b border-dark-600">
                  <p className="text-xs text-gray-500 mb-2 font-medium uppercase tracking-wider">Favorites</p>
                  <div className="flex flex-wrap gap-2">
                    {favorites.map(symbol => (
                      <button
                        key={symbol}
                        onClick={() => { onSelect(symbol); setIsOpen(false); }}
                        className={clsx(
                          "px-3 py-1.5 rounded-lg text-sm font-medium transition-all",
                          symbol === selected
                            ? "bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30"
                            : "bg-dark-700 text-gray-300 hover:bg-dark-600"
                        )}
                      >
                        {symbol.replace('/USDT', '')}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Symbol List */}
              <div className="max-h-64 overflow-y-auto">
                {loading ? (
                  <div className="p-8 text-center">
                    <div className="w-6 h-6 border-2 border-neon-cyan border-t-transparent rounded-full animate-spin mx-auto" />
                  </div>
                ) : filteredSymbols.length === 0 ? (
                  <div className="p-8 text-center text-gray-500 text-sm">
                    No symbols found
                  </div>
                ) : (
                  <div className="p-2">
                    {filteredSymbols.slice(0, 50).map(symbol => (
                      <button
                        key={symbol}
                        onClick={() => { onSelect(symbol); setIsOpen(false); }}
                        className={clsx(
                          "w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all",
                          symbol === selected
                            ? "bg-neon-cyan/10 text-neon-cyan"
                            : "text-gray-300 hover:bg-dark-700"
                        )}
                      >
                        <button
                          onClick={(e) => { e.stopPropagation(); toggleFavorite(symbol); }}
                          className="p-1"
                        >
                          <Star 
                            className={clsx(
                              "w-4 h-4 transition-colors",
                              favorites.includes(symbol) 
                                ? "text-neon-yellow fill-neon-yellow" 
                                : "text-gray-600"
                            )} 
                          />
                        </button>
                        <span className="font-mono text-sm">{symbol}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)} 
        />
      )}
    </div>
  );
}

