'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import Sidebar from '@/components/layout/Sidebar'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { isAuthenticated, initAuth } = useAuthStore()
  const [isLoading, setIsLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    initAuth()
    setIsLoading(false)
    
    // Загружаем состояние sidebar
    const saved = localStorage.getItem('sidebarOpen')
    if (saved !== null) {
      setSidebarOpen(saved === 'true')
    }
  }, [initAuth])

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, isLoading, router])

  // Слушаем изменения sidebar из localStorage
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('sidebarOpen')
      if (saved !== null) {
        setSidebarOpen(saved === 'true')
      }
    }
    
    window.addEventListener('storage', handleStorageChange)
    
    // Также слушаем custom event для изменений в том же окне
    const handleSidebarToggle = (e: CustomEvent) => {
      setSidebarOpen(e.detail)
    }
    
    window.addEventListener('sidebarToggle' as any, handleSidebarToggle as any)
    
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('sidebarToggle' as any, handleSidebarToggle as any)
    }
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Загрузка...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <main className={`transition-all duration-300 ease-in-out ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
        {children}
      </main>
    </div>
  )
}
