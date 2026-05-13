import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Topbar from '../../components/Topbar'
import { deleteUser, getUser, type AdminUser } from '../../api/users'
import { useFlashStore } from '../../store/flash'

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const flash = useFlashStore((s) => s.show)
  const [user, setUser] = useState<AdminUser | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    getUser(id).then(setUser).catch((e) => setError(e?.response?.data?.detail || 'Not found'))
  }, [id])

  async function handleDelete() {
    if (!user) return
    if (!window.confirm(`Delete ${user.email}?`)) return
    try {
      await deleteUser(user.id)
      flash(`Deleted ${user.email}`, 'success')
      navigate('/admin/users')
    } catch (e: any) {
      flash(e?.response?.data?.detail || 'Delete failed', 'error')
    }
  }

  return (
    <div className="app-shell">
      <Topbar />
      <div style={{ padding: '24px 32px' }}>
        <div style={{ marginBottom: 18 }}>
          <span onClick={() => navigate('/admin/users')} style={{ cursor: 'pointer', fontSize: 12, color: 'var(--text-mute)' }}>← All users</span>
        </div>
        {error && <div style={{ color: '#ef4444' }}>{error}</div>}
        {!user && !error && <div style={{ color: 'var(--text-mute)' }}>Loading…</div>}
        {user && (
          <div style={{ maxWidth: 520 }}>
            <h1 style={{ margin: '0 0 4px', fontSize: 24, fontWeight: 500, letterSpacing: '-0.02em' }}>
              {user.full_name || user.email}
            </h1>
            <div style={{ color: 'var(--text-mute)', fontSize: 13, marginBottom: 22 }}>{user.email}</div>

            <dl style={{ display: 'grid', gridTemplateColumns: '140px 1fr', gap: '10px 16px', background: 'var(--surface)', border: '1px solid var(--border)', padding: 18, margin: 0 }}>
              {[
                ['Program', user.program ?? '—'],
                ['Year of study', user.year_of_study ?? '—'],
                ['Status', user.status],
                ['Created', new Date(user.created_at).toLocaleString()],
                ['User ID', user.id],
              ].map(([k, v]) => (
                <div key={String(k)} style={{ display: 'contents' }}>
                  <dt style={{ color: 'var(--text-mute)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{k}</dt>
                  <dd style={{ margin: 0, fontSize: 14 }}>{v}</dd>
                </div>
              ))}
            </dl>

            <div style={{ display: 'flex', gap: 8, marginTop: 18 }}>
              <button onClick={() => navigate(`/admin/users/${user.id}/edit`)} style={{ background: '#3b82f6', border: '1px solid #3b82f6', color: '#fff', padding: '8px 16px', fontSize: 13, cursor: 'pointer' }}>Edit</button>
              <button onClick={() => void handleDelete()} style={{ background: 'transparent', border: '1px solid #5a1a1a', color: '#ef4444', padding: '8px 16px', fontSize: 13, cursor: 'pointer' }}>Delete</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
