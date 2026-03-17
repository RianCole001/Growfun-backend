"""
Chart Data Service for Binary Trading
Provides real OHLC candlestick data for all trading assets.

Sources:
  Crypto (BTC, ETH, BNB, SOL …) → CoinGecko OHLC API
  Gold (GOLD)                    → Yahoo Finance (GC=F)
  Oil  (OIL)                     → Yahoo Finance (CL=F)
  Forex (EURUSD, GBPUSD …)       → Yahoo Finance (EURUSD=X …)
  Fallback for any asset         → Aggregate stored AssetPrice ticks into OHLC
"""
import requests
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta, datetime, timezone as dt_timezone


# ── CoinGecko IDs ──────────────────────────────────────────────────────────────
COINGECKO_IDS = {
    'BTC':  'bitcoin',
    'ETH':  'ethereum',
    'BNB':  'binancecoin',
    'SOL':  'solana',
    'ADA':  'cardano',
    'XRP':  'ripple',
    'DOGE': 'dogecoin',
    'USDT': 'tether',
    'MATIC':'matic-network',
    'LTC':  'litecoin',
    'AVAX': 'avalanche-2',
    'LINK': 'chainlink',
    'DOT':  'polkadot',
}

# ── Yahoo Finance tickers ──────────────────────────────────────────────────────
YAHOO_TICKERS = {
    'GOLD':   'GC=F',
    'OIL':    'CL=F',
    'EURUSD': 'EURUSD=X',
    'GBPUSD': 'GBPUSD=X',
    'USDJPY': 'USDJPY=X',
    'AUDUSD': 'AUDUSD=X',
    'SILVER': 'SI=F',
    'NASDAQ': '^IXIC',
    'SP500':  '^GSPC',
}

# Interval → CoinGecko "days" param
COINGECKO_DAYS = {
    '1m':  1,
    '5m':  1,
    '15m': 1,
    '30m': 2,
    '1h':  7,
    '4h':  30,
    '1d':  90,
}

# Interval → Yahoo Finance interval string
YAHOO_INTERVAL = {
    '1m':  '1m',
    '5m':  '5m',
    '15m': '15m',
    '30m': '30m',
    '1h':  '1h',
    '4h':  '1h',   # Yahoo doesn't have 4h; use 1h and let frontend group
    '1d':  '1d',
}

# Interval → Yahoo Finance range string
YAHOO_RANGE = {
    '1m':  '1d',
    '5m':  '5d',
    '15m': '5d',
    '30m': '1mo',
    '1h':  '1mo',
    '4h':  '3mo',
    '1d':  '1y',
}


