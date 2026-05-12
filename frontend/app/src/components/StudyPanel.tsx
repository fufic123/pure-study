import { useState, useEffect, useRef } from 'react'
import type { Topic, Message } from '../types'
import { explain as apiExplain, copilot as apiCopilot } from '../api/ai'
import ComplexityMeter from './ComplexityMeter'
import Markdown from './Markdown'

interface StudyPanelProps {
  topic: Topic
  onClose: () => void
  onTransition: (topicId: string, action: 'open' | 'master') => void
  accent: string
  typewriterSpeed: number
}

const STATUS_INFO: Record<Topic['status'], { label: string; color: string }> = {
  mastered: { label: 'Mastered', color: '#22c55e' },
  in_progress: { label: 'In Progress', color: '#f59e0b' },
  available: { label: 'Available', color: '#3b82f6' },
  locked: { label: 'Locked', color: '#2a2a2a' },
}

export default function StudyPanel({
  topic,
  onClose,
  onTransition,
  accent,
  typewriterSpeed,
}: StudyPanelProps) {
  const [level, setLevel] = useState<1 | 2 | 3>(1)
  const [explanationText, setExplanationText] = useState('')
  const [explainTyping, setExplainTyping] = useState(true)
  const [copilotMsgs, setCopilotMsgs] = useState<{ role: 'user' | 'ai'; text: string }[]>([])
  const [composer, setComposer] = useState('')
  const [aiTyping, setAiTyping] = useState(false)
  const [aiTypingText, setAiTypingText] = useState('')
  const [pendingFull, setPendingFull] = useState<string | null>(null)
  const [apiHistory, setApiHistory] = useState<Message[]>([])
  const scrollRef = useRef<HTMLDivElement>(null)

  // Reset on topic change
  useEffect(() => {
    setLevel(1)
    setCopilotMsgs([])
    setComposer('')
    setAiTyping(false)
    setPendingFull(null)
    setApiHistory([])
  }, [topic.id])

  // Load explanation when topic or level changes
  useEffect(() => {
    setExplainTyping(true)
    setExplanationText('')
    let cancelled = false

    apiExplain(topic.id, level)
      .then(({ text }) => {
        if (!cancelled) {
          setExplanationText(text)
          setExplainTyping(false)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setExplanationText('Failed to load explanation.')
          setExplainTyping(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [topic.id, level])

  // Typewriter effect for copilot
  useEffect(() => {
    if (!pendingFull) return
    let i = 0
    setAiTypingText('')
    const interval = setInterval(() => {
      i += 1
      setAiTypingText(pendingFull.slice(0, i))
      if (i >= pendingFull.length) {
        clearInterval(interval)
        setCopilotMsgs((m) => [...m, { role: 'ai', text: pendingFull }])
        setAiTyping(false)
        setPendingFull(null)
        setAiTypingText('')
      }
    }, typewriterSpeed)
    return () => clearInterval(interval)
  }, [pendingFull, typewriterSpeed])

  // Auto-scroll copilot
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [copilotMsgs, aiTypingText])

  async function handleSendCopilot() {
    if (!composer.trim() || aiTyping) return
    const userMsg = composer.trim()
    setCopilotMsgs((m) => [...m, { role: 'user', text: userMsg }])
    setComposer('')
    setAiTyping(true)

    const newHistory: Message[] = [...apiHistory, { role: 'user', content: userMsg }]
    try {
      const { reply, history } = await apiCopilot(topic.id, apiHistory, userMsg)
      setApiHistory(history)
      setPendingFull(reply)
    } catch {
      setCopilotMsgs((m) => [...m, { role: 'ai', text: 'Sorry, something went wrong.' }])
      setApiHistory(newHistory)
      setAiTyping(false)
    }
  }

  const statusInfo = { ...STATUS_INFO[topic.status], color: topic.status === 'available' ? accent : STATUS_INFO[topic.status].color }

  const suggestedQuestions = [
    'Give me a simple example',
    'What does this connect to?',
    'What are common mistakes?',
  ]

  return (
    <div className="study-panel" key={topic.id}>
      <div className="study-head">
        <div className="row">
          <h2>{topic.name}</h2>
          <button className="close-btn" onClick={onClose} title="Close">
            ×
          </button>
        </div>
        <div className="row" style={{ gap: 12 }}>
          <span className="status-badge">
            <span className="dot" style={{ background: statusInfo.color }} />
            {statusInfo.label}
          </span>
          <ComplexityMeter value={topic.complexity} />
        </div>
      </div>

      <div className="study-body">
        <div className="section explanation">
          <div className="section-head">
            <span className="section-title">Explanation</span>
            <div className="level-row">
              {([1, 2, 3] as const).map((l) => (
                <span key={l} className={`level-pip ${l <= level ? 'on' : ''}`} title={`Level ${l}`} />
              ))}
              <span className="section-title" style={{ marginLeft: 4 }}>
                L{level}/3
              </span>
            </div>
          </div>
          <div className="explanation-text">
            {explainTyping ? (
              <div className="typing">
                <span />
                <span />
                <span />
              </div>
            ) : (
              <Markdown text={explanationText} />
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
                disabled={explainTyping}
              >
                I don&apos;t get it · go deeper
              </button>
            )}
            {level > 1 && (
              <button
                className="action-btn"
                onClick={() => setLevel((l) => Math.max(1, l - 1) as 1 | 2 | 3)}
                disabled={explainTyping}
              >
                ← Simpler
              </button>
            )}
          </div>
        </div>

        <div className="section copilot">
          <div className="copilot-head">
            <span className="section-title">Copilot</span>
            <span className="section-title" style={{ textTransform: 'none', color: 'var(--text-mute)' }}>
              Ask anything about this topic
            </span>
          </div>
          <div className="copilot-scroll" ref={scrollRef}>
            <div className="copilot-msgs">
              {copilotMsgs.length === 0 && !aiTyping && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {suggestedQuestions.map((q, i) => (
                    <button key={i} className="chip" style={{ textAlign: 'left' }} onClick={() => setComposer(q)}>
                      {q}
                    </button>
                  ))}
                </div>
              )}
              {copilotMsgs.map((m, i) => (
                <div key={i} className={`cop-msg ${m.role}`}>
                  {m.role === 'ai' && <div className="cop-meta">Copilot</div>}
                  <div className="cop-bubble">
                    {m.role === 'ai' ? <Markdown text={m.text} inline /> : m.text}
                  </div>
                </div>
              ))}
              {aiTyping && pendingFull && (
                <div className="cop-msg ai">
                  <div className="cop-meta">Copilot</div>
                  <div className="cop-bubble cursor-blink">
                    <Markdown text={aiTypingText} inline />
                  </div>
                </div>
              )}
              {aiTyping && !pendingFull && (
                <div className="cop-msg ai">
                  <div className="cop-meta">Copilot</div>
                  <div className="typing">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              )}
            </div>
          </div>
          <div className="copilot-composer">
            <input
              type="text"
              placeholder="Ask anything…"
              value={composer}
              onChange={(e) => setComposer(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') void handleSendCopilot()
              }}
              disabled={aiTyping}
            />
            <button
              className="send-btn"
              onClick={() => void handleSendCopilot()}
              disabled={!composer.trim() || aiTyping}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
