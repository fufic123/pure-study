import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/auth'
import AuthPage from './pages/AuthPage'
import AuthCallbackPage from './pages/AuthCallbackPage'
import OnboardingPage from './pages/OnboardingPage'
import CoursesPage from './pages/CoursesPage'
import CoursePage from './pages/CoursePage'
import GraphPage from './pages/GraphPage'
import AboutPage from './pages/AboutPage'
import ContactPage from './pages/ContactPage'
import UsersListPage from './pages/admin/UsersListPage'
import UserNewPage from './pages/admin/UserNewPage'
import UserDetailPage from './pages/admin/UserDetailPage'
import UserEditPage from './pages/admin/UserEditPage'
import CoursesListPage from './pages/admin/CoursesListPage'
import TopicsListPage from './pages/admin/TopicsListPage'
import EdgesListPage from './pages/admin/EdgesListPage'
import FlashBanner from './components/FlashBanner'

function Loading() {
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
      Loading…
    </div>
  )
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user)
  const isInitialized = useAuthStore((s) => s.isInitialized)
  if (!isInitialized) return <Loading />
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function RequireAdmin({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user)
  const isInitialized = useAuthStore((s) => s.isInitialized)
  if (!isInitialized) return <Loading />
  if (!user) return <Navigate to="/login" replace />
  if (!user.is_admin) return <Navigate to="/courses" replace />
  return <>{children}</>
}

export default function App() {
  const initialize = useAuthStore((s) => s.initialize)

  useEffect(() => {
    void initialize()
  }, [initialize])

  return (
    <>
      <FlashBanner />
      <Routes>
        {/* Public */}
        <Route path="/login" element={<AuthPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />

        {/* Authenticated */}
        <Route path="/onboarding" element={<RequireAuth><OnboardingPage /></RequireAuth>} />
        <Route path="/courses" element={<RequireAuth><CoursesPage /></RequireAuth>} />
        <Route path="/courses/:courseId" element={<RequireAuth><CoursePage /></RequireAuth>} />
        <Route path="/graph" element={<RequireAuth><GraphPage /></RequireAuth>} />

        {/* Admin */}
        <Route path="/admin" element={<Navigate to="/admin/users" replace />} />
        <Route path="/admin/users" element={<RequireAdmin><UsersListPage /></RequireAdmin>} />
        <Route path="/admin/users/new" element={<RequireAdmin><UserNewPage /></RequireAdmin>} />
        <Route path="/admin/users/:id" element={<RequireAdmin><UserDetailPage /></RequireAdmin>} />
        <Route path="/admin/users/:id/edit" element={<RequireAdmin><UserEditPage /></RequireAdmin>} />
        <Route path="/admin/courses" element={<RequireAdmin><CoursesListPage /></RequireAdmin>} />
        <Route path="/admin/topics" element={<RequireAdmin><TopicsListPage /></RequireAdmin>} />
        <Route path="/admin/edges" element={<RequireAdmin><EdgesListPage /></RequireAdmin>} />

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </>
  )
}
