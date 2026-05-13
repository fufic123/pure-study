import { useState } from 'react'
import Topbar from '../components/Topbar'
import { useFlashStore } from '../store/flash'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function ContactPage() {
  const flash = useFlashStore((s) => s.show)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [subject, setSubject] = useState('')
  const [message, setMessage] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [submitting, setSubmitting] = useState(false)

  function validate(): boolean {
    const e: Record<string, string> = {}
    if (!name.trim()) e.name = 'Required'
    if (!email.trim()) e.email = 'Required'
    else if (!EMAIL_RE.test(email)) e.email = 'Email format looks wrong'
    if (!subject.trim()) e.subject = 'Required'
    if (!message.trim() || message.trim().length < 10) e.message = 'Tell us a bit more (10+ chars)'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  function handleSubmit(ev: React.FormEvent) {
    ev.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    // UI-only — no backend endpoint. Pretend it went through.
    setTimeout(() => {
      flash('Thanks — your message has been queued. (UI-only demo.)', 'success', 4000)
      setName('')
      setEmail('')
      setSubject('')
      setMessage('')
      setSubmitting(false)
    }, 350)
  }

  const inputStyle: React.CSSProperties = {
    width: '100%',
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    color: 'var(--text)',
    padding: '8px 10px',
    fontSize: 14,
    fontFamily: 'inherit',
  }

  const field = (label: string, key: string, input: React.ReactNode) => (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: 'block', fontSize: 11, color: 'var(--text-mute)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 5 }}>{label}</label>
      {input}
      {errors[key] && <div style={{ color: '#ef4444', fontSize: 12, marginTop: 4 }}>{errors[key]}</div>}
    </div>
  )

  return (
    <div className="app-shell">
      <Topbar />
      <div style={{ padding: '32px', maxWidth: 560, margin: '0 auto', overflow: 'auto' }}>
        <h1 style={{ fontSize: 28, fontWeight: 500, letterSpacing: '-0.02em', margin: '0 0 6px' }}>Contact</h1>
        <p style={{ color: 'var(--text-mute)', fontSize: 13, margin: '0 0 22px' }}>
          Bug report, feature request, or just say hi.
        </p>
        <form onSubmit={handleSubmit} noValidate>
          {field('Name', 'name', (
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} style={inputStyle} placeholder="Jane Doe" />
          ))}
          {field('Email', 'email', (
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} style={inputStyle} placeholder="you@example.com" />
          ))}
          {field('Subject', 'subject', (
            <input type="text" value={subject} onChange={(e) => setSubject(e.target.value)} style={inputStyle} placeholder="What's this about?" />
          ))}
          {field('Message', 'message', (
            <textarea value={message} onChange={(e) => setMessage(e.target.value)} style={{ ...inputStyle, minHeight: 120, resize: 'vertical' }} placeholder="Tell us more…" />
          ))}
          <button type="submit" disabled={submitting} style={{ background: '#3b82f6', border: '1px solid #3b82f6', color: '#fff', padding: '9px 18px', fontSize: 13, cursor: 'pointer', marginTop: 6 }}>
            {submitting ? '…' : 'Send message'}
          </button>
        </form>
      </div>
    </div>
  )
}
