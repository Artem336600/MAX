'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'
import { Package, Key, Palette, Sparkles, Copy, CheckCircle, ArrowRight, ExternalLink, TestTube } from 'lucide-react'

interface CreatedModule {
  id: string
  name: string
  api_key: string
  status: string
}

export default function CreateModuleSimplePage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [moduleName, setModuleName] = useState('')
  const [hasUI, setHasUI] = useState(false)
  const [uiTitle, setUITitle] = useState('')
  const [uiIcon, setUIIcon] = useState('📦')
  const [createdModule, setCreatedModule] = useState<CreatedModule | null>(null)
  const [creating, setCreating] = useState(false)
  const [copied, setCopied] = useState(false)

  const icons = ['📦', '⚡', '💪', '💰', '📚', '🎮', '🔧', '🏋️', '😴', '🎯', '📊', '🚀', '🎨', '🔔', '📝', '🌟']

  const copyApiKey = () => {
    if (createdModule) {
      navigator.clipboard.writeText(createdModule.api_key)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleCreate = async () => {
    if (!moduleName.trim()) return
    
    setCreating(true)
    
    try {
      const manifest: any = {
        description: `Модуль ${moduleName}`,
        permissions: ['database', 'notifications'],
        functions: []
      }

      if (hasUI) {
        // Генерируем безопасный путь (только латиница, цифры, дефисы)
        const safePath = moduleName
          .toLowerCase()
          .replace(/[^a-z0-9\s-]/g, '') // Удаляем все кроме латиницы, цифр, пробелов и дефисов
          .replace(/\s+/g, '-') // Заменяем пробелы на дефисы
          .replace(/-+/g, '-') // Убираем повторяющиеся дефисы
          .trim()
        
        const path = safePath ? `/dashboard/${safePath}` : `/dashboard/module-${Date.now()}`
        
        manifest.pages = [{
          title: uiTitle || moduleName,
          icon: uiIcon,
          path: path,
          order: 100
        }]
      }

      const response = await api.post('/modules', {
        name: moduleName,
        description: `Модуль ${moduleName}`,
        version: '1.0.0',
        manifest
      })

      setCreatedModule({
        id: response.data.id,
        name: response.data.name,
        api_key: response.data.api_key,
        status: response.data.status
      })
      
      setStep(3)
      
      // Если есть UI - показать сообщение и перезагрузить
      if (hasUI) {
        setTimeout(() => {
          if (confirm('✅ Модуль создан!\n\nUI модуля будет добавлен в боковую панель.\nПерезагрузить страницу сейчас?')) {
            window.location.reload()
          }
        }, 1000)
      }
    } catch (error) {
      console.error('Error creating module:', error)
      alert('Ошибка при создании модуля')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Создание модуля
        </h1>
        <p className="text-gray-600">
          Простой способ создать модуль для Eidos
        </p>
      </div>

      {/* Progress */}
      <div className="flex items-center justify-center mb-8">
        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
              step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'
            }`}>
              1
            </div>
            <span className="font-medium">Название</span>
          </div>
          
          <div className="w-12 h-0.5 bg-gray-300" />
          
          <div className={`flex items-center gap-2 ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
              step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'
            }`}>
              2
            </div>
            <span className="font-medium">UI</span>
          </div>
          
          <div className="w-12 h-0.5 bg-gray-300" />
          
          <div className={`flex items-center gap-2 ${step >= 3 ? 'text-green-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
              step >= 3 ? 'bg-green-600 text-white' : 'bg-gray-200'
            }`}>
              ✓
            </div>
            <span className="font-medium">Готово</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="bg-white rounded-xl shadow-lg border p-8">
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Package className="w-6 h-6 text-blue-600" />
                Название модуля
              </h2>
              <p className="text-gray-600 mb-6">
                Придумайте уникальное название для вашего модуля
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Название *
              </label>
              <input
                type="text"
                value={moduleName}
                onChange={(e) => setModuleName(e.target.value)}
                className="w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                placeholder="Например: Workout Analyzer"
                autoFocus
              />
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-blue-900 mb-1">
                    Что дальше?
                  </h3>
                  <p className="text-sm text-blue-700">
                    После создания вы получите API ключ для подключения вашего модуля к Eidos. 
                    Модуль будет создан в режиме черновика для тестирования.
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={!moduleName.trim()}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg font-medium"
            >
              Далее
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Palette className="w-6 h-6 text-purple-600" />
                Пользовательский интерфейс
              </h2>
              <p className="text-gray-600 mb-6">
                Нужен ли вашему модулю собственный UI в боковой панели?
              </p>
            </div>

            <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg border-2 border-gray-200">
              <input
                type="checkbox"
                id="has_ui"
                checked={hasUI}
                onChange={(e) => setHasUI(e.target.checked)}
                className="w-6 h-6 text-blue-600 rounded"
              />
              <label htmlFor="has_ui" className="flex-1 cursor-pointer">
                <div className="font-semibold text-gray-900">Добавить пункт в боковую панель</div>
                <div className="text-sm text-gray-600">Модуль будет отображаться в меню слева</div>
              </label>
            </div>

            {hasUI && (
              <div className="space-y-4 pl-4 border-l-4 border-purple-200">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Название в меню
                  </label>
                  <input
                    type="text"
                    value={uiTitle}
                    onChange={(e) => setUITitle(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder={moduleName}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Иконка
                  </label>
                  <div className="flex gap-2 flex-wrap">
                    {icons.map((icon) => (
                      <button
                        key={icon}
                        onClick={() => setUIIcon(icon)}
                        className={`text-2xl p-2 border-2 rounded-lg transition ${
                          uiIcon === icon
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        {icon}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                  <div className="text-sm text-purple-900 font-medium mb-2">Предпросмотр:</div>
                  <div className="flex items-center gap-3 p-2 bg-white rounded border">
                    <span className="text-2xl">{uiIcon}</span>
                    <span className="font-medium">{uiTitle || moduleName}</span>
                  </div>
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="px-6 py-3 border-2 rounded-lg hover:bg-gray-50 transition"
              >
                Назад
              </button>
              <button
                onClick={handleCreate}
                disabled={creating}
                className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 flex items-center justify-center gap-2 text-lg font-medium"
              >
                {creating ? 'Создание...' : 'Создать модуль'}
                <Sparkles className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {step === 3 && createdModule && (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Модуль создан!
              </h2>
              <p className="text-gray-600">
                Ваш модуль "{createdModule.name}" готов к разработке
              </p>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Key className="w-6 h-6 text-blue-600" />
                <h3 className="font-bold text-gray-900">API Ключ</h3>
              </div>
              
              <div className="bg-white rounded-lg p-4 mb-4">
                <code className="text-sm font-mono text-gray-800 break-all block">
                  {createdModule.api_key}
                </code>
              </div>

              <button
                onClick={copyApiKey}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
              >
                {copied ? (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Скопировано!
                  </>
                ) : (
                  <>
                    <Copy className="w-5 h-5" />
                    Скопировать API ключ
                  </>
                )}
              </button>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <TestTube className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-yellow-900 mb-1">
                    Режим тестирования
                  </h3>
                  <p className="text-sm text-yellow-700 mb-3">
                    Модуль создан в режиме черновика. Только вы можете видеть и тестировать его. 
                    {hasUI && ' Пункт меню уже добавлен в боковую панель!'}
                  </p>
                  <p className="text-sm text-yellow-700">
                    После тестирования вы сможете опубликовать модуль в маркетплейс.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Что дальше?</h3>
              <ol className="space-y-2 text-sm text-gray-700">
                <li className="flex items-start gap-2">
                  <span className="font-bold text-blue-600">1.</span>
                  <span>Используйте API ключ в вашем модуле для подключения к Eidos</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-blue-600">2.</span>
                  <span>Запустите ваш модуль локально (например, на порту 8082)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-blue-600">3.</span>
                  <span>Протестируйте функциональность</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-blue-600">4.</span>
                  <span>Опубликуйте модуль в "Мои модули" когда будете готовы</span>
                </li>
              </ol>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => window.open('/MODULE_DEVELOPMENT_GUIDE.md', '_blank')}
                className="flex-1 px-6 py-3 border-2 rounded-lg hover:bg-gray-50 transition flex items-center justify-center gap-2"
              >
                <ExternalLink className="w-5 h-5" />
                Руководство разработчика
              </button>
              <button
                onClick={() => router.push('/dashboard/modules/my')}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
              >
                Перейти к модулям
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
