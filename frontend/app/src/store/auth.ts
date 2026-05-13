import { create } from 'zustand'
import { logout as apiLogout, refresh } from '../api/auth'
import type { User } from '../types'

interface AuthState {
  user: User | null
  isInitialized: boolean
  login: (user: User) => void
  logout: () => Promise<void>
  initialize: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isInitialized: false,

  login(user) {
    set({ user })
  },

  async logout() {
    try {
      await apiLogout()
    } catch {
      // cookie cleared server-side on best-effort basis
    }
    set({ user: null })
  },

  async initialize() {
    try {
      const { email, is_admin } = await refresh()
      set({
        user: { id: '', email, name: email.split('@')[0], is_admin },
        isInitialized: true,
      })
    } catch {
      set({ user: null, isInitialized: true })
    }
  },
}))
