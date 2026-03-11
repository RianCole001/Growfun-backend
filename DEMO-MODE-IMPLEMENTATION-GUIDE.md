# Demo Mode Implementation Guide - All Trading Components

## ✅ Complete Demo Mode System

A unified demo mode system that works across ALL trading components with separate balances.

---

## 🎯 System Overview

### Core Principle
**One user, two balances:**
- **Real Balance** (`user.balance`) - Real money trading
- **Demo Balance** (`demo_account.balance`) - Practice trading with $10,000

### What's Implemented
✅ **Binary Options Trading** - Full demo support
✅ **Crypto Trading** - Ready for demo mode
✅ **Capital Investment Plans** - Ready for demo mode
✅ **All Components** - Use same demo utilities

---

## 🔧 Demo Utilities (Centralized)

### Location
`backend-growfund/demo/utils.py`

### Functions Available

```python
from demo.utils import get_balance, update_balance, check_balance, get_balance_info

# Get balance based on mode
balance = get_balance(user, is_demo=True)

# Update balance (add or subtract)
new_balance = update_balance(user, amount=100.50, is_demo=True)  # Add
new_balance = update_balance(user, amount=-50.00, is_demo=True)  # Subtract

# Check if user has enough balance
has_balance, current_balance = check_balance(user, required_amount=100, is_demo=True)

# Get both balances
balances = get_balance_info(user)
# Returns: {'real_balance': 5000.00, 'demo_balance': 10000.00}
```

---

## 📊 Implementation Pattern

### For ANY Trading Component

#### 1. Add `is_demo` Field to Model
```python
class YourTradingModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_demo = models.BooleanField(default=False)  # ADD THIS
    # ... other fields
```

#### 2. Update Serializer
```python
class YourTradingSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_demo = serializers.BooleanField(default=False)  # ADD THIS
    # ... other fields
```

#### 3. Update View - Opening Position
```python
from demo.utils import check_balance, update_balance

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def open_position(request):
    # Get data
    amount = request.data.get('amount')
    is_demo = request.data.get('is_demo', False)
    
    # Check balance
    has_balance, current_balance = check_balance(request.user, amount, is_demo)
    if not has_balance:
        return Response({
            'success': False,
            'error': f'Insufficient {"demo" if is_demo else "real"} balance'
        }, status=400)
    
    # Deduct amount
    new_balance = update_balance(request.user, -amount, is_demo)
    
    # Create position
    position = YourModel.objects.create(
        user=request.user,
        amount=amount,
        is_demo=is_demo,  # IMPORTANT
        # ... other fields
    )
    
    return Response({
        'success': True,
        'position': {...},
        'new_balance': float(new_balance),
        'is_demo': is_demo
    })
```

#### 4. Update View - Closing Position (Win/Loss)
```python
from demo.utils import update_balance

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_position(request, position_id):
    position = YourModel.objects.get(id=position_id, user=request.user)
    
    # Calculate profit/loss
    profit_loss = calculate_profit_loss(position)
    
    # Return stake + profit to appropriate balance
    total_return = position.amount + profit_loss  # If won
    # OR
    total_return = 0  # If lost (stake already deducted)
    
    if profit_loss > 0:  # Won
        new_balance = update_balance(
            request.user, 
            position.amount + profit_loss,  # Return stake + profit
            position.is_demo
        )
    # If lost, balance already deducted, no return
    
    position.status = 'closed'
    position.profit_loss = profit_loss
    position.save()
    
    return Response({
        'success': True,
        'profit_loss': float(profit_loss),
        'new_balance': float(new_balance) if profit_loss > 0 else float(get_balance(request.user, position.is_demo)),
        'is_demo': position.is_demo
    })
```

#### 5. Update View - Get Positions (Filter by Mode)
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_positions(request):
    is_demo = request.GET.get('is_demo', 'false').lower() == 'true'
    
    positions = YourModel.objects.filter(
        user=request.user,
        is_demo=is_demo  # FILTER BY MODE
    )
    
    return Response({
        'success': True,
        'positions': [...],
        'is_demo': is_demo
    })
