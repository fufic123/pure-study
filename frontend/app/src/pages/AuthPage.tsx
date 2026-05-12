import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login as apiLogin, register as apiRegister, getGoogleAuthUrl } from '../api/auth'
import { useAuthStore } from '../store/auth'
import type { User } from '../types'

function GoogleIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
      <path
        d="M21.6 12.2c0-.7-.1-1.4-.2-2H12v3.8h5.4c-.2 1.3-.9 2.4-2 3.1v2.6h3.3c1.9-1.8 3-4.4 3-7.5z"
        fill="#fff"
        opacity="0.9"
      />
      <path
        d="M12 22c2.7 0 5-.9 6.6-2.4l-3.2-2.5c-.9.6-2 1-3.4 1-2.6 0-4.8-1.8-5.6-4.1H3.1v2.6C4.7 19.7 8.1 22 12 22z"
        fill="#fff"
        opacity="0.6"
      />
      <path
        d="M6.4 14c-.2-.6-.3-1.3-.3-2s.1-1.4.3-2V7.4H3.1C2.4 8.8 2 10.4 2 12s.4 3.2 1.1 4.6L6.4 14z"
        fill="#fff"
        opacity="0.4"
      />
      <path
        d="M12 5.9c1.5 0 2.8.5 3.8 1.5l2.9-2.9C16.9 2.9 14.7 2 12 2 8.1 2 4.7 4.3 3.1 7.4L6.4 10c.8-2.3 3-4.1 5.6-4.1z"
        fill="#fff"
        opacity="0.7"
      />
    </svg>
  )
}

export default function AuthPage() {
  const navigate = useNavigate()
  const loginStore = useAuthStore((s) => s.login)
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      let tokens
      let user: User
      if (mode === 'login') {
        tokens = await apiLogin(email, password)
        // Decode user from token or use email as fallback
        user = { id: '', email, name: email.split('@')[0] }
      } else {
        tokens = await apiRegister(email, password, name)
        user = { id: '', email, name: name || email.split('@')[0] }
      }
      loginStore(user, tokens)
      if (mode === 'register') {
        navigate('/onboarding')
      } else {
        navigate('/courses')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-aside">
        <div className="brand">
          <span className="brand-mark" />
          <span>PURE.STUDY</span>
        </div>
        <div className="auth-tagline">
          <h1>Learn anything as a graph, not a list.</h1>
          <p>
            Pure builds you a personalized prerequisite graph for any subject — then explains,
            quizzes, and unlocks topics as you grow.
          </p>
        </div>
        <div className="auth-meta">
          <span>v0.4 · prototype</span>
          <span>knowledge graph</span>
        </div>
      </div>
      <div className="auth-form-wrap">
        <form className="auth-form" onSubmit={(e) => void handleSubmit(e)}>
          <h2>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
          <p className="sub">
            {mode === 'login'
              ? 'Continue building your knowledge graph.'
              : 'Free during the prototype.'}
          </p>

          {error && (
            <div
              style={{
                color: '#f87171',
                fontSize: 13,
                marginBottom: 14,
                padding: '8px 12px',
                border: '1px solid #3a1a1a',
                background: '#1a0a0a',
              }}
            >
              {error}
            </div>
          )}

          {mode === 'register' && (
            <div className="field">
              <label>Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required
              />
            </div>
          )}
          <div className="field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>
          <div className="field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>

          <div className="divider">or</div>

          <button
            type="button"
            className="btn btn-ghost"
            disabled={googleLoading}
            onClick={() => {
              setGoogleLoading(true)
              setError(null)
              getGoogleAuthUrl()
                .then((url) => { window.location.href = url })
                .catch(() => {
                  setError('Could not reach Google. Try again.')
                  setGoogleLoading(false)
                })
            }}
          >
            <GoogleIcon /> {googleLoading ? '…' : 'Continue with Google'}
          </button>

          <div className="auth-switch">
            {mode === 'login' ? (
              <>
                New to Pure?{' '}
                <a onClick={() => setMode('register')}>Create an account</a>
              </>
            ) : (
              <>
                Already have an account?{' '}
                <a onClick={() => setMode('login')}>Sign in</a>
              </>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}
