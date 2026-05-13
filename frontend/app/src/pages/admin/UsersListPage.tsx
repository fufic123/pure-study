import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { deleteUser, listUsers, type AdminUser } from '../../api/users'
import { useFlashStore } from '../../store/flash'
import Topbar from '../../components/Topbar'

export default function UsersListPage() {
  const navigate = useNavigate()
  const flash = useFlashStore((s) => s.show)
  const [users, setUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function reload() {
    setLoading(true)
    try {
      setUsers(await listUsers())
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void reload()
  }, [])

  async function handleDelete(u: AdminUser) {
    if (!window.confirm(`Delete user ${u.email}? This cannot be undone.`)) return
    try {
      await deleteUser(u.id)
      flash(`Deleted ${u.email}`, 'success')
      void reload()
    } catch (e) {
      flash(e instanceof Error ? e.message : 'Delete failed', 'error')
    }
  }

  return (
    <div className="app-shell">
      <Topbar />
      <div style={{ padding: '24px 32px', overflow: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 18 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 24, fontWeight: 500, letterSpacing: '-0.02em' }}>Users</h1>
            <p style={{ margin: '4px 0 0', color: 'var(--text-mute)', fontSize: 13 }}>
              Admin management — {users.length} total
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <a
              className="btn"
              href="/auth/users/report.html"
              target="_blank"
              rel="noreferrer"
              style={{
                padding: '7px 12px',
                fontSize: 12,
                border: '1px solid var(--border)',
                color: 'var(--text-dim)',
                textDecoration: 'none',
              }}
            >
              XML/XSLT report ↗
            </a>
            <button
              onClick={() => navigate('/admin/users/new')}
              style={{
                padding: '7px 14px',
                background: '#3b82f6',
                border: '1px solid #3b82f6',
                color: '#fff',
                fontSize: 13,
                cursor: 'pointer',
              }}
            >
              + New user
            </button>
          </div>
        </div>

        {loading && <div style={{ color: 'var(--text-mute)' }}>Loading…</div>}
        {error && <div style={{ color: '#ef4444' }}>{error}</div>}

        {!loading && !error && (
          <table style={{ width: '100%', borderCollapse: 'collapse', background: 'var(--surface)', border: '1px solid var(--border)' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)' }}>
                {['Full name', 'Email', 'Program', 'Year', 'Status', 'Created', ''].map((h) => (
                  <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontSize: 11, color: 'var(--text-mute)', textTransform: 'uppercase', letterSpacing: '0.06em', borderBottom: '1px solid var(--border)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr><td colSpan={7} style={{ padding: 14, color: 'var(--text-mute)', fontStyle: 'italic' }}>No users yet.</td></tr>
              ) : users.map((u) => (
                <tr key={u.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '10px 14px' }}>
                    <a onClick={() => navigate(`/admin/users/${u.id}`)} style={{ cursor: 'pointer', color: 'var(--text)' }}>
                      {u.full_name || <span style={{ color: 'var(--text-mute)' }}>—</span>}
                    </a>
                  </td>
                  <td style={{ padding: '10px 14px', color: 'var(--text-dim)' }}>{u.email}</td>
                  <td style={{ padding: '10px 14px' }}>{u.program || <span style={{ color: 'var(--text-mute)' }}>—</span>}</td>
                  <td style={{ padding: '10px 14px' }}>{u.year_of_study ?? <span style={{ color: 'var(--text-mute)' }}>—</span>}</td>
                  <td style={{ padding: '10px 14px' }}>
                    <span style={{
                      padding: '2px 8px',
                      fontSize: 11,
                      fontFamily: 'var(--font-mono)',
                      border: '1px solid',
                      color: u.status === 'active' ? '#22c55e' : 'var(--text-mute)',
                      borderColor: u.status === 'active' ? 'rgba(34,197,94,0.4)' : 'var(--border)',
                    }}>{u.status}</span>
                  </td>
                  <td style={{ padding: '10px 14px', color: 'var(--text-mute)', fontSize: 12 }}>{u.created_at.slice(0, 10)}</td>
                  <td style={{ padding: '10px 14px', textAlign: 'right' }}>
                    <button onClick={() => navigate(`/admin/users/${u.id}/edit`)} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-dim)', padding: '3px 8px', fontSize: 11, cursor: 'pointer', marginRight: 6 }}>Edit</button>
                    <button onClick={() => void handleDelete(u)} style={{ background: 'transparent', border: '1px solid #5a1a1a', color: '#ef4444', padding: '3px 8px', fontSize: 11, cursor: 'pointer' }}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