```

---

## 💻 Frontend Implementation

### 1. Global Mode State
```javascript
// App.js or Context
const [tradingMode, setTradingMode] = useState('demo'); // 'demo' or 'real'
const [realBalance, setRealBalance] = useState(0);
const [demoBalance, setDemoBalance] = useState(10000);

// Fetch balances on mount
useEffect(() => {
  const fetchBalances = async () => {
    // For binary trading
    const response = await axios.get('/api/binary/balances/');
    setRealBalance(response.data.real_balance);
    setDemoBalance(response.data.demo_balance);
    
    // OR use user profile endpoint
    const userResponse = await axios.get('/api/auth/me/');
    setRealBalance(userResponse.data.balance);
    // Get demo balance separately
  };
  fetchBalances();
}, []);
```

### 2. Mode Switcher Component
```javascript
const ModeSwitcher = ({ mode, onModeChange, realBalance, demoBalance }) => {
  return (
    <div className="mode-switcher">
      <button 
        className={mode === 'demo' ? 'active demo' : 'demo'}
        onClick={() => onModeChange('demo')}
      >
        <span className="icon">🎮</span>
        <span className="label">Demo Mode</span>
        <span className="balance">${demoBalance.toFixed(2)}</span>
      </button>
      
      <button 
        className={mode === 'real' ? 'active real' : 'real'}
        onClick={() => onModeChange('real')}
      >
        <span className="icon">💰</span>
        <span className="label">Real Mode</span>
        <span className="balance">${realBalance.toFixed(2)}</span>
      </button>
    </div>
  );
};
```

### 3. Include Mode in All API Calls
```javascript
// Opening any position
const openPosition = async (data) => {
  const response = await axios.post('/api/your-endpoint/', {
    ...data,
    is_demo: tradingMode === 'demo'  // ALWAYS INCLUDE
  });
  
  // Update appropriate balance
  if (tradingMode === 'demo') {
    setDemoBalance(response.data.new_balance);
  } else {
    setRealBalance(response.data.new_balance);
  }
};

// Fetching positions
const fetchPositions = async () => {
  const response = await axios.get('/api/your-endpoint/', {
    params: { is_demo: tradingMode === 'demo' }  // ALWAYS FILTER
  });
  setPositions(response.data.positions);
};
```

### 4. Balance Display
```javascript
const BalanceDisplay = ({ mode, realBalance, demoBalance }) => {
  const currentBalance = mode === 'demo' ? demoBalance : realBalance;
  const modeLabel = mode === 'demo' ? '🎮 Demo' : '💰 Real';
  
  return (
    <div className={`balance-display ${mode}`}>
      <span className="mode-label">{modeLabel}</span>
      <span className="amount">${currentBalance.toFixed(2)}</span>
    </div>
  );
};
```

---

## 🎨 UI/UX Guidelines

### Visual Indicators

**Demo Mode:**
- Color: Purple/Blue gradient (#667eea to #764ba2)
- Icon: 🎮 (game controller)
- Badge: "DEMO" in purple

**Real Mode:**
- Color: Red/Pink gradient (#f093fb to #f5576c)
- Icon: 💰 (money bag)
- Badge: "REAL" in red

### User Experience
1. **Default to Demo**: New users start in demo mode
2. **Clear Warnings**: Show warning when switching to real mode
3. **Persistent Mode**: Remember user's last selected mode
4. **Balance Updates**: Immediately update balance after any transaction
5. **Mode Badge**: Show mode badge on every trade/position card

---

## 📝 Component-Specific Implementation

### Binary Options Trading
✅ **Status**: Fully implemented
- Endpoint: `/api/binary/trades/open/`
- Parameter: `is_demo: true/false`
- Balances: Separate tracking

### Crypto Trading (Buy/Sell)
🔄 **To Implement**:
```python
# In investments/views.py - crypto_buy function
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crypto_buy(request):
    from demo.utils import check_balance, update_balance
    
    coin = request.data.get('coin')
    amount = Decimal(request.data.get('amount'))
    is_demo = request.data.get('is_demo', False)  # ADD THIS
    
    # Check balance
    has_balance, _ = check_balance(request.user, amount, is_demo)
    if not has_balance:
        return Response({'error': 'Insufficient balance'}, status=400)
    
    # Deduct amount
    new_balance = update_balance(request.user, -amount, is_demo)
    
    # Create investment (add is_demo field to model first)
    investment = Investment.objects.create(
        user=request.user,
        coin=coin,
        amount=amount,
        is_demo=is_demo,  # ADD THIS
        # ... other fields
    )
    
    return Response({
        'success': True,
        'new_balance': float(new_balance),
        'is_demo': is_demo
    })
