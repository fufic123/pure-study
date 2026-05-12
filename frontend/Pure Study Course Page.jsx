// Course Page — 3-column layout: materials | mini-graph progress | AI conversation
const { useState: useStateCP, useEffect: useEffectCP, useRef: useRefCP, useMemo: useMemoCP } = React;

function CoursePage({ course, topics, accent, typewriterSpeed, onTransition, density, recentIds, onAddRecent }) {
  // Pick "current" topic: the most recent in_progress, fallback to first available
  const initialCurrent = useMemoCP(() => {
    const recentInProgress = recentIds.map(id => topics.find(t => t.id === id)).find(t => t && t.status === "in_progress");
    if (recentInProgress) return recentInProgress.id;
    const inProgress = topics.find(t => t.status === "in_progress");
    if (inProgress) return inProgress.id;
    const available = topics.find(t => t.status === "available");
    return available?.id || topics[0]?.id;
  }, []);

  const [currentId, setCurrentId] = useStateCP(initialCurrent);
  const currentTopic = topics.find(t => t.id === currentId);

  function handlePickTopic(id) {
    const t = topics.find(x => x.id === id);
    if (!t || t.status === "locked") return;
    setCurrentId(id);
    onAddRecent(id);
  }

  return (
    <div className="course-page">
      {/* LEFT: Course header + materials list */}
      <aside className="cp-materials">
        <div className="cp-course-head">
          <span className="course-domain">{course.domain}</span>
          <h2>{course.name}</h2>
          <p className="cp-goal">{course.goal}</p>
          <div className="cp-progress-row">
            <div className="progress-bar">
              <div className="progress-fill" style={{width: `${(topics.filter(t=>t.status==='mastered').length / topics.length) * 100}%`}}></div>
            </div>
            <div className="progress-meta">
              <span>{topics.filter(t=>t.status==='mastered').length}/{topics.length} mastered</span>
              <span>{Math.round((topics.filter(t=>t.status==='mastered').length / topics.length) * 100)}%</span>
            </div>
          </div>
        </div>

        <div className="cp-materials-head">
          <span className="section-title">Materials · {topics.length} topics</span>
        </div>
        <div className="cp-materials-list">
          {topics.map(t => (
            <button
              key={t.id}
              className={`material-row ${t.id === currentId ? "active" : ""} ${t.status === "locked" ? "locked" : ""}`}
              onClick={() => handlePickTopic(t.id)}
              disabled={t.status === "locked"}
              title={t.status === "locked" ? "Complete prerequisites first" : ""}
            >
              <span
                className="material-status"
                style={{background: t.status === "mastered" ? "#22c55e" : t.status === "in_progress" ? "#f59e0b" : t.status === "available" ? accent : "transparent", border: t.status === "locked" ? "1px solid var(--border-strong)" : "none"}}
              ></span>
              <span className="material-name">{t.name}</span>
              <span className="material-complexity">L{t.complexity}</span>
            </button>
          ))}
        </div>
      </aside>

      {/* CENTER: Mini graph + topic header */}
      <main className="cp-center">
        <div className="cp-center-head">
          <div>
            <span className="section-title">Now studying</span>
            <h2 className="cp-topic-name">{currentTopic?.name}</h2>
          </div>
          <div className="cp-topic-meta">
            <span className="status-badge">
              <span className="dot" style={{background: currentTopic?.status === "mastered" ? "#22c55e" : currentTopic?.status === "in_progress" ? "#f59e0b" : accent}}></span>
              {currentTopic?.status.replace("_", " ")}
            </span>
            <ComplexityMeter value={currentTopic?.complexity || 1} />
          </div>
        </div>

        <div className="cp-graph-wrap">
          <span className="cp-graph-label">Knowledge graph</span>
          <GraphView
            topics={topics}
            accent={accent}
            density={density}
            showMinimap={false}
            onSelectTopic={handlePickTopic}
            selectedId={currentId}
            recentIds={recentIds}
            flashEdgeIds={[]}
            compact
          />
        </div>

        {currentTopic && (
          <div className="cp-explanation">
            <ExplanationBlock topic={currentTopic} accent={accent} onTransition={onTransition} />
          </div>
        )}
      </main>

      {/* RIGHT: Always-open AI conversation */}
      <aside className="cp-chat">
        <CopilotChat key={currentId} topic={currentTopic} typewriterSpeed={typewriterSpeed} accent={accent} />
      </aside>
    </div>
  );
}

