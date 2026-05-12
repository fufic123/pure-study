// Auth, Onboarding, Courses, Command Palette screens
const { useState: useStateAux, useEffect: useEffectAux, useRef: useRefAux } = React;

// ============ Login / Register ============
function AuthScreen({ mode, onAuthed, onSwitch }) {
  const [email, setEmail] = useStateAux(mode === "login" ? "alex@purestudy.app" : "");
  const [password, setPassword] = useStateAux(mode === "login" ? "••••••••" : "");
  const [name, setName] = useStateAux("");
  const [loading, setLoading] = useStateAux(false);

  function handleSubmit(e) {
    e?.preventDefault();
    setLoading(true);
    setTimeout(() => onAuthed({ email, name: name || email.split("@")[0], isNew: mode === "register" }), 600);
  }

  return (
    <div className="auth-shell">
      <div className="auth-aside">
        <div className="brand">
          <span className="brand-mark"></span>
          <span>PURE.STUDY</span>
        </div>
        <div className="auth-tagline">
          <h1>Learn anything as a graph, not a list.</h1>
          <p>Pure builds you a personalized prerequisite graph for any subject — then explains, quizzes, and unlocks topics as you grow.</p>
        </div>
        <div className="auth-meta">
          <span>v0.4 · prototype</span>
          <span>36 nodes loaded</span>
        </div>
      </div>
      <div className="auth-form-wrap">
        <form className="auth-form" onSubmit={handleSubmit}>
          <h2>{mode === "login" ? "Welcome back" : "Create your account"}</h2>
          <p className="sub">{mode === "login" ? "Continue building your knowledge graph." : "Free during the prototype."}</p>

          {mode === "register" && (
            <div className="field">
              <label>Name</label>
              <input value={name} onChange={e => setName(e.target.value)} placeholder="Your name" required />
            </div>
          )}
          <div className="field">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="field">
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "…" : (mode === "login" ? "Sign in" : "Create account")}
          </button>

          <div className="divider">or</div>

          <button type="button" className="btn btn-ghost" onClick={handleSubmit}>
            <GoogleIcon /> Continue with Google
          </button>

          <div className="auth-switch">
            {mode === "login" ? (
              <>New to Pure? <a onClick={() => onSwitch("register")}>Create an account</a></>
            ) : (
              <>Already have an account? <a onClick={() => onSwitch("login")}>Sign in</a></>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
      <path d="M21.6 12.2c0-.7-.1-1.4-.2-2H12v3.8h5.4c-.2 1.3-.9 2.4-2 3.1v2.6h3.3c1.9-1.8 3-4.4 3-7.5z" fill="#fff" opacity="0.9"/>
      <path d="M12 22c2.7 0 5-.9 6.6-2.4l-3.2-2.5c-.9.6-2 1-3.4 1-2.6 0-4.8-1.8-5.6-4.1H3.1v2.6C4.7 19.7 8.1 22 12 22z" fill="#fff" opacity="0.6"/>
      <path d="M6.4 14c-.2-.6-.3-1.3-.3-2s.1-1.4.3-2V7.4H3.1C2.4 8.8 2 10.4 2 12s.4 3.2 1.1 4.6L6.4 14z" fill="#fff" opacity="0.4"/>
      <path d="M12 5.9c1.5 0 2.8.5 3.8 1.5l2.9-2.9C16.9 2.9 14.7 2 12 2 8.1 2 4.7 4.3 3.1 7.4L6.4 10c.8-2.3 3-4.1 5.6-4.1z" fill="#fff" opacity="0.7"/>
    </svg>
  );
}

// ============ Onboarding ============
function Onboarding({ onComplete, embedded }) {
  const [history, setHistory] = useStateAux([OC_DATA.ONBOARDING_SCRIPT[0]]);
  const [step, setStep] = useStateAux(1);
  const [composer, setComposer] = useStateAux("");
  const [aiTyping, setAiTyping] = useStateAux(false);
  const [done, setDone] = useStateAux(false);
  const scrollRef = useRefAux(null);

  useEffectAux(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [history, aiTyping]);

  const expectedUserMsg = OC_DATA.ONBOARDING_SCRIPT[step]?.role === "user" ? OC_DATA.ONBOARDING_SCRIPT[step] : null;

  function sendUser(textOverride) {
    const text = textOverride ?? composer.trim();
    if (!text) return;
    const userMsg = { role: "user", text };
    setHistory(h => [...h, userMsg]);
    setComposer("");

    // Find the next AI msg in script
    const nextAiIdx = step + 1;
    const aiMsg = OC_DATA.ONBOARDING_SCRIPT[nextAiIdx];
    if (aiMsg) {
      setAiTyping(true);
      setTimeout(() => {
        setHistory(h => [...h, aiMsg]);
        setAiTyping(false);
        setStep(nextAiIdx + 1);
        if (aiMsg.done) setDone(true);
      }, 1100);
    } else {
      setStep(s => s + 1);
    }
  }

  return (
    <div className="onboarding" style={embedded ? {height: "100%"} : {}}>
      {!embedded && (
        <div className="onboarding-header">
          <div className="brand"><span className="brand-mark"></span><span>PURE.STUDY · ONBOARDING</span></div>
          <div className="onboarding-progress">Step {Math.min(Math.ceil(step/2)+1, 4)} of 4</div>
        </div>
      )}
      <div className="chat-scroll" ref={scrollRef}>
        <div className="chat-inner">
          {history.map((m, i) => (
            <div key={i} className={`bubble-row ${m.role}`}>
              {m.role === "ai" && <div className="avatar ai">P</div>}
              <div className={`bubble ${m.role}`}>{m.text}</div>
              {m.role === "user" && <div className="avatar">YOU</div>}
            </div>
          ))}
          {aiTyping && (
            <div className="bubble-row ai">
              <div className="avatar ai">P</div>
              <div className="typing"><span></span><span></span><span></span></div>
            </div>
          )}
        </div>
      </div>
      <div className="composer-wrap">
        {!done && expectedUserMsg && !aiTyping && (
          <div className="suggested-replies">
            <button className="chip" onClick={() => sendUser(expectedUserMsg.text)}>{expectedUserMsg.text}</button>
          </div>
        )}
        {done && (
          <div className="suggested-replies" style={{justifyContent: "center"}}>
            <button className="btn btn-primary" style={{maxWidth: 240}} onClick={onComplete}>
              Open my graph →
            </button>
          </div>
        )}
        {!done && (
          <div className="composer">
            <textarea
              placeholder={aiTyping ? "Pure is typing…" : "Type your reply…"}
              value={composer}
              onChange={e => setComposer(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendUser(); }}}
              disabled={aiTyping}
              rows={1}
            />
            <button className="send-btn" disabled={!composer.trim() || aiTyping} onClick={() => sendUser()}>
              Send
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ============ Courses ============
function CoursesView({ courses, onOpen, onNew }) {
  return (
    <div className="courses-view">
      <div className="courses-head">
        <div>
          <h1>Your courses</h1>
          <div className="sub">{courses.length} active · {courses.reduce((a, c) => a + c.mastered, 0)} topics mastered</div>
        </div>
        <button className="btn btn-primary" style={{width: "auto", padding: "10px 16px"}} onClick={onNew}>
          + New course
        </button>
      </div>
      <div className="courses-grid">
        {courses.map(c => (
          <div key={c.id} className="course-card" onClick={() => onOpen(c.id)}>
            <span className="course-domain">{c.domain}</span>
            <h3>{c.name}</h3>
            <p className="course-goal">{c.goal}</p>
            <div className="course-progress">
              <div className="progress-bar">
                <div className="progress-fill" style={{width: `${(c.mastered / c.total) * 100}%`}}></div>
              </div>
              <div className="progress-meta">
                <span>{c.mastered} / {c.total} mastered</span>
                <span>{Math.round((c.mastered / c.total) * 100)}%</span>
              </div>
            </div>
          </div>
        ))}
        <div className="course-card new" onClick={onNew}>
          <div style={{fontSize: 28, fontWeight: 200, lineHeight: 1}}>+</div>
          <div>Start a new course</div>
          <div style={{fontSize: 11, color: "var(--text-mute)", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.08em"}}>
            Pure builds the graph
          </div>
        </div>
      </div>
    </div>
  );
}

// ============ Command Palette (⌘K) ============
function CommandPalette({ topics, onPick, onClose, accent }) {
  const [q, setQ] = useStateAux("");
  const [active, setActive] = useStateAux(0);
  const inputRef = useRefAux(null);

  useEffectAux(() => { inputRef.current?.focus(); }, []);

  const filtered = topics
    .filter(t => t.name.toLowerCase().includes(q.toLowerCase()))
    .sort((a, b) => {
      const order = { available: 0, in_progress: 1, mastered: 2, locked: 3 };
      return order[a.status] - order[b.status];
    });

  function handleKey(e) {
    if (e.key === "Escape") onClose();
    else if (e.key === "ArrowDown") { e.preventDefault(); setActive(i => Math.min(i + 1, filtered.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive(i => Math.max(i - 1, 0)); }
    else if (e.key === "Enter") { if (filtered[active]) onPick(filtered[active].id); }
  }

  useEffectAux(() => { setActive(0); }, [q]);

  return (
    <div className="cmdk-backdrop" onClick={onClose}>
      <div className="cmdk" onClick={e => e.stopPropagation()}>
        <div className="cmdk-input-wrap">
          <span style={{color: "var(--text-mute)", fontSize: 12, fontFamily: "var(--font-mono)"}}>⌘K</span>
          <input
            ref={inputRef}
            value={q}
            onChange={e => setQ(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Jump to a topic…"
          />
          <span className="kbd">esc</span>
        </div>
        <div className="cmdk-list">
          <div className="cmdk-section">Topics ({filtered.length})</div>
          {filtered.length === 0 && <div className="cmdk-empty">No topics match "{q}"</div>}
          {filtered.slice(0, 20).map((t, i) => (
            <div
              key={t.id}
              className={`cmdk-item ${i === active ? "active" : ""}`}
              onMouseEnter={() => setActive(i)}
              onClick={() => onPick(t.id)}
            >
              <span className="dot" style={{background: t.status === "available" ? accent : t.status === "mastered" ? "#22c55e" : t.status === "in_progress" ? "#f59e0b" : "#2a2a2a"}}></span>
              <span className="cmdk-name">{t.name}</span>
              <span className="cmdk-tag">{t.status.replace("_", " ")} · L{t.complexity}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

window.AuthScreen = AuthScreen;
window.Onboarding = Onboarding;
window.CoursesView = CoursesView;
window.CommandPalette = CommandPalette;
