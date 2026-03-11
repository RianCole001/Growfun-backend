"""
House Edge Algorithm for Binary Options Trading
Ensures platform profitability through subtle manipulation
"""
from decimal import Decimal
from .models import HouseEdgeConfig, UserTradingStats
import random
import time


class HouseEdgeCalculator:
    """Calculate and apply house edge to trades"""
    
    def __init__(self, user, asset, amount):
        self.user = user
        self.asset = asset
        self.amount = Decimal(str(amount))
        self.config = self._get_config()
        self.stats = self._get_user_stats()
    
    def _get_config(self):
        """Get active house edge configuration"""
        config = HouseEdgeConfig.objects.filter(is_active=True).first()
        if not config:
            # Create default config if none exists
            config = HouseEdgeConfig.objects.create(
                name='Default',
                is_active=True
            )
        return config
    
    def _get_user_stats(self):
        """Get or create user trading stats"""
        stats, created = UserTradingStats.objects.get_or_create(user=self.user)
        return stats
    
    def calculate_payout_reduction(self):
        """
        Calculate payout reduction based on multiple factors
        Returns: (adjusted_payout, house_edge_percentage)
        """
        base_payout = self.asset.base_payout
        edge = Decimal('0.00')
        
        # Factor 1: Win streak reduction
        if self.stats.current_win_streak >= 5:
            edge += self.config.win_streak_5_reduction
        elif self.stats.current_win_streak >= 3:
            edge += self.config.win_streak_3_reduction
        
        # Factor 2: High amount reduction
        if self.amount >= self.config.very_high_amount_threshold:
            edge += self.config.very_high_amount_reduction
        elif self.amount >= self.config.high_amount_threshold:
            edge += self.config.high_amount_reduction
        
        # Factor 3: High profit user reduction
        if self.stats.net_profit >= self.config.high_profit_threshold:
            edge += self.config.high_profit_reduction
        
        # Cap maximum edge at 30%
        edge = min(edge, Decimal('30.00'))
        
        adjusted_payout = base_payout - edge
        
        return adjusted_payout, edge
    
    def adjust_strike_price(self, current_price, direction):
        """
        Adjust strike price slightly against user's favor
        This is the most subtle and effective manipulation
        """
        adjustment = self.config.strike_price_adjustment
        
        if direction == 'buy':
            # For BUY trades, increase strike price (harder to win)
            adjusted_price = current_price * (Decimal('1') + adjustment)
        else:
            # For SELL trades, decrease strike price (harder to win)
            adjusted_price = current_price * (Decimal('1') - adjustment)
        
        return adjusted_price
    
    def calculate_execution_delay(self, edge_percentage):
        """
        Calculate execution delay based on house edge
        Higher edge = longer delay
        """
        # Scale delay based on edge percentage
        edge_factor = float(edge_percentage) / 30.0  # Normalize to 0-1
        delay_range = self.config.max_delay_ms - self.config.min_delay_ms
        delay = self.config.min_delay_ms + int(delay_range * edge_factor)
        
        return delay
    
    def apply_execution_delay(self, delay_ms):
        """Apply execution delay in milliseconds"""
        time.sleep(delay_ms / 1000.0)
    
    def get_trade_parameters(self, current_price, direction):
        """
        Get all adjusted trade parameters with house edge applied
        Returns: dict with adjusted values
        """
        # Calculate payout reduction
        adjusted_payout, edge = self.calculate_payout_reduction()
        
        # Adjust strike price
        adjusted_strike = self.adjust_strike_price(current_price, direction)
        
        # Calculate execution delay
        delay_ms = self.calculate_execution_delay(edge)
        
        return {
            'base_payout': self.asset.base_payout,
            'adjusted_payout': adjusted_payout,
            'house_edge': edge,
            'original_price': current_price,
            'adjusted_strike_price': adjusted_strike,
            'execution_delay_ms': delay_ms,
            'user_win_streak': self.stats.current_win_streak,
            'user_total_profit': self.stats.net_profit
        }
