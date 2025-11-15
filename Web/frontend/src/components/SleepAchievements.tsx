'use client'

import { Award, Star, Trophy, Target, Zap } from 'lucide-react'

interface Achievement {
  id: string
  title: string
  description: string
  icon: any
  unlocked: boolean
  progress?: number
  total?: number
}

interface SleepAchievementsProps {
  records: Array<{ quality: number; duration: number }>
}

export default function SleepAchievements({ records }: SleepAchievementsProps) {
  // Подсчет достижений
  const goodSleepStreak = () => {
    let streak = 0
    for (const record of records) {
      if (record.quality >= 7) streak++
      else break
    }
    return streak
  }
  
  const totalRecords = records.length
  const avgQuality = records.reduce((sum, r) => sum + r.quality, 0) / (records.length || 1)
  const streak = goodSleepStreak()
  
  const achievements: Achievement[] = [
    {
      id: 'first_week',
      title: 'Первая неделя',
      description: 'Отслеживайте сон 7 дней подряд',
      icon: Star,
      unlocked: totalRecords >= 7,
      progress: Math.min(totalRecords, 7),
      total: 7
    },
    {
      id: 'good_streak',
      title: 'Хороший сон',
      description: '7 дней подряд качественного сна',
      icon: Trophy,
      unlocked: streak >= 7,
      progress: Math.min(streak, 7),
      total: 7
    },
    {
      id: 'early_bird',
      title: 'Ранняя пташка',
      description: 'Засыпайте до 23:00 неделю подряд',
      icon: Zap,
      unlocked: false, // TODO: реализовать проверку
      progress: 0,
      total: 7
    },
    {
      id: 'consistency',
      title: 'Консистентность',
      description: '30 дней трекинга',
      icon: Target,
      unlocked: totalRecords >= 30,
      progress: Math.min(totalRecords, 30),
      total: 30
    },
    {
      id: 'quality_master',
      title: 'Мастер качества',
      description: 'Средний балл 8+ за месяц',
      icon: Award,
      unlocked: totalRecords >= 30 && avgQuality >= 8,
      progress: totalRecords >= 30 ? Math.min(avgQuality, 10) : 0,
      total: 10
    }
  ]
  
  const unlockedCount = achievements.filter(a => a.unlocked).length
  
  return (
    <div className="bg-white rounded-xl border p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900">Достижения</h3>
          <p className="text-sm text-gray-600">
            Разблокировано: {unlockedCount} из {achievements.length}
          </p>
        </div>
        <div className="text-3xl">🏆</div>
      </div>
      
      <div className="space-y-4">
        {achievements.map((achievement) => {
          const Icon = achievement.icon
          const progress = achievement.progress || 0
          const total = achievement.total || 100
          const percentage = (progress / total) * 100
          
          return (
            <div
              key={achievement.id}
              className={`
                relative overflow-hidden rounded-lg border-2 p-4 transition
                ${achievement.unlocked 
                  ? 'border-yellow-400 bg-gradient-to-r from-yellow-50 to-orange-50' 
                  : 'border-gray-200 bg-gray-50'
                }
              `}
            >
              <div className="flex items-start gap-4">
                <div className={`
                  w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0
                  ${achievement.unlocked 
                    ? 'bg-yellow-400 text-white' 
                    : 'bg-gray-200 text-gray-400'
                  }
                `}>
                  <Icon className="w-6 h-6" />
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-gray-900">{achievement.title}</h4>
                    {achievement.unlocked && (
                      <span className="text-xs bg-yellow-400 text-yellow-900 px-2 py-0.5 rounded-full font-medium">
                        Разблокировано!
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{achievement.description}</p>
                  
                  {!achievement.unlocked && achievement.total && (
                    <div>
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                        <span>Прогресс</span>
                        <span>{progress} / {total}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full transition-all duration-500"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              {achievement.unlocked && (
                <div className="absolute top-2 right-2">
                  <div className="w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center animate-bounce">
                    <span className="text-lg">✓</span>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
      
      {/* Overall Progress */}
      <div className="mt-6 pt-6 border-t">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Общий прогресс</span>
          <span className="text-sm font-bold text-indigo-600">
            {Math.round((unlockedCount / achievements.length) * 100)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div 
            className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 h-full transition-all duration-500"
            style={{ width: `${(unlockedCount / achievements.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}
