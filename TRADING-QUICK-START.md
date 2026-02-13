# Trading System - Quick Start

## Prerequisites
- Backend running on http://localhost:8000
- Frontend running on http://localhost:3000
- User authenticated with valid JWT token

## Step 1: Apply Database Migrations

```bash
cd backend-growfund

# Activate virtual environment (if not already active)
venv\Scripts\activate

# Run migrations
py manage.py migrate investments
```

## Step 2: Verify Backend

```bash
# Check if migrations applied successfully
py manage.py showmigrations investments

# Should show:
# [X] 0001_initial
```

## Step 3: Start Frontend

```bash
cd Growfund-Dashboard/trading-dashboard

# Start development server
npm start
```

## Step 4: Access Trading System

1. Open http://localhost:3000
2. Login with your credentials
3. Navigate to "Trade Now" page
4. Select Gold or USDT
5. Click "Open [Asset] Trade"

## Quick Test

### Test Gold Trading
1. Click "Trade Now" in navigation
2. Select "🥇 Gold Trading"
3. View live gold chart (updates every 500ms)
4. Click "Open Gold Trade"
5. Enter:
   - Trade Type: Buy
   - Quantity: 0.5
   - Stop Loss: 2040
   - Take Profit: 2060
   - Duration: 1 Hour
6. Click "Open Trade"

### Test USDT Trading
1. Select "💵 USDT Trading"
2. View live USDT chart
3. Click "Open USDT Trade"
4. Enter:
   - Trade Type: Buy
   - Quantity: 100
   - Stop Loss: 0.99
   - Take Profit: 1.01
   - Duration: 30 Minutes
5. Click "Open Trade"

## View Open Trades

1. Scroll down to "Open Trades" section
2. Click "▶ Open Trades" to expand
3. View all active trades with:
   - Current P&L
   - Stop Loss/Take Profit levels
   - Time remaining
4. Close trades manually by entering exit price

## View Trade History

1. Scroll down to "Trade History" section
2. Click "▶ Trade History" to expand
3. Filter by close reason:
   - All
   - Manual
   - Stop Loss
   - Take Profit
   - Expired
4. View detailed trade statistics

## API Testing with Curl

### Create Trade
```bash
curl -X POST http://localhost:8000/api/investments/trades/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "gold",
    "trade_type": "buy",
    "entry_price": 2050,
    "quantity": 0.5,
    "stop_loss": 2040,
    "take_profit": 2060,
    "timeframe": "1h"
  }'
```

### Get Open Trades
```bash
curl -X GET http://localhost:8000/api/investments/trades/open_trades/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Close Trade
```bash
curl -X POST http://localhost:8000/api/investments/trades/{trade_id}/close/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exit_price": 2055,
    "close_reason": "manual"
  }'
```

### Get Trade History
```bash
curl -X GET http://localhost:8000/api/investments/trades/history/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Features Overview

### Gold Trading
- Real-time chart with 0.2% volatility
- Buy/Sell positions
- Stop loss & take profit
- Time-based expiry (1m to 1d)
- Live P&L tracking

### USDT Trading
- Stablecoin with 0.01% volatility
- Same trading features as Gold
- Ideal for stable value trading
- Low volatility for precise trading

### Risk Management
- Automatic stop loss execution
- Automatic take profit execution
- Trade expiry after time duration
- Real-time balance validation

### Trade Management
- Open trades dashboard
- Manual trade closure
- Trade history with statistics
- Filter and search capabilities

## Common Issues

### "Insufficient Balance" Error
- Check available balance in top right
- Reduce trade quantity
- Ensure balance > (quantity × entry price)

### Trade Not Appearing
- Refresh page (F5)
- Check browser console for errors
- Verify authentication token is valid

### Charts Not Updating
- Check if "LIVE" button is active
- Verify internet connection
- Refresh page

### Stop Loss/Take Profit Not Triggering
- Ensure price reaches the level
- Check trade status is "open"
- Verify values are set correctly

## Next Steps

1. **Explore Charts**: Try different timeframes (15M, 30M, 1H, 4H)
2. **Test Risk Management**: Set stop loss and take profit levels
3. **Monitor Trades**: Watch real-time P&L updates
4. **Analyze History**: Review past trades and performance
5. **Optimize Strategy**: Adjust quantities and risk levels

## Support

For detailed information, see: `TRADING-SYSTEM-SETUP.md`

For API documentation, check backend logs and Django admin panel.
