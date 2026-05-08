"""
Synthetic Price Engine - Regime-Based Stochastic Model
Generates realistic price movements with trend, noise, and volatility regimes
"""
import random
import time
import math
from collections import deque
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candle:
    """OHLC Candle data structure"""
    time: int  # Unix timestamp
    open: float
    high: float
    low: float
    close: float
    
    def to_dict(self):
        return {
            'time': self.time,
            'open': round(self.open, 5),
            'high': round(self.high, 5),
            'low': round(self.low, 5),
            'close': round(self.close, 5),
        }


class CandleBuilder:
    """Builds OHLC candles from tick data"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.open = None
        self.high = float('-inf')
        self.low = float('inf')
        self.close = None
        self.tick_count = 0
    
    def update(self, price: float):
        """Update candle with new tick price"""
        if self.open is None:
            self.open = price
        
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price
        self.tick_count += 1
    
    def get_candle(self, timestamp: int) -> Candle:
        """Get completed candle and reset"""
        if self.open is None:
            return None
        
        candle = Candle(
            time=timestamp,
            open=self.open,
            high=self.high,
            low=self.low,
            close=self.close
        )
        self.reset()
        return candle
    
    def has_data(self) -> bool:
        return self.open is not None


class SyntheticPriceEngine:
    """
    Stochastic price engine with regime switching
    Generates realistic price movements that feel organic
    """
    
    def __init__(self, asset_symbol: str, start_price: float = None):
        self.asset_symbol = asset_symbol
        
        # Set default prices based on asset
        default_prices = {
            'GOLD': 1850.50,
            'BTC': 45000.00,
            'ETH': 2500.00,
            'USDT': 1.00,
            'EUR/USD': 1.0850,
            'GBP/USD': 1.2650,
        }
        
        self.price = start_price or default_prices.get(asset_symbol, 100.00)
        self.history = deque(maxlen=1000)
        
        # Regime states
        self.trend = 0  # -1 down, 0 neutral, 1 up
        self.volatility = 0.0003  # Base volatility
        self.drift = 0.0  # Directional bias
        
        # Regime switching parameters
        self.regime_duration = 0
        self.regime_max_duration = random.randint(20, 60)
        
        # House edge parameters
        self.user_bias = 0  # Bias based on user positions
        
        # Price bounds (prevent unrealistic movements)
        self.min_price = self.price * 0.5
        self.max_price = self.price * 2.0
        
        # Momentum tracking
        self.momentum = 0.0
        self.momentum_decay = 0.95
        
        # Initialize history
        self.history.append(self.price)
    
    def switch_regime(self):
        """Randomly change market regime"""
        self.regime_duration += 1
        
        # Force regime switch after max duration
        if self.regime_duration >= self.regime_max_duration or random.random() < 0.02:
            # Choose new trend
            self.trend = random.choice([-1, 0, 0, 1])  # Bias towards neutral
            
            # Choose new volatility
            self.volatility = random.uniform(0.0001, 0.0006)
            
            # Reset regime duration
            self.regime_duration = 0
            self.regime_max_duration = random.randint(20, 60)
            
            # Reset momentum on regime change
            self.momentum *= 0.5
    
    def calculate_user_bias(self, active_trades: List[Dict]) -> float:
        """
        Calculate bias based on active user positions
        Returns: -1 to 1 (negative = pressure down, positive = pressure up)
        """
        if not active_trades:
            return 0
        
        buy_count = sum(1 for t in active_trades if t.get('direction') == 'buy')
        sell_count = sum(1 for t in active_trades if t.get('direction') == 'sell')
        
        total = buy_count + sell_count
        if total == 0:
            return 0
        
        # If more buys, slight downward pressure (house edge)
        # If more sells, slight upward pressure
        imbalance = (buy_count - sell_count) / total
        
        return -imbalance * 0.3  # Scale down the bias
    
    def generate_tick(self, active_trades: Optional[List[Dict]] = None) -> float:
        """
        Generate next price tick
        
        Args:
            active_trades: List of active trades for house edge calculation
        
        Returns:
            New price value
        """
        # Check for regime switch
        self.switch_regime()
        
        # Calculate user bias (house edge)
        if active_trades:
            self.user_bias = self.calculate_user_bias(active_trades)
        
        # Momentum effect (trend persistence)
        momentum_effect = self.trend * random.uniform(0.00005, 0.0002)
        self.momentum = self.momentum * self.momentum_decay + momentum_effect
        
        # Random noise (Gaussian distribution)
        noise = random.gauss(0, self.volatility)
        
        # House edge bias (very subtle)
        bias = self.user_bias * 0.00005
        
        # Mean reversion (prevent price from drifting too far)
        mean_price = sum(list(self.history)[-20:]) / min(20, len(self.history))
        mean_reversion = (mean_price - self.price) * 0.001
        
        # Combine all effects
        delta = self.momentum + noise + bias + mean_reversion
        
        # Apply price change
        new_price = self.price + (self.price * delta)
        
        # Enforce price bounds
        new_price = max(self.min_price, min(self.max_price, new_price))
        
        # Update state
        self.price = new_price
        self.history.append(new_price)
        
        return round(new_price, 5)
    
    def get_current_price(self) -> float:
        """Get current price"""
        return round(self.price, 5)
    
    def get_price_history(self, count: int = 100) -> List[float]:
        """Get recent price history"""
        history_list = list(self.history)
        return history_list[-count:] if len(history_list) > count else history_list
    
    def generate_historical_candles(self, count: int = 100, interval_seconds: int = 60) -> List[Candle]:
        """
        Generate historical candles for chart initialization
        
        Args:
            count: Number of candles to generate
            interval_seconds: Candle interval in seconds
        
        Returns:
            List of Candle objects
        """
        candles = []
        current_time = int(time.time())
        temp_price = self.price
        
        for i in range(count, 0, -1):
            candle_time = current_time - (i * interval_seconds)
            
            # Generate ticks for this candle
            candle_builder = CandleBuilder()
            ticks_per_candle = max(10, interval_seconds // 5)
            
            for _ in range(ticks_per_candle):
                # Simulate price movement
                change = random.gauss(0, self.volatility) * temp_price
                temp_price = max(self.min_price, min(self.max_price, temp_price + change))
                candle_builder.update(temp_price)
            
            candle = candle_builder.get_candle(candle_time)
            if candle:
                candles.append(candle)
        
        return candles


class PriceEngineManager:
    """Manages multiple price engines for different assets"""
    
    _instance = None
    _engines: Dict[str, SyntheticPriceEngine] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_engine(self, asset_symbol: str, start_price: float = None) -> SyntheticPriceEngine:
        """Get or create price engine for asset"""
        if asset_symbol not in self._engines:
            self._engines[asset_symbol] = SyntheticPriceEngine(asset_symbol, start_price)
        return self._engines[asset_symbol]
    
    def get_price(self, asset_symbol: str) -> float:
        """Get current price for asset"""
        engine = self.get_engine(asset_symbol)
        return engine.get_current_price()
    
    def generate_tick(self, asset_symbol: str, active_trades: Optional[List[Dict]] = None) -> float:
        """Generate new tick for asset"""
        engine = self.get_engine(asset_symbol)
        return engine.generate_tick(active_trades)
    
    def get_historical_candles(self, asset_symbol: str, count: int = 100) -> List[Dict]:
        """Get historical candles for asset"""
        engine = self.get_engine(asset_symbol)
        candles = engine.generate_historical_candles(count)
        return [c.to_dict() for c in candles]


# Global instance
price_engine_manager = PriceEngineManager()
