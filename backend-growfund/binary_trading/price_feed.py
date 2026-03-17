"""
Price Feed Service for Binary Trading
Provides real-time price updates for assets.
- Crypto assets (BTC, ETH) use CoinGecko API
- Commodities (GOLD, OIL) use a public metals/commodities API with fallback
- Forex (EURUSD, GBPUSD) use exchangerate API with fallback
- All assets fall back to a seeded random walk if external APIs are unavailable
"""
from decimal import Decimal
import random
import requests
from .models import TradingAsset, AssetPrice
from django.utils import timezone


# CoinGecko IDs for crypto assets
COINGECKO_IDS = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'BNB': 'binancecoin',
    'SOL': 'solana',
    'ADA': 'cardano',
    'XRP': 'ripple',
    'DOGE': 'dogecoin',
    'USDT': 'tether',
}

# Fallback base prices (used only when all APIs fail)
FALLBACK_PRICES = {
    'OIL':    Decimal('75.50'),
    'GOLD':   Decimal('2050.00'),
    'EURUSD': Decimal('1.0850'),
    'GBPUSD': Decimal('1.2650'),
    'BTC':    Decimal('65000.00'),
    'ETH':    Decimal('3200.00'),
    'BNB':    Decimal('420.00'),
    'SOL':    Decimal('150.00'),
}


class PriceFeedService:
    """Generate and manage asset prices"""

    # How long (seconds) a cached price is considered fresh
    PRICE_TTL = 10

    @classmethod
    def get_current_price(cls, asset_symbol):
        """
        Get current price for an asset.
        Returns a fresh cached price if available, otherwise fetches live.
        """
        latest = AssetPrice.objects.filter(
            asset__symbol=asset_symbol
        ).order_by('-timestamp').first()

        if latest:
            age = (timezone.now() - latest.timestamp).total_seconds()
            if age < cls.PRICE_TTL:
                return latest.price

        return cls._fetch_and_store(asset_symbol)

    @classmethod
    def _fetch_and_store(cls, asset_symbol):
        """Fetch a live price and persist it."""
        price = cls._fetch_live_price(asset_symbol)
        if price is None:
            price = cls._random_walk_price(asset_symbol)
        if price is None:
            return None

        try:
            asset = TradingAsset.objects.get(symbol=asset_symbol)
            AssetPrice.objects.create(asset=asset, price=price)
        except TradingAsset.DoesNotExist:
            pass

        return price

    @classmethod
    def _fetch_live_price(cls, symbol):
        """
        Fetch a real market price.
        Returns Decimal or None on failure.
        """
        # --- Crypto via CoinGecko ---
        if symbol in COINGECKO_IDS:
            try:
                resp = requests.get(
                    'https://api.coingecko.com/api/v3/simple/price',
                    params={'ids': COINGECKO_IDS[symbol], 'vs_currencies': 'usd'},
                    timeout=5
                )
                if resp.status_code == 200:
                    data = resp.json()
                    usd = data.get(COINGECKO_IDS[symbol], {}).get('usd')
                    if usd:
                        return Decimal(str(usd))
            except Exception as e:
                print(f"⚠️ CoinGecko fetch failed for {symbol}: {e}")
            return None

        # --- Gold via metals-api (free tier) or fallback ---
        if symbol == 'GOLD':
            try:
                resp = requests.get(
                    'https://api.metals.live/v1/spot/gold',
                    timeout=5
                )
                if resp.status_code == 200:
                    data = resp.json()
                    # metals.live returns [{"gold": price}]
                    price = data[0].get('gold') if isinstance(data, list) else data.get('price')
                    if price:
                        return Decimal(str(price))
            except Exception as e:
                print(f"⚠️ Gold price fetch failed: {e}")
            return None

        # --- Oil: no reliable free API, use random walk from last known ---
        if symbol == 'OIL':
            return None  # falls through to random walk

        # --- Forex via exchangerate-api (free, no key needed for major pairs) ---
        forex_map = {
            'EURUSD': ('EUR', 'USD'),
            'GBPUSD': ('GBP', 'USD'),
            'USDJPY': ('USD', 'JPY'),
            'AUDUSD': ('AUD', 'USD'),
        }
        if symbol in forex_map:
            base, quote = forex_map[symbol]
            try:
                resp = requests.get(
                    f'https://open.er-api.com/v6/latest/{base}',
                    timeout=5
                )
                if resp.status_code == 200:
                    data = resp.json()
                    rate = data.get('rates', {}).get(quote)
                    if rate:
                        return Decimal(str(rate))
            except Exception as e:
                print(f"⚠️ Forex fetch failed for {symbol}: {e}")
            return None

        return None

    @classmethod
    def _random_walk_price(cls, asset_symbol):
        """
        Produce a price via random walk from the last stored price.
        Used as a last-resort fallback for assets with no live feed (OIL, etc.)
        """
        try:
            asset = TradingAsset.objects.get(symbol=asset_symbol)
        except TradingAsset.DoesNotExist:
            return None

        last = AssetPrice.objects.filter(asset=asset).order_by('-timestamp').first()
        base = last.price if last else FALLBACK_PRICES.get(asset_symbol, Decimal('100.00'))

        volatility = float(asset.volatility)
        change = random.uniform(-volatility, volatility)
        return base * (Decimal('1') + Decimal(str(round(change, 8))))

    @classmethod
    def update_all_prices(cls):
        """Fetch and return current prices for all active assets."""
        assets = TradingAsset.objects.filter(is_active=True)
        prices = {}
        for asset in assets:
            price = cls.get_current_price(asset.symbol)
            if price:
                prices[asset.symbol] = {
                    'symbol': asset.symbol,
                    'name': asset.name,
                    'price': float(price),
                    'timestamp': timezone.now().isoformat()
                }
        return prices

    @classmethod
    def initialize_prices(cls):
        """Seed initial prices for all assets that have none stored."""
        for symbol, base_price in FALLBACK_PRICES.items():
            try:
                asset = TradingAsset.objects.get(symbol=symbol)
                if not AssetPrice.objects.filter(asset=asset).exists():
                    AssetPrice.objects.create(asset=asset, price=base_price)
            except TradingAsset.DoesNotExist:
                pass
