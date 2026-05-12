import { create } from 'zustand'
import { listTopics, transitionTopic } from '../api/graph'
import type { Topic, FlashEdge } from '../types'

interface TopicsState {
  topics: Topic[]
  recentIds: string[]
  flashEdgeIds: FlashEdge[]
  toast: string | null
  loadTopics: () => Promise<void>
  openTopic: (id: string) => Promise<void>
  masterTopic: (id: string) => Promise<void>
  addRecent: (id: string) => void
  setToast: (msg: string | null) => void
  setFlashEdges: (edges: FlashEdge[]) => void
}

export const useTopicsStore = create<TopicsState>((set, _get) => ({
  topics: [],
  recentIds: [],
  flashEdgeIds: [],
  toast: null,

  async loadTopics() {
    const topics = await listTopics()
    set({ topics })
  },

  async openTopic(id) {
    // Optimistic update
    set((s) => ({
      topics: s.topics.map((t) =>
        t.id === id && t.status === 'available' ? { ...t, status: 'in_progress' } : t,
      ),
    }))
    try {
      const updated = await transitionTopic(id, 'open')
      set((s) => ({
        topics: s.topics.map((t) => (t.id === id ? { ...updated } : t)),
      }))
    } catch {
      // Roll back optimistic update on error
      set((s) => ({
        topics: s.topics.map((t) =>
          t.id === id ? { ...t, status: 'available' } : t,
        ),
      }))
    }
  },

  async masterTopic(id) {
    // Optimistic update
    set((s) => ({
      topics: s.topics.map((t) =>
        t.id === id && t.status === 'in_progress' ? { ...t, status: 'mastered' } : t,
      ),
    }))
    try {
      const result = await transitionTopic(id, 'master')
      const unlocked = result.unlocked ?? []

      set((s) => {
        const updated = s.topics.map((t) => {
          if (t.id === id) return { ...result }
          if (unlocked.includes(t.id)) return { ...t, status: 'available' as const }
          return t
        })
        return { topics: updated }
      })

      if (unlocked.length > 0) {
        const flashEdges: FlashEdge[] = unlocked.map((to) => ({ from: id, to }))
        set({ flashEdgeIds: flashEdges })
        set({
          toast: `Mastered. ${unlocked.length} new topic${unlocked.length > 1 ? 's' : ''} unlocked.`,
        })
        setTimeout(() => set({ toast: null }), 3500)
        setTimeout(() => set({ flashEdgeIds: [] }), 1600)
      } else {
        set({ toast: 'Mastered.' })
        setTimeout(() => set({ toast: null }), 2000)
      }
    } catch {
      // Roll back
      set((s) => ({
        topics: s.topics.map((t) =>
          t.id === id ? { ...t, status: 'in_progress' } : t,
        ),
      }))
    }
  },

  addRecent(id) {
    set((s) => {
      const filtered = s.recentIds.filter((r) => r !== id)
      return { recentIds: [id, ...filtered].slice(0, 5) }
    })
  },

  setToast(msg) {
    set({ toast: msg })
  },

  setFlashEdges(edges) {
    set({ flashEdgeIds: edges })
  },
}))
