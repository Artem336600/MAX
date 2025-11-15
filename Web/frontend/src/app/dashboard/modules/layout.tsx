'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { Package, Store, Boxes, User, Settings } from 'lucide-react'

export default function ModulesLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  const tabs = [
    { href: '/dashboard/modules', label: 'Маркетплейс', icon: Store, exact: true },
    { href: '/dashboard/modules/installed', label: 'Установленные', icon: Boxes },
    { href: '/dashboard/modules/my', label: 'Мои модули', icon: User },
    { href: '/dashboard/modules/manage', label: 'Управление', icon: Settings },
  ]

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-6">
          <Package className="w-8 h-8 text-purple-600" />
          <h1 className="text-2xl font-bold text-gray-900">Модули</h1>
        </div>

        {/* Tabs */}
        <div className="border-b">
          <nav className="flex gap-6">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = tab.exact 
                ? pathname === tab.href 
                : pathname.startsWith(tab.href)

              return (
                <Link
                  key={tab.href}
                  href={tab.href}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 transition ${
                    isActive
                      ? 'border-purple-600 text-purple-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </Link>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Content */}
      {children}
    </div>
  )
}
