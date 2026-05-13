import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import { useFlashStore } from '../store/flash'

interface TopbarProps {
  onSearch?: () => void
}

export default function Topbar({ onSearch }: TopbarProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const flash = useFlashStore((s) => s.show)
  const route = location.pathname

  async function handleLogout() {
    await logout()
    flash('You have been logged out.', 'info')
    navigate('/login')
  }

  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className="brand" style={{ fontSize: 12, cursor: 'pointer' }} onClick={() => navigate('/courses')}>
          <span className="brand-mark" />
          <span>PURE.STUDY</span>
        </div>
        <span style={{ width: 1, height: 16, background: 'var(--border)' }} />
        <span
          className={`nav-link ${route === '/courses' ? 'active' : ''}`}
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
        <span
          className={`nav-link ${route === '/about' ? 'active' : ''}`}
          onClick={() => navigate('/about')}
        >
          About
        </span>
        <span
          className={`nav-link ${route === '/contact' ? 'active' : ''}`}
          onClick={() => navigate('/contact')}
        >
          Contact
        </span>
        {user?.is_admin && (
          <span
            className={`nav-link ${route.startsWith('/admin') ? 'active' : ''}`}
            onClick={() => navigate('/admin/users')}
            style={{ color: '#f59e0b' }}
            title="Admin area"
          >
            Admin
          </span>
        )}
      </div>
      <div className="topbar-right">
        {route === '/graph' && onSearch && (
          <div className="searchbar-trigger" onClick={onSearch}>
            <span style={{ color: 'var(--text-mute)' }}>⌕</span>
            <span className="label">Search topics…</span>
            <span className="kbd">⌘K</span>
          </div>
        )}
        {user ? (
          <>
            <span style={{ fontSize: 12, color: 'var(--text-mute)' }}>{user.email}</span>
            <div className="avatar-pill">{(user.name[0] || 'A').toUpperCase()}</div>
            <button
              onClick={() => void handleLogout()}
              style={{
                background: 'transparent',
                border: '1px solid var(--border)',
                color: 'var(--text-dim)',
                padding: '4px 10px',
                fontSize: 11,
                fontFamily: 'var(--font-mono)',
                letterSpacing: '0.04em',
                textTransform: 'uppercase',
                cursor: 'pointer',
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <button
            onClick={() => navigate('/login')}
            style={{
              background: '#3b82f6',
              border: '1px solid #3b82f6',
              color: '#fff',
              padding: '4px 14px',
              fontSize: 11,
              fontFamily: 'var(--font-mono)',
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
              cursor: 'pointer',
            }}
          >
            Sign in
          </button>
        )}
      </div>
    </div>
  )
}
