import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Topbar from '../../components/Topbar'
import UserForm, { type UserFormValues } from './UserForm'
import { getUser, updateUser, type AdminUser } from '../../api/users'
import { useFlashStore } from '../../store/flash'

export default function UserEditPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const flash = useFlashStore((s) => s.show)
  const [user, setUser] = useState<AdminUser | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    getUser(id).then(setUser).catch((e) => setError(e?.response?.data?.detail || 'Not found'))
  }, [id])

  async function handleSubmit(v: UserFormValues) {
    if (!id) return
    await updateUser(id, {
      email: v.email,
      full_name: v.full_name,
      program: v.program,
      year_of_study: v.year_of_study,
      status: v.status,
    })
    flash('User updated.', 'success')
    navigate(`/admin/users/${id}`)
  }

  return (
    <div className="app-shell">
      <Topbar />
      <div style={{ padding: '24px 32px', overflow: 'auto' }}>
        <div style={{ marginBottom: 18 }}>
          <span onClick={() => navigate('/admin/users')} style={{ cursor: 'pointer', fontSize: 12, color: 'var(--text-mute)' }}>← All users</span>
        </div>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 500 }}>Edit user</h1>
        {error && <div style={{ color: '#ef4444', marginTop: 12 }}>{error}</div>}
        {!user && !error && <div style={{ color: 'var(--text-mute)', marginTop: 12 }}>Loading…</div>}
        {user && (
          <div style={{ marginTop: 18 }}>
            <UserForm
              initial={{
                email: user.email,
                full_name: user.full_name ?? '',
                program: user.program ?? '',
                year_of_study: user.year_of_study ?? 1,
                status: user.status,
              }}
              requirePassword={false}
              submitLabel="Save changes"
              onSubmit={handleSubmit}
              onCancel={() => navigate(`/admin/users/${user.id}`)}
            />
          </div>
        )}
      </div>
    </div>
  )
}
