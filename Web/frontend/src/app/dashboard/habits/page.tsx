'use client'

import { useState, useEffect } from 'react'
import api from '@/lib/api'
import { Target, Plus, TrendingUp, CheckCircle, Circle } from 'lucide-react'

interface Habit {
  id: string
  name: string
  description: string
  frequency: string
  target_count: number
  icon: string
  color: string
  active: boolean
  created_at: string
}

interface HabitStats {
  habit_id: string
  habit_name: string
  current_streak: number
  longest_streak: number
  completion_rate: number
  total_completions: number
}

export default function HabitTrackerPage() {
  const [habits, setHabits] = useState<Habit[]>([])
  const [stats, setStats] = useState<HabitStats[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newHabit, setNewHabit] = useState({
    name: '',
    description: '',
    frequency: 'daily',
    target_count: 1,
    icon: '🎯',
    color: '#3B82F6'
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [habitsRes, statsRes] = await Promise.all([
        api.get('/habits'),
        api.get('/habits/stats/overview')
      ])
      setHabits(habitsRes.data)
      setStats(statsRes.data)
    } catch (error) {
      console.error('Error loading habits:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddHabit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/habits', newHabit)
      setShowAddModal(false)
      setNewHabit({
        name: '',
        description: '',
        frequency: 'daily',
        target_count: 1,
        icon: '🎯',
        color: '#3B82F6'
      })
      loadData()
    } catch (error) {
      console.error('Error adding habit:', error)
      alert('Ошибка при добавлении привычки')
    }
  }

  const handleToggleHabit = async (habitId: string) => {
    try {
      await api.post(`/habits/${habitId}/log`)
      loadData()
    } catch (error) {
      console.error('Error logging habit:', error)
    }
  }

  const getFrequencyText = (frequency: string) => {
    const texts: Record<string, string> = {
      daily: 'Ежедневно',
      weekly: 'Еженедельно',
      monthly: 'Ежемесячно'
    }
    return texts[frequency] || frequency
  }

  const getCompletionColor = (rate: number) => {
    if (rate >= 80) return 'text-green-600 bg-green-50'
    if (rate >= 60) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Target className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">Трекер привычек</h1>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Добавить привычку
          </button>
        </div>
        <p className="text-gray-600">
          Формируйте полезные привычки и отслеживайте прогресс
        </p>
      </div>

      {/* Today's Habits */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Сегодня</h2>
        
        {habits.length === 0 ? (
          <div className="bg-white rounded-xl border p-12 text-center">
            <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Нет привычек
            </h3>
            <p className="text-gray-600 mb-6">
              Создайте свою первую привычку
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Добавить привычку
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {habits.filter(h => h.active).map((habit) => {
              const habitStat = stats.find(s => s.habit_id === habit.id)
              
              return (
                <div
                  key={habit.id}
                  className="bg-white rounded-xl border p-6 hover:shadow-lg transition cursor-pointer"
                  onClick={() => handleToggleHabit(habit.id)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl">{habit.icon}</span>
                      <div>
                        <h3 className="font-semibold text-gray-900">{habit.name}</h3>
                        <p className="text-sm text-gray-600">
                          {getFrequencyText(habit.frequency)}
                        </p>
                      </div>
                    </div>
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>

                  {habit.description && (
                    <p className="text-sm text-gray-600 mb-4">
                      {habit.description}
                    </p>
                  )}

                  {habitStat && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Текущая серия</span>
                        <span className="font-semibold text-gray-900">
                          🔥 {habitStat.current_streak} дней
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Выполнение</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCompletionColor(habitStat.completion_rate)}`}>
                          {habitStat.completion_rate.toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Statistics */}
      {stats.length > 0 && (
        <div className="bg-white rounded-xl border">
          <div className="p-6 border-b">
            <h2 className="text-xl font-bold text-gray-900">Статистика</h2>
          </div>
          <div className="p-6">
            <div className="space-y-6">
              {stats.map((stat) => (
                <div key={stat.habit_id} className="border-b last:border-0 pb-6 last:pb-0">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">{stat.habit_name}</h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCompletionColor(stat.completion_rate)}`}>
                      {stat.completion_rate.toFixed(0)}%
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Текущая серия</div>
                      <div className="text-2xl font-bold text-gray-900">
                        {stat.current_streak}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Лучшая серия</div>
                      <div className="text-2xl font-bold text-gray-900">
                        {stat.longest_streak}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Всего выполнений</div>
                      <div className="text-2xl font-bold text-gray-900">
                        {stat.total_completions}
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${stat.completion_rate}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Новая привычка
            </h2>

            <form onSubmit={handleAddHabit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Название
                </label>
                <input
                  type="text"
                  value={newHabit.name}
                  onChange={(e) => setNewHabit({ ...newHabit, name: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Например: Медитация"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Описание
                </label>
                <textarea
                  value={newHabit.description}
                  onChange={(e) => setNewHabit({ ...newHabit, description: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Зачем эта привычка?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Частота
                </label>
                <select
                  value={newHabit.frequency}
                  onChange={(e) => setNewHabit({ ...newHabit, frequency: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="daily">Ежедневно</option>
                  <option value="weekly">Еженедельно</option>
                  <option value="monthly">Ежемесячно</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Иконка
                </label>
                <div className="grid grid-cols-6 gap-2">
                  {['🎯', '💪', '📚', '🧘', '🏃', '💻', '🎨', '🎵', '🍎', '💧', '😴', '🌟'].map((emoji) => (
                    <button
                      key={emoji}
                      type="button"
                      onClick={() => setNewHabit({ ...newHabit, icon: emoji })}
                      className={`text-2xl p-2 rounded-lg border-2 transition ${
                        newHabit.icon === emoji
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50 transition"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  Создать
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
