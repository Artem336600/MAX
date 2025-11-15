'use client'

interface SleepChartProps {
  data: Array<{ date: string; quality: number; duration: number }>
}

export default function SleepChart({ data }: SleepChartProps) {
  if (!data || data.length === 0) return null

  const maxQuality = 10
  const maxDuration = Math.max(...data.map(d => d.duration), 10)

  return (
    <div className="space-y-6">
      {/* Quality Chart */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Качество сна</h3>
        <div className="flex items-end gap-2 h-32">
          {data.map((record, index) => {
            const height = (record.quality / maxQuality) * 100
            const color = record.quality >= 8 ? 'bg-green-500' : 
                         record.quality >= 6 ? 'bg-yellow-500' : 'bg-red-500'
            
            return (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full bg-gray-100 rounded-t-lg overflow-hidden relative group">
                  <div 
                    className={`${color} transition-all duration-500 ease-out hover:opacity-80`}
                    style={{ height: `${height}%`, minHeight: '4px' }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent" />
                  </div>
                  {/* Tooltip */}
                  <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
                    {record.quality}/10
                  </div>
                </div>
                <span className="text-xs text-gray-600">
                  {new Date(record.date).toLocaleDateString('ru-RU', { weekday: 'short' })}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Duration Chart */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Длительность сна</h3>
        <div className="flex items-end gap-2 h-32">
          {data.map((record, index) => {
            const height = (record.duration / maxDuration) * 100
            const color = record.duration >= 7 ? 'bg-indigo-500' : 
                         record.duration >= 6 ? 'bg-blue-500' : 'bg-purple-500'
            
            return (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full bg-gray-100 rounded-t-lg overflow-hidden relative group">
                  <div 
                    className={`${color} transition-all duration-500 ease-out hover:opacity-80`}
                    style={{ height: `${height}%`, minHeight: '4px' }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent" />
                  </div>
                  {/* Tooltip */}
                  <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
                    {record.duration}ч
                  </div>
                </div>
                <span className="text-xs text-gray-600">
                  {new Date(record.date).toLocaleDateString('ru-RU', { day: 'numeric' })}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
