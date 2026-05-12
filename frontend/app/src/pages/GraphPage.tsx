import { useState, useEffect } from 'react'
import { useTopicsStore } from '../store/topics'
import Topbar from '../components/Topbar'
import GraphView from '../components/GraphView'
import StudyPanel from '../components/StudyPanel'
import CommandPalette from '../components/CommandPalette'
import Toast from '../components/Toast'

const ACCENT = '#3b82f6'
const DENSITY = 1
const TYPEWRITER_SPEED = 18

export default function GraphPage() {
  const { topics, recentIds, flashEdgeIds, toast, loadTopics, openTopic, masterTopic, addRecent } =
    useTopicsStore()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [showCmdk, setShowCmdk] = useState(false)

  useEffect(() => {
    if (topics.length === 0) {
      void loadTopics()
    }
  }, [topics.length, loadTopics])

  // Keyboard shortcuts
  useEffect(() => {
    function handle(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setShowCmdk((s) => !s)
      }
      if (e.key === 'Escape') {
        if (showCmdk) setShowCmdk(false)
        else if (selectedId) setSelectedId(null)
      }
    }
    window.addEventListener('keydown', handle)
    return () => window.removeEventListener('keydown', handle)
  }, [showCmdk, selectedId])

  function handleSelectTopic(id: string) {
    const t = topics.find((x) => x.id === id)
    if (!t || t.status === 'locked') return
    setSelectedId(id)
    setShowCmdk(false)
    addRecent(id)
  }

  async function handleTransition(id: string, action: 'open' | 'master') {
    if (action === 'open') await openTopic(id)
    else await masterTopic(id)
  }

  const selectedTopic = topics.find((t) => t.id === selectedId) ?? null

  return (
    <div className="app-shell">
      <Topbar onSearch={() => setShowCmdk(true)} />
      <div className={`graph-view ${selectedTopic ? 'with-panel' : ''}`}>
        <GraphView
          topics={topics}
          accent={ACCENT}
          density={DENSITY}
          showMinimap
          onSelectTopic={handleSelectTopic}
          selectedId={selectedId}
          recentIds={recentIds}
          flashEdgeIds={flashEdgeIds}
        />
        {selectedTopic && (
          <StudyPanel
            topic={selectedTopic}
            onClose={() => setSelectedId(null)}
            onTransition={(id, action) => void handleTransition(id, action)}
            accent={ACCENT}
            typewriterSpeed={TYPEWRITER_SPEED}
          />
        )}
      </div>

      {showCmdk && (
        <CommandPalette
          topics={topics}
          accent={ACCENT}
          onPick={handleSelectTopic}
          onClose={() => setShowCmdk(false)}
        />
      )}

      {toast && <Toast message={toast} />}
    </div>
  )
}
