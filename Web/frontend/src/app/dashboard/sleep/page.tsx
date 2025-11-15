'use client'

import { useState, useEffect } from 'react'
import api from '@/lib/api'
import { 
  Moon, Plus, TrendingUp, Calendar, Clock, 
  Activity, Award, AlertCircle, CheckCircle,
  BarChart3, Zap, Brain, Heart, Target, Star
} from 'lucide-react'

interface SleepRecord {
  id: string
  quality: number
  duration: number
  sleep_time: string
  wake_time: string
  mood: string
  notes: string
  created_at: string
}

interface SleepStats {
  avg_duration: number
  avg_quality: number
  total_records: number
  best_quality: number
  worst_quality: number
}

export default function SleepTrackerPage() {
  const [records, setRecords] = useState<SleepRecord[]>([])
  const [stats, setStats] = useState<SleepStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newRecord, setNewRecord] = useState({
    quality: 5,
    duration: 8,
    sleep_time: '',
    wake_time: '',
    mood: 'good',
    notes: ''
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [recordsRes, statsRes] = await Promise.all([
        api.get('/sleep/records'),
        api.get('/sleep/stats')
      ])
      setRecords(recordsRes.data)
      setStats(statsRes.data)
    } catch (error) {
      console.error('Error loading sleep data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddRecord = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/sleep/records', newRecord)
      setShowAddModal(false)
      setNewRecord({
        quality: 5,
        duration: 8,
        sleep_time: '',
        wake_time: '',
        mood: 'good',
        notes: ''
      })
      loadData()
    } catch (error) {
      console.error('Error adding record:', error)
      alert('Ошибка при добавлении записи')
    }
  }

  const getQualityColor = (quality: number) => {
    if (quality >= 8) return 'text-green-600 bg-green-50'
    if (quality >= 6) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getMoodEmoji = (mood: string) => {
    const moods: Record<string, string> = {
      great: '😄',
      good: '🙂',
      normal: '😐',
      bad: '😔',
      terrible: '😫'
    }
    return moods[mood] || '😐'
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
            <Moon className="w-8 h-8 text-indigo-600" />
            <h1 className="text-3xl font-bold text-gray-900">Трекер сна</h1>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Добавить запись
          </button>
        </div>
        <p className="text-gray-600">
          Отслеживайте качество сна и улучшайте свой режим
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl border p-6">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-5 h-5 text-indigo-600" />
              <h3 className="font-semibold text-gray-900">Средняя длительность</h3>
            </div>
            <p className="text-3xl font-bold text-indigo-600">
              {stats.avg_duration.toFixed(1)}ч
            </p>
          </div>

          <div className="bg-white rounded-xl border p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <h3 className="font-semibold text-gray-900">Среднее качество</h3>
            </div>
            <p className="text-3xl font-bold text-green-600">
              {stats.avg_quality.toFixed(1)}/10
            </p>
          </div>

          <div className="bg-white rounded-xl border p-6">
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold text-gray-900">Всего записей</h3>
            </div>
            <p className="text-3xl font-bold text-blue-600">
              {stats.total_records}
            </p>
          </div>

          <div className="bg-white rounded-xl border p-6">
            <div className="flex items-center gap-3 mb-2">
              <Moon className="w-5 h-5 text-purple-600" />
              <h3 className="font-semibold text-gray-900">Лучшее качество</h3>
            </div>
            <p className="text-3xl font-bold text-purple-600">
              {stats.best_quality}/10
            </p>
          </div>
        </div>
      )}

      {/* Records List */}
      <div className="bg-white rounded-xl border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">История сна</h2>
        </div>

        {records.length === 0 ? (
          <div className="p-12 text-center">
            <Moon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Нет записей
            </h3>
            <p className="text-gray-600 mb-6">
              Начните отслеживать свой сон
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
            >
              Добавить первую запись
            </button>
          </div>
        ) : (
          <div className="divide-y">
            {records.map((record) => (
              <div key={record.id} className="p-6 hover:bg-gray-50 transition">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <span className="text-2xl">{getMoodEmoji(record.mood)}</span>
                      <div>
                        <div className="font-semibold text-gray-900">
                          {new Date(record.sleep_time).toLocaleDateString('ru-RU', {
                            day: 'numeric',
                            month: 'long',
                            year: 'numeric'
                          })}
                        </div>
                        <div className="text-sm text-gray-600">
                          {new Date(record.sleep_time).toLocaleTimeString('ru-RU', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })} - {new Date(record.wake_time).toLocaleTimeString('ru-RU', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-6">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-600">
                          {record.duration}ч
                        </span>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-sm font-medium ${getQualityColor(record.quality)}`}>
                        Качество: {record.quality}/10
                      </div>
                    </div>

                    {record.notes && (
                      <p className="mt-3 text-sm text-gray-600">
                        {record.notes}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Добавить запись о сне
            </h2>

            <form onSubmit={handleAddRecord} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Время сна
                </label>
                <input
                  type="datetime-local"
                  value={newRecord.sleep_time}
                  onChange={(e) => setNewRecord({ ...newRecord, sleep_time: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Время пробуждения
                </label>
                <input
                  type="datetime-local"
                  value={newRecord.wake_time}
                  onChange={(e) => setNewRecord({ ...newRecord, wake_time: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Качество сна: {newRecord.quality}/10
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={newRecord.quality}
                  onChange={(e) => setNewRecord({ ...newRecord, quality: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Настроение
                </label>
                <select
                  value={newRecord.mood}
                  onChange={(e) => setNewRecord({ ...newRecord, mood: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="great">😄 Отлично</option>
                  <option value="good">🙂 Хорошо</option>
                  <option value="normal">😐 Нормально</option>
                  <option value="bad">😔 Плохо</option>
                  <option value="terrible">😫 Ужасно</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Заметки (опционально)
                </label>
                <textarea
                  value={newRecord.notes}
                  onChange={(e) => setNewRecord({ ...newRecord, notes: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                  rows={3}
                  placeholder="Как прошла ночь?"
                />
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
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                >
                  Добавить
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
