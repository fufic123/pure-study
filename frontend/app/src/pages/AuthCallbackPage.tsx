import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import type { User } from '../types'

export default function AuthCallbackPage() {
  const navigate = useNavigate()
  const loginStore = useAuthStore((s) => s.login)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const accessToken = params.get('access_token')
    const refreshToken = params.get('refresh_token')

    if (!accessToken || !refreshToken) {
      navigate('/login', { replace: true })
      return
    }

    // Decode email from JWT payload (base64 middle part)
    let email = ''
    try {
      const payload = JSON.parse(atob(accessToken.split('.')[1]))
      email = payload.sub ?? ''
    } catch {
      // ignore decode errors
    }

    const user: User = { id: '', email, name: email.split('@')[0] || 'User' }
    loginStore(user, { access_token: accessToken, refresh_token: refreshToken })
    navigate('/courses', { replace: true })
  }, [])

  return (
    <div
      style={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--text-mute)',
        fontFamily: 'var(--font-mono)',
        fontSize: 12,
      }}
    >
      Signing you in…
    </div>
  )
}
