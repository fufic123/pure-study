import { useState, useEffect, useRef, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getCourse } from '../api/graph'
import { explain as apiExplain, copilot as apiCopilot } from '../api/ai'
import { useTopicsStore } from '../store/topics'
import Topbar from '../components/Topbar'
import GraphView from '../components/GraphView'
import ComplexityMeter from '../components/ComplexityMeter'
import Markdown from '../components/Markdown'
import Toast from '../components/Toast'
import type { Topic, Message } from '../types'

const ACCENT = '#3b82f6'
const TYPEWRITER_SPEED = 18
const DENSITY = 1

// ─── Explanation block ────────────────────────────────────────────────────────
interface ExplanationBlockProps {
  topic: Topic
  onTransition: (id: string, action: 'open' | 'master') => void
}

function ExplanationBlock({ topic, onTransition }: ExplanationBlockProps) {
  const [level, setLevel] = useState<1 | 2 | 3>(1)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    setText('')
    let cancelled = false
    apiExplain(topic.id, level)
      .then(({ text: t }) => {
        if (!cancelled) {
          setText(t)
          setLoading(false)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setText('Failed to load explanation.')
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [topic.id, level])

  return (
    <div className="explanation-block">
      <div className="section-head">
        <span className="section-title">Explanation</span>
        <div className="level-row">
          {([1, 2, 3] as const).map((l) => (
            <span key={l} className={`level-pip ${l <= level ? 'on' : ''}`} />
          ))}
          <span className="section-title" style={{ marginLeft: 4 }}>
            L{level}/3
          </span>
        </div>
      </div>
      <div className="explanation-text">
        {loading ? (
          <div className="typing">
            <span />
            <span />
            <span />
          </div>
        ) : (
          <Markdown text={text} />
        )}
      </div>
      <div className="explanation-actions">
        {topic.status === 'available' && (
          <button className="action-btn start" onClick={() => onTransition(topic.id, 'open')}>
            Start studying →
          </button>
        )}
        {topic.status === 'in_progress' && (
          <button
            className="action-btn start"
            style={{ background: '#22c55e', borderColor: '#22c55e' }}
            onClick={() => onTransition(topic.id, 'master')}
          >
            Mark as mastered ✓
          </button>
        )}
        {level < 3 && (
          <button
            className="action-btn"
            onClick={() => setLevel((l) => Math.min(3, l + 1) as 1 | 2 | 3)}
            disabled={loading}
          >
            I don&apos;t get it · go deeper
          </button>
        )}
        {level > 1 && (
          <button
            className="action-btn"
            onClick={() => setLevel((l) => Math.max(1, l - 1) as 1 | 2 | 3)}
            disabled={loading}
          >
            ← Simpler
          </button>
        )}
      </div>
    </div>
  )
}

// ─── Copilot chat ─────────────────────────────────────────────────────────────
interface CopilotChatProps {
  topic: Topic
}

function CopilotChat({ topic }: CopilotChatProps) {
  const [msgs, setMsgs] = useState<{ role: 'user' | 'ai'; text: string }[]>([
    {
      role: 'ai',
      text: `Hi — I'm your AI tutor for **${topic.name}**.\n\nAsk me anything: clarifications, examples, common pitfalls, or "quiz me."`,
    },
  ])
  const [composer, setComposer] = useState('')
  const [pendingFull, setPendingFull] = useState<string | null>(null)
  const [typingText, setTypingText] = useState('')
  const [waiting, setWaiting] = useState(false)
  const [apiHistory, setApiHistory] = useState<Message[]>([])
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [msgs, typingText])

  useEffect(() => {
    if (!pendingFull) return
    let i = 0
    setTypingText('')
    const id = setInterval(() => {
      i++
      setTypingText(pendingFull.slice(0, i))
      if (i >= pendingFull.length) {
        clearInterval(id)
        setMsgs((m) => [...m, { role: 'ai', text: pendingFull }])
        setPendingFull(null)
        setWaiting(false)
        setTypingText('')
      }
    }, TYPEWRITER_SPEED)
    return () => clearInterval(id)
  }, [pendingFull])

  async function send(textOverride?: string) {
    const text = textOverride ?? composer.trim()
    if (!text || waiting) return
    setMsgs((m) => [...m, { role: 'user', text }])
    setComposer('')
    setWaiting(true)

    try {
      const { reply, history } = await apiCopilot(topic.id, apiHistory, text)
      setApiHistory(history)
      setPendingFull(reply)
    } catch {
      setMsgs((m) => [...m, { role: 'ai', text: 'Sorry, something went wrong.' }])
      setWaiting(false)
    }
  }

  const suggested = ['Give me an example', 'What does this connect to?', 'Quiz me']

  return (
    <div className="cp-chat-inner">
      <div className="cp-chat-head">
        <div>
          <span className="section-title">AI Tutor</span>
          <div className="cp-chat-topic">on {topic.name}</div>
        </div>
        <span className="cp-chat-status">
          <span className="cp-chat-pulse" />
          Online
        </span>
      </div>
      <div className="cp-chat-scroll" ref={scrollRef}>
        {msgs.map((m, i) => (
          <div key={i} className={`cop-msg ${m.role}`}>
            {m.role === 'ai' && <div className="cop-meta">Pure</div>}
            <div className="cop-bubble">
              {m.role === 'ai' ? <Markdown text={m.text} inline /> : m.text}
            </div>
          </div>
        ))}
        {pendingFull && (
          <div className="cop-msg ai">
            <div className="cop-meta">Pure</div>
            <div className="cop-bubble cursor-blink">
              <Markdown text={typingText} inline />
            </div>
          </div>
        )}
        {waiting && !pendingFull && (
          <div className="cop-msg ai">
            <div className="cop-meta">Pure</div>
            <div className="typing">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
        {msgs.length === 1 && !waiting && (
          <div className="cp-suggested">
            {suggested.map((q, i) => (
              <button key={i} className="chip" onClick={() => void send(q)}>
                {q}
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="cp-chat-composer">
        <input
          type="text"
          placeholder={waiting ? 'Pure is typing…' : 'Ask anything…'}
          value={composer}
          onChange={(e) => setComposer(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') void send()
          }}
          disabled={waiting}
        />
        <button
          className="send-btn"
          onClick={() => void send()}
          disabled={!composer.trim() || waiting}
        >
          Send
        </button>
      </div>
    </div>
  )
}

// ─── Course Page ──────────────────────────────────────────────────────────────
export default function CoursePage() {
  const { courseId } = useParams<{ courseId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { openTopic, masterTopic, addRecent, recentIds, flashEdgeIds, toast } = useTopicsStore()

  const { data: course, isLoading } = useQuery({
    queryKey: ['course', courseId],
    queryFn: () => getCourse(courseId!),
    enabled: !!courseId,
  })

  const topics = course?.topics ?? []

  const initialId = useMemo(() => {
    const inProgress = topics.find((t) => t.status === 'in_progress')
    if (inProgress) return inProgress.id
    const available = topics.find((t) => t.status === 'available')
    return available?.id ?? topics[0]?.id ?? null
  }, [topics])

  const [currentId, setCurrentId] = useState<string | null>(null)

  useEffect(() => {
    if (!currentId && initialId) setCurrentId(initialId)
  }, [initialId, currentId])

  const currentTopic = topics.find((t) => t.id === currentId)

  function handlePickTopic(id: string) {
    const t = topics.find((x) => x.id === id)
    if (!t || t.status === 'locked') return
    setCurrentId(id)
    addRecent(id)
  }

  async function handleTransition(id: string, action: 'open' | 'master') {
    if (action === 'open') await openTopic(id)
    else await masterTopic(id)
    await queryClient.invalidateQueries({ queryKey: ['course', courseId] })
  }

  if (isLoading) {
    return (
      <div className="app-shell">
        <Topbar />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-mute)' }}>
          Loading…
        </div>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="app-shell">
        <Topbar />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-mute)' }}>
          Course not found.{' '}
          <span style={{ cursor: 'pointer', color: 'var(--text)', marginLeft: 8 }} onClick={() => navigate('/courses')}>
            Go back
          </span>
        </div>
      </div>
    )
  }

  const masteredCount = topics.filter((t) => t.status === 'mastered').length

  return (
    <div className="app-shell">
      <Topbar />
      <div className="course-page">
        {/* LEFT: materials list */}
        <aside className="cp-materials">
          <div className="cp-course-head">
            <span className="course-domain">{course.domain}</span>
            <h2>{course.name}</h2>
            <p className="cp-goal">{course.goal}</p>
            <div className="cp-progress-row">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${topics.length ? (masteredCount / topics.length) * 100 : 0}%` }}
                />
              </div>
              <div className="progress-meta">
                <span>
                  {masteredCount}/{topics.length} mastered
                </span>
                <span>{topics.length ? Math.round((masteredCount / topics.length) * 100) : 0}%</span>
              </div>
            </div>
          </div>
          <div className="cp-materials-head">
            <span className="section-title">Materials · {topics.length} topics</span>
          </div>
          <div className="cp-materials-list">
            {topics.map((t) => (
              <button
                key={t.id}
                className={`material-row ${t.id === currentId ? 'active' : ''} ${t.status === 'locked' ? 'locked' : ''}`}
                onClick={() => handlePickTopic(t.id)}
                disabled={t.status === 'locked'}
                title={t.status === 'locked' ? 'Complete prerequisites first' : ''}
              >
                <span
                  className="material-status"
                  style={{
                    background:
                      t.status === 'mastered'
                        ? '#22c55e'
                        : t.status === 'in_progress'
                          ? '#f59e0b'
                          : t.status === 'available'
                            ? ACCENT
                            : 'transparent',
                    border: t.status === 'locked' ? '1px solid var(--border-strong)' : 'none',
                  }}
                />
                <span className="material-name">{t.name}</span>
                <span className="material-complexity">L{t.complexity}</span>
              </button>
            ))}
          </div>
        </aside>

        {/* CENTER: graph + explanation */}
        <main className="cp-center">
          <div className="cp-center-head">
            <div>
              <span className="section-title">Now studying</span>
              <h2 className="cp-topic-name">{currentTopic?.name ?? '—'}</h2>
            </div>
            <div className="cp-topic-meta">
              {currentTopic && (
                <>
                  <span className="status-badge">
                    <span
                      className="dot"
                      style={{
                        background:
                          currentTopic.status === 'mastered'
                            ? '#22c55e'
                            : currentTopic.status === 'in_progress'
                              ? '#f59e0b'
                              : ACCENT,
                      }}
                    />
                    {currentTopic.status.replace('_', ' ')}
                  </span>
                  <ComplexityMeter value={currentTopic.complexity} />
                </>
              )}
            </div>
          </div>

          <div className="cp-graph-wrap">
            <span className="cp-graph-label">Knowledge graph</span>
            <GraphView
              topics={topics}
              accent={ACCENT}
              density={DENSITY}
              showMinimap={false}
              onSelectTopic={handlePickTopic}
              selectedId={currentId}
              recentIds={recentIds}
              flashEdgeIds={flashEdgeIds}
              compact
            />
          </div>

          {currentTopic && (
            <div className="cp-explanation">
              <ExplanationBlock
                key={currentTopic.id}
                topic={currentTopic}
                onTransition={(id, action) => void handleTransition(id, action)}
              />
            </div>
          )}
        </main>

        {/* RIGHT: AI chat */}
        <aside className="cp-chat">
          {currentTopic && <CopilotChat key={currentTopic.id} topic={currentTopic} />}
        </aside>
      </div>

      {toast && <Toast message={toast} />}
    </div>
  )
}
