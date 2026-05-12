import { useState, useEffect, useRef } from 'react'
import type { Topic } from '../types'

interface CommandPaletteProps {
  topics: Topic[]
  accent: string
  onPick: (id: string) => void
  onClose: () => void
}

function statusColor(status: Topic['status'], accent: string): string {
  if (status === 'mastered') return '#22c55e'
  if (status === 'in_progress') return '#f59e0b'
  if (status === 'available') return accent
  return '#2a2a2a'
}

export default function CommandPalette({ topics, accent, onPick, onClose }: CommandPaletteProps) {
  const [q, setQ] = useState('')
  const [active, setActive] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const filtered = topics
    .filter((t) => t.name.toLowerCase().includes(q.toLowerCase()))
    .sort((a, b) => {
      const order: Record<Topic['status'], number> = {
        available: 0,
        in_progress: 1,
        mastered: 2,
        locked: 3,
      }
      return order[a.status] - order[b.status]
    })

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === 'Escape') onClose()
    else if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActive((i) => Math.min(i + 1, filtered.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActive((i) => Math.max(i - 1, 0))
    } else if (e.key === 'Enter') {
      const t = filtered[active]
      if (t) onPick(t.id)
    }
  }

  useEffect(() => {
    setActive(0)
  }, [q])

  return (
    <div className="cmdk-backdrop" onClick={onClose}>
      <div className="cmdk" onClick={(e) => e.stopPropagation()}>
        <div className="cmdk-input-wrap">
          <span style={{ color: 'var(--text-mute)', fontSize: 12, fontFamily: 'var(--font-mono)' }}>
            ⌘K
          </span>
          <input
            ref={inputRef}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Jump to a topic…"
          />
          <span className="kbd">esc</span>
        </div>
        <div className="cmdk-list">
          <div className="cmdk-section">Topics ({filtered.length})</div>
          {filtered.length === 0 && (
            <div className="cmdk-empty">No topics match &ldquo;{q}&rdquo;</div>
          )}
          {filtered.slice(0, 20).map((t, i) => (
            <div
              key={t.id}
              className={`cmdk-item ${i === active ? 'active' : ''}`}
              onMouseEnter={() => setActive(i)}
              onClick={() => onPick(t.id)}
            >
              <span className="dot" style={{ background: statusColor(t.status, accent) }} />
              <span className="cmdk-name">{t.name}</span>
              <span className="cmdk-tag">
                {t.status.replace('_', ' ')} · L{t.complexity}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
