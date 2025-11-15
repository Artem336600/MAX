'use client'

import { useState, useEffect } from 'react'
import api from '@/lib/api'
import { Package, Power, PowerOff, Trash2 } from 'lucide-react'

interface UserModule {
  id: string
  enabled: boolean
  installed_at: string
  module: {
    id: string
    name: string
    description: string
    version: string
    rating: number
    installs: number
  }
}

export default function InstalledModulesPage() {
  const [modules, setModules] = useState<UserModule[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadModules()
  }, [])

  const loadModules = async () => {
    try {
      const response = await api.get('/modules/installed/list')
      setModules(response.data)
    } catch (error) {
      console.error('Error loading modules:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUninstall = async (moduleId: string) => {
    if (!confirm('Удалить модуль?')) return
    
    try {
      await api.delete(`/modules/${moduleId}/uninstall`)
      loadModules()
    } catch (error) {
      console.error('Error uninstalling module:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Загрузка...</div>
      </div>
    )
  }

  return (
    <div>
      {modules.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
          <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Нет установленных модулей
          </h3>
          <p className="text-gray-600">
            Установите модули из маркетплейса
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {modules.map((userModule) => (
            <div
              key={userModule.id}
              className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {userModule.module.name}
                    </h3>
                    <span className={`flex items-center gap-1 text-xs px-2 py-1 rounded ${
                      userModule.enabled 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {userModule.enabled ? (
                        <>
                          <Power className="w-3 h-3" />
                          Активен
                        </>
                      ) : (
                        <>
                          <PowerOff className="w-3 h-3" />
                          Отключен
                        </>
                      )}
                    </span>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                      v{userModule.module.version}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-4">
                    {userModule.module.description || 'Без описания'}
                  </p>
                  
                  <div className="flex items-center gap-6 text-sm text-gray-500">
                    <span>⭐ {userModule.module.rating.toFixed(1)}</span>
                    <span>📥 {userModule.module.installs} установок</span>
                    <span>📅 Установлен {new Date(userModule.installed_at).toLocaleDateString('ru-RU')}</span>
                  </div>
                </div>

                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => handleUninstall(userModule.module.id)}
                    className="p-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition"
                    title="Удалить"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
