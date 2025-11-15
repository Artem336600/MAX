'use client'

import { useAuthStore } from '@/store/authStore'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Calendar, MessageSquare, Package } from 'lucide-react'

export default function DashboardPage() {
  const { user, logout } = useAuthStore()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Добро пожаловать в Eidos! 🎉
        </h2>
        <p className="text-gray-600">
          Ваш персональный ИИ-ассистент готов к работе
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Link
          href="/dashboard/calendar"
          className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition group"
        >
          <Calendar className="w-12 h-12 text-blue-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-600">
            Календарь
          </h3>
          <p className="text-gray-600 text-sm">
            Управляйте событиями и напоминаниями
          </p>
        </Link>

        <Link
          href="/dashboard/chat"
          className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition group"
        >
          <MessageSquare className="w-12 h-12 text-green-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-green-600">
            Чат с ИИ
          </h3>
          <p className="text-gray-600 text-sm">
            Общайтесь с персональным ассистентом
          </p>
        </Link>

        <Link
          href="/dashboard/modules"
          className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition group"
        >
          <Package className="w-12 h-12 text-purple-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-purple-600">
            Модули
          </h3>
          <p className="text-gray-600 text-sm">
            Маркетплейс и создание модулей
          </p>
        </Link>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Информация о профиле
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Email:</span>
            <span className="font-medium">{user?.email}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">ID:</span>
            <span className="font-mono text-xs">{user?.id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Роль:</span>
            <span className="font-medium">{user?.role}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
