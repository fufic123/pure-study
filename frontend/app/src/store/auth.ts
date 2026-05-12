import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { clearTokens } from '../api/client'
import { refresh } from '../api/auth'
import type { User, AuthTokens } from '../types'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isInitialized: boolean
  login: (user: User, tokens: AuthTokens) => void
  logout: () => void
  setAccessToken: (token: string) => void
  initialize: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isInitialized: false,

      login(user, tokens) {
        localStorage.setItem('access_token', tokens.access_token)
        localStorage.setItem('refresh_token', tokens.refresh_token)
        set({
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
        })
      },

      logout() {
        clearTokens()
        set({ user: null, accessToken: null, refreshToken: null })
      },

      setAccessToken(token) {
        localStorage.setItem('access_token', token)
        set({ accessToken: token })
      },

      async initialize() {
        const stored = get()
        if (stored.accessToken) {
          // Token exists — try a silent refresh to validate it
          const rt = stored.refreshToken
          if (rt) {
            try {
              const { access_token } = await refresh(rt)
              get().setAccessToken(access_token)
            } catch {
              get().logout()
            }
          }
        }
        set({ isInitialized: true })
      },
    }),
    {
      name: 'pure-auth',
      partialize: (s) => ({
        user: s.user,
        accessToken: s.accessToken,
        refreshToken: s.refreshToken,
      }),
    },
  ),
)
