"use strict";
let STATE = null;

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function toast(msg, isErr = false) {
  const t = $("toast");
  t.textContent = msg;
  t.className = "toast" + (isErr ? " err" : "");
  setTimeout(() => (t.className = "toast hidden"), 2600);
}

async function act(fn) {
  try { await fn(); await refresh(); }
  catch (e) { toast((e && e.data && e.data.detail) || ("error " + (e.status || "")), true); await refresh(); }
}

function citationChip(c) {
  if (!c) return "";
  if (c.kind === "doc_page") return `<span class="chip" title="document ${c.document_id}, page ${c.page}">10-K p.${c.page}</span>`;
  if (c.kind === "external_url") return `<span class="chip ext" title="${esc(c.source_url)}">agency · ${esc(c.as_of || "")}</span>`;
  if (c.kind === "reference_data") return `<span class="chip ref" title="reference data (not a 10-K page)">ref-data</span>`;
  return "";
}

function mdToHtml(md) {
  return (md || "").split("\n").map((ln) => {
    if (ln.startsWith("## ")) return `<h2>${esc(ln.slice(3))}</h2>`;
    if (ln.startsWith("# ")) return `<h1>${esc(ln.slice(2))}</h1>`;
    if (ln.trim() === "") return "";
    return `<p>${esc(ln)}</p>`;
  }).join("");
}

function diffHtml(diff) {
  return (diff || "").split("\n").map((ln) => {
    if (ln.startsWith("- ")) return `<span class="del">${esc(ln)}</span>`;
    if (ln.startsWith("+ ")) return `<span class="add">${esc(ln)}</span>`;
    return esc(ln);
  }).join("\n");
}

// ---- step definitions -------------------------------------------------------
const STEPS = [
  { n: 1, title: "Doc extraction", req: 0, tag: ["real", "REAL Claude"], render: renderExtract },
  { n: 2, title: "Analyst gate (HITL)", req: 1, tag: ["hitl", "human gate"], render: renderGate },
  { n: 3, title: "Model + score", req: 2, tag: ["canned", "canned"], render: renderScore },
  { n: 4, title: "Due diligence", req: 3, tag: ["canned", "canned"], render: renderDD },
  { n: 5, title: "Compile CAM", req: 4, tag: ["real", "compile + REAL prose"], render: renderCompile },
  { n: 6, title: "CAM edit gate", req: 5, tag: ["real", "REAL + HITL"], render: renderEdit },
  { n: 7, title: "RAG chatbot", req: 5, tag: ["real", "REAL Claude"], render: renderChat },
  { n: 8, title: "Monitor / re-trigger", req: 5, tag: ["canned", "monitor"], render: renderMonitor },
];

function renderExtract(s) {
  const has = s.fields.length > 0;
  return `<button class="btn" ${s.deal.current_step < 0 ? "disabled" : ""} onclick="act(()=>API.post('/api/deal/extract'))">
            ${has ? "Re-run extraction" : "Run extraction agent"}</button>
          ${has ? `<p class="meta">${s.fields.length} fields extracted, each stamped with source page + confidence + reliability tier.</p>` : ""}`;
}

function renderGate(s) {
  if (s.fields.length === 0) return `<p class="meta">Run extraction first.</p>`;
  const pending = s.fields.filter((f) => f.hitl_required && (f.produced_by || "").startsWith("agent"));
  const rows = s.fields.map((f) => {
    const low = f.confidence < 0.7;
    const cls = f.hitl_required && (f.produced_by || "").startsWith("agent") ? "flag-hitl" : (low ? "flag-low" : "");
    return `<tr class="${cls}">
      <td>${esc(f.key)}${f.hitl_required ? ' <span class="tag hitl">HITL</span>' : ""}</td>
      <td><input class="cell" value="${esc(f.value)}" onchange="act(()=>API.patch('/api/deal/fields/${f.id}',{value:this.value}))"></td>
      <td>${citationChip(f.citation)}</td>
      <td class="conf"><span class="bar ${low ? "low" : ""}"><i style="width:${Math.round(f.confidence * 100)}%"></i></span> ${f.confidence.toFixed(2)}</td>
      <td><span class="muted">${esc(f.reliability_tier)}</span><br><span class="muted">v${f.version} · ${esc((f.produced_by || "").replace("agent:", "").replace("human:", "✎"))}</span></td>
    </tr>`;
  }).join("");
  const blocked = pending.length > 0;
  const approved = s.deal.current_step >= 2;
  return `<table><thead><tr><th>field</th><th>value</th><th>cite</th><th>conf</th><th>tier / ver</th></tr></thead><tbody>${rows}</tbody></table>
    ${blocked ? `<p class="meta">⚠ Review the HITL-mandatory field(s) before approving: <b>${pending.map((p) => esc(p.key)).join(", ")}</b> (edit the value to record a human review).</p>` : ""}
    <button class="btn" ${blocked ? "disabled" : ""} onclick="act(()=>API.post('/api/deal/fields/approve'))">${approved ? "Re-approve fields" : "Approve fields"}</button>`;
}

