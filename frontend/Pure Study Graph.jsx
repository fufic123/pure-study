// Graph view: d3-force simulation, zoom/pan, minimap, tooltip
// Globals expected: React, ReactDOM, d3, OC_DATA

const { useState, useEffect, useRef, useMemo, useCallback } = React;

function GraphView({ topics, accent, onSelectTopic, selectedId, density, showMinimap, recentIds, onUnlockedFlash, flashEdgeIds, compact }) {
  const svgRef = useRef(null);
  const wrapRef = useRef(null);
  const minimapRef = useRef(null);
  const simRef = useRef(null);
  const [tooltip, setTooltip] = useState(null);
  const [zoom, setZoom] = useState({ k: 1, x: 0, y: 0 });

  // Build links from prereqs
  const links = useMemo(() => {
    const all = [];
    topics.forEach(t => {
      t.prereqs.forEach(p => {
        all.push({ source: p, target: t.id });
      });
    });
    return all;
  }, [topics]);

  useEffect(() => {
    const wrap = wrapRef.current;
    if (!wrap) return;
    const W = wrap.clientWidth;
    const H = wrap.clientHeight;

    // Clone topic data for d3 (positions get mutated)
    const nodes = topics.map(t => ({ ...t }));
    const linkData = links.map(l => ({ source: l.source, target: l.target }));

    const sim = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(linkData).id(d => d.id)
        .distance(d => 60 + Math.abs((d.source.complexity || 1) - (d.target.complexity || 1)) * 8 * density)
        .strength(0.4))
      .force("charge", d3.forceManyBody().strength(-260 * density))
      .force("center", d3.forceCenter(W / 2, H / 2))
      .force("collide", d3.forceCollide().radius(d => 8 + d.complexity * 1.6 + 8))
      .alphaDecay(0.025);

    simRef.current = sim;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Defs: arrow marker, glow filters
    const defs = svg.append("defs");
    defs.append("marker")
      .attr("id", "arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 16)
      .attr("refY", 0)
      .attr("markerWidth", 5)
      .attr("markerHeight", 5)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#3a3a3a");

    // Glow filter for available nodes
    const glow = defs.append("filter")
      .attr("id", "node-glow")
      .attr("x", "-100%").attr("y", "-100%")
      .attr("width", "300%").attr("height", "300%");
    glow.append("feGaussianBlur").attr("stdDeviation", "4").attr("result", "blur");
    glow.append("feMerge").selectAll("feMergeNode")
      .data(["blur", "SourceGraphic"]).enter()
      .append("feMergeNode").attr("in", d => d);

    const root = svg.append("g").attr("class", "zoom-root");

    const linkSel = root.append("g")
      .attr("class", "links")
      .selectAll("path")
      .data(linkData)
      .enter()
      .append("path")
      .attr("class", "edge")
      .attr("opacity", d => {
        const s = typeof d.source === "object" ? d.source.status : nodes.find(n => n.id === d.source)?.status;
        const t = typeof d.target === "object" ? d.target.status : nodes.find(n => n.id === d.target)?.status;
        if (s === "locked" || t === "locked") return 0.18;
        return 0.45;
      })
      .attr("stroke", d => {
        const t = typeof d.target === "object" ? d.target.status : nodes.find(n => n.id === d.target)?.status;
        if (t === "mastered") return "#2a4a36";
        return "#2a2a2a";
      })
      .attr("marker-end", "url(#arrow)");

    const nodeSel = root.append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(nodes)
      .enter()
      .append("g")
      .attr("class", d => `node node-${d.status}`)
      .style("cursor", d => d.status === "locked" ? "not-allowed" : "pointer")
      .on("mouseenter", (event, d) => {
        const r = wrap.getBoundingClientRect();
        setTooltip({
          x: event.clientX,
          y: event.clientY,
          name: d.name,
          status: d.status,
          complexity: d.complexity,
          locked: d.status === "locked"
        });
        d3.select(event.currentTarget).select(".node-circle")
          .attr("r", 8 + d.complexity * 1.6 + 2);
      })
      .on("mousemove", (event) => {
        setTooltip(t => t ? { ...t, x: event.clientX, y: event.clientY } : null);
      })
      .on("mouseleave", (event, d) => {
        setTooltip(null);
        d3.select(event.currentTarget).select(".node-circle")
          .attr("r", 8 + d.complexity * 1.6);
      })
      .on("click", (event, d) => {
        if (d.status === "locked") return;
        onSelectTopic(d.id);
      });

    // Pulse halo for available
    nodeSel.filter(d => d.status === "available")
      .append("circle")
      .attr("class", "pulse-halo")
      .attr("r", 0)
      .attr("fill", "none")
      .attr("stroke", accent)
      .attr("stroke-width", 1.5)
      .attr("opacity", 0)
      .style("animation", "node-pulse 2.4s ease-in-out infinite");

    nodeSel.append("circle")
      .attr("class", "node-circle")
      .attr("r", d => 8 + d.complexity * 1.6)
      .attr("fill", d => {
        switch (d.status) {
          case "locked": return "#0a0a0a";
          case "available": return accent;
          case "in_progress": return "#f59e0b";
          case "mastered": return "#22c55e";
          default: return "#3a3a3a";
        }
      })
      .attr("stroke", d => {
        switch (d.status) {
          case "locked": return "#2a2a2a";
          case "available": return accent;
          case "in_progress": return "#f59e0b";
          case "mastered": return "#22c55e";
          default: return "#3a3a3a";
        }
      })
      .attr("stroke-width", d => d.status === "locked" ? 1 : 1.5)
      .attr("filter", d => d.status === "available" ? "url(#node-glow)" : null)
      .attr("opacity", d => d.status === "locked" ? 0.55 : 1);

    nodeSel.append("text")
      .attr("class", "node-label")
      .attr("dy", d => 8 + d.complexity * 1.6 + 14)
      .text(d => d.name);

    // Selected ring
    nodeSel.filter(d => d.id === selectedId)
      .append("circle")
      .attr("class", "selected-ring")
      .attr("r", d => 8 + d.complexity * 1.6 + 6)
      .attr("fill", "none")
      .attr("stroke", "#f1f1f1")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "2 3");

    // Recent ring (small dot indicator)
    nodeSel.filter(d => recentIds.includes(d.id) && d.id !== selectedId)
      .append("circle")
      .attr("r", 2)
      .attr("cx", d => 8 + d.complexity * 1.6)
      .attr("cy", d => -(8 + d.complexity * 1.6))
      .attr("fill", "#f1f1f1");

    // d3-zoom
    const zoomBehavior = d3.zoom()
      .scaleExtent([0.3, 3])
      .on("zoom", (event) => {
        root.attr("transform", event.transform);
        setZoom({ k: event.transform.k, x: event.transform.x, y: event.transform.y });
      });
    svg.call(zoomBehavior);

    // Initial centering — start the simulation, settle a bit
    sim.on("tick", () => {
      linkSel.attr("d", d => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy) * 1.6;
        return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
      });
      nodeSel.attr("transform", d => `translate(${d.x},${d.y})`);

      // Update minimap
      if (minimapRef.current) {
        renderMinimap(minimapRef.current, nodes, W, H);
      }
    });

    // Cleanup
    return () => {
      sim.stop();
    };
  }, [topics, links, density]); // re-create only when graph topology changes

  // Refresh accent + selection without rebuilding sim
  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll(".node-available .node-circle")
      .attr("fill", accent)
      .attr("stroke", accent);
    svg.selectAll(".pulse-halo").attr("stroke", accent);
  }, [accent]);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll(".selected-ring").remove();
    if (!selectedId) return;
    const sel = svg.selectAll(".node").filter(d => d.id === selectedId);
    sel.append("circle")
      .attr("class", "selected-ring")
      .attr("r", d => 8 + d.complexity * 1.6 + 6)
      .attr("fill", "none")
      .attr("stroke", "#f1f1f1")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "2 3");
  }, [selectedId]);

  // Flash edges (unlock animation)
  useEffect(() => {
    if (!flashEdgeIds || flashEdgeIds.length === 0) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll(".edge").each(function(d) {
      const sId = typeof d.source === "object" ? d.source.id : d.source;
      const tId = typeof d.target === "object" ? d.target.id : d.target;
      if (flashEdgeIds.some(e => e.from === sId && e.to === tId)) {
        d3.select(this).classed("unlocked-flash", true);
        setTimeout(() => d3.select(this).classed("unlocked-flash", false), 1400);
      }
    });
  }, [flashEdgeIds]);

  return (
    <div ref={wrapRef} className="graph-canvas-wrap">
      <svg ref={svgRef}></svg>
      {!compact && <div className="legend">
        <div className="legend-row"><span className="legend-dot" style={{background: "#22c55e"}}></span><span>Mastered</span></div>
        <div className="legend-row"><span className="legend-dot" style={{background: "#f59e0b"}}></span><span>In progress</span></div>
        <div className="legend-row"><span className="legend-dot" style={{background: accent}}></span><span>Available</span></div>
        <div className="legend-row"><span className="legend-dot" style={{background: "#2a2a2a", border: "1px solid #3a3a3a"}}></span><span>Locked</span></div>
      </div>}
      {!compact && <div className="graph-overlay-stats">
        <div className="stat-card">
          <div className="stat-num">{topics.filter(t => t.status === "mastered").length}<span style={{color: "var(--text-mute)", fontSize: 13}}>/{topics.length}</span></div>
          <div className="stat-label">Mastered</div>
        </div>
        <div className="stat-card">
          <div className="stat-num">{topics.filter(t => t.status === "in_progress").length}</div>
          <div className="stat-label">In progress</div>
        </div>
        <div className="stat-card">
          <div className="stat-num">{topics.filter(t => t.status === "available").length}</div>
          <div className="stat-label">Available</div>
        </div>
      </div>}
      {!compact && recentIds.length > 0 && (
        <div className="recent-panel">
          <div className="recent-header"><span>Recently studied</span><span>{recentIds.length}</span></div>
          <div className="recent-list">
            {recentIds.map(id => {
              const t = topics.find(x => x.id === id);
              if (!t) return null;
              return (
                <div key={id} className="recent-item" onClick={() => onSelectTopic(id)}>
                  <span className="recent-status" style={{background: statusColor(t.status, accent)}}></span>
                  <span className="recent-name">{t.name}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
      {showMinimap && (
        <div className="minimap">
          <span className="minimap-label">Map</span>
          <svg ref={minimapRef}></svg>
        </div>
      )}
      {tooltip && (
        <div className="tooltip" style={{ left: tooltip.x + 14, top: tooltip.y + 14 }}>
          <div>{tooltip.name}</div>
          <div className="tt-status">
            {tooltip.locked ? "Locked — complete prerequisites first" : `${tooltip.status.replace("_", " ")} · complexity ${tooltip.complexity}/10`}
          </div>
        </div>
      )}
    </div>
  );
}

function statusColor(s, accent) {
  if (s === "mastered") return "#22c55e";
  if (s === "in_progress") return "#f59e0b";
  if (s === "available") return accent;
  return "#2a2a2a";
}

function renderMinimap(svgEl, nodes, W, H) {
  const sel = d3.select(svgEl);
  const w = svgEl.clientWidth || 140;
  const h = svgEl.clientHeight || 100;
  // Compute bounds
  const xs = nodes.map(n => n.x).filter(v => v != null);
  const ys = nodes.map(n => n.y).filter(v => v != null);
  if (xs.length === 0) return;
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const sx = w / (maxX - minX + 40);
  const sy = h / (maxY - minY + 40);
  const s = Math.min(sx, sy);
  sel.selectAll("*").remove();
  const g = sel.append("g")
    .attr("transform", `translate(${(w - (maxX - minX) * s) / 2 - minX * s}, ${(h - (maxY - minY) * s) / 2 - minY * s})`);
  g.selectAll("circle")
    .data(nodes)
    .enter()
    .append("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", d => Math.max(1, d.complexity * 0.3))
    .attr("fill", d => {
      switch (d.status) {
        case "mastered": return "#22c55e";
        case "in_progress": return "#f59e0b";
        case "available": return "#3b82f6";
        default: return "#3a3a3a";
      }
    })
    .attr("opacity", d => d.status === "locked" ? 0.4 : 0.9);
}

window.GraphView = GraphView;
