'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'
import { Package, Key, Palette, Sparkles, Copy, CheckCircle } from 'lucide-react'

interface CreatedModule {
  id: string
  name: string
  api_key: string
  status: string
  has_ui: boolean
  ui_config?: {
    title: string
    icon: string
    path: string
  }
}

export default function CreateModulePage() {
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
        const path = `/dashboard/${moduleName.toLowerCase().replace(/\s+/g, '-')}`
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
        status: response.data.status,
        has_ui: hasUI,
        ui_config: hasUI ? {
          title: uiTitle || moduleName,
          icon: uiIcon,
          path: `/dashboard/${moduleName.toLowerCase().replace(/\s+/g, '-')}`
        } : undefined
      })
      
      setStep(3)
    } catch (error) {
      console.error('Error creating module:', error)
      alert('Ошибка при создании модуля')
    } finally {
      setCreating(false)
    }
  }

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Основная информация
              </h2>
              <p className="text-gray-600">
                Расскажите о вашем модуле
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Название модуля *
              </label>
              <input
                type="text"
                value={moduleData.name}
                onChange={(e) => setModuleData({ ...moduleData, name: e.target.value })}
                className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Например: Workout Analyzer"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Описание *
              </label>
              <textarea
                value={moduleData.description}
                onChange={(e) => setModuleData({ ...moduleData, description: e.target.value })}
                className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={4}
                placeholder="Опишите функциональность вашего модуля..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Версия
                </label>
                <input
                  type="text"
                  value={moduleData.version}
                  onChange={(e) => setModuleData({ ...moduleData, version: e.target.value })}
                  className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="1.0.0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Категория
                </label>
                <select
                  value={moduleData.category}
                  onChange={(e) => setModuleData({ ...moduleData, category: e.target.value })}
                  className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {categories.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.icon} {cat.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Иконка модуля
              </label>
              <div className="flex gap-2 flex-wrap">
                {icons.map((icon) => (
                  <button
                    key={icon}
                    onClick={() => setModuleData({ ...moduleData, icon })}
                    className={`text-3xl p-3 border-2 rounded-lg transition ${
                      moduleData.icon === icon
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {icon}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Подключение модуля
              </h2>
              <p className="text-gray-600">
                Укажите URL вашего модуля для подключения к Eidos
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Code className="w-5 h-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-medium text-blue-900 mb-1">
                    Как это работает?
                  </h3>
                  <p className="text-sm text-blue-700">
                    Ваш модуль должен быть запущен как HTTP сервер. Eidos будет отправлять запросы на указанный URL для взаимодействия с модулем.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Webhook URL *
              </label>
              <input
                type="url"
                value={moduleData.webhook_url}
                onChange={(e) => setModuleData({ ...moduleData, webhook_url: e.target.value })}
                className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                placeholder="http://localhost:8082"
              />
              <p className="text-sm text-gray-500 mt-2">
                Например: http://localhost:8082 или https://your-module.com
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3">Пример запуска модуля:</h3>
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
{`# Python
python server.py

# Node.js
npm start

# Docker
docker run -p 8082:8082 my-module`}
              </pre>
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Тестирование модуля
              </h2>
              <p className="text-gray-600">
                Проверьте подключение к вашему модулю
              </p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <TestTube className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-medium text-yellow-900 mb-1">
                    Убедитесь что модуль запущен
                  </h3>
                  <p className="text-sm text-yellow-700">
                    Перед тестированием убедитесь, что ваш модуль запущен и доступен по указанному URL.
                  </p>
                </div>
              </div>
            </div>

            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <TestTube className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Тестовое подключение
              </h3>
              <p className="text-gray-600 mb-6">
                URL: {moduleData.webhook_url || 'не указан'}
              </p>
              
              <button
                onClick={handleTestModule}
                disabled={!moduleData.webhook_url || testing}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {testing ? 'Тестирование...' : 'Запустить тест'}
              </button>
            </div>

            {testResult && (
              <div className={`border-2 rounded-lg p-6 ${
                testResult.success
                  ? 'border-green-200 bg-green-50'
                  : 'border-red-200 bg-red-50'
              }`}>
                <div className="flex items-start gap-3">
                  {testResult.success ? (
                    <Check className="w-6 h-6 text-green-600" />
                  ) : (
                    <span className="text-2xl">❌</span>
                  )}
                  <div className="flex-1">
                    <h3 className={`font-semibold mb-2 ${
                      testResult.success ? 'text-green-900' : 'text-red-900'
                    }`}>
                      {testResult.message}
                    </h3>
                    {testResult.details && (
                      <pre className="text-sm bg-white p-3 rounded border overflow-x-auto">
                        {JSON.stringify(testResult.details, null, 2)}
                      </pre>
                    )}
                    {testResult.error && (
                      <p className="text-sm text-red-700">
                        Ошибка: {testResult.error}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Пользовательский интерфейс
              </h2>
              <p className="text-gray-600">
                Добавьте страницу модуля в боковую панель
              </p>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Palette className="w-5 h-5 text-purple-600 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-medium text-purple-900 mb-1">
                    Опциональная функция
                  </h3>
                  <p className="text-sm text-purple-700">
                    Если ваш модуль имеет веб-интерфейс, вы можете добавить ссылку на него в боковую панель Eidos.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
              <input
                type="checkbox"
                id="has_ui"
                checked={moduleData.has_ui}
                onChange={(e) => setModuleData({ ...moduleData, has_ui: e.target.checked })}
                className="w-5 h-5 text-blue-600 rounded"
              />
              <label htmlFor="has_ui" className="font-medium text-gray-900 cursor-pointer">
                Добавить пункт в боковую панель
              </label>
            </div>

            {moduleData.has_ui && (
              <div className="space-y-4 pl-8 border-l-4 border-blue-200">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Название в меню
                  </label>
                  <input
                    type="text"
                    value={moduleData.ui_config.title}
                    onChange={(e) => setModuleData({
                      ...moduleData,
                      ui_config: { ...moduleData.ui_config, title: e.target.value }
                    })}
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder={moduleData.name}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Иконка
                  </label>
                  <div className="flex gap-2">
                    {icons.map((icon) => (
                      <button
                        key={icon}
                        onClick={() => setModuleData({
                          ...moduleData,
                          ui_config: { ...moduleData.ui_config, icon }
                        })}
                        className={`text-2xl p-2 border rounded-lg ${
                          moduleData.ui_config.icon === icon
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200'
                        }`}
                      >
                        {icon}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL путь
                  </label>
                  <input
                    type="text"
                    value={moduleData.ui_config.path}
                    onChange={(e) => setModuleData({
                      ...moduleData,
                      ui_config: { ...moduleData.ui_config, path: e.target.value }
                    })}
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                    placeholder={`/dashboard/${moduleData.name.toLowerCase().replace(/\s+/g, '-')}`}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Порядок в меню
                  </label>
                  <input
                    type="number"
                    value={moduleData.ui_config.order}
                    onChange={(e) => setModuleData({
                      ...moduleData,
                      ui_config: { ...moduleData.ui_config, order: parseInt(e.target.value) }
                    })}
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    min="0"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Меньшее число = выше в списке
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">Предпросмотр:</h4>
                  <div className="flex items-center gap-3 p-3 bg-white rounded-lg border">
                    <span className="text-2xl">{moduleData.ui_config.icon}</span>
                    <span className="font-medium">
                      {moduleData.ui_config.title || moduleData.name}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )

      case 5:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Готово к созданию!
              </h2>
              <p className="text-gray-600">
                Проверьте информацию перед созданием модуля
              </p>
            </div>

            <div className="bg-white border-2 border-gray-200 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-4">
                <div className="text-4xl">{moduleData.icon}</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900">{moduleData.name}</h3>
                  <p className="text-gray-600">{moduleData.description}</p>
                </div>
                <span className="text-sm bg-gray-100 px-3 py-1 rounded">
                  v{moduleData.version}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Категория</div>
                  <div className="font-medium">
                    {categories.find(c => c.value === moduleData.category)?.label}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Webhook URL</div>
                  <div className="font-mono text-sm">{moduleData.webhook_url}</div>
                </div>
              </div>

              {moduleData.has_ui && (
                <div className="pt-4 border-t">
                  <div className="text-sm text-gray-600 mb-2">Пользовательский интерфейс</div>
                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <span className="text-2xl">{moduleData.ui_config.icon}</span>
                    <div>
                      <div className="font-medium">{moduleData.ui_config.title || moduleData.name}</div>
                      <div className="text-sm text-gray-600">{moduleData.ui_config.path}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-green-900 mb-1">
                    Модуль будет создан как черновик
                  </h3>
                  <p className="text-sm text-green-700">
                    После создания вы сможете протестировать модуль и опубликовать его в маркетплейс.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  const isStepValid = () => {
    switch (step) {
      case 1:
        return moduleData.name && moduleData.description
      case 2:
        return moduleData.webhook_url
      case 3:
        return testResult?.success
      case 4:
        return !moduleData.has_ui || (moduleData.ui_config.title && moduleData.ui_config.path)
      case 5:
        return true
      default:
        return false
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[
            { num: 1, label: 'Информация', icon: Package },
            { num: 2, label: 'Подключение', icon: Code },
            { num: 3, label: 'Тестирование', icon: TestTube },
            { num: 4, label: 'Интерфейс', icon: Palette },
            { num: 5, label: 'Готово', icon: Check },
          ].map((s, index) => {
            const Icon = s.icon
            const isActive = step === s.num
            const isCompleted = step > s.num
            
            return (
              <div key={s.num} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition ${
                    isCompleted
                      ? 'bg-green-500 border-green-500 text-white'
                      : isActive
                      ? 'bg-blue-500 border-blue-500 text-white'
                      : 'bg-white border-gray-300 text-gray-400'
                  }`}>
                    {isCompleted ? <Check className="w-6 h-6" /> : <Icon className="w-6 h-6" />}
                  </div>
                  <div className={`text-sm font-medium mt-2 ${
                    isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                  }`}>
                    {s.label}
                  </div>
                </div>
                {index < 4 && (
                  <div className={`h-0.5 flex-1 mx-2 ${
                    isCompleted ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Content */}
      <div className="bg-white rounded-xl shadow-lg border p-8 mb-6">
        {renderStep()}
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          disabled={step === 1}
          className="px-6 py-3 border rounded-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <ArrowLeft className="w-5 h-5" />
          Назад
        </button>

        {step < 5 ? (
          <button
            onClick={handleNext}
            disabled={!isStepValid()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            Далее
            <ArrowRight className="w-5 h-5" />
          </button>
        ) : (
          <button
            onClick={handleCreate}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
          >
            <Upload className="w-5 h-5" />
            Создать модуль
          </button>
        )}
      </div>
    </div>
  )
}