function renderScore(s) {
  if (s.deal.current_step < 2) return `<p class="meta">Approve the fields first.</p>`;
  const sc = s.scorecard;
  const ratios = s.ratios.map((r) => `<tr><td>${esc(r.name)}</td><td><b>${esc(r.value)}</b></td></tr>`).join("");
  const grade = sc ? `<div class="grade-cmp">
      <div class="grade">${esc(sc.internal_grade)}<span class="sub">internal (model)</span></div>
      <div class="grade">${esc(s.deal.agency_grade)}<span class="sub">public agency</span></div>
    </div>
    <p class="note">Internal grade is conservative / through-the-cycle; the agency grade is issuer-level. A one-notch gap is a methodology difference, not an error.</p>
    <div class="cards"><div class="card"><h4>PD</h4>${(sc.pd * 100).toFixed(1)}%</div>
      <div class="card"><h4>LGD</h4>${(sc.lgd * 100).toFixed(0)}%</div>
      <div class="card"><h4>EAD</h4>$${esc(sc.ead)}M</div>
      <div class="card"><h4>Qualitative</h4>${(sc.qualitative_dims || []).map((q) => `${esc(q.dimension)} ${citationChip(q.citation)}`).join("<br>")}</div></div>` : "";
  return `<button class="btn" onclick="act(()=>API.post('/api/deal/score'))">${sc ? "Re-run model + score" : "Run model + score"}</button>
    ${sc ? `<table>${ratios}</table>${grade}` : ""}`;
}

function renderDD(s) {
  if (s.deal.current_step < 3) return `<p class="meta">Run scoring first.</p>`;
  const cards = s.dd_findings.map((d) => `<div class="card"><h4>${esc(d.finding_type)} ${citationChip(d.citation)}</h4>${esc(d.result)}</div>`).join("");
  return `<button class="btn" onclick="act(()=>API.post('/api/deal/diligence'))">${s.dd_findings.length ? "Re-run due diligence" : "Run due diligence"}</button>
    ${s.dd_findings.length ? `<div class="cards">${cards}</div>` : ""}`;
}

function renderCompile(s) {
  if (s.deal.current_step < 4) return `<p class="meta">Run due diligence first.</p>`;
  const cam = s.cam;
  const body = cam ? `<div class="cam"><h1>Credit Application Memo — ${esc(s.deal.borrower_name)} <span class="muted">v${cam.version}</span></h1>` +
    (cam.slots || []).map((sl) => `<h2>${esc(sl.section)}</h2>
       <div class="slot-src">slot &larr; ${esc(sl.source_table)}#${esc(sl.source_id)}${sl.source_version ? " v" + sl.source_version : ""} ${citationChip(sl.citation)}</div>
       <p>${esc(sl.prose)}</p>`).join("") + `</div>` : "";
  return `<button class="btn" onclick="act(()=>API.post('/api/deal/cam/compile'))">${cam ? "Recompile CAM" : "Compile CAM"}</button>
    <p class="meta">Each slot is stamped with its upstream source record + citation (deterministic) before Claude writes the prose.</p>${body}`;
}

function renderEdit(s) {
  if (s.deal.current_step < 5) return `<p class="meta">Compile the CAM first.</p>`;
  const pend = (window._lastEdit && window._lastEdit.status === "proposed") ? window._lastEdit : null;
  let html = `<div class="row"><input class="text grow" id="edit-instr" placeholder="e.g. add the automotive supply-agreement mitigant to the risk section">
      <button class="btn" onclick="proposeEdit()">Propose edit</button></div>`;
  if (pend) {
    html += `<p class="meta">Proposed by ${esc(pend.produced_by)} — approve to apply, reject to discard:</p>
      <div class="diff">${diffHtml(pend.proposed_diff)}</div>
      <div class="row" style="margin-top:8px">
        <button class="btn" onclick="resolveEdit(${pend.id},'approve')">Approve &amp; apply</button>
        <button class="btn danger" onclick="resolveEdit(${pend.id},'reject')">Reject</button></div>`;
  }
  return html;
}

function renderChat(s) {
  if (s.deal.current_step < 5) return `<p class="meta">Compile the CAM first.</p>`;
  const log = s.chat.map((m) => `<div class="msg ${m.role}">${esc(m.content)}
     ${(m.citations || []).map(citationChip).join(" ")}</div>`).join("");
  return `<div class="chatlog">${log || '<p class="meta">Ask about the deal pack — answers cite the persisted source page.</p>'}</div>
    <div class="row"><input class="text grow" id="chat-q" placeholder="where did the leverage figure come from?"
      onkeydown="if(event.key==='Enter')askChat()"><button class="btn" onclick="askChat()">Ask</button></div>`;
}

