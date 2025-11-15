import { create } from 'zustand'

interface User {
  id: string
  name: string
  email: string
  role: string
}

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  setAuth: (token: string, user: User) => void
  logout: () => void
  initAuth: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,

  setAuth: (token: string, user: User) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    set({ token, user, isAuthenticated: true })
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ token: null, user: null, isAuthenticated: false })
  },

  initAuth: () => {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr)
        set({ token, user, isAuthenticated: true })
      } catch (error) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
  },
}))
