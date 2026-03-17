"""
Trade Execution Service
Handles opening and closing of binary trades.
"""
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.db import transaction, models
from .models import BinaryTrade, TradingAsset, UserTradingStats
from .house_edge import HouseEdgeCalculator
from .price_feed import PriceFeedService


class TradeExecutionService:

    @staticmethod
    def validate_trade_limits(user, asset, amount):
        """Validate trade against platform risk limits (real trades only)."""
        from .models import HouseEdgeConfig

        config = HouseEdgeConfig.objects.filter(is_active=True).first()
        if not config:
            return True, None

        open_trades = BinaryTrade.objects.filter(user=user, status='active').count()
        if open_trades >= config.max_open_trades_per_user:
            return False, f"Maximum {config.max_open_trades_per_user} open trades allowed"

        asset_exposure = BinaryTrade.objects.filter(
            user=user, asset=asset, status='active'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        if asset_exposure + amount > config.max_exposure_per_asset:
            return False, f"Maximum ${config.max_exposure_per_asset} exposure per asset"

        total_exposure = BinaryTrade.objects.filter(
            user=user, status='active'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        if total_exposure + amount > config.max_total_exposure:
            return False, f"Maximum ${config.max_total_exposure} total exposure"

        return True, None

    @staticmethod
    def open_trade(user, asset_symbol, direction, amount, expiry_seconds, is_demo=False):
        """
        Open a new binary trade with house edge applied.

        Flow:
        1. Validate asset, amount, balance.
        2. Fetch current price (live market).
        3. Compute house edge parameters (adjusted payout + adjusted strike).
           The strike price is already adjusted inside get_trade_parameters —
           we do NOT call adjust_strike_price a second time.
        4. Record execution delay in the trade (but do NOT sleep inside the
           DB transaction — that would hold the connection open).
        5. Deduct balance and persist the trade atomically.

        Returns: (trade_object, error_message)
        """
        # --- Validate asset ---
        try:
            asset = TradingAsset.objects.get(symbol=asset_symbol, is_active=True)
        except TradingAsset.DoesNotExist:
            return None, "Asset not found or inactive"

        if amount < asset.min_trade_amount:
            return None, f"Minimum trade amount is ${asset.min_trade_amount}"
        if amount > asset.max_trade_amount:
            return None, f"Maximum trade amount is ${asset.max_trade_amount}"

        # --- Validate balance ---
        if is_demo:
            from demo.models import DemoAccount
            demo_account, _ = DemoAccount.objects.get_or_create(
                user=user, defaults={'balance': Decimal('10000.00')}
            )
            if demo_account.balance < amount:
                return None, "Insufficient demo balance"
        else:
            if user.balance < amount:
                return None, "Insufficient balance"
            valid, error = TradeExecutionService.validate_trade_limits(user, asset, amount)
            if not valid:
                return None, error

        # --- Fetch live price BEFORE entering the transaction ---
        current_price = PriceFeedService.get_current_price(asset_symbol)
        if not current_price:
            return None, "Unable to get current price for this asset"

        # --- Compute house edge parameters (includes adjusted strike price) ---
        calculator = HouseEdgeCalculator(user, asset, amount)
        params = calculator.get_trade_parameters(current_price, direction)

        # The adjusted strike is already computed inside get_trade_parameters.
        # Use it directly — do NOT call adjust_strike_price again.
        adjusted_strike = params['adjusted_strike_price']
        expires_at = timezone.now() + timedelta(seconds=expiry_seconds)

        # --- Persist atomically ---
        try:
            with transaction.atomic():
                if is_demo:
                    from demo.models import DemoAccount
                    demo_account = DemoAccount.objects.select_for_update().get(user=user)
                    if demo_account.balance < amount:
                        return None, "Insufficient demo balance"
                    demo_account.balance -= amount
                    demo_account.save(update_fields=['balance'])
                else:
                    # Re-fetch user inside transaction to avoid race conditions
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    locked_user = User.objects.select_for_update().get(pk=user.pk)
                    if locked_user.balance < amount:
                        return None, "Insufficient balance"
                    locked_user.balance -= amount
                    locked_user.save(update_fields=['balance'])
                    # Sync the in-memory user object
                    user.balance = locked_user.balance

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
                    user_total_profit=params['user_total_profit'],
                    is_demo=is_demo,
                )
        except Exception as e:
            return None, f"Failed to open trade: {str(e)}"

        return trade, None

    @staticmethod
    def close_trade(trade_id):
        """
        Close a single trade and settle profit/loss.
        Each close runs in its own atomic transaction.
        Returns: (trade_object, error_message)
        """
        try:
            with transaction.atomic():
                try:
                    trade = BinaryTrade.objects.select_for_update().get(id=trade_id)
                except BinaryTrade.DoesNotExist:
                    return None, "Trade not found"

                if trade.status != 'active':
                    return None, f"Trade is already {trade.status}"

                # Fetch final price
                final_price = PriceFeedService.get_current_price(trade.asset.symbol)
                if not final_price:
                    return None, "Unable to get final price"

                # Determine outcome
                if trade.direction == 'buy':
                    won = final_price > trade.strike_price
                else:
                    won = final_price < trade.strike_price

                if won:
                    profit = trade.amount * (trade.adjusted_payout_percentage / Decimal('100'))
                    trade.status = 'won'
                    trade.profit_loss = profit
                    payout = trade.amount + profit

                    if trade.is_demo:
                        from demo.models import DemoAccount
                        demo_account = DemoAccount.objects.select_for_update().get(user=trade.user)
                        demo_account.balance += payout
                        demo_account.save(update_fields=['balance'])
                    else:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        u = User.objects.select_for_update().get(pk=trade.user_id)
                        u.balance += payout
                        u.save(update_fields=['balance'])
                else:
                    trade.status = 'lost'
                    trade.profit_loss = -trade.amount
                    # Stake was already deducted on open — nothing to do

                trade.final_price = final_price
                trade.closed_at = timezone.now()
                trade.save()

        except Exception as e:
            return None, f"Error closing trade: {str(e)}"

        # Update stats outside the transaction (non-critical, demo trades skipped)
        if not trade.is_demo:
            try:
                TradeExecutionService.update_user_stats(trade)
            except Exception as e:
                print(f"⚠️ Failed to update stats for trade {trade_id}: {e}")

        return trade, None

    @staticmethod
    def update_user_stats(trade):
        """Update UserTradingStats after a real trade closes."""
        stats, _ = UserTradingStats.objects.get_or_create(user=trade.user)

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

        # Flag suspiciously high win rates
        if stats.total_trades >= 50:
            win_rate = (stats.total_wins / stats.total_trades) * 100
            if win_rate > 75 and not stats.is_flagged:
                stats.is_flagged = True
                stats.flag_reason = f"High win rate: {win_rate:.2f}% after {stats.total_trades} trades"
                stats.flagged_at = timezone.now()

        stats.save()

    @staticmethod
    def close_expired_trades():
        """
        Close all trades whose expiry time has passed.
        Each trade is closed in its own transaction so one failure
        does not roll back the others.
        """
        expired = BinaryTrade.objects.filter(
            status='active',
            expires_at__lte=timezone.now()
        ).values_list('id', flat=True)

        results = {'closed': 0, 'errors': 0, 'error_details': []}

        for trade_id in expired:
            _, error = TradeExecutionService.close_trade(trade_id)
            if error:
                results['errors'] += 1
                results['error_details'].append({'trade_id': str(trade_id), 'error': error})
            else:
                results['closed'] += 1

        return results
