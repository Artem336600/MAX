'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'
import { Package, Plus, Edit, Trash2, Upload, Eye, EyeOff, TestTube } from 'lucide-react'

interface Module {
  id: string
  name: string
  description: string
  version: string
  status: string
  rating: number
  installs: number
  api_key: string
  created_at: string
}

export default function MyModulesPage() {
  const router = useRouter()
  const [modules, setModules] = useState<Module[]>([])
  const [loading, setLoading] = useState(true)
  const [showNewModal, setShowNewModal] = useState(false)
  const [newModule, setNewModule] = useState({
    name: '',
    description: '',
    version: '1.0.0'
  })

  useEffect(() => {
    loadModules()
  }, [])

  const loadModules = async () => {
    try {
      const response = await api.get('/modules/my')
      setModules(response.data)
    } catch (error) {
      console.error('Error loading modules:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePublish = async (moduleId: string, currentStatus: string) => {
    const newStatus = currentStatus === 'public' ? 'draft' : 'public'
    const action = newStatus === 'public' ? 'опубликовать' : 'снять с публикации'
    
    if (!confirm(`Вы уверены, что хотите ${action} этот модуль?`)) {
      return
    }
    
    try {
      await api.put(`/modules/${moduleId}`, {
        status: newStatus
      })
      loadModules()
    } catch (error) {
      console.error('Error publishing module:', error)
      alert('Ошибка при публикации модуля')
    }
  }

  const handleDelete = async (moduleId: string, moduleName: string) => {
    if (!confirm(`Вы уверены, что хотите удалить модуль "${moduleName}"? Это действие нельзя отменить.`)) {
      return
    }
    
    try {
      await api.delete(`/modules/${moduleId}`)
      loadModules()
    } catch (error) {
      console.error('Error deleting module:', error)
      alert('Ошибка при удалении модуля')
    }
  }

  const handleTestMode = (moduleId: string, moduleName: string) => {
    alert(`🧪 Тестовый режим активен!\n\n` +
          `Модуль "${moduleName}" работает в режиме черновика:\n\n` +
          `✅ Модуль виден только вам\n` +
          `✅ UI отображается в боковой панели (обновите страницу)\n` +
          `✅ Все функции доступны для тестирования\n` +
          `✅ ИИ может использовать модуль\n\n` +
          `Страница будет перезагружена для обновления меню.`)
    
    // Перезагрузить страницу чтобы обновить sidebar
    setTimeout(() => window.location.reload(), 1000)
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      await api.post('/modules', {
        ...newModule,
        manifest: {
          description: newModule.description,
          permissions: []
        }
      })
      
      setShowNewModal(false)
      setNewModule({ name: '', description: '', version: '1.0.0' })
      loadModules()
    } catch (error) {
      console.error('Error creating module:', error)
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
      {/* Create Button */}
      <div className="mb-6 flex justify-end">
        <button
          onClick={() => router.push('/dashboard/modules/create-simple')}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Создать модуль
        </button>
      </div>

      {/* Modules List */}
      {modules.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
          <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            У вас пока нет модулей
          </h3>
          <p className="text-gray-600 mb-6">
            Создайте свой первый модуль для Eidos
          </p>
          <button
            onClick={() => router.push('/dashboard/modules/create-simple')}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
          >
            Создать модуль
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {modules.map((module) => (
            <div
              key={module.id}
              className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {module.name}
                    </h3>
                    <span className={`text-xs px-2 py-1 rounded ${
                      module.status === 'public' ? 'bg-green-100 text-green-700' :
                      module.status === 'draft' ? 'bg-gray-100 text-gray-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {module.status}
                    </span>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                      v{module.version}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-4">
                    {module.description || 'Без описания'}
                  </p>
                  
                  <div className="flex items-center gap-6 text-sm text-gray-500 mb-4">
                    <span>⭐ {module.rating.toFixed(1)}</span>
                    <span>📥 {module.installs} установок</span>
                    <span>📅 {new Date(module.created_at).toLocaleDateString('ru-RU')}</span>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-600 mb-1">API Key:</div>
                    <code className="text-xs font-mono text-gray-800 break-all">
                      {module.api_key}
                    </code>
                  </div>
                </div>

                <div className="flex gap-2 ml-4">
                  {module.status === 'draft' && (
                    <button
                      onClick={() => handleTestMode(module.id, module.name)}
                      className="p-2 border border-yellow-200 bg-yellow-50 rounded-lg hover:bg-yellow-100 text-yellow-700 transition"
                      title="Тестовый режим"
                    >
                      <TestTube className="w-5 h-5" />
                    </button>
                  )}
                  <button
                    onClick={() => handlePublish(module.id, module.status)}
                    className={`p-2 border rounded-lg transition ${
                      module.status === 'public'
                        ? 'bg-green-50 border-green-200 hover:bg-green-100 text-green-700'
                        : 'bg-blue-50 border-blue-200 hover:bg-blue-100 text-blue-700'
                    }`}
                    title={module.status === 'public' ? 'Снять с публикации' : 'Опубликовать в маркетплейс'}
                  >
                    {module.status === 'public' ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Upload className="w-5 h-5" />
                    )}
                  </button>
                  <button
                    onClick={() => router.push(`/dashboard/modules/${module.id}`)}
                    className="p-2 border rounded-lg hover:bg-gray-50 transition"
                    title="Редактировать"
                  >
                    <Edit className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(module.id, module.name)}
                    className="p-2 border border-red-200 rounded-lg hover:bg-red-50 text-red-600 transition"
                    title="Удалить модуль"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showNewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Создать новый модуль
            </h2>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Название *
                </label>
                <input
                  type="text"
                  value={newModule.name}
                  onChange={(e) => setNewModule({ ...newModule, name: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Sleep Tracker"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Описание
                </label>
                <textarea
                  value={newModule.description}
                  onChange={(e) => setNewModule({ ...newModule, description: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Отслеживание качества сна"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Версия
                </label>
                <input
                  type="text"
                  value={newModule.version}
                  onChange={(e) => setNewModule({ ...newModule, version: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="1.0.0"
                  required
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50 transition"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                >
                  Создать
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Подробный гайд по созданию модулей */}
      <div className="mt-12 bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl border-2 border-purple-200 p-8">
        <div className="flex items-center gap-3 mb-6">
          <Package className="w-10 h-10 text-purple-600" />
          <h2 className="text-3xl font-bold text-gray-900">
            Как создать свой модуль?
          </h2>
        </div>
        
        <p className="text-lg text-gray-700 mb-8">
          Пошаговое руководство по созданию модуля для Eidos
        </p>

        <div className="space-y-6">
          {/* Шаги 1-7 с подробными инструкциями */}
          <div className="bg-white rounded-xl p-6 border-2 border-purple-100">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-purple-600 text-white rounded-full flex items-center justify-center text-xl font-bold flex-shrink-0">1</div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 mb-3">Создайте модуль в системе</h3>
                <p className="text-gray-700 mb-4">Нажмите кнопку "Создать модуль" выше. Укажите название и выберите, нужен ли UI.</p>
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-sm text-purple-900 font-medium mb-2">💡 Совет:</p>
                  <p className="text-sm text-purple-800">Если ваш модуль будет отображать данные пользователю - включите UI.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 border-2 border-purple-100">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-purple-600 text-white rounded-full flex items-center justify-center text-xl font-bold flex-shrink-0">2</div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 mb-3">Получите API ключ</h3>
                <p className="text-gray-700 mb-4">После создания вы получите уникальный API ключ. Сохраните его!</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 border-2 border-purple-100">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-purple-600 text-white rounded-full flex items-center justify-center text-xl font-bold flex-shrink-0">3</div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 mb-3">Создайте HTTP сервер</h3>
                <p className="text-gray-700 mb-4">Ваш модуль должен быть HTTP сервером с endpoints: /health, /manifest, /message</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 border-2 border-green-200">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-green-600 text-white rounded-full flex items-center justify-center text-xl font-bold flex-shrink-0">✓</div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 mb-3">Готово!</h3>
                <p className="text-gray-700 mb-4">Протестируйте в режиме черновика и опубликуйте в маркетплейс</p>
                <a href="/dashboard/modules/create/guide" className="text-purple-600 hover:underline">Подробное руководство →</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
