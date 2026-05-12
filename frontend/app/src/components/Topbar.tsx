import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

interface TopbarProps {
  onSearch?: () => void
}

export default function Topbar({ onSearch }: TopbarProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const route = location.pathname

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className="brand" style={{ fontSize: 12 }}>
          <span className="brand-mark" />
          <span>PURE.STUDY</span>
        </div>
        <span style={{ width: 1, height: 16, background: 'var(--border)' }} />
        <span
          className={`nav-link ${route === '/courses' ? 'active' : ''}`}
          onClick={() => navigate('/courses')}
        >
          Dashboard
        </span>
        <span
          className={`nav-link ${route.startsWith('/courses/') ? 'active' : ''}`}
          onClick={() => navigate('/courses')}
        >
          Courses
        </span>
        <span
          className={`nav-link ${route === '/graph' ? 'active' : ''}`}
          onClick={() => navigate('/graph')}
        >
          Graph
        </span>
      </div>
      <div className="topbar-right">
        {route === '/graph' && onSearch && (
          <div className="searchbar-trigger" onClick={onSearch}>
            <span style={{ color: 'var(--text-mute)' }}>⌕</span>
            <span className="label">Search topics…</span>
            <span className="kbd">⌘K</span>
          </div>
        )}
        <span style={{ fontSize: 12, color: 'var(--text-mute)', cursor: 'pointer' }} onClick={handleLogout}>
          {user?.name ?? 'account'}
        </span>
        <div className="avatar-pill">{(user?.name ?? 'A')[0].toUpperCase()}</div>
      </div>
    </div>
  )
}
