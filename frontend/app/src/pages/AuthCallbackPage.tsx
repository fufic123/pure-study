import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

export default function AuthCallbackPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const isInitialized = useAuthStore((s) => s.isInitialized)

  useEffect(() => {
    if (!isInitialized) return
    navigate(user ? '/courses' : '/login', { replace: true })
  }, [isInitialized, user, navigate])

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
