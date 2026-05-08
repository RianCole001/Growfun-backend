// ============================================
// READY-TO-USE REACT COMPONENTS
// Copy and paste these into your project
// ============================================

import React, { useState, useEffect } from 'react';
import axios from 'axios';

// ============================================
// 1. BALANCE DISPLAY COMPONENT
// ============================================
export const BalanceDisplay = ({ refreshTrigger }) => {
  const [balance, setBalance] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchBalance();
  }, [refreshTrigger]);

  const fetchBalance = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/accounts/profile/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setBalance(response.data.data.balance);
      setError('');
    } catch (err) {
      setError('Failed to fetch balance');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading balance...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="balance-display">
      <h2>Account Balance</h2>
      <div className="balance-amount">${parseFloat(balance).toFixed(2)}</div>
      <button onClick={fetchBalance} className="btn-refresh">Refresh</button>
    </div>
  );
};

// ============================================
// 2. ADMIN BALANCE CREDIT COMPONENT
// ============================================
export const AdminBalanceCredit = ({ userId, onSuccess }) => {
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `http://localhost:8000/api/accounts/admin/users/${userId}/balance/`,
        {
          action: 'credit',
          amount: parseFloat(amount),
          note: note
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setSuccess(`Successfully credited $${amount}`);
      setAmount('');
      setNote('');
      
      if (onSuccess) {
        onSuccess(response.data.data);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to credit balance');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-balance-credit">
      <h3>Credit User Balance</h3>
      
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Amount ($)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Enter amount"
            required
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label>Note (Optional)</label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Enter reason for credit"
            disabled={loading}
            rows="3"
          />
        </div>

        <button 
          type="submit" 
          disabled={loading || !amount}
          className="btn-submit"
        >
          {loading ? 'Processing...' : 'Credit Balance'}
        </button>
      </form>
    </div>
  );
};

// ============================================
// 3. TRANSACTION HISTORY COMPONENT
// ============================================
export const TransactionHistory = ({ refreshTrigger }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTransactions();
  }, [refreshTrigger, filter]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const url = filter === 'all' 
        ? 'http://localhost:8000/api/transactions/'
        : `http://localhost:8000/api/transactions/?type=${filter}`;

      const response = await axios.get(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setTransactions(response.data.results || response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch transactions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getTypeLabel = (type) => {
    const labels = {
      'deposit': 'Deposit',
      'withdrawal': 'Withdrawal',
      'admin_credit': '✓ Admin Credit',
      'admin_debit': '✗ Admin Debit',
      'investment': 'Investment',
      'profit': 'Profit',
      'referral_bonus': 'Referral Bonus'
    };
    return labels[type] || type;
  };

  const getStatusColor = (status) => {
    const colors = {
      'completed': '#28a745',
      'pending': '#ffc107',
      'processing': '#17a2b8',
      'failed': '#dc3545',
      'cancelled': '#6c757d'
    };
    return colors[status] || '#000';
  };

  if (loading) return <div className="loading">Loading transactions...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="transaction-history">
      <h3>Transaction History</h3>

      <div className="filter-buttons">
        <button 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button 
          className={filter === 'admin_credit' ? 'active' : ''}
          onClick={() => setFilter('admin_credit')}
        >
          Admin Credits
        </button>
        <button 
          className={filter === 'deposit' ? 'active' : ''}
          onClick={() => setFilter('deposit')}
        >
          Deposits
        </button>
        <button 
          className={filter === 'withdrawal' ? 'active' : ''}
          onClick={() => setFilter('withdrawal')}
        >
          Withdrawals
        </button>
      </div>

      {transactions.length === 0 ? (
        <p className="no-data">No transactions found</p>
      ) : (
        <table className="transactions-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Date</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((txn) => (
              <tr key={txn.id}>
                <td>
                  <span className="badge">{getTypeLabel(txn.transaction_type)}</span>
                </td>
                <td className="amount">${parseFloat(txn.amount).toFixed(2)}</td>
                <td>
                  <span 
                    className="status"
                    style={{ color: getStatusColor(txn.status) }}
                  >
                    {txn.status}
                  </span>
                </td>
                <td>{new Date(txn.created_at).toLocaleDateString()}</td>
                <td className="description">{txn.description || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

// ============================================
// 4. ADMIN DASHBOARD PAGE
// ============================================
export const AdminDashboard = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedUserId, setSelectedUserId] = useState('');

  const handleCreditSuccess = (data) => {
    setRefreshTrigger(prev => prev + 1);
    alert(`Successfully credited $${data.transaction.amount}`);
  };

  return (
    <div className="admin-dashboard">
      <div className="container">
        <h1>Admin Dashboard - Balance Management</h1>

        <div className="dashboard-grid">
          <div className="card">
            <div className="card-body">
              <h5>Credit User Balance</h5>
              
              <div className="form-group">
                <label>Select User ID</label>
                <input
                  type="number"
                  value={selectedUserId}
                  onChange={(e) => setSelectedUserId(e.target.value)}
                  placeholder="Enter user ID"
                  className="form-input"
                />
              </div>

              {selectedUserId && (
                <AdminBalanceCredit 
                  userId={selectedUserId}
                  onSuccess={handleCreditSuccess}
                />
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <BalanceDisplay refreshTrigger={refreshTrigger} />
            </div>
          </div>
        </div>

        <div className="card" style={{ marginTop: '20px' }}>
          <div className="card-body">
            <TransactionHistory refreshTrigger={refreshTrigger} />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================
// 5. USER DASHBOARD PAGE
// ============================================
export const UserDashboard = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  return (
    <div className="user-dashboard">
      <div className="container">
        <h1>Dashboard</h1>

        <div className="dashboard-grid">
          <div className="card">
            <div className="card-body">
              <BalanceDisplay refreshTrigger={refreshTrigger} />
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <TransactionHistory refreshTrigger={refreshTrigger} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================
// CSS STYLING
// ============================================
export const styles = `
.balance-display {
  text-align: center;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.balance-amount {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 20px 0;
}

.btn-refresh {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-refresh:hover {
  background: rgba(255, 255, 255, 0.3);
}

.admin-balance-credit {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn-submit {
  width: 100%;
  padding: 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-submit:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.btn-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.alert {
  padding: 12px 16px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.alert-success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.transaction-history {
  padding: 20px;
}

.filter-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-buttons button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-buttons button.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.filter-buttons button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.transactions-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.transactions-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.transactions-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
}

.transactions-table td {
  padding: 12px;
  border-bottom: 1px solid #dee2e6;
}

.transactions-table tbody tr:hover {
  background: #f8f9fa;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  background: #e7f3ff;
  color: #0066cc;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.amount {
  font-weight: 600;
  color: #28a745;
}

.status {
  font-weight: 600;
}

.description {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 20px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  background: #f8d7da;
  color: #721c24;
  padding: 12px 16px;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-body {
  padding: 20px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.admin-dashboard,
.user-dashboard {
  background: #f5f5f5;
  min-height: 100vh;
  padding: 20px 0;
}

h1 {
  color: #333;
  margin-bottom: 30px;
}

h3 {
  color: #333;
  margin-bottom: 20px;
}

h5 {
  color: #333;
  margin-bottom: 15px;
}
`;

// ============================================
// USAGE EXAMPLE
// ============================================
/*
import { AdminDashboard, UserDashboard } from './components';

// In your App.jsx or routing:
<Route path="/admin/dashboard" element={<AdminDashboard />} />
<Route path="/dashboard" element={<UserDashboard />} />

// Add the CSS to your global styles:
import { styles } from './components';
// Then add the styles to your CSS file
*/