class ChartService:

    @classmethod
    def get_ohlc(cls, symbol: str, interval: str = '1m', limit: int = 100):
        """
        Return OHLC candles for `symbol` at `interval`.
        Each candle: { time, open, high, low, close, volume }
        `time` is a Unix timestamp (seconds).
        """
        symbol = symbol.upper()

        # 1. Crypto via CoinGecko
        if symbol in COINGECKO_IDS:
            candles = cls._coingecko_ohlc(symbol, interval, limit)
            if candles:
                return candles

        # 2. Commodities / Forex / Indices via Yahoo Finance
        if symbol in YAHOO_TICKERS:
            candles = cls._yahoo_ohlc(symbol, interval, limit)
            if candles:
                return candles

        # 3. Fallback: build OHLC from stored AssetPrice ticks
        return cls._db_ohlc(symbol, interval, limit)

    # ── CoinGecko ──────────────────────────────────────────────────────────────
    @classmethod
    def _coingecko_ohlc(cls, symbol, interval, limit):
        """
        CoinGecko /coins/{id}/ohlc returns [timestamp_ms, open, high, low, close].
        Granularity is determined by `days`:
          days=1  → 30-min candles
          days≤30 → 4-hour candles
          days≤90 → daily candles
        We request the appropriate days and trim to `limit`.
        """
        gecko_id = COINGECKO_IDS[symbol]
        days = COINGECKO_DAYS.get(interval, 1)
        try:
            resp = requests.get(
                f'https://api.coingecko.com/api/v3/coins/{gecko_id}/ohlc',
                params={'vs_currency': 'usd', 'days': days},
                timeout=8
            )
            if resp.status_code != 200:
                return None
            raw = resp.json()  # [[ts_ms, o, h, l, c], ...]
            candles = [
                {
                    'time':   c[0] // 1000,
                    'open':   float(c[1]),
                    'high':   float(c[2]),
                    'low':    float(c[3]),
                    'close':  float(c[4]),
                    'volume': 0,
                }
                for c in raw
            ]
            return candles[-limit:]
        except Exception as e:
            print(f"⚠️ CoinGecko OHLC failed for {symbol}: {e}")
            return None

    # ── Yahoo Finance ──────────────────────────────────────────────────────────
    @classmethod
    def _yahoo_ohlc(cls, symbol, interval, limit):
        """
        Yahoo Finance v8 chart API — no API key required.
        Returns OHLC candles for commodities, forex, indices.
        """
        ticker = YAHOO_TICKERS[symbol]
        yf_interval = YAHOO_INTERVAL.get(interval, '1m')
        yf_range = YAHOO_RANGE.get(interval, '1d')

        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        params = {
            'interval': yf_interval,
            'range':    yf_range,
        }

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=8)
            if resp.status_code != 200:
                return None

            data = resp.json()
            result = data.get('chart', {}).get('result', [])
            if not result:
                return None

            chart = result[0]
            timestamps = chart.get('timestamp', [])
            quote = chart.get('indicators', {}).get('quote', [{}])[0]

            opens   = quote.get('open',   [])
            highs   = quote.get('high',   [])
            lows    = quote.get('low',    [])
            closes  = quote.get('close',  [])
            volumes = quote.get('volume', [])

            candles = []
            for i, ts in enumerate(timestamps):
                o = opens[i]   if i < len(opens)   else None
                h = highs[i]   if i < len(highs)   else None
                l = lows[i]    if i < len(lows)    else None
                c = closes[i]  if i < len(closes)  else None
                v = volumes[i] if i < len(volumes) else 0

                # Skip candles with missing data
                if None in (o, h, l, c):
                    continue

                candles.append({
                    'time':   int(ts),
                    'open':   round(float(o), 5),
                    'high':   round(float(h), 5),
                    'low':    round(float(l), 5),
                    'close':  round(float(c), 5),
                    'volume': int(v) if v else 0,
                })

            return candles[-limit:] if candles else None

        except Exception as e:
            print(f"⚠️ Yahoo Finance OHLC failed for {symbol} ({ticker}): {e}")
            return None

    # ── DB fallback ────────────────────────────────────────────────────────────
    @classmethod
    def _db_ohlc(cls, symbol, interval, limit):
        """
        Aggregate stored AssetPrice tick records into OHLC candles.
        Used when all external APIs fail or for custom/admin coins.
        """
        from .models import AssetPrice, TradingAsset

        interval_seconds = {
            '1m':  60,
            '5m':  300,
            '15m': 900,
            '30m': 1800,
            '1h':  3600,
            '4h':  14400,
            '1d':  86400,
        }.get(interval, 60)

        lookback_seconds = interval_seconds * limit * 2  # fetch extra to ensure enough candles
        since = timezone.now() - timedelta(seconds=lookback_seconds)

        try:
            asset = TradingAsset.objects.get(symbol=symbol)
        except TradingAsset.DoesNotExist:
            return []

        ticks = list(
            AssetPrice.objects.filter(asset=asset, timestamp__gte=since)
            .order_by('timestamp')
            .values_list('timestamp', 'price')
        )

        if not ticks:
            return []

        # Group ticks into buckets
        candles = []
        bucket_start = None
        bucket_prices = []

        for ts, price in ticks:
            price = float(price)
            # Align to interval boundary
            ts_epoch = int(ts.timestamp())
            bucket = (ts_epoch // interval_seconds) * interval_seconds

            if bucket_start is None:
                bucket_start = bucket

            if bucket == bucket_start:
                bucket_prices.append(price)
            else:
                if bucket_prices:
                    candles.append({
                        'time':   bucket_start,
                        'open':   bucket_prices[0],
                        'high':   max(bucket_prices),
                        'low':    min(bucket_prices),
                        'close':  bucket_prices[-1],
                        'volume': 0,
                    })
                bucket_start = bucket
                bucket_prices = [price]

        # Flush last bucket
        if bucket_prices:
            candles.append({
                'time':   bucket_start,
                'open':   bucket_prices[0],
                'high':   max(bucket_prices),
                'low':    min(bucket_prices),
                'close':  bucket_prices[-1],
                'volume': 0,
            })

        return candles[-limit:]
