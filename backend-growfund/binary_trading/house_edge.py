"""
House Edge Algorithm for Binary Options Trading
Ensures platform profitability through payout reduction and strike price adjustment.
"""
from decimal import Decimal
from .models import HouseEdgeConfig, UserTradingStats


class HouseEdgeCalculator:
    """Calculate and apply house edge to trades."""

    def __init__(self, user, asset, amount):
        self.user = user
        self.asset = asset
        self.amount = Decimal(str(amount))
        self.config = self._get_config()
        self.stats = self._get_user_stats()

    def _get_config(self):
        config = HouseEdgeConfig.objects.filter(is_active=True).first()
        if not config:
            config = HouseEdgeConfig.objects.create(name='Default', is_active=True)
        return config

    def _get_user_stats(self):
        stats, _ = UserTradingStats.objects.get_or_create(user=self.user)
        return stats

    def calculate_payout_reduction(self):
        """
        Calculate total payout reduction based on:
        - User win streak
        - Trade amount size
        - User's cumulative net profit
        Returns: (adjusted_payout, house_edge_percentage)
        """
        base_payout = self.asset.base_payout
        edge = Decimal('0.00')

        # Win streak penalty
        if self.stats.current_win_streak >= 5:
            edge += self.config.win_streak_5_reduction
        elif self.stats.current_win_streak >= 3:
            edge += self.config.win_streak_3_reduction

        # High trade amount penalty
        if self.amount >= self.config.very_high_amount_threshold:
            edge += self.config.very_high_amount_reduction
        elif self.amount >= self.config.high_amount_threshold:
            edge += self.config.high_amount_reduction

        # High cumulative profit penalty
        if self.stats.net_profit >= self.config.high_profit_threshold:
            edge += self.config.high_profit_reduction

        # Cap at 30%
        edge = min(edge, Decimal('30.00'))

        adjusted_payout = base_payout - edge
        return adjusted_payout, edge

    def adjust_strike_price(self, current_price, direction):
        """
        Shift the strike price slightly against the user.
        BUY  → raise strike (user needs price to go higher to win)
        SELL → lower strike (user needs price to go lower to win)
        """
        adjustment = self.config.strike_price_adjustment
        if direction == 'buy':
            return current_price * (Decimal('1') + adjustment)
        else:
            return current_price * (Decimal('1') - adjustment)

    def get_execution_delay_ms(self, edge_percentage):
        """
        Return execution delay in milliseconds (NOT applied here — caller decides).
        Higher house edge → longer delay (price moves further against user).
        """
        edge_factor = float(edge_percentage) / 30.0
        delay_range = self.config.max_delay_ms - self.config.min_delay_ms
        return self.config.min_delay_ms + int(delay_range * edge_factor)

    def get_trade_parameters(self, current_price, direction):
        """
        Return all adjusted trade parameters.
        Strike price adjustment is computed here once — do NOT call
        adjust_strike_price again in the caller.
        """
        adjusted_payout, edge = self.calculate_payout_reduction()
        adjusted_strike = self.adjust_strike_price(current_price, direction)
        delay_ms = self.get_execution_delay_ms(edge)

        return {
            'base_payout': self.asset.base_payout,
            'adjusted_payout': adjusted_payout,
            'house_edge': edge,
            'original_price': current_price,
            'adjusted_strike_price': adjusted_strike,
            'execution_delay_ms': delay_ms,
            'user_win_streak': self.stats.current_win_streak,
            'user_total_profit': self.stats.net_profit,
        }
