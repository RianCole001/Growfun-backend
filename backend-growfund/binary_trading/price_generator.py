"""
Synthetic Price Generator Engine
Generates realistic, continuous price streams using stochastic time-series modeling.

Model: P(t+1) = P(t) + drift + noise + momentum

Features:
- Regime switching (trending up/down, sideways)
- Volatility scaling (calm vs spike periods)
- Momentum persistence (short-term trends)
- Realistic candle structure (OHLC consistency)
- House edge integration (micro drift bias)
"""
import random
import math
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
import numpy as np


class MarketRegime:
    """Market behavior regimes"""
    TRENDING_UP = 'trending_up'
    TRENDING_DOWN = 'trending_down'
    SIDEWAYS = 'sideways'
    VOLATILE = 'volatile'


class PriceGenerator:
    """
    Stochastic price generator for binary trading.
    Produces realistic price movements that resemble forex/crypto markets.
    """
    
    def __init__(self, symbol, base_price, volatility=0.0050):
        """
        Initialize price generator.
        
        Args:
            symbol: Asset symbol (e.g., 'EURUSD', 'BTC')
            base_price: Starting price
            volatility: Base volatility (default 0.5% = 0.0050)
        """
        self.symbol = symbol
        self.current_price = Decimal(str(base_price))
        self.base_volatility = Decimal(str(volatility))
        
        # State variables
        self.momentum = Decimal('0')
        self.regime = MarketRegime.SIDEWAYS
        self.regime_duration = 0
        self.regime_counter = 0
        self.volatility_multiplier = Decimal('1.0')
        
        # Drift bias (for house edge)
        self.drift_bias = Decimal('0')
        
        # Price history for momentum calculation
        self.price_history = []
        self.max_history = 20
        
    def set_drift_bias(self, bias):
        """
        Set directional drift bias (used for house edge control).
        Positive = upward bias, Negative = downward bias
        Range: -0.0005 to +0.0005 (0.05%)
        """
        self.drift_bias = Decimal(str(bias))
    
    def _switch_regime(self):
        """Randomly switch market regime"""
        regimes = [
            MarketRegime.TRENDING_UP,
            MarketRegime.TRENDING_DOWN,
            MarketRegime.SIDEWAYS,
            MarketRegime.VOLATILE
        ]
        
        # Weighted probabilities (sideways most common)
        weights = [0.25, 0.25, 0.40, 0.10]
        self.regime = random.choices(regimes, weights=weights)[0]
        
        # Set regime duration (30-120 ticks)
        self.regime_duration = random.randint(30, 120)
        self.regime_counter = 0
        
        # Adjust volatility based on regime
        if self.regime == MarketRegime.VOLATILE:
            self.volatility_multiplier = Decimal('2.5')
        elif self.regime == MarketRegime.SIDEWAYS:
            self.volatility_multiplier = Decimal('0.5')
        else:
            self.volatility_multiplier = Decimal('1.0')
    
    def _calculate_drift(self):
        """Calculate directional drift component"""
        drift = Decimal('0')
        
        # Regime-based drift
        if self.regime == MarketRegime.TRENDING_UP:
            drift = self.base_volatility * Decimal('0.3')
        elif self.regime == MarketRegime.TRENDING_DOWN:
            drift = self.base_volatility * Decimal('-0.3')
        elif self.regime == MarketRegime.SIDEWAYS:
            drift = Decimal('0')
        else:  # VOLATILE
            drift = Decimal('0')
        
        # Add house edge bias
        drift += self.drift_bias
        
        return drift
    
    def _calculate_noise(self):
        """Calculate random Gaussian noise component"""
        # Box-Muller transform for Gaussian distribution
        u1 = random.random()
        u2 = random.random()
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        
        noise = Decimal(str(z)) * self.base_volatility * self.volatility_multiplier
        return noise
    
    def _calculate_momentum(self):
        """Calculate momentum component (trend persistence)"""
        if len(self.price_history) < 3:
            return Decimal('0')
        
        # Calculate recent price change
        recent_change = self.price_history[-1] - self.price_history[-3]
        
        # Momentum decays over time (0.3 persistence factor)
        momentum_change = recent_change * Decimal('0.3')
        
        # Update momentum with decay
        self.momentum = self.momentum * Decimal('0.7') + momentum_change * Decimal('0.3')
        
        # Cap momentum to prevent runaway trends
        max_momentum = self.base_volatility * Decimal('2.0')
        self.momentum = max(min(self.momentum, max_momentum), -max_momentum)
        
        return self.momentum
    
    def generate_tick(self):
        """
        Generate next price tick.
        
        Returns:
            dict: {
                'symbol': str,
                'price': Decimal,
                'timestamp': datetime,
                'regime': str
            }
        """
        # Check if regime should switch
        self.regime_counter += 1
        if self.regime_counter >= self.regime_duration:
            self._switch_regime()
        
        # Calculate price components
        drift = self._calculate_drift()
        noise = self._calculate_noise()
        momentum = self._calculate_momentum()
        
        # Compute price change
        change = drift + noise + momentum
        
        # Update price
        new_price = self.current_price * (Decimal('1') + change)
        
        # Ensure price doesn't go negative or too extreme
        if new_price <= Decimal('0'):
            new_price = self.current_price * Decimal('0.99')
        
        # Prevent extreme jumps (max 2% per tick)
        max_change = self.current_price * Decimal('0.02')
        price_diff = new_price - self.current_price
        if abs(price_diff) > max_change:
            new_price = self.current_price + (max_change if price_diff > 0 else -max_change)
        
        self.current_price = new_price
        
        # Update price history
        self.price_history.append(self.current_price)
        if len(self.price_history) > self.max_history:
            self.price_history.pop(0)
        
        return {
            'symbol': self.symbol,
            'price': self.current_price,
            'timestamp': timezone.now(),
            'regime': self.regime,
            'change_percent': float(change * Decimal('100'))
        }
    
    def generate_candle(self, duration_seconds=60, ticks_per_candle=60):
        """
        Generate a complete OHLC candle.
        
        Args:
            duration_seconds: Candle duration in seconds
            ticks_per_candle: Number of ticks to generate for the candle
        
        Returns:
            dict: {
                'symbol': str,
                'open': Decimal,
                'high': Decimal,
                'low': Decimal,
                'close': Decimal,
                'timestamp': datetime,
                'volume': int (simulated)
            }
        """
        open_price = self.current_price
        high_price = open_price
        low_price = open_price
        
        # Generate ticks for the candle
        for _ in range(ticks_per_candle):
            tick = self.generate_tick()
            price = tick['price']
            
            high_price = max(high_price, price)
            low_price = min(low_price, price)
        
        close_price = self.current_price
        
        # Simulate volume (higher volatility = higher volume)
        base_volume = 1000
        volatility_factor = float(self.volatility_multiplier)
        volume = int(base_volume * volatility_factor * random.uniform(0.5, 1.5))
        
        return {
            'symbol': self.symbol,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'timestamp': timezone.now(),
            'volume': volume
        }
    
    def adjust_for_trade_imbalance(self, buy_volume, sell_volume):
        """
        Adjust drift bias based on trade volume imbalance.
        If too many users are buying, bias price downward (against them).
        
        Args:
            buy_volume: Total stake on BUY trades
            sell_volume: Total stake on SELL trades
        """
        total_volume = buy_volume + sell_volume
        
        if total_volume == 0:
            self.drift_bias = Decimal('0')
            return
        
        buy_ratio = buy_volume / total_volume
        
        # If buy ratio > 60%, bias downward
        # If buy ratio < 40%, bias upward
        if buy_ratio > Decimal('0.60'):
            # Bias against buyers (downward)
            bias_strength = (buy_ratio - Decimal('0.60')) / Decimal('0.40')
            self.drift_bias = -self.base_volatility * Decimal('0.2') * bias_strength
        elif buy_ratio < Decimal('0.40'):
            # Bias against sellers (upward)
            bias_strength = (Decimal('0.40') - buy_ratio) / Decimal('0.40')
            self.drift_bias = self.base_volatility * Decimal('0.2') * bias_strength
        else:
            # Balanced, no bias
            self.drift_bias = Decimal('0')


