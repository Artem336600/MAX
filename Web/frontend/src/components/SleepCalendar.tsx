'use client'

interface SleepCalendarProps {
  records: Array<{ date: string; quality: number }>
}

export default function SleepCalendar({ records }: SleepCalendarProps) {
  const today = new Date()
  const currentMonth = today.getMonth()
  const currentYear = today.getFullYear()
  
  // Получить дни месяца
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate()
  const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay()
  
  // Создать карту качества сна по датам
  const qualityMap = new Map(
    records.map(r => [
      new Date(r.date).toDateString(),
      r.quality
    ])
  )
  
  const getQualityColor = (quality: number | undefined) => {
    if (!quality) return 'bg-gray-100'
    if (quality >= 8) return 'bg-green-500'
    if (quality >= 6) return 'bg-yellow-500'
    return 'bg-red-500'
  }
  
  const days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
  const monthName = today.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
  
  return (
    <div className="bg-white rounded-xl border p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">{monthName}</h3>
      
      {/* Days of week */}
      <div className="grid grid-cols-7 gap-2 mb-2">
        {days.map(day => (
          <div key={day} className="text-center text-xs font-medium text-gray-600">
            {day}
          </div>
        ))}
      </div>
      
      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-2">
        {/* Empty cells for days before month starts */}
        {Array.from({ length: (firstDayOfMonth + 6) % 7 }).map((_, i) => (
          <div key={`empty-${i}`} />
        ))}
        
        {/* Days of month */}
        {Array.from({ length: daysInMonth }).map((_, i) => {
          const day = i + 1
          const date = new Date(currentYear, currentMonth, day)
          const dateStr = date.toDateString()
          const quality = qualityMap.get(dateStr)
          const isToday = date.toDateString() === today.toDateString()
          
          return (
            <div
              key={day}
              className={`
                aspect-square rounded-lg flex items-center justify-center text-sm
                ${getQualityColor(quality)}
                ${quality ? 'text-white font-semibold' : 'text-gray-400'}
                ${isToday ? 'ring-2 ring-indigo-600 ring-offset-2' : ''}
                transition hover:scale-110 cursor-pointer group relative
              `}
            >
              {day}
              {quality && (
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap z-10">
                  Качество: {quality}/10
                </div>
              )}
            </div>
          )
        })}
      </div>
      
      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-green-500" />
          <span className="text-gray-600">Отлично (8+)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-yellow-500" />
          <span className="text-gray-600">Хорошо (6-8)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-red-500" />
          <span className="text-gray-600">Плохо (&lt;6)</span>
        </div>
      </div>
    </div>
  )
}
