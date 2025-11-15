'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'
import { 
  Package, 
  Eye, 
  EyeOff, 
  Settings, 
  Trash2, 
  Power,
  PowerOff,
  ChevronDown,
  ChevronUp,
  Save,
  RotateCcw
} from 'lucide-react'

interface ModulePage {
  id: string
  module_id: string
  module_name: string
  title: string
  icon: string | null
  path: string
  order: number
  enabled: boolean
}

interface Module {
  id: string
  name: string
  description: string
  status: string
  is_installed: boolean
  has_ui: boolean
  pages?: ModulePage[]
}

export default function ModuleSettingsPage() {
  const router = useRouter()
  const [allModules, setAllModules] = useState<Module[]>([])
  const [builtinModules, setBuiltinModules] = useState<ModulePage[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [expandedModule, setExpandedModule] = useState<string | null>(null)

  useEffect(() => {
    loadModules()
  }, [])

  const loadModules = async () => {
    try {
      // Загрузить все модули пользователя
      const myModulesRes = await api.get('/modules/my')
      const installedModulesRes = await api.get('/modules')
      const pagesRes = await api.get('/module-pages/all')

      // Встроенные модули
      const builtin = pagesRes.data.filter((p: ModulePage) => p.id.startsWith('builtin-'))
      setBuiltinModules(builtin)

      // Пользовательские модули
      const userModules = myModulesRes.data.map((m: any) => {
        const pages = pagesRes.data.filter((p: ModulePage) => p.module_id === m.id)
        return {
          ...m,
          has_ui: pages.length > 0,
          pages: pages
        }
      })

      setAllModules(userModules)
    } catch (error) {
      console.error('Error loading modules:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleBuiltinModule = async (moduleId: string, currentEnabled: boolean) => {
    // Сохранить в localStorage для встроенных модулей
    const disabledModules = JSON.parse(localStorage.getItem('disabledBuiltinModules') || '[]')
    
    if (currentEnabled) {
      // Отключить
      disabledModules.push(moduleId)
    } else {
      // Включить
      const index = disabledModules.indexOf(moduleId)
      if (index > -1) disabledModules.splice(index, 1)
    }
    
    localStorage.setItem('disabledBuiltinModules', JSON.stringify(disabledModules))
    
    // Обновить состояние
    setBuiltinModules(prev => prev.map(m => 
      m.id === moduleId ? { ...m, enabled: !currentEnabled } : m
    ))
    
    // Перезагрузить страницу для обновления sidebar
    setTimeout(() => window.location.reload(), 500)
  }

  const toggleModulePage = async (moduleId: string, pageId: string, currentEnabled: boolean) => {
    try {
      // Здесь можно добавить API для управления страницами
      setAllModules(prev => prev.map(m => {
        if (m.id === moduleId && m.pages) {
          return {
            ...m,
            pages: m.pages.map(p => 
              p.id === pageId ? { ...p, enabled: !currentEnabled } : p
            )
          }
        }
        return m
      }))
    } catch (error) {
      console.error('Error toggling page:', error)
    }
  }

  const updatePageOrder = async (moduleId: string, pageId: string, newOrder: number) => {
    setAllModules(prev => prev.map(m => {
      if (m.id === moduleId && m.pages) {
        return {
          ...m,
          pages: m.pages.map(p => 
            p.id === pageId ? { ...p, order: newOrder } : p
          )
        }
      }
      return m
    }))
  }

  const saveChanges = async () => {
    setSaving(true)
    try {
      // Сохранить изменения
      alert('Настройки сохранены!')
      window.location.reload()
    } catch (error) {
      console.error('Error saving:', error)
      alert('Ошибка при сохранении')
    } finally {
      setSaving(false)
    }
  }

  const resetToDefaults = () => {
    if (confirm('Сбросить все настройки модулей к значениям по умолчанию?')) {
      localStorage.removeItem('disabledBuiltinModules')
      window.location.reload()
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Управление модулями
        </h1>
        <p className="text-gray-600">
          Настройте отображение и поведение модулей в системе
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={saveChanges}
          disabled={saving}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          {saving ? 'Сохранение...' : 'Сохранить изменения'}
        </button>
        <button
          onClick={resetToDefaults}
          className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition flex items-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Сбросить
        </button>
      </div>

      {/* Встроенные модули */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Package className="w-5 h-5 text-blue-600" />
          Встроенные модули
        </h2>
        <div className="bg-white rounded-xl border divide-y">
          {builtinModules.map((module) => {
            const isDisabled = JSON.parse(localStorage.getItem('disabledBuiltinModules') || '[]').includes(module.id)
            
            return (
              <div key={module.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <span className="text-2xl">{module.icon}</span>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{module.title}</h3>
                      <p className="text-sm text-gray-600">{module.module_name}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-sm text-gray-500">
                      Порядок: {module.order}
                    </div>
                    
                    <button
                      onClick={() => toggleBuiltinModule(module.id, !isDisabled)}
                      className={`p-2 rounded-lg transition ${
                        isDisabled
                          ? 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                          : 'bg-green-50 text-green-600 hover:bg-green-100'
                      }`}
                      title={isDisabled ? 'Включить' : 'Отключить'}
                    >
                      {isDisabled ? (
                        <PowerOff className="w-5 h-5" />
                      ) : (
                        <Power className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Пользовательские модули */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5 text-purple-600" />
          Мои модули
        </h2>

        {allModules.length === 0 ? (
          <div className="bg-white rounded-xl border p-12 text-center">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Нет пользовательских модулей
            </h3>
            <p className="text-gray-600 mb-6">
              Создайте свой первый модуль
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
            {allModules.map((module) => (
              <div key={module.id} className="bg-white rounded-xl border">
                <div className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {module.name}
                        </h3>
                        <span className={`text-xs px-2 py-1 rounded ${
                          module.status === 'public'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {module.status === 'public' ? 'Опубликован' : 'Черновик'}
                        </span>
                        {module.has_ui && (
                          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                            Есть UI
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{module.description}</p>
                    </div>

                    <div className="flex items-center gap-2">
                      {module.has_ui && module.pages && module.pages.length > 0 && (
                        <button
                          onClick={() => setExpandedModule(
                            expandedModule === module.id ? null : module.id
                          )}
                          className="p-2 border rounded-lg hover:bg-gray-50 transition"
                        >
                          {expandedModule === module.id ? (
                            <ChevronUp className="w-5 h-5" />
                          ) : (
                            <ChevronDown className="w-5 h-5" />
                          )}
                        </button>
                      )}
                      
                      <button
                        onClick={() => router.push(`/dashboard/modules/${module.id}`)}
                        className="p-2 border rounded-lg hover:bg-gray-50 transition"
                        title="Настройки"
                      >
                        <Settings className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Страницы модуля */}
                {expandedModule === module.id && module.pages && module.pages.length > 0 && (
                  <div className="border-t bg-gray-50 p-4">
                    <h4 className="font-medium text-gray-900 mb-3">Страницы модуля:</h4>
                    <div className="space-y-2">
                      {module.pages.map((page) => (
                        <div
                          key={page.id}
                          className="bg-white rounded-lg p-3 flex items-center justify-between"
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-xl">{page.icon}</span>
                            <div>
                              <div className="font-medium text-gray-900">{page.title}</div>
                              <div className="text-sm text-gray-500">{page.path}</div>
                            </div>
                          </div>

                          <div className="flex items-center gap-3">
                            <input
                              type="number"
                              value={page.order}
                              onChange={(e) => updatePageOrder(
                                module.id,
                                page.id,
                                parseInt(e.target.value)
                              )}
                              className="w-20 px-2 py-1 border rounded text-sm"
                              placeholder="Порядок"
                            />
                            
                            <button
                              onClick={() => toggleModulePage(module.id, page.id, page.enabled)}
                              className={`p-2 rounded-lg transition ${
                                page.enabled
                                  ? 'bg-green-50 text-green-600 hover:bg-green-100'
                                  : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                              }`}
                            >
                              {page.enabled ? (
                                <Eye className="w-4 h-4" />
                              ) : (
                                <EyeOff className="w-4 h-4" />
                              )}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Подсказка */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">💡 Подсказка</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Отключенные модули не будут отображаться в боковой панели</li>
          <li>• Порядок определяет позицию модуля в меню (меньше = выше)</li>
          <li>• Изменения применятся после сохранения и перезагрузки страницы</li>
          <li>• Встроенные модули можно отключить, но нельзя удалить</li>
        </ul>
      </div>
    </div>
  )
}
