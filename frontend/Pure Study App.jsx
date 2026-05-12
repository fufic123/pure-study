// Main app: routing, state, tweaks, screen orchestration

const { useState: useStateApp, useEffect: useEffectApp, useMemo: useMemoApp, useCallback: useCallbackApp } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "#3b82f6",
  "density": 1,
  "typewriterSpeed": 18,
  "showMinimap": true
}/*EDITMODE-END*/;

const COURSES = [
  {
    id: "ochem",
    name: "Organic Chemistry",
    goal: "Pass spring class with an A — final in May",
    domain: "Chemistry",
    mastered: 7,
    total: 36
  },
  {
    id: "linalg",
    name: "Linear Algebra",
    goal: "Build foundation for ML coursework",
    domain: "Mathematics",
    mastered: 12,
    total: 24
  },
  {
    id: "music",
    name: "Music Theory",
    goal: "Read and write lead sheets fluently",
    domain: "Music",
    mastered: 18,
    total: 22
  }
];

function App() {
  const [tweaks, setTweak] = useTweaks(TWEAK_DEFAULTS);

  const [route, setRoute] = useStateApp("login"); // login | register | onboarding | courses | course | graph
  const [activeCourseId, setActiveCourseId] = useStateApp("ochem");
  const [user, setUser] = useStateApp(null);
  const [topics, setTopics] = useStateApp(OC_DATA.TOPICS);
  const [selectedId, setSelectedId] = useStateApp(null);
  const [recentIds, setRecentIds] = useStateApp(["conform", "alkenes"]);
  const [showCmdk, setShowCmdk] = useStateApp(false);
  const [showNewCourse, setShowNewCourse] = useStateApp(false);
  const [flashEdges, setFlashEdges] = useStateApp([]);
  const [toast, setToast] = useStateApp(null);

  // Apply accent to CSS var globally
  useEffectApp(() => {
    document.documentElement.style.setProperty("--accent", tweaks.accent);
  }, [tweaks.accent]);

  // Keyboard shortcuts
  useEffectApp(() => {
    function handle(e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (route === "graph") setShowCmdk(s => !s);
      }
      if (e.key === "Escape") {
        if (showCmdk) setShowCmdk(false);
        else if (showNewCourse) setShowNewCourse(false);
        else if (selectedId) setSelectedId(null);
      }
    }
    window.addEventListener("keydown", handle);
    return () => window.removeEventListener("keydown", handle);
  }, [route, showCmdk, showNewCourse, selectedId]);

  function handleAuthed(u) {
    setUser(u);
    if (u.isNew) setRoute("onboarding");
    else setRoute("courses");
  }

  function openCourse(id) {
    setActiveCourseId(id);
    setRoute("course");
  }

  function addRecent(id) {
    setRecentIds(prev => {
      const filtered = prev.filter(p => p !== id);
      return [id, ...filtered].slice(0, 5);
    });
  }

  function handleSelectTopic(id) {
    const t = topics.find(x => x.id === id);
    if (!t || t.status === "locked") return;
    setSelectedId(id);
    setShowCmdk(false);
    setRecentIds(prev => {
      const filtered = prev.filter(p => p !== id);
      return [id, ...filtered].slice(0, 5);
    });
  }

  function handleTransition(topicId, action) {
    setTopics(prev => {
      let next = prev.map(t => {
        if (t.id !== topicId) return t;
        if (action === "open" && t.status === "available") return { ...t, status: "in_progress" };
        if (action === "complete" && t.status === "in_progress") return { ...t, status: "mastered" };
        return t;
      });

      // If just mastered, unlock dependents whose prereqs are all mastered
      if (action === "complete") {
        const newlyUnlocked = [];
        next = next.map(t => {
          if (t.status !== "locked") return t;
          const allPrereqsMastered = t.prereqs.every(p => {
            const pT = next.find(x => x.id === p);
            return pT && pT.status === "mastered";
          });
          if (allPrereqsMastered && t.prereqs.length > 0) {
            newlyUnlocked.push(t.id);
            return { ...t, status: "available" };
          }
          return t;
        });
        if (newlyUnlocked.length > 0) {
          setFlashEdges(newlyUnlocked.map(t => ({ from: topicId, to: t })));
          setToast({ msg: `Mastered. ${newlyUnlocked.length} new topic${newlyUnlocked.length > 1 ? "s" : ""} unlocked.` });
          setTimeout(() => setToast(null), 3500);
          setTimeout(() => setFlashEdges([]), 1600);
        } else {
          setToast({ msg: "Mastered." });
          setTimeout(() => setToast(null), 2000);
        }
      }
      return next;
    });
  }

  const selectedTopic = useMemoApp(() => topics.find(t => t.id === selectedId), [selectedId, topics]);

  // ===== Render by route =====
  if (route === "login") {
    return <AuthScreen mode="login" onAuthed={handleAuthed} onSwitch={r => setRoute(r)} />;
  }
  if (route === "register") {
    return <AuthScreen mode="register" onAuthed={handleAuthed} onSwitch={r => setRoute(r)} />;
  }
  if (route === "onboarding") {
    return <Onboarding onComplete={() => setRoute("courses")} />;
  }

  const activeCourse = COURSES.find(c => c.id === activeCourseId) || COURSES[0];

  return (
    <div className="app-shell">
      <Topbar
        route={route}
        user={user}
        onNav={setRoute}
        onSearch={() => setShowCmdk(true)}
      />
      {route === "courses" && (
        <CoursesView
          courses={COURSES.map(c => ({...c, mastered: c.id === "ochem" ? topics.filter(t => t.status === "mastered").length : c.mastered, total: c.id === "ochem" ? topics.length : c.total}))}
          onOpen={openCourse}
          onNew={() => setShowNewCourse(true)}
        />
      )}
      {route === "course" && (
        <CoursePage
          course={activeCourse}
          topics={topics}
          accent={tweaks.accent}
          typewriterSpeed={tweaks.typewriterSpeed}
          density={tweaks.density}
          onTransition={handleTransition}
          recentIds={recentIds}
          onAddRecent={addRecent}
        />
      )}
      {route === "graph" && (
        <div className={`graph-view ${selectedTopic ? "with-panel" : ""}`}>
          <GraphView
            topics={topics}
            accent={tweaks.accent}
            density={tweaks.density}
            showMinimap={tweaks.showMinimap}
            onSelectTopic={handleSelectTopic}
            selectedId={selectedId}
            recentIds={recentIds}
            flashEdgeIds={flashEdges}
          />
          {selectedTopic && (
            <StudyPanel
              topic={selectedTopic}
              onClose={() => setSelectedId(null)}
              onTransition={handleTransition}
              accent={tweaks.accent}
              typewriterSpeed={tweaks.typewriterSpeed}
            />
          )}
        </div>
      )}

      {showCmdk && (
        <CommandPalette
          topics={topics}
          accent={tweaks.accent}
          onPick={handleSelectTopic}
          onClose={() => setShowCmdk(false)}
        />
      )}

      {showNewCourse && (
        <div className="modal-backdrop" onClick={() => setShowNewCourse(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-head">
              <h3>New course</h3>
              <button className="close-btn" style={{width: 28, height: 28, border: "1px solid var(--border)", color: "var(--text-mute)"}} onClick={() => setShowNewCourse(false)}>×</button>
            </div>
            <Onboarding onComplete={() => { setShowNewCourse(false); setRoute("course"); }} embedded />
          </div>
        </div>
      )}

      {toast && (
        <div className="toast">
          <span className="toast-dot"></span>
          <span>{toast.msg}</span>
        </div>
      )}

      <TweaksPanel title="Tweaks">
        <TweakSection title="Visuals">
          <TweakColor label="Accent color" value={tweaks.accent} onChange={v => setTweak("accent", v)} />
          <TweakToggle label="Show minimap" value={tweaks.showMinimap} onChange={v => setTweak("showMinimap", v)} />
        </TweakSection>
        <TweakSection title="Graph">
          <TweakSlider label="Force density" min={0.5} max={2.0} step={0.1} value={tweaks.density} onChange={v => setTweak("density", v)} />
        </TweakSection>
        <TweakSection title="Copilot">
          <TweakSlider label="Typewriter speed (ms/char)" min={4} max={50} step={2} value={tweaks.typewriterSpeed} onChange={v => setTweak("typewriterSpeed", v)} />
        </TweakSection>
        <TweakSection title="Navigate">
          <TweakButton label="Login" onClick={() => setRoute("login")} />
          <TweakButton label="Onboarding" onClick={() => setRoute("onboarding")} />
          <TweakButton label="Dashboard" onClick={() => setRoute("courses")} />
          <TweakButton label="Course page" onClick={() => setRoute("course")} />
          <TweakButton label="Graph" onClick={() => setRoute("graph")} />
        </TweakSection>
      </TweaksPanel>
    </div>
  );
}

function Topbar({ route, user, onNav, onSearch }) {
  return (
    <div className="topbar" data-screen-label={`App · ${route}`}>
      <div className="topbar-left">
        <div className="brand" style={{fontSize: 12}}>
          <span className="brand-mark"></span>
          <span>PURE.STUDY</span>
        </div>
        <span style={{width: 1, height: 16, background: "var(--border)"}}></span>
        <span className={`nav-link ${route === "courses" ? "active" : ""}`} onClick={() => onNav("courses")}>Dashboard</span>
        <span className={`nav-link ${route === "course" ? "active" : ""}`} onClick={() => onNav("course")}>Course</span>
        <span className={`nav-link ${route === "graph" ? "active" : ""}`} onClick={() => onNav("graph")}>Graph</span>
      </div>
      <div className="topbar-right">
        {route === "graph" && (
          <div className="searchbar-trigger" onClick={onSearch}>
            <span style={{color: "var(--text-mute)"}}>⌕</span>
            <span className="label">Search topics…</span>
            <span className="kbd">⌘K</span>
          </div>
        )}
        <span style={{fontSize: 12, color: "var(--text-mute)"}}>{user?.name || "alex"}</span>
        <div className="avatar-pill">{(user?.name || "A")[0].toUpperCase()}</div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
