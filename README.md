# TRADER — Multi-Timeframe Crypto Market Analysis

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)

**Async FastAPI service + React dashboard that pulls live OHLCV data from five exchanges, computes technical and market-structure features across 10 timeframes, and combines a set of statistical estimators into 1h / 1d / 1w price-target ranges with confidence scores.**

</div>

---

## ✨ Features

### 📊 Multi-Timeframe Analysis
- Analysis across **1m, 5m, 15m, 30m, 1h, 2h, 4h, 8h, 1d, 1w** timeframes
- Automatic timeframe bias detection
- MTF alignment scoring

### 📈 Technical Indicators
- **Momentum**: RSI, MACD, Stochastic, CCI
- **Trend**: EMA (9, 21, 50, 100, 200), SMA, VWAP
- **Volatility**: ATR, Bollinger Bands

### 🔍 Market Structure Analysis
- Higher Highs / Higher Lows detection
- Lower Highs / Lower Lows identification
- Break of Structure (BOS) alerts
- Change of Character (CHoCH) detection

### 💎 Smart Money Concepts
- **Order Blocks**: Bullish & Bearish OB identification
- **Fair Value Gaps**: Imbalance detection with fill tracking
- **Liquidity Zones**: Buy-side & Sell-side liquidity mapping
- **Supply & Demand Zones**: Fresh zone identification

### 🎯 Price-Target Estimation (signal ensemble)
- ~15 independent estimators: weighted momentum, linear-regression projection, mean reversion, ATR / volatility projection, swing projection, Fibonacci, VWAP, volume profile, divergence, order-block, liquidity and FVG targets
- Estimates are weighted by agreement (confluence) into **1h / 1d / 1w** target ranges with Low / Medium / High confidence
- Key levels with invalidation points
- Prediction cache to avoid recomputation on hot symbols

### 🖥️ Modern Dashboard
- Real-time price updates
- TradingView-style candlestick charts
- Cyberpunk-inspired dark theme
- Responsive design

---

## 🏗️ Architecture

```
TRADER/
├── backend/                 # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── config.py       # Configuration
│   │   ├── models.py       # Pydantic models
│   │   ├── routes/         # API endpoints
│   │   │   ├── market.py   # Market data routes
│   │   │   └── analysis.py # Analysis routes
│   │   └── services/       # Business logic
│   │       ├── exchange.py # CCXT exchange service
│   │       ├── indicators.py # Technical indicators
│   │       ├── structure.py  # Market structure
│   │       └── analyzer.py   # Main analysis engine
│   ├── requirements.txt
│   └── run.py
│
└── frontend/               # React TypeScript Frontend
    ├── src/
    │   ├── components/    # React components
    │   ├── api/           # API client
    │   ├── types/         # TypeScript types
    │   └── App.tsx        # Main application
    ├── package.json
    └── vite.config.ts
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`

---

## 📡 API Endpoints

### Market Data
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/market/symbols/{exchange}` | Get available trading pairs |
| `GET /api/v1/market/ticker/{symbol}` | Get current price |
| `GET /api/v1/market/ohlcv/{symbol}` | Get candlestick data |
| `GET /api/v1/market/orderbook/{symbol}` | Get order book |

### Analysis
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/analysis/full/{symbol}` | **Full multi-timeframe analysis** |
| `GET /api/v1/analysis/indicators/{symbol}` | Technical indicators only |
| `GET /api/v1/analysis/structure/{symbol}` | Market structure only |
| `GET /api/v1/analysis/fibonacci/{symbol}` | Fibonacci levels |

### Example Request

```bash
curl http://localhost:8000/api/v1/analysis/full/BTC-USDT
```

---

## 🎨 Dashboard Preview

The dashboard features:
- **Cyberpunk neon aesthetic** with cyan and pink accents
- **Real-time price updates** with flash animations
- **Interactive candlestick charts** powered by Lightweight Charts
- **Multi-timeframe bias grid** showing all TF biases at a glance
- **Smart Money Concepts panel** with OBs, FVGs, and liquidity zones
- **Professional analysis narrative** in markdown format

---

## ⚙️ Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
# API Settings
DEBUG=true
DEFAULT_EXCHANGE=binance

# Cache TTL (seconds)
CACHE_TTL_TICKER=5
CACHE_TTL_OHLCV=30
CACHE_TTL_ANALYSIS=60
```

### Supported Exchanges

- ✅ Binance
- ✅ Bybit
- ✅ Coinbase
- ✅ Kraken
- ✅ OKX

---

## 📊 Analysis Response Structure

```json
{
  "symbol": "BTC/USDT",
  "current_price": 97500.00,
  "market_context": {
    "short_tf_trend": "Uptrend",
    "mid_tf_trend": "Uptrend",
    "high_tf_trend": "Uptrend",
    "volatility": "Normal",
    "market_phase": "Markup"
  },
  "mtf_summary": {
    "alignment": "Fully Aligned Bullish"
  },
  "next_1h_outlook": {
    "bias": "Bullish",
    "probability": "High"
  },
  "next_1d_outlook": {
    "bias": "Bullish",
    "probability": "Medium"
  },
  "confidence": "High"
}
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance async web framework
- **CCXT** - Cryptocurrency exchange library
- **ta** - Technical analysis indicators
- **NumPy & SciPy** - Scientific computing

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Framer Motion** - Animations
- **Lightweight Charts** - TradingView-style charts
- **Lucide Icons** - Icon library


## 🧪 Evaluation & Roadmap

The estimators are rule-based and statistical (no trained model yet). Next steps to make the predictions measurable:

- [ ] Walk-forward backtest on historical OHLCV: directional accuracy and MAE of 1h / 1d targets vs. naive baselines (last close, drift)
- [ ] Calibration check: do "High confidence" calls actually hit more often than "Low"?
- [ ] Learn the ensemble weights (e.g. gradient boosting on estimator outputs) instead of fixed heuristics
- [ ] Unit tests for indicator and market-structure functions

## ⚠️ Disclaimer

This platform is for **educational and research purposes only**. Cryptocurrency trading involves substantial risk. Past performance does not guarantee future results. Always do your own research and never invest more than you can afford to lose.

