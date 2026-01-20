import React, { useState, useEffect } from 'react';
import { PlusCircle, TrendingUp, TrendingDown, DollarSign, Filter, Download, Upload, RefreshCw, Server, AlertCircle, LogOut, User, Lock } from 'lucide-react';
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { supabase } from './supabaseClient';
import API_URL from './config';

const API_BASE_URL = API_URL;

const CashFlowApp = () => {
  // Supabase Auth state
  const [user, setUser] = useState(null);
  const [authView, setAuthView] = useState('sign_in');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [username, setUsername] = useState('');
  const [businessName, setBusinessName] = useState('');
  const [error, setError] = useState('');

  // App state
  const [transactions, setTransactions] = useState([]);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [filter, setFilter] = useState('all');
  const [dateRange, setDateRange] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  const [newTransaction, setNewTransaction] = useState({
    type: 'income',
    amount: '',
    category: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    payment_method: 'Cash',
    currency: 'USD'
  });

  const currencies = {
    USD: { symbol: '$', name: 'US Dollar', rate: 1 },
    EUR: { symbol: '€', name: 'Euro', rate: 0.92 },
    GBP: { symbol: '£', name: 'British Pound', rate: 0.79 },
    JPY: { symbol: '¥', name: 'Japanese Yen', rate: 149.50 },
    INR: { symbol: '₹', name: 'Indian Rupee', rate: 83.20 },
    AUD: { symbol: 'A$', name: 'Australian Dollar', rate: 1.52 },
    CAD: { symbol: 'C$', name: 'Canadian Dollar', rate: 1.35 },
    CHF: { symbol: 'CHF', name: 'Swiss Franc', rate: 0.88 },
    CNY: { symbol: '¥', name: 'Chinese Yuan', rate: 7.24 },
    AED: { symbol: 'د.إ', name: 'UAE Dirham', rate: 3.67 },
  };

  const categories = {
    income: ['Salary', 'Business', 'Investment', 'Freelance', 'Other'],
    expense: ['Food', 'Transport', 'Utilities', 'Rent', 'Entertainment', 'Shopping', 'Healthcare', 'Other']
  };

  const paymentMethods = ['Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 'UPI', 'Other'];

  // Supabase Auth: check for user on mount and on auth state change
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  // Fetch transactions when user logs in
  useEffect(() => {
    if (user) {
      fetchTransactions();
    }
  }, [user]);

  // Filter transactions whenever dependencies change
  useEffect(() => {
    filterTransactions();
  }, [transactions, filter, dateRange, searchTerm]);

  // Backend health check
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      setError(error.message);
    }
    setLoading(false);
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!username.trim()) {
      setError('Username is required');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    
    setLoading(true);
    const { data, error } = await supabase.auth.signUp({ email, password });
    if (error) {
      setError(error.message);
    } else {
      if (data.user) {
        await supabase
          .from('profiles')
          .insert([
            {
              user_id: data.user.id,
              username,
              business_name: businessName || null,
            },
          ]);
      }
      alert('Account created! Please check your email to confirm.');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setUsername('');
      setBusinessName('');
      setAuthView('sign_in');
    }
    setLoading(false);
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setTransactions([]);
    setFilteredTransactions([]);
  };

  const checkBackendConnection = async () => {
    setBackendStatus('checking');
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        setBackendStatus('connected');
      } else {
        setBackendStatus('disconnected');
      }
    } catch (err) {
      setBackendStatus('disconnected');
    }
  };

  const fetchTransactions = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get Supabase session token
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`${API_BASE_URL}/transactions?limit=1000`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTransactions(data);
    } catch (err) {
      setError(`Failed to fetch transactions: ${err.message}`);
    }
    setLoading(false);
  };

  const filterTransactions = () => {
    let filtered = [...transactions];
    if (filter !== 'all') {
      filtered = filtered.filter(t => t.type === filter);
    }
    if (searchTerm) {
      filtered = filtered.filter(t =>
        (t.description && t.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (t.category && t.category.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    if (dateRange !== 'all') {
      const now = new Date();
      filtered = filtered.filter(t => {
        const transDate = new Date(t.date);
        const diffDays = Math.floor((now - transDate) / (1000 * 60 * 60 * 24));
        if (dateRange === '7days') return diffDays <= 7;
        if (dateRange === '30days') return diffDays <= 30;
        if (dateRange === '90days') return diffDays <= 90;
        return true;
      });
    }
    setFilteredTransactions(filtered.sort((a, b) => new Date(b.date) - new Date(a.date)));
  };

  const addTransaction = async () => {
    if (!newTransaction.amount || !newTransaction.category) {
      alert('Please fill in Amount and Category');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // Get Supabase session token
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`${API_BASE_URL}/transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({
          type: newTransaction.type,
          amount: parseFloat(newTransaction.amount),
          category: newTransaction.category,
          description: newTransaction.description || '',
          date: newTransaction.date,
          payment_method: newTransaction.payment_method,
          currency: newTransaction.currency
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add transaction');
      }
      await fetchTransactions();
      setNewTransaction({
        type: 'income',
        amount: '',
        category: '',
        description: '',
        date: new Date().toISOString().split('T')[0],
        payment_method: 'Cash',
        currency: selectedCurrency
      });
      setShowAddModal(false);
      alert('Transaction added successfully!');
    } catch (err) {
      setError(`Error adding transaction: ${err.message}`);
      alert(`Error: ${err.message}`);
    }
    setLoading(false);
  };

  const deleteTransaction = async (id) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) return;
    setLoading(true);
    try {
      // Get Supabase session token
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`${API_BASE_URL}/transactions/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
        }
      });
      if (!response.ok) {
        throw new Error('Failed to delete transaction');
      }
      await fetchTransactions();
      alert('Transaction deleted successfully!');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
    setLoading(false);
  };

  const exportData = (format) => {
    if (filteredTransactions.length === 0) {
      alert('No transactions to export');
      return;
    }

    const filename = `transactions_${new Date().toISOString().split('T')[0]}`;

    if (format === 'csv') {
      const headers = ['Date', 'Type', 'Category', 'Amount', 'Currency', 'Payment Method', 'Description'];
      const csvData = filteredTransactions.map(t => [
        t.date, t.type, t.category, t.amount, t.currency, t.payment_method, t.description || ''
      ]);
      const csvContent = [
        headers.join(','),
        ...csvData.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${filename}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } else if (format === 'excel') {
      // Create Excel-compatible HTML table
      const headers = ['Date', 'Type', 'Category', 'Amount', 'Currency', 'Payment Method', 'Description'];
      let excelContent = '<table><thead><tr>';
      headers.forEach(h => excelContent += `<th>${h}</th>`);
      excelContent += '</tr></thead><tbody>';
      filteredTransactions.forEach(t => {
        excelContent += `<tr>
          <td>${t.date}</td>
          <td>${t.type}</td>
          <td>${t.category}</td>
          <td>${t.amount}</td>
          <td>${t.currency}</td>
          <td>${t.payment_method}</td>
          <td>${t.description || ''}</td>
        </tr>`;
      });
      excelContent += '</tbody></table>';
      const blob = new Blob([excelContent], { type: 'application/vnd.ms-excel' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${filename}.xls`;
      a.click();
      window.URL.revokeObjectURL(url);
    } else if (format === 'json') {
      const jsonContent = JSON.stringify(filteredTransactions, null, 2);
      const blob = new Blob([jsonContent], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${filename}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
    }
    alert(`Transactions exported successfully as ${format.toUpperCase()}!`);
  };

  const importData = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    const fileExtension = file.name.split('.').pop().toLowerCase();
    const reader = new FileReader();

    reader.onload = async (e) => {
      try {
        let transactions = [];
        const text = e.target.result;

        if (fileExtension === 'json') {
          transactions = JSON.parse(text);
        } else if (fileExtension === 'csv' || fileExtension === 'xls' || fileExtension === 'xlsx') {
          const lines = text.split('\n');
          for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim() === '') continue;
            const values = lines[i].match(/"([^"]*)"|([^,]+)/g)?.map(v => v.replace(/^"|"$/g, '')) || [];
            if (values.length >= 7) {
              transactions.push({
                date: values[0],
                type: values[1],
                category: values[2],
                amount: parseFloat(values[3]),
                currency: values[4],
                payment_method: values[5],
                description: values[6]
              });
            }
          }
        }

        setLoading(true);
        // Get Supabase session token
        const { data: { session } } = await supabase.auth.getSession();
        
        for (const transaction of transactions) {
          await fetch(`${API_BASE_URL}/transactions`, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${session?.access_token}`,
            },
            body: JSON.stringify(transaction)
          });
        }
        await fetchTransactions();
        alert(`Successfully imported ${transactions.length} transactions!`);
        event.target.value = '';
      } catch (err) {
        alert(`Import failed: ${err.message}`);
      }
      setLoading(false);
    };
    reader.readAsText(file);
  };

  const formatCurrency = (amount) => {
    const currencyInfo = currencies[selectedCurrency] || currencies.USD;
    return `${currencyInfo.symbol}${parseFloat(amount).toFixed(2)}`;
  };

  const getTotals = () => {
    const income = filteredTransactions
      .filter(t => t.type === 'income')
      .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const expenses = filteredTransactions
      .filter(t => t.type === 'expense')
      .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    return { income, expenses, balance: income - expenses };
  };

  const getCategoryData = () => {
    const categoryTotals = {};
    filteredTransactions
      .filter(t => t.type === 'expense')
      .forEach(t => {
        categoryTotals[t.category] = (categoryTotals[t.category] || 0) + parseFloat(t.amount);
      });
    return Object.entries(categoryTotals).map(([name, value]) => ({
      name,
      value: parseFloat(value.toFixed(2))
    }));
  };

  const getChartData = () => {
    const last30Days = [];
    const now = new Date();
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const dayTransactions = transactions.filter(t => t.date === dateStr);
      const income = dayTransactions
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + parseFloat(t.amount), 0);
      const expenses = dayTransactions
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + parseFloat(t.amount), 0);
      last30Days.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        income: parseFloat(income.toFixed(2)),
        expenses: parseFloat(expenses.toFixed(2)),
        net: parseFloat((income - expenses).toFixed(2))
      });
    }
    return last30Days;
  };

  const totals = getTotals();
  const chartData = getChartData();
  const categoryData = getCategoryData();
  const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

  // Auth UI
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          {backendStatus === 'disconnected' && (
            <div className="mb-4 p-4 rounded-lg bg-red-100 border-2 border-red-500">
              <div className="flex items-center gap-3">
                <Server size={24} className="text-red-600" />
                <div>
                  <p className="font-semibold">Backend Disconnected</p>
                  <p className="text-sm text-gray-600">Start your server: python main.py</p>
                </div>
              </div>
            </div>
          )}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-gray-800 mb-2">CashFlow Manager</h1>
              <p className="text-gray-600">Track your finances with ease</p>
            </div>
            {authView === 'sign_in' ? (
              <form onSubmit={handleSignIn} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div className="flex gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setAuthView('sign_up')}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                  >
                    Create Account
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition disabled:opacity-50"
                  >
                    {loading ? 'Logging in...' : 'Login'}
                  </button>
                </div>
                {error && <p className="text-red-600 mt-2">{error}</p>}
              </form>
            ) : (
              <form onSubmit={handleSignUp} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Username *</label>
                  <input
                    type="text"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                    placeholder="Choose a username"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Password (min 6 chars) *</label>
                  <input
                    type="password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="Enter password"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password *</label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter password"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Business Name (Optional)</label>
                  <input
                    type="text"
                    value={businessName}
                    onChange={e => setBusinessName(e.target.value)}
                    placeholder="Your business name (optional)"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  />
                </div>
                <div className="flex gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => {
                      setAuthView('sign_in');
                      setUsername('');
                      setBusinessName('');
                      setConfirmPassword('');
                      setError('');
                    }}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                  >
                    Back to Login
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Register'}
                  </button>
                </div>
                {error && <p className="text-red-600 mt-2">{error}</p>}
              </form>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Main app (authenticated)
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 mb-2">CashFlow Manager</h1>
              <p className="text-gray-600">Welcome back, {user.email}!</p>
            </div>
            <div className="flex gap-2">
              <div className="relative">
                <label className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition cursor-pointer">
                  <Upload size={20} />
                  Import
                  <input type="file" accept=".csv,.xlsx,.xls,.json" onChange={importData} className="hidden" />
                </label>
              </div>
              <div className="relative group">
                <button
                  className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
                >
                  <Download size={20} />
                  Export
                </button>
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 hidden group-hover:block z-10">
                  <button
                    onClick={() => exportData('csv')}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 rounded-t-lg"
                  >
                    Export as CSV
                  </button>
                  <button
                    onClick={() => exportData('excel')}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    Export as Excel
                  </button>
                  <button
                    onClick={() => exportData('json')}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 rounded-b-lg"
                  >
                    Export as JSON
                  </button>
                </div>
              </div>
              <button
                onClick={() => setShowAddModal(true)}
                className="flex items-center gap-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition shadow-lg"
              >
                <PlusCircle size={20} />
                Add Transaction
              </button>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl border-2 border-green-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-green-600 font-semibold">Total Income</span>
                <TrendingUp className="text-green-600" size={24} />
              </div>
              <p className="text-3xl font-bold text-green-700">{formatCurrency(totals.income)}</p>
            </div>
            <div className="bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-xl border-2 border-red-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-red-600 font-semibold">Total Expenses</span>
                <TrendingDown className="text-red-600" size={24} />
              </div>
              <p className="text-3xl font-bold text-red-700">{formatCurrency(totals.expenses)}</p>
            </div>
            <div className={`bg-gradient-to-br ${totals.balance >= 0 ? 'from-blue-50 to-blue-100 border-blue-200' : 'from-orange-50 to-orange-100 border-orange-200'} p-6 rounded-xl border-2`}>
              <div className="flex items-center justify-between mb-2">
                <span className={`${totals.balance >= 0 ? 'text-blue-600' : 'text-orange-600'} font-semibold`}>Net Balance</span>
                <DollarSign className={totals.balance >= 0 ? 'text-blue-600' : 'text-orange-600'} size={24} />
              </div>
              <p className={`text-3xl font-bold ${totals.balance >= 0 ? 'text-blue-700' : 'text-orange-700'}`}>{formatCurrency(totals.balance)}</p>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="bg-gray-50 p-6 rounded-xl">
              <h3 className="text-xl font-semibold mb-4">30-Day Trend</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="income" stroke="#10b981" strokeWidth={2} />
                  <Line type="monotone" dataKey="expenses" stroke="#ef4444" strokeWidth={2} />
                  <Line type="monotone" dataKey="net" stroke="#3b82f6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-gray-50 p-6 rounded-xl">
              <h3 className="text-xl font-semibold mb-4">Expenses by Category</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <div className="flex items-center gap-2">
              <Filter size={20} className="text-gray-600" />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Types</option>
                <option value="income">Income Only</option>
                <option value="expense">Expenses Only</option>
              </select>
            </div>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Time</option>
              <option value="7days">Last 7 Days</option>
              <option value="30days">Last 30 Days</option>
              <option value="90days">Last 90 Days</option>
            </select>
            <input
              type="text"
              placeholder="Search transactions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <select
              value={selectedCurrency}
              onChange={(e) => setSelectedCurrency(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {Object.entries(currencies).map(([code, info]) => (
                <option key={code} value={code}>{code} - {info.name}</option>
              ))}
            </select>
          </div>

          {/* Transactions List */}
          <div>
            <h2 className="text-2xl font-bold mb-4">Recent Transactions</h2>
            {loading && <p className="text-center text-gray-600">Loading...</p>}
            {!loading && filteredTransactions.length === 0 && (
              <p className="text-center text-gray-600 py-8">No transactions found. Add your first transaction!</p>
            )}
            <div className="space-y-3">
              {filteredTransactions.map((transaction) => (
                <div
                  key={transaction.id}
                  className={`p-4 rounded-lg border-2 ${transaction.type === 'income' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${transaction.type === 'income' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
                          {transaction.category}
                        </span>
                        <span className="text-gray-600 text-sm">{transaction.payment_method}</span>
                        <span className="text-gray-500 text-sm">{new Date(transaction.date).toLocaleDateString()}</span>
                      </div>
                      {transaction.description && (
                        <p className="text-gray-700">{transaction.description}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`text-2xl font-bold ${transaction.type === 'income' ? 'text-green-700' : 'text-red-700'}`}>
                        {transaction.type === 'income' ? '+' : '-'}{formatCurrency(transaction.amount)}
                      </span>
                      <button
                        onClick={() => deleteTransaction(transaction.id)}
                        className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Add Transaction Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold mb-6">Add New Transaction</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                  <select
                    value={newTransaction.type}
                    onChange={(e) => setNewTransaction({ ...newTransaction, type: e.target.value, category: '' })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Amount *</label>
                  <input
                    type="number"
                    value={newTransaction.amount}
                    onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                    step="0.01"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category *</label>
                  <select
                    value={newTransaction.category}
                    onChange={(e) => setNewTransaction({ ...newTransaction, category: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select category</option>
                    {categories[newTransaction.type].map((cat) => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Payment Method</label>
                  <select
                    value={newTransaction.payment_method}
                    onChange={(e) => setNewTransaction({ ...newTransaction, payment_method: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {paymentMethods.map((method) => (
                      <option key={method} value={method}>{method}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                  <input
                    type="date"
                    value={newTransaction.date}
                    onChange={(e) => setNewTransaction({ ...newTransaction, date: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
                  <select
                    value={newTransaction.currency}
                    onChange={(e) => setNewTransaction({ ...newTransaction, currency: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {Object.entries(currencies).map(([code, info]) => (
                      <option key={code} value={code}>{code} - {info.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={newTransaction.description}
                    onChange={(e) => setNewTransaction({ ...newTransaction, description: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    rows="3"
                    placeholder="Optional description..."
                  />
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={addTransaction}
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition disabled:opacity-50"
                >
                  {loading ? 'Adding...' : 'Add Transaction'}
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Logout Button at Bottom */}
        <div className="mt-6 flex justify-center">
          <button
            onClick={handleSignOut}
            className="flex items-center gap-2 px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition shadow-lg"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};

export default CashFlowApp;