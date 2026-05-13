import { useLocation, useNavigate } from 'react-router-dom'

const tabs = [
  { path: '/admin/users', label: 'Users (Postgres)' },
  { path: '/admin/courses', label: 'Courses (FalkorDB)' },
  { path: '/admin/topics', label: 'Topics (FalkorDB)' },
  { path: '/admin/edges', label: 'Edges (FalkorDB)' },
]

export default function AdminNav() {
  const navigate = useNavigate()
  const location = useLocation()
  return (
    <div
      style={{
        display: 'flex',
        gap: 4,
        borderBottom: '1px solid var(--border)',
        padding: '0 32px',
        background: 'var(--surface)',
      }}
    >
      {tabs.map((t) => {
        const active = location.pathname === t.path || location.pathname.startsWith(t.path + '/')
        return (
          <button
            key={t.path}
            onClick={() => navigate(t.path)}
            style={{
              background: 'transparent',
              border: 'none',
              borderBottom: active ? '2px solid #f59e0b' : '2px solid transparent',
              color: active ? 'var(--text)' : 'var(--text-mute)',
              padding: '12px 16px',
              fontSize: 12,
              fontFamily: 'var(--font-mono)',
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
              cursor: 'pointer',
            }}
          >
            {t.label}
          </button>
        )
      })}
    </div>
  )
}
