import { useFlashStore } from '../store/flash'

export default function FlashBanner() {
  const message = useFlashStore((s) => s.message)
  const kind = useFlashStore((s) => s.kind)
  const clear = useFlashStore((s) => s.clear)
  if (!message) return null

  const color = kind === 'success' ? '#22c55e' : kind === 'error' ? '#ef4444' : '#3b82f6'
  return (
    <div
      style={{
        position: 'fixed',
        top: 16,
        left: '50%',
        transform: 'translateX(-50%)',
        background: 'rgba(10,10,10,0.95)',
        border: `1px solid ${color}`,
        color: '#f1f1f1',
        padding: '10px 18px',
        fontSize: 13,
        zIndex: 9999,
        cursor: 'pointer',
        maxWidth: 520,
        backdropFilter: 'blur(8px)',
      }}
      onClick={clear}
      role="status"
      aria-live="polite"
    >
      <span style={{ color, marginRight: 8, fontFamily: 'var(--font-mono)', fontSize: 11 }}>
        {kind.toUpperCase()}
      </span>
      {message}
    </div>
  )
}