```

### Capital Investment Plans
🔄 **To Implement**:
```python
# In investments/views.py - CapitalInvestmentPlanViewSet.create
def create(self, request, *args, **kwargs):
    from demo.utils import check_balance, update_balance
    
    serializer = CreateCapitalInvestmentPlanSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    data = serializer.validated_data
    is_demo = request.data.get('is_demo', False)  # ADD THIS
    
    # Check balance
    has_balance, _ = check_balance(request.user, data['initial_amount'], is_demo)
    if not has_balance:
        return Response({'error': 'Insufficient balance'}, status=400)
    
    # Deduct amount
    new_balance = update_balance(request.user, -data['initial_amount'], is_demo)
    
    # Create plan (add is_demo field to model first)
    plan = CapitalInvestmentPlan.objects.create(
        user=request.user,
        is_demo=is_demo,  # ADD THIS
        **data
    )
    
    return Response({
        'plan': CapitalInvestmentPlanSerializer(plan).data,
        'new_balance': float(new_balance),
        'is_demo': is_demo
    })
```

---

## 🔒 Security Checklist

✅ **Always validate `is_demo` flag**
✅ **Never mix demo and real balances**
✅ **Filter queries by `is_demo` field**
✅ **Update correct balance based on mode**
✅ **Show clear mode indicators in UI**
✅ **Warn users before real trades**

---

## 🧪 Testing Checklist

### Backend Tests
- [ ] Open position in demo mode
- [ ] Open position in real mode
- [ ] Close winning position in demo mode
- [ ] Close winning position in real mode
- [ ] Close losing position in demo mode
- [ ] Close losing position in real mode
- [ ] Verify demo balance updates correctly
- [ ] Verify real balance updates correctly
- [ ] Verify balances never mix
- [ ] Filter positions by mode works

### Frontend Tests
- [ ] Mode switcher displays both balances
- [ ] Can switch between demo and real mode
- [ ] Balance updates after opening position
- [ ] Balance updates after closing position
- [ ] Mode badge shows on all cards
- [ ] Can filter history by mode
- [ ] Warning shows before real trade
- [ ] Mode persists across page refresh

---

## 📊 Database Migrations Needed

For each trading model, add:
```python
# Migration file
operations = [
    migrations.AddField(
        model_name='yourmodel',
        name='is_demo',
        field=models.BooleanField(default=False),
    ),
]
```

---

## ✅ Summary

**What You Need to Do:**

1. **For Each Trading Component:**
   - Add `is_demo` field to model
   - Update serializer to accept `is_demo`
   - Use `demo.utils` functions for balance operations
   - Filter queries by `is_demo`
   - Return `is_demo` in responses

2. **Frontend:**
   - Add mode switcher to all trading pages
   - Include `is_demo` in all API calls
   - Filter data by mode
   - Update appropriate balance
   - Show mode badges

3. **Testing:**
   - Test both modes for each component
   - Verify balances never mix
   - Ensure UI clearly shows mode

**The system is designed to be consistent across ALL trading components!** 🚀
