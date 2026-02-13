# Trading System Setup Guide - Gold & USDT

## Overview
Complete trading system for Gold and USDT with advanced risk management features including stop loss, take profit, and time-based expiry.

## Features Implemented

### 1. Trading Assets
- **Gold (GOLD/USD)**: Real-time streaming chart with 0.2% volatility
- **USDT (USDT/USD)**: Stablecoin with minimal 0.01% volatility

### 2. Trading Options
- **Buy/Sell**: Long and short positions
- **Quantity**: Flexible quantity input with percentage quick-select buttons
- **Stop Loss**: Automatic trade closure at specified loss level
- **Take Profit**: Automatic trade closure at specified profit level
- **Time-Based Expiry**: Trade automatically closes after selected duration
  - 1 Minute, 5 Minutes, 15 Minutes, 30 Minutes
  - 1 Hour, 4 Hours, 1 Day

### 3. Risk Management
- Real-time P&L calculation
- Automatic stop loss/take profit execution
- Trade expiry monitoring
- Balance validation before trade execution

### 4. Trade Management
- Open trades display with real-time updates
- Manual trade closure with custom exit price
- Trade history with close reason tracking
- Filter by close reason (manual, stop loss, take profit, expired)

## Backend Setup

### 1. Database Models
Two main models created:

**Trade Model**
- Stores active and closed trades
- Tracks entry/exit prices, quantities, and P&L
- Manages stop loss, take profit, and expiry

**TradeHistory Model**
- Archives closed trades
- Records close reason and final P&L
- Maintains trading statistics

### 2. API Endpoints

```
POST   /api/investments/trades/                    - Create new trade
GET    /api/investments/trades/                    - List all trades
GET    /api/investments/trades/{id}/               - Get trade details
POST   /api/investments/trades/{id}/close/         - Close trade manually
POST   /api/investments/trades/{id}/update_price/  - Update price & check SL/TP
GET    /api/investments/trades/open_trades/        - Get open trades only
GET    /api/investments/trades/closed_trades/      - Get closed trades only
GET    /api/investments/trades/history/            - Get trade history
```

### 3. Installation Steps

#### Step 1: Run Migrations
```bash
cd backend-growfund
py manage.py makemigrations investments
py manage.py migrate investments
```

#### Step 2: Verify Installation
```bash
py manage.py shell
>>> from investments.models import Trade, TradeHistory
>>> print("Models loaded successfully")
```

## Frontend Setup

### 1. New Components Created

**TradingModal.js**
- Modal for opening new trades
- Form validation for all fields
- Real-time balance checking
- Error handling and user feedback

**OpenTrades.js**
- Display active trades
- Real-time P&L updates
- Manual trade closure
- Status indicators (open, expired, stop loss hit, take profit hit)

**TradeHistory.js**
- Historical trade records
- Filter by close reason
- Performance statistics
- Sortable table view

**USDTChart.js**
- Live USDT price chart
- Real-time streaming (500ms updates)
- Line/Area chart toggle
- Multiple timeframes (15M, 30M, 1H, 4H)

**TradeNow.js** (Updated)
- Asset selector (Gold/USDT)
- Integrated chart display
- Quick trade button
- Open trades and history sections

### 2. API Integration
Added trading endpoints to `services/api.js`:
```javascript
tradingAPI.createTrade(data)
tradingAPI.getTrades()
tradingAPI.closeTrade(id, data)
tradingAPI.getOpenTrades()
tradingAPI.getClosedTrades()
tradingAPI.getTradeHistory()
```

## Usage Guide

### Opening a Trade

1. Navigate to "Trade Now" page
2. Select asset (Gold or USDT)
3. View live price chart
4. Click "Open [Asset] Trade" button
5. Fill in trade details:
   - Trade Type (Buy/Sell)
   - Quantity (or use % buttons)
   - Stop Loss (optional)
   - Take Profit (optional)
   - Duration (optional)
6. Review order summary
7. Click "Open Trade"

### Managing Trades

**Open Trades Section:**
- View all active trades
- See real-time P&L
- Monitor stop loss/take profit levels
- Close trades manually with custom exit price

**Trade History Section:**
- View all closed trades
- Filter by close reason
- Analyze performance
- Track trading statistics

### Trade Closure Scenarios

1. **Manual**: User closes trade with custom exit price
2. **Stop Loss Hit**: Trade closes automatically at stop loss level
3. **Take Profit Hit**: Trade closes automatically at take profit level
4. **Expired**: Trade closes automatically after time duration expires

## Validation Rules

### Entry Validation
- Quantity must be > 0
- Entry price must be > 0
- Stop loss must be > 0
- Take profit must be > 0
- Sufficient balance for buy trades

### Logic Validation
**For Buy Trades:**
- Stop loss must be below entry price
- Take profit must be above entry price

**For Sell Trades:**
- Stop loss must be above entry price
- Take profit must be below entry price

## Real-Time Updates

### Price Updates
- Gold: Updates every 500ms with 0.2% volatility
- USDT: Updates every 500ms with 0.01% volatility

### Trade Monitoring
- Open trades refresh every 5 seconds
- P&L recalculated on each price update
- Stop loss/take profit checked automatically

## Testing

### Test Trade Creation
```bash
curl -X POST http://localhost:8000/api/investments/trades/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
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

### Test Trade Closure
```bash
curl -X POST http://localhost:8000/api/investments/trades/{trade_id}/close/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exit_price": 2055,
    "close_reason": "manual"
  }'
```

## Performance Metrics

### P&L Calculation
- **Buy Trade**: (Exit Price - Entry Price) × Quantity
- **Sell Trade**: (Entry Price - Exit Price) × Quantity
- **Percentage**: (P&L / (Entry Price × Quantity)) × 100

### Risk Management
- Stop loss prevents losses beyond specified level
- Take profit locks in gains at target level
- Time expiry prevents holding trades indefinitely

## Future Enhancements

1. **Advanced Charts**: Candlestick charts with technical indicators
2. **Partial Closes**: Close portion of trade at different prices
3. **Trailing Stop Loss**: Dynamic stop loss that follows price
4. **Alerts**: Email/SMS notifications for trade events
5. **Analytics**: Detailed trading statistics and performance reports
6. **Multiple Assets**: Add more trading pairs (crypto, forex, etc.)
7. **Leverage Trading**: Margin trading with leverage options
8. **Automated Strategies**: Bot trading with predefined strategies

## Troubleshooting

### Trades Not Appearing
- Check user authentication token
- Verify trades are created in database
- Check browser console for API errors

### P&L Not Updating
- Ensure price updates are running (check intervals)
- Verify trade status is 'open'
- Check for JavaScript errors in console

### Stop Loss/Take Profit Not Triggering
- Verify prices are being updated
- Check stop loss/take profit values are valid
- Ensure trade status is 'open'

## Support

For issues or questions:
1. Check browser console for errors
2. Review backend logs: `py manage.py runserver`
3. Verify database migrations: `py manage.py showmigrations investments`
4. Test API endpoints directly with curl or Postman
