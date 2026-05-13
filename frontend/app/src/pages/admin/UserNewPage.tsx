import { useNavigate } from 'react-router-dom'
import Topbar from '../../components/Topbar'
import UserForm, { type UserFormValues } from './UserForm'
import { createUser } from '../../api/users'
import { useFlashStore } from '../../store/flash'

export default function UserNewPage() {
  const navigate = useNavigate()
  const flash = useFlashStore((s) => s.show)

  async function handleSubmit(v: UserFormValues) {
    await createUser({
      email: v.email,
      password: v.password!,
      full_name: v.full_name,
      program: v.program,
      year_of_study: v.year_of_study,
      status: v.status,
    })
    flash('User created.', 'success')
    navigate('/admin/users')
  }

  return (
    <div className="app-shell">
      <Topbar />
      <div style={{ padding: '24px 32px', overflow: 'auto' }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 500 }}>New user</h1>
        <p style={{ color: 'var(--text-mute)', fontSize: 13, marginBottom: 22 }}>
          Admin creates the record. The user will be able to sign in with the email and password right away.
        </p>
        <UserForm
          requirePassword
          submitLabel="Create user"
          onSubmit={handleSubmit}
          onCancel={() => navigate('/admin/users')}
        />
      </div>
    </div>
  )
}
