'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'
import { Package, Search, Download, Plus } from 'lucide-react'
import Link from 'next/link'

interface Module {
  id: string
  name: string
  description: string
  author_id: string
  version: string
  status: string
  rating: number
  installs: number
  is_installed: boolean
}

export default function ModulesPage() {
  const router = useRouter()
  const [modules, setModules] = useState<Module[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadModules()
  }, [])

  const loadModules = async () => {
    try {
      const response = await api.get('/modules')
      setModules(response.data)
    } catch (error) {
      console.error('Error loading modules:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInstall = async (moduleId: string) => {
    try {
      await api.post(`/modules/${moduleId}/install`)
      loadModules()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка установки')
    }
  }

  const filteredModules = modules.filter(module =>
    module.name.toLowerCase().includes(search.toLowerCase()) ||
    module.description?.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Загрузка...</div>
      </div>
    )
  }

  return (
    <div>
      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Поиск модулей..."
          className="w-full pl-10 pr-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
      </div>

      {/* Modules Grid */}
      {filteredModules.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
          <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Модули не найдены
          </h3>
          <p className="text-gray-600">
            Попробуйте изменить поисковый запрос
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredModules.map((module) => (
            <div
              key={module.id}
              className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {module.name}
                  </h3>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {module.description || 'Без описания'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                <span>⭐ {module.rating.toFixed(1)}</span>
                <span>📥 {module.installs}</span>
                <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                  v{module.version}
                </span>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => router.push(`/dashboard/modules/${module.id}`)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50 transition text-sm"
                >
                  Подробнее
                </button>
                {module.is_installed ? (
                  <button
                    disabled
                    className="flex-1 px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm cursor-not-allowed"
                  >
                    ✓ Установлен
                  </button>
                ) : (
                  <button
                    onClick={() => handleInstall(module.id)}
                    className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm flex items-center justify-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Установить
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
