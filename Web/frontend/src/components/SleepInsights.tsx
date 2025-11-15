'use client'

import { Brain, Zap, Target, TrendingUp, AlertCircle } from 'lucide-react'

interface SleepInsightsProps {
  stats: {
    avg_duration: number
    avg_quality: number
    best_quality: number
    worst_quality: number
    total_records: number
  }
  records: Array<{ quality: number; duration: number; sleep_time: string }>
}

export default function SleepInsights({ stats, records }: SleepInsightsProps) {
  // Анализ паттернов
  const getBestDay = () => {
    if (!records.length) return null
    const sorted = [...records].sort((a, b) => b.quality - a.quality)
    const best = sorted[0]
    const date = new Date(best.sleep_time)
    return date.toLocaleDateString('ru-RU', { weekday: 'long' })
  }
  
  const getOptimalTime = () => {
    if (!records.length) return '22:30 - 06:30'
    const avgSleepHour = records.reduce((sum, r) => {
      const hour = new Date(r.sleep_time).getHours()
      return sum + hour
    }, 0) / records.length
    
    const sleepTime = Math.floor(avgSleepHour)
    const wakeTime = (sleepTime + Math.floor(stats.avg_duration)) % 24
    return `${sleepTime}:00 - ${wakeTime}:00`
  }
  
  const getImprovement = () => {
    if (records.length < 7) return 0
    const recent = records.slice(0, 7)
    const older = records.slice(7, 14)
    if (!older.length) return 0
    
    const recentAvg = recent.reduce((sum, r) => sum + r.quality, 0) / recent.length
    const olderAvg = older.reduce((sum, r) => sum + r.quality, 0) / older.length
    
    return Math.round(((recentAvg - olderAvg) / olderAvg) * 100)
  }
  
  const improvement = getImprovement()
  const bestDay = getBestDay()
  const optimalTime = getOptimalTime()
  
  const insights = [
    {
      icon: Brain,
      color: 'text-purple-600 bg-purple-50',
      title: 'Лучший день',
      description: bestDay ? `Вы спите лучше всего в ${bestDay}` : 'Недостаточно данных',
      show: !!bestDay
    },
    {
      icon: Zap,
      color: 'text-blue-600 bg-blue-50',
      title: 'Оптимальное время',
      description: `Рекомендуем спать ${optimalTime}`,
      show: true
    },
    {
      icon: TrendingUp,
      color: improvement > 0 ? 'text-green-600 bg-green-50' : 'text-orange-600 bg-orange-50',
      title: 'Прогресс',
      description: improvement > 0 
        ? `Качество сна улучшилось на ${improvement}%` 
        : improvement < 0
        ? `Качество сна снизилось на ${Math.abs(improvement)}%`
        : 'Качество сна стабильное',
      show: records.length >= 7
    },
    {
      icon: Target,
      color: 'text-indigo-600 bg-indigo-50',
      title: 'Рекомендация',
      description: stats.avg_duration < 7 
        ? 'Увеличьте длительность сна на 30-60 минут'
        : stats.avg_duration > 9
        ? 'Попробуйте сократить сон до 7-9 часов'
        : 'Отличная длительность сна!',
      show: true
    },
    {
      icon: AlertCircle,
      color: 'text-red-600 bg-red-50',
      title: 'Внимание',
      description: 'Низкое качество сна последние 3 дня',
      show: records.slice(0, 3).every(r => r.quality < 6)
    }
  ]
  
  return (
    <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border-2 border-indigo-100 p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center">
          <Brain className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-gray-900">Персональные инсайты</h3>
          <p className="text-sm text-gray-600">На основе анализа ваших данных</p>
        </div>
      </div>
      
      <div className="space-y-3">
        {insights.filter(i => i.show).map((insight, index) => {
          const Icon = insight.icon
          return (
            <div 
              key={index}
              className="bg-white rounded-lg p-4 flex items-start gap-3 hover:shadow-md transition"
            >
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${insight.color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-1">{insight.title}</h4>
                <p className="text-sm text-gray-600">{insight.description}</p>
              </div>
            </div>
          )
        })}
      </div>
      
      {/* Quick Tips */}
      <div className="mt-6 bg-white rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-3">💡 Быстрые советы</h4>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="text-indigo-600 mt-0.5">•</span>
            <span>Ложитесь спать и просыпайтесь в одно время</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-indigo-600 mt-0.5">•</span>
            <span>Избегайте экранов за час до сна</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-indigo-600 mt-0.5">•</span>
            <span>Создайте комфортную температуру в спальне (18-20°C)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-indigo-600 mt-0.5">•</span>
            <span>Избегайте кофеина после 14:00</span>
          </li>
        </ul>
      </div>
    </div>
  )
}
