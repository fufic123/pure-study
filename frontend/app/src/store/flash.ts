import { create } from 'zustand'

export type FlashKind = 'success' | 'error' | 'info'

interface FlashState {
  message: string | null
  kind: FlashKind
  show: (message: string, kind?: FlashKind, ttlMs?: number) => void
  clear: () => void
}

let timer: number | null = null

export const useFlashStore = create<FlashState>((set) => ({
  message: null,
  kind: 'info',
  show(message, kind = 'info', ttlMs = 3500) {
    if (timer !== null) {
      window.clearTimeout(timer)
      timer = null
    }
    set({ message, kind })
    timer = window.setTimeout(() => {
      set({ message: null })
      timer = null
    }, ttlMs)
  },
  clear() {
    if (timer !== null) {
      window.clearTimeout(timer)
      timer = null
    }
    set({ message: null })
  },
}))