// Compact explanation block for course page
function ExplanationBlock({ topic, accent, onTransition }) {
  const [level, setLevel] = useStateCP(1);
  const [text, setText] = useStateCP("");
  const [loading, setLoading] = useStateCP(true);

  useEffectCP(() => {
    setLoading(true);
    setText("");
    const t = setTimeout(() => {
      setText(OC_DATA.getExplanation(topic.id, level));
      setLoading(false);
    }, 280);
    return () => clearTimeout(t);
  }, [topic.id, level]);

  return (
    <div className="explanation-block">
      <div className="section-head">
        <span className="section-title">Explanation</span>
        <div className="level-row">
          {[1, 2, 3].map(l => (
            <span key={l} className={`level-pip ${l <= level ? "on" : ""}`}></span>
          ))}
          <span className="section-title" style={{marginLeft: 4}}>L{level}/3</span>
        </div>
      </div>
      <div className="explanation-text">
        {loading ? <div className="typing"><span></span><span></span><span></span></div> : <Markdown text={text} />}
      </div>
      <div className="explanation-actions">
        {topic.status === "available" && (
          <button className="action-btn start" onClick={() => onTransition(topic.id, "open")}>Start studying →</button>
        )}
        {topic.status === "in_progress" && (
          <button className="action-btn start" style={{background: "#22c55e", borderColor: "#22c55e"}} onClick={() => onTransition(topic.id, "complete")}>Mark as mastered ✓</button>
        )}
        {level < 3 && (
          <button className="action-btn" onClick={() => setLevel(level + 1)} disabled={loading}>I don't get it · go deeper</button>
        )}
        {level > 1 && (
          <button className="action-btn" onClick={() => setLevel(level - 1)} disabled={loading}>← Simpler</button>
        )}
      </div>
    </div>
  );
}

// Reusable copilot chat — opens immediately with greeting, suggested questions
function CopilotChat({ topic, typewriterSpeed, accent }) {
  const [msgs, setMsgs] = useStateCP([
    { role: "ai", text: `Hi — I'm your AI tutor for **${topic?.name || "this topic"}**.\n\nAsk me anything: clarifications, examples, common pitfalls, or "quiz me." I have your full graph context.` }
  ]);
  const [composer, setComposer] = useStateCP("");
  const [pending, setPending] = useStateCP(null);
  const [typingText, setTypingText] = useStateCP("");
  const [waiting, setWaiting] = useStateCP(false);
  const scrollRef = useRefCP(null);

  useEffectCP(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [msgs, typingText]);

  useEffectCP(() => {
    if (!pending) return;
    let i = 0;
    setTypingText("");
    const id = setInterval(() => {
      i++;
      setTypingText(pending.slice(0, i));
      if (i >= pending.length) {
        clearInterval(id);
        setMsgs(m => [...m, { role: "ai", text: pending }]);
        setPending(null);
        setWaiting(false);
        setTypingText("");
      }
    }, typewriterSpeed);
    return () => clearInterval(id);
  }, [pending, typewriterSpeed]);

  function send(textOverride) {
    const text = textOverride ?? composer.trim();
    if (!text || waiting) return;
    setMsgs(m => [...m, { role: "user", text }]);
    setComposer("");
    setWaiting(true);
    setTimeout(() => {
      setPending(OC_DATA.getCopilotReply(topic.id, text));
    }, 700);
  }

  const suggested = topic?.id === "chirality"
    ? ["Why does chirality matter in drug design?", "What's a meso compound?", "Quiz me on R/S"]
    : topic?.id === "sn1sn2"
    ? ["How do I tell SN1 from SN2 on an exam?", "What's a carbocation rearrangement?", "Quiz me"]
    : ["Give me an example", "What does this connect to?", "Quiz me"];

  return (
    <div className="cp-chat-inner">
      <div className="cp-chat-head">
        <div>
          <span className="section-title">AI Tutor</span>
          <div className="cp-chat-topic">on {topic?.name}</div>
        </div>
        <span className="cp-chat-status">
          <span className="cp-chat-pulse"></span>
          Online
        </span>
      </div>
      <div className="cp-chat-scroll" ref={scrollRef}>
        {msgs.map((m, i) => (
          <div key={i} className={`cop-msg ${m.role}`}>
            {m.role === "ai" && <div className="cop-meta">Pure</div>}
            <div className="cop-bubble">
              {m.role === "ai" ? <Markdown text={m.text} inline /> : m.text}
            </div>
          </div>
        ))}
        {pending && (
          <div className="cop-msg ai">
            <div className="cop-meta">Pure</div>
            <div className="cop-bubble cursor-blink">
              <Markdown text={typingText} inline />
            </div>
          </div>
        )}
        {waiting && !pending && (
          <div className="cop-msg ai">
            <div className="cop-meta">Pure</div>
            <div className="typing"><span></span><span></span><span></span></div>
          </div>
        )}
        {msgs.length === 1 && !waiting && (
          <div className="cp-suggested">
            {suggested.map((q, i) => (
              <button key={i} className="chip" onClick={() => send(q)}>{q}</button>
            ))}
          </div>
        )}
      </div>
      <div className="cp-chat-composer">
        <input
          type="text"
          placeholder={waiting ? "Pure is typing…" : "Ask anything…"}
          value={composer}
          onChange={e => setComposer(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter") send(); }}
          disabled={waiting}
        />
        <button className="send-btn" onClick={() => send()} disabled={!composer.trim() || waiting}>Send</button>
      </div>
    </div>
  );
}

window.CoursePage = CoursePage;
