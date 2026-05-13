import Topbar from '../components/Topbar'

export default function AboutPage() {
  return (
    <div className="app-shell">
      <Topbar />
      <div style={{ padding: '32px', overflow: 'auto', maxWidth: 760, margin: '0 auto', color: 'var(--text)' }}>
        <h1 style={{ fontSize: 32, fontWeight: 500, letterSpacing: '-0.02em', margin: '0 0 6px' }}>About Pure Study</h1>
        <p style={{ color: 'var(--text-mute)', fontSize: 13, margin: 0, fontFamily: 'var(--font-mono)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          A personalised learning platform — built around a prerequisite graph
        </p>

        <h2 style={{ marginTop: 32 }}>What it does</h2>
        <p>
          Pure Study turns any subject into a personalised knowledge graph. You tell it what you want to
          master, your level, and your time budget; it builds a graph of topics, unlocks them in the right
          order, and walks you through each one with AI-generated explanations at three escalating levels
          of depth.
        </p>

        <h2 style={{ marginTop: 24 }}>How it works</h2>
        <ul style={{ paddingLeft: 22, lineHeight: 1.7 }}>
          <li><strong>Onboarding agent</strong> interviews you and constructs the initial graph.</li>
          <li><strong>Explanation agent</strong> produces level-1, level-2, level-3 walkthroughs of each topic.</li>
          <li><strong>Copilot agent</strong> answers follow-up questions, with awareness of what you've mastered.</li>
          <li><strong>Knowledge graph</strong> tracks state — locked, available, in-progress, mastered — and unlocks topics as their prerequisites are completed.</li>
        </ul>

        <h2 style={{ marginTop: 24 }}>Architecture</h2>
        <p>
          Microservices behind a single gateway: <code>auth</code> (Postgres + RS256 JWT in httpOnly cookies),
          <code> graph</code> (FalkorDB / Cypher), <code>ai</code> (Anthropic Claude), <code>material</code>
          (MIT OCW + Wikipedia scrapers), and <code>gateway</code> (rate-limited Redis-backed reverse proxy
          enforcing JWT). The frontend is a React 18 / Vite SPA served via Nginx, with a separate static
          landing page for SEO.
        </p>

        <h2 style={{ marginTop: 24 }}>Stack</h2>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text-dim)' }}>
          Python 3.12 · FastAPI · SQLAlchemy 2 · Postgres 16 · FalkorDB · Redis 7 · Anthropic Claude ·
          React 18 · Vite · D3.js · TypeScript · Docker Compose · Nginx
        </p>
      </div>
    </div>
  )
}