class PriceGeneratorManager:
    """
    Manages multiple price generators for different assets.
    Singleton pattern to maintain state across requests.
    """
    _instance = None
    _generators = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_generator(self, symbol, base_price=None, volatility=None):
        """
        Get or create a price generator for an asset.
        
        Args:
            symbol: Asset symbol
            base_price: Initial price (only used if creating new generator)
            volatility: Volatility (only used if creating new generator)
        
        Returns:
            PriceGenerator instance
        """
        if symbol not in self._generators:
            if base_price is None:
                # Get base price from database or use default
                from .models import AssetPrice, TradingAsset
                try:
                    asset = TradingAsset.objects.get(symbol=symbol)
                    latest = AssetPrice.objects.filter(asset=asset).order_by('-timestamp').first()
                    base_price = latest.price if latest else Decimal('100.00')
                    volatility = asset.volatility if volatility is None else volatility
                except:
                    base_price = Decimal('100.00')
                    volatility = Decimal('0.0050')
            
            self._generators[symbol] = PriceGenerator(symbol, base_price, volatility)
        
        return self._generators[symbol]
    
    def update_all_generators(self):
        """
        Generate new ticks for all active generators.
        
        Returns:
            dict: {symbol: tick_data}
        """
        ticks = {}
        for symbol, generator in self._generators.items():
            tick = generator.generate_tick()
            ticks[symbol] = tick
        return ticks
    
    def adjust_generator_for_trades(self, symbol):
        """
        Adjust price generator based on current trade imbalance.
        Called periodically to apply house edge through price bias.
        """
        from .models import BinaryTrade, TradingAsset
        from django.db.models import Sum
        from decimal import Decimal
        
        try:
            asset = TradingAsset.objects.get(symbol=symbol)
            active_trades = BinaryTrade.objects.filter(
                asset=asset,
                status='active',
                is_demo=False
            )
            
            buy_volume = active_trades.filter(direction='buy').aggregate(
                total=Sum('amount'))['total'] or Decimal('0')
            sell_volume = active_trades.filter(direction='sell').aggregate(
                total=Sum('amount'))['total'] or Decimal('0')
            
            generator = self.get_generator(symbol)
            generator.adjust_for_trade_imbalance(buy_volume, sell_volume)
            
        except Exception as e:
            print(f"⚠️ Failed to adjust generator for {symbol}: {e}")
