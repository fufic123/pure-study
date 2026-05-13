import { useEffect, useState } from 'react'
import Topbar from '../../components/Topbar'
import AdminNav from '../../components/AdminNav'
import { listAllEdges, type AdminEdge } from '../../api/admin'
import { listUsers, type AdminUser } from '../../api/users'

const EDGE_COLOR: Record<string, string> = {
  CONTAINS: '#3b82f6',
  REQUIRES: '#f59e0b',
}

export default function EdgesListPage() {
  const [edges, setEdges] = useState<AdminEdge[]>([])
  const [emailMap, setEmailMap] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [typeFilter, setTypeFilter] = useState('all')

  useEffect(() => {
    Promise.all([listAllEdges(), listUsers()])
      .then(([e, u]: [AdminEdge[], AdminUser[]]) => {
        setEdges(e)
        const map: Record<string, string> = {}
        u.forEach((x) => { map[x.id] = x.email })
        setEmailMap(map)
        setError(null)
      })
      .catch((e) => setError(e?.response?.data?.detail || 'Failed to load'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = typeFilter === 'all' ? edges : edges.filter((e) => e.edge_type === typeFilter)
  const types = Array.from(new Set(edges.map((e) => e.edge_type)))

  return (
    <div className="app-shell">
      <Topbar />
      <AdminNav />
      <div style={{ padding: '24px 32px', overflow: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 24, fontWeight: 500, letterSpacing: '-0.02em' }}>Edges</h1>
            <p style={{ margin: '4px 0 18px', color: 'var(--text-mute)', fontSize: 13 }}>
              All relationships in FalkorDB — {filtered.length} of {edges.length} shown
            </p>
          </div>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 10px', fontSize: 12 }}
          >
            <option value="all">All types</option>
            {types.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        {loading && <div style={{ color: 'var(--text-mute)' }}>Loading…</div>}
        {error && <div style={{ color: '#ef4444' }}>{error}</div>}
        {!loading && !error && (
          <table style={{ width: '100%', borderCollapse: 'collapse', background: 'var(--surface)', border: '1px solid var(--border)' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)' }}>
                {['Type', 'From', 'To', 'Owner'].map((h) => (
                  <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontSize: 11, color: 'var(--text-mute)', textTransform: 'uppercase', letterSpacing: '0.06em', borderBottom: '1px solid var(--border)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={4} style={{ padding: 14, color: 'var(--text-mute)', fontStyle: 'italic' }}>No edges.</td></tr>
              ) : filtered.map((e, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '10px 14px' }}>
                    <span style={{
                      padding: '2px 8px', fontSize: 10, fontFamily: 'var(--font-mono)',
                      border: `1px solid ${EDGE_COLOR[e.edge_type] || 'var(--border)'}`,
                      color: EDGE_COLOR[e.edge_type] || 'var(--text-dim)',
                      letterSpacing: '0.04em',
                    }}>{e.edge_type}</span>
                  </td>
                  <td style={{ padding: '10px 14px', fontSize: 13 }}>
                    {e.from_name || <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-mute)' }}>{e.from_id.slice(0, 8)}…</span>}
                  </td>
                  <td style={{ padding: '10px 14px', fontSize: 13 }}>
                    {e.to_name || <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-mute)' }}>{e.to_id.slice(0, 8)}…</span>}
                  </td>
                  <td style={{ padding: '10px 14px', fontSize: 12, color: 'var(--text-dim)' }}>
                    {emailMap[e.user_id] || e.user_id.slice(0, 8) + '…'}
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
