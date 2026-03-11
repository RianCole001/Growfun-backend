"""
Trade Execution Service
Handles opening and closing of binary trades
"""
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import BinaryTrade, TradingAsset, UserTradingStats
from .house_edge import HouseEdgeCalculator
from .price_feed import PriceFeedService


class TradeExecutionService:
    """Service for executing binary trades"""
    
    @staticmethod
    def validate_trade_limits(user, asset, amount):
        """Validate trade against risk limits"""
        from .models import HouseEdgeConfig
        
        config = HouseEdgeConfig.objects.filter(is_active=True).first()
        if not config:
            return True, None
        
        # Check open trades limit
        open_trades = BinaryTrade.objects.filter(
            user=user,
            status='active'
        ).count()
        
        if open_trades >= config.max_open_trades_per_user:
            return False, f"Maximum {config.max_open_trades_per_user} open trades allowed"
        
        # Check exposure per asset
        asset_exposure = BinaryTrade.objects.filter(
            user=user,
            asset=asset,
            status='active'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        if asset_exposure + amount > config.max_exposure_per_asset:
            return False, f"Maximum ${config.max_exposure_per_asset} exposure per asset"
        
        # Check total exposure
        total_exposure = BinaryTrade.objects.filter(
            user=user,
            status='active'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        if total_exposure + amount > config.max_total_exposure:
            return False, f"Maximum ${config.max_total_exposure} total exposure"
        
        return True, None
    
    @staticmethod
    @transaction.atomic
    def open_trade(user, asset_symbol, direction, amount, expiry_seconds):
        """
        Open a new binary trade with house edge applied
        Returns: (trade_object, error_message)
        """
        from django.db import models
        
        # Get asset
        try:
            asset = TradingAsset.objects.get(symbol=asset_symbol, is_active=True)
        except TradingAsset.DoesNotExist:
            return None, "Asset not found or inactive"
        
        # Validate amount
        if amount < asset.min_trade_amount:
            return None, f"Minimum trade amount is ${asset.min_trade_amount}"
        if amount > asset.max_trade_amount:
            return None, f"Maximum trade amount is ${asset.max_trade_amount}"
        
        # Check user balance
        if user.balance < amount:
            return None, "Insufficient balance"
        
        # Validate trade limits
        valid, error = TradeExecutionService.validate_trade_limits(user, asset, amount)
        if not valid:
            return None, error
        
        # Get current price
        current_price = PriceFeedService.get_current_price(asset_symbol)
        if not current_price:
            return None, "Unable to get current price"
        
        # Calculate house edge
        calculator = HouseEdgeCalculator(user, asset, amount)
        params = calculator.get_trade_parameters(current_price, direction)
        
        # Apply execution delay
        calculator.apply_execution_delay(params['execution_delay_ms'])
        
        # Get price after delay (price may have moved)
        delayed_price = PriceFeedService.get_current_price(asset_symbol)
        adjusted_strike = calculator.adjust_strike_price(delayed_price, direction)
        
        # Calculate expiry time
        expires_at = timezone.now() + timedelta(seconds=expiry_seconds)
        
        # Deduct amount from user balance
        user.balance -= amount
        user.save(update_fields=['balance'])
        
        # Create trade
        trade = BinaryTrade.objects.create(
            user=user,
            asset=asset,
            direction=direction,
            amount=amount,
            strike_price=adjusted_strike,
            base_payout_percentage=params['base_payout'],
            adjusted_payout_percentage=params['adjusted_payout'],
            house_edge_applied=params['house_edge'],
            expiry_seconds=expiry_seconds,
            expires_at=expires_at,
            status='active',
            execution_delay_ms=params['execution_delay_ms'],
            user_win_streak=params['user_win_streak'],
            user_total_profit=params['user_total_profit']
        )
        
        return trade, None
    
    @staticmethod
    @transaction.atomic
    def close_trade(trade_id):
        """
        Close a trade and calculate profit/loss
        Returns: (trade_object, error_message)
        """
        try:
            trade = BinaryTrade.objects.select_for_update().get(id=trade_id)
        except BinaryTrade.DoesNotExist:
            return None, "Trade not found"
        
        if trade.status != 'active':
            return None, "Trade is not active"
        
        # Get final price
        final_price = PriceFeedService.get_current_price(trade.asset.symbol)
        if not final_price:
            return None, "Unable to get final price"
        
        # Determine winner
        if trade.direction == 'buy':
            won = final_price > trade.strike_price
        else:  # sell
            won = final_price < trade.strike_price
        
        # Calculate profit/loss
        if won:
            profit = trade.amount * (trade.adjusted_payout_percentage / Decimal('100'))
            trade.status = 'won'
            trade.profit_loss = profit
            
            # Return stake + profit to user
            trade.user.balance += (trade.amount + profit)
        else:
            trade.status = 'lost'
            trade.profit_loss = -trade.amount
            # User already lost the stake (deducted on open)
        
        trade.final_price = final_price
        trade.closed_at = timezone.now()
        trade.user.save(update_fields=['balance'])
        trade.save()
        
        # Update user stats
        TradeExecutionService.update_user_stats(trade)
        
        return trade, None
    
    @staticmethod
    def update_user_stats(trade):
        """Update user trading statistics after trade closes"""
        stats, created = UserTradingStats.objects.get_or_create(user=trade.user)
        
        stats.total_trades += 1
        stats.total_volume += trade.amount
        
        if trade.status == 'won':
            stats.total_wins += 1
            stats.current_win_streak += 1
            stats.current_loss_streak = 0
            stats.max_win_streak = max(stats.max_win_streak, stats.current_win_streak)
            stats.total_profit += trade.profit_loss
        elif trade.status == 'lost':
            stats.total_losses += 1
            stats.current_loss_streak += 1
            stats.current_win_streak = 0
            stats.total_loss += abs(trade.profit_loss)
        
        stats.net_profit = stats.total_profit - stats.total_loss
        
        # Flag users with suspicious win rates
        if stats.total_trades >= 50:
            win_rate = (stats.total_wins / stats.total_trades) * 100
            if win_rate > 75 and not stats.is_flagged:
                stats.is_flagged = True
                stats.flag_reason = f"High win rate: {win_rate:.2f}% after {stats.total_trades} trades"
                stats.flagged_at = timezone.now()
        
        stats.save()
    
    @staticmethod
    def close_expired_trades():
        """Close all expired trades (called by scheduler)"""
        from django.db.models import Q
        
        expired_trades = BinaryTrade.objects.filter(
            status='active',
            expires_at__lte=timezone.now()
        )
        
        results = {'closed': 0, 'errors': 0}
        
        for trade in expired_trades:
            _, error = TradeExecutionService.close_trade(trade.id)
            if error:
                results['errors'] += 1
            else:
                results['closed'] += 1
        
        return results
