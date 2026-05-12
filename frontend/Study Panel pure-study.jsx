// Study panel — explanation + copilot chat with typewriter
const { useState: useStateSP, useEffect: useEffectSP, useRef: useRefSP } = React;

function StudyPanel({ topic, onClose, onTransition, accent, typewriterSpeed }) {
  const [level, setLevel] = useStateSP(1);
  const [explanationText, setExplanationText] = useStateSP("");
  const [explainTyping, setExplainTyping] = useStateSP(true);
  const [copilotMsgs, setCopilotMsgs] = useStateSP([]);
  const [composer, setComposer] = useStateSP("");
  const [aiTyping, setAiTyping] = useStateSP(false);
  const [aiTypingText, setAiTypingText] = useStateSP("");
  const [pendingFull, setPendingFull] = useStateSP(null);
  const scrollRef = useRefSP(null);

  // Reset on topic change
  useEffectSP(() => {
    setLevel(1);
    setCopilotMsgs([]);
    setComposer("");
    setAiTyping(false);
    setPendingFull(null);
  }, [topic.id]);

  // Load explanation when topic or level changes (with brief loading state)
  useEffectSP(() => {
    setExplainTyping(true);
    setExplanationText("");
    const full = OC_DATA.getExplanation(topic.id, level);
    // Stream in: simple ~200ms delay then drop full text (markdown rendered)
    const t = setTimeout(() => {
      setExplanationText(full);
      setExplainTyping(false);
    }, 320);
    return () => clearTimeout(t);
  }, [topic.id, level]);

  // Typewriter for AI copilot messages
  useEffectSP(() => {
    if (!pendingFull) return;
    let i = 0;
    setAiTypingText("");
    const interval = setInterval(() => {
      i += 1;
      setAiTypingText(pendingFull.slice(0, i));
      if (i >= pendingFull.length) {
        clearInterval(interval);
        // Commit message
        setCopilotMsgs(m => [...m, { role: "ai", text: pendingFull }]);
        setAiTyping(false);
        setPendingFull(null);
        setAiTypingText("");
      }
    }, typewriterSpeed);
    return () => clearInterval(interval);
  }, [pendingFull, typewriterSpeed]);

  // Auto-scroll copilot
  useEffectSP(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [copilotMsgs, aiTypingText]);

  function handleEscalate() {
    if (level < 3) {
      setLevel(level + 1);
    }
  }

  function handleStart() {
    onTransition(topic.id, "open"); // available -> in_progress
  }

  function handleMaster() {
    onTransition(topic.id, "complete"); // in_progress -> mastered
  }

  function handleSendCopilot() {
    if (!composer.trim() || aiTyping) return;
    const userMsg = composer.trim();
    setCopilotMsgs(m => [...m, { role: "user", text: userMsg }]);
    setComposer("");
    setAiTyping(true);
    // Simulate latency
    setTimeout(() => {
      const reply = OC_DATA.getCopilotReply(topic.id, userMsg);
      setPendingFull(reply);
    }, 700);
  }

  const statusInfo = {
    mastered:    { label: "Mastered",    color: "#22c55e" },
    in_progress: { label: "In Progress", color: "#f59e0b" },
    available:   { label: "Available",   color: accent },
    locked:      { label: "Locked",      color: "#2a2a2a" }
  }[topic.status];

  const suggestedQuestions = topic.id === "chirality"
    ? ["Why does chirality matter in drug design?", "What's a meso compound?", "Walk me through R/S assignment"]
    : topic.id === "sn1sn2"
    ? ["How do I quickly tell SN1 from SN2 on an exam?", "What's a carbocation rearrangement?", "Why do polar protic solvents favor SN1?"]
    : ["Give me a simple example", "What does this connect to?", "What are common mistakes?"];

  return (
    <div className="study-panel" key={topic.id}>
      <div className="study-head">
        <div className="row">
          <h2>{topic.name}</h2>
          <button className="close-btn" onClick={onClose} title="Close">×</button>
        </div>
        <div className="row" style={{gap: 12}}>
          <span className="status-badge">
            <span className="dot" style={{background: statusInfo.color}}></span>
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
              {[1, 2, 3].map(l => (
                <span key={l} className={`level-pip ${l <= level ? "on" : ""}`} title={`Level ${l}`}></span>
              ))}
              <span className="section-title" style={{marginLeft: 4}}>L{level}/3</span>
            </div>
          </div>
          <div className="explanation-text">
            {explainTyping ? (
              <div className="typing"><span></span><span></span><span></span></div>
            ) : (
              <Markdown text={explanationText} />
            )}
          </div>
          <div className="explanation-actions">
            {topic.status === "available" && (
              <button className="action-btn start" onClick={handleStart}>Start studying →</button>
            )}
            {topic.status === "in_progress" && (
              <button className="action-btn start" style={{background: "#22c55e", borderColor: "#22c55e"}} onClick={handleMaster}>Mark as mastered ✓</button>
            )}
            {level < 3 && (
              <button className="action-btn" onClick={handleEscalate} disabled={explainTyping}>I don't get it · go deeper</button>
            )}
            {level > 1 && (
              <button className="action-btn" onClick={() => setLevel(level - 1)} disabled={explainTyping}>← Simpler</button>
            )}
          </div>
        </div>

        <div className="section copilot">
          <div className="copilot-head">
            <span className="section-title">Copilot</span>
            <span className="section-title" style={{textTransform: "none", color: "var(--text-mute)"}}>Ask anything about this topic</span>
          </div>
          <div className="copilot-scroll" ref={scrollRef}>
            <div className="copilot-msgs">
              {copilotMsgs.length === 0 && !aiTyping && (
                <div style={{display: "flex", flexWrap: "wrap", gap: 6}}>
                  {suggestedQuestions.map((q, i) => (
                    <button
                      key={i}
                      className="chip"
                      style={{textAlign: "left"}}
                      onClick={() => { setComposer(q); }}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
              {copilotMsgs.map((m, i) => (
                <div key={i} className={`cop-msg ${m.role}`}>
                  {m.role === "ai" && <div className="cop-meta">Copilot</div>}
                  <div className="cop-bubble">
                    {m.role === "ai" ? <Markdown text={m.text} inline /> : m.text}
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
                  <div className="typing"><span></span><span></span><span></span></div>
                </div>
              )}
            </div>
          </div>
          <div className="copilot-composer">
            <input
              type="text"
              placeholder="Ask anything…"
              value={composer}
              onChange={e => setComposer(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter") handleSendCopilot(); }}
              disabled={aiTyping}
            />
            <button className="send-btn" onClick={handleSendCopilot} disabled={!composer.trim() || aiTyping}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ComplexityMeter({ value }) {
  const segs = 10;
  return (
    <div className="complexity-meter">
      {Array.from({length: segs}).map((_, i) => (
        <span key={i} className={`seg ${i < value ? "on" : ""}`}></span>
      ))}
      <span className="label">Complexity {value}/10</span>
    </div>
  );
}

// Tiny markdown renderer: bold (**text**), code (`text`), paragraphs.
function Markdown({ text, inline }) {
  if (!text) return null;
  const parts = inline ? [text] : text.split(/\n\n+/);
  return (
    <>
      {parts.map((p, i) => {
        const html = inlineMd(p);
        if (inline) {
          return <span key={i} dangerouslySetInnerHTML={{ __html: html }} />;
        }
        return <p key={i} dangerouslySetInnerHTML={{ __html: html }} />;
      })}
    </>
  );
}

function inlineMd(s) {
  let out = s
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/^- (.+)$/gm, "<span style='display:block; padding-left: 14px; position:relative;'><span style='position:absolute; left:0; color:var(--text-mute);'>·</span>$1</span>");
  // Convert single newlines to <br>
  out = out.replace(/\n/g, "<br>");
  return out;
}

window.StudyPanel = StudyPanel;
window.Markdown = Markdown;
window.ComplexityMeter = ComplexityMeter;
