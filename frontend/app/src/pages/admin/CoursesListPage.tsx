import { useEffect, useState } from 'react'
import Topbar from '../../components/Topbar'
import AdminNav from '../../components/AdminNav'
import { listAllCourses, type AdminCourse } from '../../api/admin'
import { listUsers, type AdminUser } from '../../api/users'

export default function CoursesListPage() {
  const [courses, setCourses] = useState<AdminCourse[]>([])
  const [emailMap, setEmailMap] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([listAllCourses(), listUsers()])
      .then(([c, u]: [AdminCourse[], AdminUser[]]) => {
        setCourses(c)
        const map: Record<string, string> = {}
        u.forEach((x) => { map[x.id] = x.email })
        setEmailMap(map)
        setError(null)
      })
      .catch((e) => setError(e?.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="app-shell">
      <Topbar />
      <AdminNav />
      <div style={{ padding: '24px 32px', overflow: 'auto' }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 500, letterSpacing: '-0.02em' }}>Courses</h1>
        <p style={{ margin: '4px 0 18px', color: 'var(--text-mute)', fontSize: 13 }}>
          All Course nodes across every user graph in FalkorDB — {courses.length} total
        </p>
        {loading && <div style={{ color: 'var(--text-mute)' }}>Loading…</div>}
        {error && <div style={{ color: '#ef4444' }}>{error}</div>}
        {!loading && !error && (
          <table style={{ width: '100%', borderCollapse: 'collapse', background: 'var(--surface)', border: '1px solid var(--border)' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)' }}>
                {['Name', 'Goal', 'Domain', 'Owner', 'Course ID'].map((h) => (
                  <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontSize: 11, color: 'var(--text-mute)', textTransform: 'uppercase', letterSpacing: '0.06em', borderBottom: '1px solid var(--border)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {courses.length === 0 ? (
                <tr><td colSpan={5} style={{ padding: 14, color: 'var(--text-mute)', fontStyle: 'italic' }}>No courses anywhere yet.</td></tr>
              ) : courses.map((c) => (
                <tr key={c.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '10px 14px' }}>{c.name}</td>
                  <td style={{ padding: '10px 14px', color: 'var(--text-dim)', fontSize: 13 }}>{c.goal}</td>
                  <td style={{ padding: '10px 14px' }}>
                    <span style={{ padding: '2px 8px', fontSize: 11, fontFamily: 'var(--font-mono)', border: '1px solid var(--border)', color: 'var(--text-dim)' }}>{c.domain}</span>
                  </td>
                  <td style={{ padding: '10px 14px', fontSize: 12, color: 'var(--text-dim)' }}>
                    {emailMap[c.user_id] || c.user_id.slice(0, 8) + '…'}
                  </td>
                  <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-mute)' }}>{c.id.slice(0, 8)}…</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
