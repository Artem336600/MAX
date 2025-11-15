'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Calendar, MessageSquare, Package, Menu, X, LogOut, Settings } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { useModulePages } from '@/hooks/useModulePages';

interface SidebarProps {
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}

export default function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()
  const { pages: modulePages, loading } = useModulePages();
  const router = useRouter()
  const [isOpen, setIsOpen] = useState(true)
  
  // Debug
  useEffect(() => {
    console.log('[Sidebar] Module pages:', modulePages, 'Loading:', loading)
  }, [modulePages, loading])

  // Сохраняем состояние в localStorage
  useEffect(() => {
    const saved = localStorage.getItem('sidebarOpen')
    if (saved !== null) {
      setIsOpen(saved === 'true')
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('sidebarOpen', String(isOpen))
    // Отправляем custom event для синхронизации
    window.dispatchEvent(new CustomEvent('sidebarToggle', { detail: isOpen }))
  }, [isOpen])

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  const menuItems = [
    { href: '/dashboard', icon: Home, label: 'Главная', active: true },
    { href: '/dashboard/calendar', icon: Calendar, label: 'Календарь', active: true },
    { href: '/dashboard/chat', icon: MessageSquare, label: 'Чат с ИИ', active: true },
    { href: '/dashboard/modules', icon: Package, label: 'Модули', active: true },
  ]

  return (
    <>
      {/* Overlay для мобильных */}
      <div
        className={`fixed inset-0 bg-black transition-opacity duration-300 z-40 lg:hidden ${
          isOpen ? 'opacity-50' : 'opacity-0 pointer-events-none'
        }`}
        onClick={() => setIsOpen(false)}
      />

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full bg-white border-r shadow-xl z-50 transition-all duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } w-64`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
                E
              </div>
              <span className="font-bold text-xl">Eidos</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
              title="Скрыть меню"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* User info */}
          <div className="p-4 border-b">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">
                {user?.name?.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-gray-900 truncate">{user?.name}</div>
                <div className="text-sm text-gray-500 truncate">{user?.email}</div>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return item.active ? (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                  onClick={() => {
                    // Закрываем sidebar на мобильных после клика
                    if (window.innerWidth < 1024) {
                      setIsOpen(false)
                    }
                  }}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              ) : (
                <div
                  key={item.href}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-400 cursor-not-allowed"
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                  <span className="ml-auto text-xs bg-gray-100 px-2 py-1 rounded">Скоро</span>
                </div>
              )
            })}

            {/* Динамические страницы модулей */}
            {!loading && modulePages.map((page) => {
              const isActive = pathname === page.path
              
              return (
                <Link
                  key={page.id}
                  href={page.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                  onClick={() => {
                    if (window.innerWidth < 1024) {
                      setIsOpen(false)
                    }
                  }}
                >
                  <span className="text-xl">{page.icon || '📄'}</span>
                  <span className="font-medium">{page.title}</span>
                  {page.id.startsWith('draft-') && (
                    <span className="ml-auto text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded">
                      Тест
                    </span>
                  )}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-red-600 hover:bg-red-50 transition"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Выйти</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Toggle button - показываем только когда sidebar закрыт */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed top-4 left-4 z-30 p-2.5 bg-white border rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300"
          title="Показать меню"
        >
          <Menu className="w-5 h-5" />
        </button>
      )}
    </>
  )
}
