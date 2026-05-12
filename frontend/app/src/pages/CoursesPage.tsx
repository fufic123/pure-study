import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listCourses } from '../api/graph'
import Topbar from '../components/Topbar'

export default function CoursesPage() {
  const navigate = useNavigate()
  const { data: courses = [], isLoading } = useQuery({
    queryKey: ['courses'],
    queryFn: listCourses,
  })

  return (
    <div className="app-shell">
      <Topbar />
      <div className="courses-view">
        <div className="courses-head">
          <div>
            <h1>Your courses</h1>
            <div className="sub">{courses.length} active</div>
          </div>
          <button
            className="btn btn-primary"
            style={{ width: 'auto', padding: '10px 16px' }}
            onClick={() => navigate('/onboarding')}
          >
            + New course
          </button>
        </div>

        {isLoading && (
          <div style={{ color: 'var(--text-mute)', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
            Loading courses…
          </div>
        )}

        <div className="courses-grid">
          {courses.map((c) => (
            <div key={c.id} className="course-card" onClick={() => navigate(`/courses/${c.id}`)}>
              <span className="course-domain">{c.domain}</span>
              <h3>{c.name}</h3>
              <p className="course-goal">{c.goal}</p>
            </div>
          ))}
          <div className="course-card new" onClick={() => navigate('/onboarding')}>
            <div style={{ fontSize: 28, fontWeight: 200, lineHeight: 1 }}>+</div>
            <div>Start a new course</div>
            <div
              style={{
                fontSize: 11,
                color: 'var(--text-mute)',
                fontFamily: 'var(--font-mono)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
              }}
            >
              Pure builds the graph
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
