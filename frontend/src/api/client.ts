import axios from 'axios';
import type { FullAnalysis, Ticker, OHLCV } from '../types';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// Symbol formatting helpers
const formatSymbol = (symbol: string) => symbol.replace('/', '-');

export const marketApi = {
  async getSymbols(exchange: string = 'binance'): Promise<string[]> {
    const response = await api.get(`/market/symbols/${exchange}`);
    return response.data.symbols;
  },

  async getTicker(symbol: string, exchange: string = 'binance'): Promise<Ticker> {
    const response = await api.get(`/market/ticker/${formatSymbol(symbol)}`, {
      params: { exchange }
    });
    return response.data;
  },

  async getOHLCV(
    symbol: string,
    timeframe: string = '1h',
    exchange: string = 'binance',
    limit: number = 500
  ): Promise<OHLCV[]> {
    const response = await api.get(`/market/ohlcv/${formatSymbol(symbol)}`, {
      params: { timeframe, exchange, limit }
    });
    return response.data.data;
  },

  async getOrderBook(symbol: string, exchange: string = 'binance', limit: number = 50) {
    const response = await api.get(`/market/orderbook/${formatSymbol(symbol)}`, {
      params: { exchange, limit }
    });
    return response.data;
  }
};

export const analysisApi = {
  async getFullAnalysis(symbol: string, exchange: string = 'binance'): Promise<FullAnalysis> {
    const response = await api.get(`/analysis/full/${formatSymbol(symbol)}`, {
      params: { exchange }
    });
    return response.data;
  },

  async getIndicators(symbol: string, timeframe: string = '1h', exchange: string = 'binance') {
    const response = await api.get(`/analysis/indicators/${formatSymbol(symbol)}`, {
      params: { timeframe, exchange }
    });
    return response.data;
  },

  async getStructure(symbol: string, timeframe: string = '1h', exchange: string = 'binance') {
    const response = await api.get(`/analysis/structure/${formatSymbol(symbol)}`, {
      params: { timeframe, exchange }
    });
    return response.data;
  },

  async getFibonacci(symbol: string, timeframe: string = '4h', exchange: string = 'binance') {
    const response = await api.get(`/analysis/fibonacci/${formatSymbol(symbol)}`, {
      params: { timeframe, exchange }
    });
    return response.data;
  }
};

// WebSocket connection for real-time ticker
export class TickerWebSocket {
  private ws: WebSocket | null = null;
  private symbol: string;
  private onMessage: (data: Ticker) => void;
  private onError: (error: Event) => void;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor(
    symbol: string,
    onMessage: (data: Ticker) => void,
    onError: (error: Event) => void = () => {}
  ) {
    this.symbol = symbol;
    this.onMessage = onMessage;
    this.onError = onError;
  }

  connect() {
    const wsUrl = `ws://${window.location.host}/ws/ticker/${this.symbol.replace('/', '-')}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'ticker') {
        this.onMessage(data.data);
      }
    };

    this.ws.onerror = (error) => {
      this.onError(error);
    };

    this.ws.onclose = () => {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), 3000);
      }
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default api;

