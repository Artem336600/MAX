'use client'

import { useState, useEffect } from 'react'
import api from '@/lib/api'
import { Calendar, Plus, X, ChevronLeft, ChevronRight } from 'lucide-react'

interface Event {
  id: string
  title: string
  description?: string
  start_time: string
  end_time?: string
  all_day: boolean
  color: string
}

export default function CalendarPage() {
  const [events, setEvents] = useState<Event[]>([])
  const [showModal, setShowModal] = useState(false)
  const [loading, setLoading] = useState(true)
  const [currentDate, setCurrentDate] = useState(new Date())
  const [view, setView] = useState<'month' | 'list'>('month')
  
  // Form state
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [color, setColor] = useState('#3B82F6')

  useEffect(() => {
    loadEvents()
  }, [])

  const loadEvents = async () => {
    try {
      const response = await api.get('/calendar/events')
      setEvents(response.data)
    } catch (error) {
      console.error('Error loading events:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateEvent = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      await api.post('/calendar/events', {
        title,
        description,
        start_time: new Date(startTime).toISOString(),
        end_time: endTime ? new Date(endTime).toISOString() : null,
        color
      })
      
      // Reset form
      setTitle('')
      setDescription('')
      setStartTime('')
      setEndTime('')
      setColor('#3B82F6')
      setShowModal(false)
      
      // Reload events
      loadEvents()
    } catch (error) {
      console.error('Error creating event:', error)
    }
  }

  const handleDeleteEvent = async (id: string) => {
    if (!confirm('Удалить событие?')) return
    
    try {
      await api.delete(`/calendar/events/${id}`)
      loadEvents()
    } catch (error) {
      console.error('Error deleting event:', error)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Получить дни месяца для календарной сетки
  const getCalendarDays = () => {
    const year = currentDate.getFullYear()
    const month = currentDate.getMonth()
    
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    
    const startDay = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1
    const daysInMonth = lastDay.getDate()
    
    const days: (Date | null)[] = []
    
    // Пустые ячейки в начале
    for (let i = 0; i < startDay; i++) {
      days.push(null)
    }
    
    // Дни месяца
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i))
    }
    
    return days
  }

  // Получить события для конкретного дня
  const getEventsForDay = (date: Date) => {
    return events.filter(event => {
      const eventDate = new Date(event.start_time)
      return eventDate.getDate() === date.getDate() &&
             eventDate.getMonth() === date.getMonth() &&
             eventDate.getFullYear() === date.getFullYear()
    })
  }

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))
  }

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))
  }

  const today = () => {
    setCurrentDate(new Date())
  }

  const isToday = (date: Date) => {
    const now = new Date()
    return date.getDate() === now.getDate() &&
           date.getMonth() === now.getMonth() &&
           date.getFullYear() === now.getFullYear()
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Загрузка...</div>
      </div>
    )
  }

  const calendarDays = getCalendarDays()
  const monthName = currentDate.toLocaleString('ru-RU', { month: 'long', year: 'numeric' })

  return (
    <div className="p-8">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Calendar className="w-8 h-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Календарь</h1>
          </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 border rounded-lg p-1">
                <button
                  onClick={() => setView('month')}
                  className={`px-3 py-1 rounded ${view === 'month' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'}`}
                >
                  Месяц
                </button>
                <button
                  onClick={() => setView('list')}
                  className={`px-3 py-1 rounded ${view === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'}`}
                >
                  Список
                </button>
              </div>
              <button
                onClick={() => setShowModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="w-5 h-5" />
                Создать
              </button>
            </div>
          </div>
        </div>

        {view === 'month' ? (
          <div className="bg-white rounded-xl shadow-sm border">
            {/* Навигация по месяцам */}
            <div className="flex items-center justify-between p-4 border-b">
              <button
                onClick={prevMonth}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-4">
                <h2 className="text-xl font-semibold capitalize">{monthName}</h2>
                <button
                  onClick={today}
                  className="px-3 py-1 text-sm border rounded-lg hover:bg-gray-50 transition"
                >
                  Сегодня
                </button>
              </div>
              <button
                onClick={nextMonth}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>

            {/* Дни недели */}
            <div className="grid grid-cols-7 border-b">
              {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].map(day => (
                <div key={day} className="p-3 text-center text-sm font-medium text-gray-600 border-r last:border-r-0">
                  {day}
                </div>
              ))}
            </div>

            {/* Сетка календаря */}
            <div className="grid grid-cols-7">
              {calendarDays.map((date, index) => {
                if (!date) {
                  return <div key={`empty-${index}`} className="min-h-[120px] border-r border-b bg-gray-50" />
                }

                const dayEvents = getEventsForDay(date)
                const today = isToday(date)

                return (
                  <div
                    key={date.toISOString()}
                    className={`min-h-[120px] border-r border-b p-2 ${today ? 'bg-blue-50' : 'hover:bg-gray-50'} transition`}
                  >
                    <div className={`text-sm font-medium mb-2 ${today ? 'text-blue-600' : 'text-gray-700'}`}>
                      {date.getDate()}
                    </div>
                    <div className="space-y-1">
                      {dayEvents.slice(0, 3).map(event => (
                        <div
                          key={event.id}
                          className="text-xs p-1 rounded truncate cursor-pointer hover:opacity-80"
                          style={{ backgroundColor: event.color + '20', color: event.color }}
                          title={`${event.title} - ${formatTime(event.start_time)}`}
                        >
                          {formatTime(event.start_time)} {event.title}
                        </div>
                      ))}
                      {dayEvents.length > 3 && (
                        <div className="text-xs text-gray-500 pl-1">
                          +{dayEvents.length - 3} ещё
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ) : (
          // Вид списком
          events.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Нет событий
            </h3>
            <p className="text-gray-600 mb-6">
              Создайте первое событие в календаре
            </p>
            <button
              onClick={() => setShowModal(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Создать событие
            </button>
          </div>
        ) : events.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Нет событий
            </h3>
            <p className="text-gray-600 mb-6">
              Создайте первое событие в календаре
            </p>
            <button
              onClick={() => setShowModal(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Создать событие
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {events.map((event) => (
              <div
                key={event.id}
                className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: event.color }}
                      />
                      <h3 className="text-lg font-semibold text-gray-900">
                        {event.title}
                      </h3>
                    </div>
                    {event.description && (
                      <p className="text-gray-600 mb-3">{event.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>📅 {formatDate(event.start_time)}</span>
                      {event.end_time && (
                        <span>→ {formatDate(event.end_time)}</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteEvent(event.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ))}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Новое событие
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateEvent} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Название *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Встреча, задача..."
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Описание
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Дополнительная информация..."
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Начало *
                </label>
                <input
                  type="datetime-local"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Конец
                </label>
                <input
                  type="datetime-local"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Цвет
                </label>
                <div className="flex gap-2">
                  {['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'].map((c) => (
                    <button
                      key={c}
                      type="button"
                      onClick={() => setColor(c)}
                      className={`w-8 h-8 rounded-full ${color === c ? 'ring-2 ring-offset-2 ring-gray-400' : ''}`}
                      style={{ backgroundColor: c }}
                    />
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
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
