"""
Time-Locked Prediction Cache Service.
Predictions are locked for their timeframe duration and only update when expired.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

# Cache directory
CACHE_DIR = Path(__file__).parent.parent.parent / "prediction_cache"
CACHE_DIR.mkdir(exist_ok=True)


class PredictionCache:
    """
    Manages time-locked predictions.
    - 1H predictions: locked for 1 hour
    - 1D predictions: locked for 1 day
    """
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_file(self, symbol: str, timeframe: str) -> Path:
        """Get cache file path for a symbol and timeframe."""
        safe_symbol = symbol.replace("/", "_").replace(":", "_")
        return self.cache_dir / f"{safe_symbol}_{timeframe}.json"
    
    def _get_lock_duration(self, timeframe: str) -> timedelta:
        """Get how long a prediction should be locked."""
        if timeframe == "1h":
            return timedelta(hours=1)
        elif timeframe == "1d":
            return timedelta(days=1)
        elif timeframe == "1w":
            return timedelta(weeks=1)
        else:
            return timedelta(hours=1)
    
    def get_prediction(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """
        Get cached prediction if still valid (not expired).
        Returns None if no valid prediction exists.
        """
        cache_file = self._get_cache_file(symbol, timeframe)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            # Check if prediction is still valid
            created_at = datetime.fromisoformat(cached['created_at'])
            expires_at = datetime.fromisoformat(cached['expires_at'])
            
            if datetime.now() < expires_at:
                # Still valid - return cached prediction
                cached['prediction']['time_remaining'] = str(expires_at - datetime.now()).split('.')[0]
                cached['prediction']['created_at'] = cached['created_at']
                cached['prediction']['expires_at'] = cached['expires_at']
                cached['prediction']['is_locked'] = True
                return cached['prediction']
            else:
                # Expired - delete and return None
                cache_file.unlink()
                return None
                
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid cache file
            cache_file.unlink()
            return None
    
    def save_prediction(self, symbol: str, timeframe: str, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a new prediction with lock duration.
        Returns the prediction with timing metadata.
        """
        cache_file = self._get_cache_file(symbol, timeframe)
        lock_duration = self._get_lock_duration(timeframe)
        
        now = datetime.now()
        expires_at = now + lock_duration
        
        cached_data = {
            'symbol': symbol,
            'timeframe': timeframe,
            'created_at': now.isoformat(),
            'expires_at': expires_at.isoformat(),
            'prediction': prediction
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cached_data, f, indent=2)
        
        # Add timing info to returned prediction
        prediction['created_at'] = now.isoformat()
        prediction['expires_at'] = expires_at.isoformat()
        prediction['time_remaining'] = str(lock_duration).split('.')[0]
        prediction['is_locked'] = True
        
        return prediction
    
    def clear_cache(self, symbol: Optional[str] = None, timeframe: Optional[str] = None):
        """Clear cache for specific symbol/timeframe or all."""
        if symbol and timeframe:
            cache_file = self._get_cache_file(symbol, timeframe)
            if cache_file.exists():
                cache_file.unlink()
        elif symbol:
            safe_symbol = symbol.replace("/", "_").replace(":", "_")
            for f in self.cache_dir.glob(f"{safe_symbol}_*.json"):
                f.unlink()
        else:
            for f in self.cache_dir.glob("*.json"):
                f.unlink()
    
    def get_all_predictions(self, symbol: str) -> Dict[str, Any]:
        """Get all valid predictions for a symbol."""
        return {
            '1h': self.get_prediction(symbol, '1h'),
            '1d': self.get_prediction(symbol, '1d'),
            '1w': self.get_prediction(symbol, '1w')
        }


# Singleton instance
prediction_cache = PredictionCache()

