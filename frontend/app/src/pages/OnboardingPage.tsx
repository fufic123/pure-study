import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { onboardingMessage } from '../api/ai'
import type { Message } from '../types'

interface ChatMessage {
  role: 'user' | 'ai'
  text: string
}

export default function OnboardingPage() {
  const navigate = useNavigate()
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      role: 'ai',
      text: "Hi! I'm Pure — your AI study companion.\n\nI'll help you build a personalized knowledge graph. To get started: what subject would you like to master?",
    },
  ])
  const [apiHistory, setApiHistory] = useState<Message[]>([])
  const [composer, setComposer] = useState('')
  const [aiTyping, setAiTyping] = useState(false)
  const [done, setDone] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const step = Math.ceil(chatHistory.length / 2)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [chatHistory, aiTyping])

  async function sendMessage(textOverride?: string) {
    const text = textOverride ?? composer.trim()
    if (!text || aiTyping) return
    setChatHistory((h) => [...h, { role: 'user', text }])
    setComposer('')
    setAiTyping(true)

    const newHistory: Message[] = [...apiHistory, { role: 'user', content: text }]
    try {
      const { reply, done: isDone } = await onboardingMessage(apiHistory, text)
      const updatedHistory: Message[] = [...newHistory, { role: 'assistant', content: reply }]
      setApiHistory(updatedHistory)
      setChatHistory((h) => [...h, { role: 'ai', text: reply }])
      if (isDone) setDone(true)
    } catch {
      setChatHistory((h) => [
        ...h,
        { role: 'ai', text: "I'm having trouble connecting. Please try again." },
      ])
      setApiHistory(newHistory)
    } finally {
      setAiTyping(false)
    }
  }

  return (
    <div className="onboarding">
      <div className="onboarding-header">
        <div className="brand">
          <span className="brand-mark" />
          <span>PURE.STUDY · ONBOARDING</span>
        </div>
        <div className="onboarding-progress">Step {Math.min(step, 4)} of 4</div>
      </div>

      <div className="chat-scroll" ref={scrollRef}>
        <div className="chat-inner">
          {chatHistory.map((m, i) => (
            <div key={i} className={`bubble-row ${m.role === 'user' ? 'user' : ''}`}>
              {m.role === 'ai' && <div className="avatar ai">P</div>}
              <div className={`bubble ${m.role === 'user' ? 'user' : ''}`}>
                {m.role === 'ai' ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.text}</ReactMarkdown>
                ) : (
                  m.text
                )}
              </div>
              {m.role === 'user' && <div className="avatar">YOU</div>}
            </div>
          ))}
          {aiTyping && (
            <div className="bubble-row">
              <div className="avatar ai">P</div>
              <div className="typing">
                <span />
                <span />
                <span />
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="composer-wrap">
        {done && (
          <div className="suggested-replies" style={{ justifyContent: 'center' }}>
            <button
              className="btn btn-primary"
              style={{ maxWidth: 240 }}
              onClick={() => navigate('/courses')}
            >
              Open my courses →
            </button>
          </div>
        )}
        {!done && (
          <div className="composer">
            <textarea
              placeholder={aiTyping ? 'Pure is typing…' : 'Type your reply…'}
              value={composer}
              onChange={(e) => setComposer(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  void sendMessage()
                }
              }}
              disabled={aiTyping}
              rows={1}
            />
            <button
              className="send-btn"
              disabled={!composer.trim() || aiTyping}
              onClick={() => void sendMessage()}
            >
              Send
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
