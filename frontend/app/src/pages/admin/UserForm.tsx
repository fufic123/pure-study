import { useState } from 'react'
import type { UserStatus } from '../../api/users'

const NAME_RE = /^[A-Za-zА-Яа-яЁё .'\-]{2,120}$/
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export interface UserFormValues {
  email: string
  password?: string
  full_name: string
  program: string
  year_of_study: number
  status: UserStatus
}

interface Props {
  initial?: Partial<UserFormValues>
  requirePassword: boolean
  submitLabel: string
  onSubmit: (v: UserFormValues) => Promise<void>
  onCancel: () => void
}

export default function UserForm({ initial, requirePassword, submitLabel, onSubmit, onCancel }: Props) {
  const [email, setEmail] = useState(initial?.email ?? '')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState(initial?.full_name ?? '')
  const [program, setProgram] = useState(initial?.program ?? '')
  const [year, setYear] = useState<string>(initial?.year_of_study?.toString() ?? '1')
  const [status, setStatus] = useState<UserStatus>(initial?.status ?? 'active')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [submitting, setSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  function validate(): boolean {
    const e: Record<string, string> = {}
    if (!email.trim()) e.email = 'Email is required'
    else if (!EMAIL_RE.test(email)) e.email = 'Email format looks wrong'
    if (requirePassword) {
      if (!password) e.password = 'Password is required'
      else if (password.length < 8) e.password = 'Password must be at least 8 characters'
    }
    if (!fullName.trim()) e.full_name = 'Full name is required'
    else if (!NAME_RE.test(fullName.trim())) e.full_name = 'Use letters, spaces, dots, apostrophes or hyphens'
    if (!program.trim()) e.program = 'Program is required'
    const y = parseInt(year, 10)
    if (!Number.isFinite(y) || y < 1 || y > 10) e.year_of_study = 'Year must be between 1 and 10'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleSubmit(ev: React.FormEvent) {
    ev.preventDefault()
    setServerError(null)
    if (!validate()) return
    setSubmitting(true)
    try {
      const payload: UserFormValues = {
        email: email.trim(),
        full_name: fullName.trim(),
        program: program.trim(),
        year_of_study: parseInt(year, 10),
        status,
      }
      if (requirePassword || password) payload.password = password
      await onSubmit(payload)
    } catch (e: any) {
      const detail = e?.response?.data?.detail
      setServerError(typeof detail === 'string' ? detail : detail?.[0]?.msg ?? 'Failed to save')
    } finally {
      setSubmitting(false)
    }
  }

  const field = (label: string, key: string, input: React.ReactNode) => (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: 'block', fontSize: 11, color: 'var(--text-mute)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 5 }}>{label}</label>
      {input}
      {errors[key] && <div style={{ color: '#ef4444', fontSize: 12, marginTop: 4 }}>{errors[key]}</div>}
    </div>
  )

  const inputStyle: React.CSSProperties = {
    width: '100%',
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    color: 'var(--text)',
    padding: '8px 10px',
    fontSize: 14,
    fontFamily: 'inherit',
  }

  return (
    <form onSubmit={(e) => void handleSubmit(e)} style={{ maxWidth: 520 }}>
      {serverError && (
        <div style={{ color: '#f87171', fontSize: 13, marginBottom: 14, padding: '8px 12px', border: '1px solid #3a1a1a', background: '#1a0a0a' }}>
          {serverError}
        </div>
      )}
      {field('Email', 'email', (
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} style={inputStyle} placeholder="you@example.com" />
      ))}
      {requirePassword && field('Password', 'password', (
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={inputStyle} placeholder="At least 8 characters" />
      ))}
      {field('Full name', 'full_name', (
        <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} style={inputStyle} placeholder="Jane Doe" />
      ))}
      {field('Program / Department', 'program', (
        <input type="text" value={program} onChange={(e) => setProgram(e.target.value)} style={inputStyle} placeholder="Computer Science" />
      ))}
      {field('Year of study', 'year_of_study', (
        <input type="number" min={1} max={10} value={year} onChange={(e) => setYear(e.target.value)} style={inputStyle} />
      ))}
      {field('Status', 'status', (
        <select value={status} onChange={(e) => setStatus(e.target.value as UserStatus)} style={inputStyle}>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      ))}

      <div style={{ display: 'flex', gap: 8, marginTop: 18 }}>
        <button type="submit" disabled={submitting} style={{ background: '#3b82f6', border: '1px solid #3b82f6', color: '#fff', padding: '8px 16px', fontSize: 13, cursor: 'pointer' }}>
          {submitting ? '…' : submitLabel}
        </button>
        <button type="button" onClick={onCancel} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-dim)', padding: '8px 16px', fontSize: 13, cursor: 'pointer' }}>
          Cancel
        </button>
      </div>
    </form>
  )
}
