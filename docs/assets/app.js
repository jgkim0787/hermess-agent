/* Hermes 과정 — 사이트 동작 (사이드바 / 코드복사 / 질문 렌더) */
(function () {
  "use strict";
  const page = document.body.dataset.page || "home";
  const slug = document.body.dataset.slug || null;
  // index 는 docs/ 루트, 나머지(modules/qa/reviews)는 한 단계 아래
  const base = page === "home" ? "" : "../";

  /* ---------- 코드 블록: highlight + 복사 버튼 ---------- */
  function enhanceCode() {
    if (window.hljs) {
      document.querySelectorAll("pre code").forEach((el) => {
        if (!el.classList.contains("output")) {
          try { window.hljs.highlightElement(el); } catch (e) {}
        }
      });
    }
    document.querySelectorAll("pre > code").forEach((code) => {
      const pre = code.parentElement;
      if (pre.classList.contains("output") || pre.querySelector(".copy-btn")) return;
      const btn = document.createElement("button");
      btn.className = "copy-btn"; btn.type = "button"; btn.textContent = "복사";
      btn.addEventListener("click", () => {
        navigator.clipboard.writeText(code.innerText).then(() => {
          btn.textContent = "복사됨"; btn.classList.add("copied");
          setTimeout(() => { btn.textContent = "복사"; btn.classList.remove("copied"); }, 1400);
        });
      });
      pre.appendChild(btn);
    });
  }

  /* ---------- 데이터 로드 ---------- */
  async function loadCurriculum() {
    try {
      const r = await fetch(base + "data/curriculum.json", { cache: "no-store" });
      return await r.json();
    } catch (e) { return null; }
  }
  async function loadQa() {
    try {
      const r = await fetch(base + "data/qa-log.jsonl", { cache: "no-store" });
      const txt = await r.text();
      return txt.split("\n").map((l) => l.trim()).filter(Boolean)
        .map((l) => { try { return JSON.parse(l); } catch (e) { return null; } }).filter(Boolean);
    } catch (e) { return []; }
  }

  const ST = { done: "✓", in_progress: "◐", planned: "○" };

  /* ---------- 사이드바 ---------- */
  function renderSidebar(cur) {
    const el = document.getElementById("sidebar");
    if (!el || !cur) return;
    const items = cur.modules.map((m) => {
      const href = base + "modules/" + m.slug + ".html";
      const active = m.slug === slug ? " active" : "";
      return `<a class="nav-item${active}" href="${href}">
        <span class="num">${m.order}</span><span class="t">${m.title}</span>
        <span class="status st-${m.status}" title="${m.status}">${ST[m.status] || ""}</span></a>`;
    }).join("");
    el.innerHTML = `<h3>커리큘럼</h3>${items}
      <h3 style="margin-top:18px">바로가기</h3>
      <a class="nav-item" href="${base}index.html"><span class="t">🏠 홈 / 로드맵</span></a>
      <a class="nav-item" href="${base}qa/index.html"><span class="t">❓ 질문 모음</span></a>`;
  }

  /* ---------- 모듈 페이지: 이번 모듈 질문 ---------- */
  function renderModuleQa(qa) {
    const box = document.getElementById("moduleQa");
    if (!box || !slug) return;
    const mine = qa.filter((q) => q.module === slug);
    if (!mine.length) return; // 기본 안내문 유지
    box.innerHTML = mine.map(qaCard).join("");
  }

  function qaCard(q) {
    const tags = (q.tags || []).map((t) => `<span class="tag">${t}</span>`).join("");
    return `<details><summary>${escapeHtml(q.question)}</summary>
      <div class="meta">${q.ts || ""} · ${q.module || "general"}</div>
      <p>${escapeHtml(q.answer_summary || "")}</p>
      <div class="tags">${tags}</div></details>`;
  }

  /* ---------- 질문 모음 페이지 ---------- */
  function renderQaPage(qa, cur) {
    const box = document.getElementById("qaAll");
    if (!box) return;
    if (!qa.length) { box.innerHTML = `<p class="hint">아직 기록된 질문이 없습니다. 학습 중 궁금한 점을 물어보면 자동으로 기록됩니다.</p>`; return; }
    const titleOf = {}; if (cur) cur.modules.forEach((m) => (titleOf[m.slug] = m.title));
    const groups = {};
    qa.forEach((q) => { (groups[q.module] = groups[q.module] || []).push(q); });
    box.innerHTML = Object.keys(groups).map((k) =>
      `<section class="module-section"><h2>${titleOf[k] || k}</h2>
        <div class="qa-list">${groups[k].map(qaCard).join("")}</div></section>`).join("");
  }

  /* ---------- 홈: 로드맵 ---------- */
  function renderRoadmap(cur) {
    const box = document.getElementById("roadmap");
    if (!box || !cur) return;
    const done = cur.modules.filter((m) => m.status === "done").length;
    const pct = Math.round((done / cur.modules.length) * 100);
    const prog = document.getElementById("progress");
    if (prog) prog.innerHTML = `<div class="progress"><i style="width:${pct}%"></i></div>
      <p class="hint">${done} / ${cur.modules.length} 모듈 완료 (${pct}%)</p>`;
    box.innerHTML = cur.modules.map((m) => {
      const planned = m.status === "planned" ? " is-planned" : "";
      const href = base + "modules/" + m.slug + ".html";
      return `<a class="mod-card${planned}" href="${href}">
        <span class="badge">${m.order}</span>
        <span><span class="t">${m.title}</span>${m.flavor ? `<span class="flavor">${m.flavor}</span>` : ""}
        <br><span class="s">${m.summary || ""}</span></span></a>`;
    }).join("");
  }

  /* ---------- 유틸 ---------- */
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
  function wireNavToggle() {
    const btn = document.getElementById("navToggle"), sb = document.getElementById("sidebar");
    if (btn && sb) btn.addEventListener("click", () => sb.classList.toggle("open"));
  }

  /* ---------- 부트 ---------- */
  document.addEventListener("DOMContentLoaded", async () => {
    enhanceCode();
    wireNavToggle();
    const [cur, qa] = await Promise.all([loadCurriculum(), loadQa()]);
    renderSidebar(cur);
    if (page === "module") renderModuleQa(qa);
    if (page === "qa") renderQaPage(qa, cur);
    if (page === "home") renderRoadmap(cur);
  });
})();
