'use client'

import { useState, useEffect } from 'react'
import api from '@/lib/api'
import { DollarSign, Plus, TrendingUp, TrendingDown, PieChart } from 'lucide-react'

interface Transaction {
  id: string
  type: string
  amount: number
  category: string
  description: string
  date: string
}

interface FinanceStats {
  total_income: number
  total_expenses: number
  balance: number
  categories: Record<string, number>
}

export default function FinanceManagerPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [stats, setStats] = useState<FinanceStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newTransaction, setNewTransaction] = useState({
    type: 'expense',
    amount: 0,
    category: 'Другое',
    description: '',
    date: new Date().toISOString().split('T')[0]
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [transactionsRes, statsRes] = await Promise.all([
        api.get('/finance/transactions'),
        api.get('/finance/stats')
      ])
      setTransactions(transactionsRes.data)
      setStats(statsRes.data)
    } catch (error) {
      console.error('Error loading finance data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddTransaction = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const amount = newTransaction.type === 'expense' 
        ? -Math.abs(newTransaction.amount)
        : Math.abs(newTransaction.amount)
      
      await api.post('/finance/transactions', {
        ...newTransaction,
        amount
      })
      setShowAddModal(false)
      setNewTransaction({
        type: 'expense',
        amount: 0,
        category: 'Другое',
        description: '',
        date: new Date().toISOString().split('T')[0]
      })
      loadData()
    } catch (error) {
      console.error('Error adding transaction:', error)
      alert('Ошибка при добавлении транзакции')
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen"><div className="text-gray-600">Загрузка...</div></div>
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <DollarSign className="w-8 h-8 text-green-600" />
            <h1 className="text-3xl font-bold text-gray-900">Финансы</h1>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Добавить транзакцию
          </button>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl border p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <h3 className="font-semibold text-gray-900">Доходы</h3>
            </div>
            <p className="text-3xl font-bold text-green-600">
              +{stats.total_income.toLocaleString()}₽
            </p>
          </div>

          <div className="bg-white rounded-xl border p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingDown className="w-5 h-5 text-red-600" />
              <h3 className="font-semibold text-gray-900">Расходы</h3>
            </div>
            <p className="text-3xl font-bold text-red-600">
              -{stats.total_expenses.toLocaleString()}₽
            </p>
          </div>

          <div className="bg-white rounded-xl border p-6">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold text-gray-900">Баланс</h3>
            </div>
            <p className={`text-3xl font-bold ${stats.balance >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
              {stats.balance.toLocaleString()}₽
            </p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">Транзакции</h2>
        </div>
        <div className="divide-y">
          {transactions.map((transaction) => (
            <div key={transaction.id} className="p-6 flex items-center justify-between hover:bg-gray-50">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                  transaction.type === 'income' ? 'bg-green-100' : 'bg-red-100'
                }`}>
                  {transaction.type === 'income' ? (
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  ) : (
                    <TrendingDown className="w-6 h-6 text-red-600" />
                  )}
                </div>
                <div>
                  <div className="font-semibold text-gray-900">{transaction.description || transaction.category}</div>
                  <div className="text-sm text-gray-600">
                    {new Date(transaction.date).toLocaleDateString('ru-RU')} • {transaction.category}
                  </div>
                </div>
              </div>
              <div className={`text-xl font-bold ${
                transaction.type === 'income' ? 'text-green-600' : 'text-red-600'
              }`}>
                {transaction.type === 'income' ? '+' : '-'}{Math.abs(transaction.amount).toLocaleString()}₽
              </div>
            </div>
          ))}
        </div>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Новая транзакция</h2>
            <form onSubmit={handleAddTransaction} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Тип</label>
                <select
                  value={newTransaction.type}
                  onChange={(e) => setNewTransaction({ ...newTransaction, type: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  <option value="expense">Расход</option>
                  <option value="income">Доход</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Сумма</label>
                <input
                  type="number"
                  value={newTransaction.amount}
                  onChange={(e) => setNewTransaction({ ...newTransaction, amount: parseFloat(e.target.value) })}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Категория</label>
                <input
                  type="text"
                  value={newTransaction.category}
                  onChange={(e) => setNewTransaction({ ...newTransaction, category: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Описание</label>
                <input
                  type="text"
                  value={newTransaction.description}
                  onChange={(e) => setNewTransaction({ ...newTransaction, description: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setShowAddModal(false)} className="flex-1 px-4 py-2 border rounded-lg">Отмена</button>
                <button type="submit" className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg">Добавить</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
