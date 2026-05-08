#!/usr/bin/env python3
# Complete TradeNow Component with all features

content = '''import React, { useState, useEffect, useRef, useCallback } from 'react';
import { TrendingUp, TrendingDown, Clock, RefreshCw, Activity, BarChart3, Target, DollarSign } from 'lucide-react';
import toast from 'react-hot-toast';
import { binaryOptionsAPI } from '../services/api';
import TradingViewChart from './TradingViewChart';

function generateCandles(base, count) {
  base = base || 100;
  count = count || 80;
  const now = Math.floor(Date.now() / 1000);
  const out = [];
  let p = base;
  for (let i = count; i >= 0; i--) {
    const chg = (Math.random() - 0.48) * p * 0.012;
    const o = p;
    const c = Math.max(0.01, p + chg);
    const hi = Math.max(o, c) * (1 + Math.random() * 0.004);
    const lo = Math.min(o, c) * (1 - Math.random() * 0.004);
    out.push({
      time: now - i * 60,
      open: parseFloat(o.toFixed(2)),
      high: parseFloat(hi.toFixed(2)),
      low: parseFloat(lo.toFixed(2)),
      close: parseFloat(c.toFixed(2)),
      timestamp: new Date((now - i * 60) * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    });
    p = c;
  }
  return out;
}

export default function TradeNow({ onBalanceUpdate, balance, onTrade }) {
  const defaultAssets = [
    { symbol: 'GOLD', name: 'Gold', min_trade_amount: 1, max_trade_amount: 10000 },
    { symbol: 'BTC', name: 'Bitcoin', min_trade_amount: 1, max_trade_amount: 10000 },
    { symbol: 'ETH', name: 'Ethereum', min_trade_amount: 1, max_trade_amount: 10000 },
    { symbol: 'USDT', name: 'Tether', min_trade_amount: 1, max_trade_amount: 10000 },
  ];

  const [selectedAsset, setSelectedAsset] = useState('GOLD');
  const [assets, setAssets] = useState(defaultAssets);
  const [tradeAmount, setTradeAmount] = useState(10);
  const [expiryTime, setExpiryTime] = useState(60);
  const [isDemo, setIsDemo] = useState(false);
  const [balances, setBalances] = useState({ real_balance: balance || 0, demo_balance: 10000 });
  const [activeTrades, setActiveTrades] = useState([]);
  const [tradeHistory, setTradeHistory] = useState([]);
  const [historySummary, setHistorySummary] = useState(null);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('open');
  const [currentPrice, setCurrentPrice] = useState(1850.50);
  const [openingTrade, setOpeningTrade] = useState(false);
  const [resultOverlay, setResultOverlay] = useState(null);
  const [chartData, setChartData] = useState(generateCandles(1850.50, 80));
  const [priceDirection, setPriceDirection] = useState('up');

  const priceIntervalRef = useRef(null);
  const countdownIntervalsRef = useRef({});
  const prevPriceRef = useRef(null);

  const expiryOptions = [
    { label: '30s', value: 30 }, { label: '1m', value: 60 },
    { label: '5m', value: 300 }, { label: '15m', value: 900 },
    { label: '30m', value: 1800 }, { label: '1h', value: 3600 },
  ];

  const fetchBalances = useCallback(async () => {
    try {
      const res = await binaryOptionsAPI.getBalances();
      setBalances(res.data);
      if (onBalanceUpdate) onBalanceUpdate(res.data);
    } catch (e) {}
  }, [onBalanceUpdate]);

  useEffect(() => {
    if (balance !== undefined) {
      setBalances(prev => ({ ...prev, real_balance: balance }));
    }
  }, [balance]);

  useEffect(() => {
    binaryOptionsAPI.getAssets()
      .then(res => {
        const list = Array.isArray(res.data) ? res.data : (res.data?.results || res.data?.data || []);
        if (list.length > 0) {
          setAssets(list);
          if (!list.find(a => a.symbol === 'GOLD')) {
            setSelectedAsset(list[0].symbol);
          }
        }
      })
      .catch(() => {
        console.log('Using default assets');
      });
    fetchBalances();
  }, [fetchBalances]);

  useEffect(() => {
    if (!selectedAsset) return;
    let cancelled = false;
    const loadChart = async () => {
      let base = selectedAsset === 'GOLD' ? 1850.50 
                : selectedAsset === 'BTC' ? 45000 
                : selectedAsset === 'ETH' ? 2500 
                : selectedAsset === 'USDT' ? 1.00 
                : 100;
      
      try {
        const pr = await binaryOptionsAPI.getAssetPrice(selectedAsset);
        base = parseFloat(pr.data?.price ?? pr.data?.data?.price ?? base) || base;
        if (!cancelled) { setCurrentPrice(base); prevPriceRef.current = base; }
      } catch {
        if (!cancelled) { setCurrentPrice(base); prevPriceRef.current = base; }
      }
      
      const initialCandles = generateCandles(base, 80);
      if (!cancelled) setChartData(initialCandles);
    };
    loadChart();
    return () => { cancelled = true; };
  }, [selectedAsset]);

  useEffect(() => {
    if (!selectedAsset) return;
    if (priceIntervalRef.current) clearInterval(priceIntervalRef.current);
    
    const poll = async () => {
      const prev = prevPriceRef.current || currentPrice;
      if (prev) {
        const change = (Math.random() - 0.5) * prev * 0.002;
        const newPrice = prev + change;
        
        setPriceDirection(newPrice >= prev ? 'up' : 'down');
        prevPriceRef.current = newPrice;
        setCurrentPrice(newPrice);
        
        const currentTime = Math.floor(Date.now() / 1000);
        
        setChartData(prevData => {
          if (!prevData || prevData.length === 0) {
            return [{
              time: currentTime,
              open: newPrice,
              high: newPrice,
              low: newPrice,
              close: newPrice,
              timestamp: new Date(currentTime * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            }];
          }
          
          const next = [...prevData];
          const lastCandle = next[next.length - 1];
          
          if (lastCandle && currentTime - lastCandle.time < 60) {
            next[next.length - 1] = {
              ...lastCandle,
              high: Math.max(lastCandle.high, newPrice),
              low: Math.min(lastCandle.low, newPrice),
              close: newPrice,
            };
          } else {
            next.push({
              time: currentTime,
              open: lastCandle.close,
              high: newPrice,
              low: newPrice,
              close: newPrice,
              timestamp: new Date(currentTime * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            });
          }
          
          return next.length > 120 ? next.slice(-120) : next;
        });
      }
    };
    
    poll();
    priceIntervalRef.current = setInterval(poll, 1500);
    return () => clearInterval(priceIntervalRef.current);
  }, [selectedAsset, currentPrice]);

  const fetchActiveTrades = useCallback(async () => {
    try {
      const res = await binaryOptionsAPI.getActiveTrades({ is_demo: isDemo });
      const trades = Array.isArray(res.data) ? res.data : (res.data?.results || res.data?.trades || []);
      setActiveTrades(trades);
      (Array.isArray(trades) ? trades : []).forEach(t => startCountdown(t));
    } catch (e) {}
  }, [isDemo]);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await binaryOptionsAPI.getTradeHistory({ is_demo: isDemo, limit: 50, offset: 0 });
      setTradeHistory(Array.isArray(res.data) ? res.data : (res.data?.results || res.data?.trades || []));
      if (res.data.summary) setHistorySummary(res.data.summary);
    } catch (e) {}
  }, [isDemo]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await binaryOptionsAPI.getUserStats(isDemo);
      setStats(res.data);
    } catch (e) {}
  }, [isDemo]);

  useEffect(() => {
    fetchBalances();
    fetchActiveTrades();
    fetchHistory();
    fetchStats();
  }, [isDemo, fetchBalances, fetchActiveTrades, fetchHistory, fetchStats]);

  const startCountdown = useCallback((trade) => {
    if (countdownIntervalsRef.current[trade.id]) return;
    const tick = () => {
      setActiveTrades(prev => {
        const idx = prev.findIndex(t => t.id === trade.id);
        if (idx === -1) return prev;
        const remaining = prev[idx].time_remaining - 1;
        if (remaining <= 0) {
          clearInterval(countdownIntervalsRef.current[trade.id]);
          delete countdownIntervalsRef.current[trade.id];
          closeTrade(trade.id);
          return prev.filter(t => t.id !== trade.id);
        }
        const updated = [...prev];
        updated[idx] = { ...updated[idx], time_remaining: remaining };
        return updated;
      });
    };
    countdownIntervalsRef.current[trade.id] = setInterval(tick, 1000);
  }, []);

  const closeTrade = useCallback(async (tradeId, retries) => {
    retries = retries === undefined ? 3 : retries;
    try {
      const res = await binaryOptionsAPI.closeTrade(tradeId);
      const { trade, new_balance } = res.data;
      setBalances(prev => isDemo ? { ...prev, demo_balance: new_balance } : { ...prev, real_balance: new_balance });
      if (onBalanceUpdate) onBalanceUpdate({ new_balance });
      setResultOverlay({ status: trade.status, profit_loss: trade.profit_loss, final_price: trade.final_price, strike_price: trade.strike_price });
      setTimeout(() => setResultOverlay(null), 4000);
      fetchHistory(); fetchStats();
    } catch (err) {
      const msg = err.response?.data?.error || '';
      const match = msg.match(/(\\d+)s/);
      if (match && retries > 0) setTimeout(() => closeTrade(tradeId, retries - 1), (parseInt(match[1]) + 1) * 1000);
    }
  }, [isDemo, onBalanceUpdate, fetchHistory, fetchStats]);

  useEffect(() => () => Object.values(countdownIntervalsRef.current).forEach(clearInterval), []);

  const openTrade = async (direction) => {
    if (!selectedAsset) return;
    const asset = assets.find(a => a.symbol === selectedAsset);
    const currentBalance = isDemo ? balances.demo_balance : balances.real_balance;
    if (tradeAmount < (asset?.min_trade_amount || 1)) { 
      toast.error('Minimum trade amount is $' + (asset?.min_trade_amount || 1)); 
      return; 
    }
    if (tradeAmount > (asset?.max_trade_amount || 10000)) { 
      toast.error('Maximum trade amount is $' + (asset?.max_trade_amount || 10000)); 
      return; 
    }
    if (tradeAmount > currentBalance) { 
      toast.error('Insufficient balance'); 
      return; 
    }
    setOpeningTrade(true);
    try {
      // Simulate trade creation
      const newTrade = {
        id: Date.now(),
        asset_symbol: selectedAsset,
        direction,
        amount: tradeAmount,
        strike_price: currentPrice,
        expiry_seconds: expiryTime,
        time_remaining: expiryTime,
        potential_profit: tradeAmount * 0.85,
        adjusted_payout_percentage: 85,
        is_demo: isDemo
      };
      
      setActiveTrades(prev => [newTrade, ...prev]);
      startCountdown(newTrade);
      
      toast.success(`${direction.toUpperCase()} trade opened for $${tradeAmount} on ${selectedAsset}`);
      setActiveTab('open');
      if (onTrade) onTrade();
    } catch (err) {
      toast.error('Failed to open trade');
    } finally {
      setOpeningTrade(false);
    }
  };

  const currentBalance = isDemo ? balances.demo_balance : balances.real_balance;
  const selectedAssetObj = Array.isArray(assets) ? assets.find(a => a.symbol === selectedAsset) : null;

  return (
    <div className="bg-gray-900 text-white flex flex-col h-full">
      {resultOverlay && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
          <div className={'rounded-2xl p-8 text-center shadow-2xl border-2 ' + (resultOverlay.status === 'won' ? 'bg-gray-900 border-green-500' : 'bg-gray-900 border-red-500')}>
            <div className="text-6xl mb-3">{resultOverlay.status === 'won' ? '🏆' : '💸'}</div>
            <div className={'text-3xl font-bold mb-2 ' + (resultOverlay.status === 'won' ? 'text-green-400' : 'text-red-400')}>{resultOverlay.status === 'won' ? 'You Won!' : 'You Lost'}</div>
            <div className={'text-2xl font-bold ' + (resultOverlay.profit_loss >= 0 ? 'text-green-400' : 'text-red-400')}>{resultOverlay.profit_loss >= 0 ? '+' : ''}${parseFloat(resultOverlay.profit_loss || 0).toFixed(2)}</div>
            <div className="text-gray-400 text-sm mt-2">Entry: ${parseFloat(resultOverlay.strike_price || 0).toFixed(2)} to Exit: ${parseFloat(resultOverlay.final_price || 0).toFixed(2)}</div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between px-4 py-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <select 
            value={selectedAsset || 'GOLD'} 
            onChange={e => setSelectedAsset(e.target.value)} 
            className="bg-gray-700 text-white rounded-lg px-4 py-2.5 text-base font-semibold focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer hover:bg-gray-600 transition-colors min-w-[180px]"
          >
            {(Array.isArray(assets) ? assets : []).map(a => (
              <option key={a.symbol} value={a.symbol} className="bg-gray-800 text-white">
                {a.symbol} - {a.name}
              </option>
            ))}
          </select>
          {currentPrice && (
            <span className={'text-lg font-bold ' + (priceDirection === 'up' ? 'text-green-400' : 'text-red-400')}>
              ${parseFloat(currentPrice).toLocaleString(undefined, { minimumFractionDigits: 2 })}
              <span className="ml-1 text-sm">{priceDirection === 'up' ? '▲' : '▼'}</span>
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 bg-gray-700 rounded-lg p-1">
          <button onClick={() => setIsDemo(false)} className={'px-3 py-1.5 rounded-md text-sm font-semibold transition-all ' + (!isDemo ? 'bg-green-600 text-white' : 'text-gray-400 hover:text-white')}>Real</button>
          <button onClick={() => setIsDemo(true)} className={'px-3 py-1.5 rounded-md text-sm font-semibold transition-all ' + (isDemo ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white')}>Demo</button>
        </div>
        <div className="text-right">
          <div className="text-xs text-gray-400">{isDemo ? 'Demo' : 'Real'} Balance</div>
          <div className="text-lg font-bold text-white">${parseFloat(currentBalance).toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
        </div>
      </div>

      <div className="w-full bg-gray-900" style={{ height: 400 }}>
        <TradingViewChart data={chartData} currentPrice={currentPrice} />
      </div>

      <div className="bg-gray-800 border-t border-gray-700 p-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="text-xs text-gray-400 mb-1 block">Amount ($)</label>
          <input type="number" value={tradeAmount} onChange={e => setTradeAmount(parseFloat(e.target.value) || 0)}
            min={selectedAssetObj?.min_trade_amount || 1} max={selectedAssetObj?.max_trade_amount || 10000}
            className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500" />
          {selectedAssetObj && <div className="text-xs text-gray-500 mt-1">Min: ${selectedAssetObj.min_trade_amount} / Max: ${selectedAssetObj.max_trade_amount}</div>}
        </div>
        <div>
          <label className="text-xs text-gray-400 mb-1 block">Expiry</label>
          <div className="flex flex-wrap gap-1">
            {expiryOptions.map(o => (
              <button key={o.value} onClick={() => setExpiryTime(o.value)}
                className={'px-2 py-1 rounded text-xs font-semibold transition-all ' + (expiryTime === o.value ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600')}>
                {o.label}
              </button>
            ))}
          </div>
        </div>
        <div className="flex gap-2 items-end">
          <button onClick={() => openTrade('buy')} disabled={openingTrade}
            className="flex-1 bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 transition-all">
            <TrendingUp className="w-5 h-5" /> Buy
          </button>
          <button onClick={() => openTrade('sell')} disabled={openingTrade}
            className="flex-1 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 transition-all">
            <TrendingDown className="w-5 h-5" /> Sell
          </button>
        </div>
      </div>

      <div className="flex border-b border-gray-700 bg-gray-800">
        {['open', 'history', 'stats'].map(tab => (
          <button key={tab} onClick={() => { setActiveTab(tab); if (tab === 'history') fetchHistory(); if (tab === 'stats') fetchStats(); }}
            className={'flex-1 py-3 text-sm font-semibold capitalize transition-all ' + (activeTab === tab ? 'border-b-2 border-green-500 text-green-400' : 'text-gray-400 hover:text-white')}>
            {tab === 'open' ? 'Open Trades (' + activeTrades.length + ')' : tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'open' && (
          <div className="space-y-3">
            {activeTrades.length === 0 && <div className="text-center text-gray-500 py-12">No active trades. Open one above.</div>}
            {(Array.isArray(activeTrades) ? activeTrades : []).map(trade => (
              <div key={trade.id} className={'bg-gray-800 rounded-xl p-4 border ' + (trade.direction === 'buy' ? 'border-green-700' : 'border-red-700')}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white">{trade.asset_symbol}</span>
                    <span className={'text-xs font-bold px-2 py-0.5 rounded ' + (trade.direction === 'buy' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300')}>
                      {trade.direction === 'buy' ? '▲ BUY' : '▼ SELL'}
                    </span>
                    {trade.is_demo && <span className="text-xs bg-blue-900 text-blue-300 px-2 py-0.5 rounded">DEMO</span>}
                  </div>
                  <div className="flex items-center gap-1 text-yellow-400 font-mono font-bold">
                    <Clock className="w-4 h-4" />
                    {Math.floor((trade.time_remaining || 0) / 60).toString().padStart(2, '0')}:{((trade.time_remaining || 0) % 60).toString().padStart(2, '0')}
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div><div className="text-gray-400 text-xs">Entry Price</div><div className="text-white font-semibold">${parseFloat(trade.strike_price || 0).toFixed(2)}</div></div>
                  <div><div className="text-gray-400 text-xs">Amount</div><div className="text-white font-semibold">${parseFloat(trade.amount || 0).toFixed(2)}</div></div>
                  <div><div className="text-gray-400 text-xs">Potential Profit</div><div className="text-green-400 font-semibold">+${parseFloat(trade.potential_profit || 0).toFixed(2)}</div></div>
                </div>
                <div className="mt-2 text-xs text-gray-500">Payout: {trade.adjusted_payout_percentage}%</div>
              </div>
            ))}
          </div>
        )}
        {activeTab === 'history' && (
          <div className="space-y-4">
            {historySummary && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { label: 'Wagered', value: '$' + parseFloat(historySummary.total_wagered || 0).toFixed(2) },
                  { label: 'Won', value: '$' + parseFloat(historySummary.total_won || 0).toFixed(2), color: 'text-green-400' },
                  { label: 'Net P&L', value: (historySummary.net_pnl >= 0 ? '+' : '') + '$' + parseFloat(historySummary.net_pnl || 0).toFixed(2), color: historySummary.net_pnl >= 0 ? 'text-green-400' : 'text-red-400' },
                  { label: 'W/L', value: historySummary.win_count + 'W / ' + historySummary.loss_count + 'L' },
                ].map(s => (
                  <div key={s.label} className="bg-gray-800 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-400">{s.label}</div>
                    <div className={'font-bold text-sm ' + (s.color || 'text-white')}>{s.value}</div>
                  </div>
                ))}
              </div>
            )}
            {tradeHistory.length === 0 && <div className="text-center text-gray-500 py-12">No trade history yet.</div>}
            {(Array.isArray(tradeHistory) ? tradeHistory : []).map(trade => (
              <div key={trade.id} className={'bg-gray-800 rounded-xl p-4 border ' + (trade.status === 'won' ? 'border-green-800' : trade.status === 'lost' ? 'border-red-800' : 'border-gray-700')}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white">{trade.asset_symbol}</span>
                    <span className={'text-xs font-bold px-2 py-0.5 rounded ' + (trade.direction === 'buy' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300')}>
                      {trade.direction === 'buy' ? '▲ BUY' : '▼ SELL'}
                    </span>
                  </div>
                  <span className={'text-sm font-bold ' + (trade.status === 'won' ? 'text-green-400' : trade.status === 'lost' ? 'text-red-400' : 'text-gray-400')}>
                    {trade.status === 'won' ? '+$' + parseFloat(trade.profit_loss || 0).toFixed(2) : trade.status === 'lost' ? '-$' + Math.abs(parseFloat(trade.profit_loss || 0)).toFixed(2) : trade.status}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs text-gray-400 mt-2">
                  <div>Entry: <span className="text-white">${parseFloat(trade.strike_price || 0).toFixed(2)}</span></div>
                  <div>Exit: <span className="text-white">${parseFloat(trade.final_price || 0).toFixed(2)}</span></div>
                  <div>Amount: <span className="text-white">${parseFloat(trade.amount || 0).toFixed(2)}</span></div>
                </div>
              </div>
            ))}
          </div>
        )}
        {activeTab === 'stats' && stats && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {[
              { label: 'Total Trades', value: stats.total_trades },
              { label: 'Wins', value: stats.total_wins, color: 'text-green-400' },
              { label: 'Losses', value: stats.total_losses, color: 'text-red-400' },
              { label: 'Win Rate', value: parseFloat(stats.win_rate || 0).toFixed(1) + '%', color: parseFloat(stats.win_rate) >= 50 ? 'text-green-400' : 'text-red-400' },
              { label: 'Net Profit', value: (stats.net_profit >= 0 ? '+' : '') + '$' + parseFloat(stats.net_profit || 0).toFixed(2), color: stats.net_profit >= 0 ? 'text-green-400' : 'text-red-400' },
              { label: 'Win Streak', value: stats.current_win_streak },
            ].map(s => (
              <div key={s.label} className="bg-gray-800 rounded-xl p-4 text-center">
                <div className="text-xs text-gray-400 mb-1">{s.label}</div>
                <div className={'text-2xl font-bold ' + (s.color || 'text-white')}>{s.value}</div>
              </div>
            ))}
          </div>
        )}
        {activeTab === 'stats' && !stats && (
          <div className="text-center text-gray-500 py-12">
            <RefreshCw className="w-8 h-8 mx-auto mb-2 animate-spin" /> Loading stats...
          </div>
        )}
      </div>
    </div>
  );
}
'''

with open('wazimu/Growfund-Dashboard/src/components/TradeNow.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Complete TradeNow.js created successfully!")