function renderMonitor(s) {
  if (s.deal.current_step < 5) return `<p class="meta">Commit the CAM first.</p>`;
  if (s.deal.status === "re_review") {
    return `<p class="meta">⚠ Agency rating action detected — agency grade now <b>${esc(s.deal.agency_grade)}</b>. The scorecard was re-opened as a pending version and the deal is in <b>re_review</b>.</p>
      <button class="btn" onclick="act(()=>API.post('/api/deal/monitor/reapprove'))">Re-approve (recompute + commit CAM v2)</button>`;
  }
  return `<p class="meta">A watcher has been polling since commit. Simulate an agency rating action to re-trigger a review.</p>
    <button class="btn" onclick="act(()=>API.post('/api/deal/monitor/fire'))">Simulate agency rating action</button>`;
}

async function proposeEdit() {
  const instr = $("edit-instr").value.trim();
  if (!instr) return;
  try { window._lastEdit = await API.post("/api/deal/cam/edit", { instruction: instr }); await refresh(); }
  catch (e) { toast((e.data && e.data.detail) || "error", true); }
}
async function resolveEdit(id, decision) {
  await act(async () => { await API.post(`/api/deal/cam/edit/${id}/resolve`, { decision }); window._lastEdit = null; });
}
async function askChat() {
  const q = $("chat-q").value.trim();
  if (!q) return;
  await act(() => API.post("/api/deal/chat", { question: q }));
}

// ---- render -----------------------------------------------------------------
function renderSteps(s) {
  const cur = s.deal ? s.deal.current_step : -1;
  $("steps").innerHTML = STEPS.map((st) => {
    const unlocked = s.deal && cur >= st.req;
    const done = s.deal && cur >= st.n;
    const cls = !unlocked ? "locked" : (done ? "done" : "active");
    const inner = s.deal ? st.render(s) : `<p class="meta">Seed a deal to begin.</p>`;
    return `<div class="step ${cls}">
      <h2>${st.n} · ${esc(st.title)} <span class="tag ${st.tag[0]}">${esc(st.tag[1])}</span></h2>
      <div>${unlocked || !s.deal ? inner : '<p class="meta">Locked — finish earlier steps.</p>'}</div>
    </div>`;
  }).join("");
}

const LEGEND = [
  ["Agent does the work", "Steps 1, 5"],
  ["Human-in-the-loop gate", "Steps 2, 6"],
  ["Per-field citation / version", "Steps 1, 3, 5, 7"],
  ["Orchestrator compiles to template", "Step 5"],
  ["RAG chatbot per doc pack", "Step 7"],
  ["Continuous monitor / re-trigger", "Step 8"],
];

function renderSide(s) {
  $("legend").innerHTML = LEGEND.map(([a, b]) => `<li><b>${esc(a)}</b><br><span class="muted">${esc(b)}</span></li>`).join("");
  const filter = $("audit-filter").value;
  const rows = (s.audit || []).filter((a) => !filter || a.actor_type === filter);
  $("audit-count").textContent = s.audit ? `(${s.audit.length})` : "";
  $("audit").innerHTML = rows.map((a) => {
    const tgt = a.target_table ? ` → ${esc(a.target_table)}#${esc(a.target_row_id)}${a.target_version ? "v" + a.target_version : ""}` : "";
    const chg = a.old_value != null ? ` <span class="muted">[${esc(a.old_value)}→${esc(a.new_value)}]</span>` : "";
    return `<li class="a-${a.actor_type}"><b>${esc(a.action)}</b> <span class="muted">${esc(a.actor)}</span>${tgt}${chg}</li>`;
  }).join("");
}

function renderHeader(s) {
  $("borrower").textContent = s.deal ? s.deal.borrower_name : "no deal";
  $("status").textContent = s.deal ? `status: ${s.deal.status} · step ${s.deal.current_step}/8` : "—";
  const live = s.llm_mode === "live";
  $("llm").textContent = `LLM: ${s.llm_mode || "?"}`;
  $("llm").className = "badge " + (live ? "live" : "stub");
  if (s.audit_verified === undefined) { $("verified").textContent = "—"; $("verified").className = "badge"; }
  else { $("verified").textContent = s.audit_verified ? "audit ✓ verified" : "audit ✗ TAMPERED";
         $("verified").className = "badge " + (s.audit_verified ? "ok" : "warn"); }
}

async function refresh() {
  STATE = await API.get("/api/deal/state");
  renderHeader(STATE); renderSteps(STATE); renderSide(STATE);
}

$("seed").onclick = () => act(async () => { window._lastEdit = null; await API.post("/api/deal/seed"); toast("deal seeded"); });
$("audit-filter").onchange = () => renderSide(STATE);
refresh();
