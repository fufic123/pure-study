import { useEffect, useState } from 'react'
import Topbar from '../../components/Topbar'
import AdminNav from '../../components/AdminNav'
import { listAllTopics, type AdminTopic } from '../../api/admin'
import { listUsers, type AdminUser } from '../../api/users'

const STATUS_COLOR: Record<string, string> = {
  locked: 'var(--text-mute)',
  available: '#3b82f6',
  in_progress: '#f59e0b',
  mastered: '#22c55e',
}

export default function TopicsListPage() {
  const [topics, setTopics] = useState<AdminTopic[]>([])
  const [emailMap, setEmailMap] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    Promise.all([listAllTopics(), listUsers()])
      .then(([t, u]: [AdminTopic[], AdminUser[]]) => {
        setTopics(t)
        const map: Record<string, string> = {}
        u.forEach((x) => { map[x.id] = x.email })
        setEmailMap(map)
        setError(null)
      })
      .catch((e) => setError(e?.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = statusFilter === 'all' ? topics : topics.filter((t) => t.status === statusFilter)

  return (
    <div className="app-shell">
      <Topbar />
      <AdminNav />
      <div style={{ padding: '24px 32px', overflow: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 24, fontWeight: 500, letterSpacing: '-0.02em' }}>Topics</h1>
            <p style={{ margin: '4px 0 18px', color: 'var(--text-mute)', fontSize: 13 }}>
              All Topic nodes across every user graph — {filtered.length} of {topics.length} shown
            </p>
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 10px', fontSize: 12 }}
          >
            <option value="all">All statuses</option>
            <option value="locked">Locked</option>
            <option value="available">Available</option>
            <option value="in_progress">In progress</option>
            <option value="mastered">Mastered</option>
          </select>
        </div>

        {loading && <div style={{ color: 'var(--text-mute)' }}>Loading…</div>}
        {error && <div style={{ color: '#ef4444' }}>{error}</div>}
        {!loading && !error && (
          <table style={{ width: '100%', borderCollapse: 'collapse', background: 'var(--surface)', border: '1px solid var(--border)' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)' }}>
                {['Name', 'Status', 'L', 'Cx', 'Course', 'Prereqs', 'Owner'].map((h) => (
                  <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontSize: 11, color: 'var(--text-mute)', textTransform: 'uppercase', letterSpacing: '0.06em', borderBottom: '1px solid var(--border)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={7} style={{ padding: 14, color: 'var(--text-mute)', fontStyle: 'italic' }}>No topics match the filter.</td></tr>
              ) : filtered.map((t) => (
                <tr key={`${t.user_id}-${t.id}`} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '10px 14px' }}>
                    <div>{t.name}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-mute)', fontFamily: 'var(--font-mono)', marginTop: 2 }}>{t.slug}</div>
                  </td>
                  <td style={{ padding: '10px 14px' }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ width: 8, height: 8, borderRadius: '50%', background: STATUS_COLOR[t.status] || 'var(--text-mute)' }} />
                      <span style={{ fontSize: 12, color: 'var(--text-dim)' }}>{t.status.replace('_', ' ')}</span>
                    </span>
                  </td>
                  <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)', fontSize: 12 }}>{t.explanation_level}/3</td>
                  <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)', fontSize: 12 }}>{t.complexity}</td>
                  <td style={{ padding: '10px 14px', fontSize: 13, color: 'var(--text-dim)' }}>
                    {t.course_name || <span style={{ color: 'var(--text-mute)' }}>—</span>}
                  </td>
                  <td style={{ padding: '10px 14px', fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-mute)' }}>
                    {t.prereqs.length === 0 ? '—' : t.prereqs.length}
                  </td>
                  <td style={{ padding: '10px 14px', fontSize: 12, color: 'var(--text-dim)' }}>
                    {emailMap[t.user_id] || t.user_id.slice(0, 8) + '…'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
