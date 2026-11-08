/* ============================================================
   文档层脚本：搜索浮层 + 右锚点高亮
   无依赖。搜索索引由 tools/build.py 生成到 /search-index.json
   ============================================================ */
(function () {
  "use strict";

  /* ── 右锚点：滚动时高亮当前小节 ─────────────────────────── */
  var anchors = Array.prototype.slice.call(document.querySelectorAll(".doc-anchors a"));
  if (anchors.length) {
    var byId = {};
    anchors.forEach(function (a) {
      var id = decodeURIComponent(a.getAttribute("href").slice(1));
      var el = document.getElementById(id);
      if (el) byId[id] = a;
    });
    var targets = Object.keys(byId).map(function (id) { return document.getElementById(id); }).filter(Boolean);
    var ticking = false;
    function update() {
      var best = null;
      var line = window.scrollY + 120;
      for (var i = 0; i < targets.length; i++) {
        if (targets[i].offsetTop <= line) best = targets[i];
      }
      anchors.forEach(function (a) { a.style.borderLeftColor = ""; a.style.color = ""; });
      if (best && byId[best.id]) {
        byId[best.id].style.borderLeftColor = "var(--doc-accent)";
        byId[best.id].style.color = "var(--doc-ink)";
      }
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
    }, { passive: true });
    update();
  }

  /* ── 搜索浮层 ──────────────────────────────────────────── */
  var openBtn = document.querySelector("[data-search-open]");
  if (!openBtn) return;

  var modal = document.createElement("div");
  modal.className = "doc-search-modal";
  modal.innerHTML =
    '<div class="doc-search-panel" role="dialog" aria-modal="true" aria-label="搜索文档">' +
      '<input class="doc-search-input" type="search" placeholder="搜教程、指南、错误码…" aria-label="搜索文档" />' +
      '<div class="doc-search-results"></div>' +
      '<div class="doc-search-foot"><span>↑↓ 选择</span><span>Enter 打开</span><span>Esc 关闭</span></div>' +
    '</div>';
  document.body.appendChild(modal);

  var input = modal.querySelector(".doc-search-input");
  var results = modal.querySelector(".doc-search-results");
  var idx = null;
  var loading = false;
  var hits = [];
  var sel = 0;

  var idxUrl = openBtn.getAttribute("data-search-index") || "search-index.json";
  var base = idxUrl.replace(/[^/]*$/, "");

  function loadIndex() {
    if (idx || loading) return;
    loading = true;
    fetch(idxUrl)
      .then(function (r) { return r.json(); })
      .then(function (data) { idx = data; loading = false; })
      .catch(function () { idx = []; loading = false; });
  }

  function score(entry, q) {
    var t = (entry.title || "").toLowerCase();
    var d = (entry.desc || "").toLowerCase();
    var x = (entry.text || "").toLowerCase();
    var s = 0;
    if (t.indexOf(q) !== -1) s += 100;
    if (d.indexOf(q) !== -1) s += 40;
    if (x.indexOf(q) !== -1) s += 12;
    (entry.headings || []).forEach(function (h) {
      if ((h.text || "").toLowerCase().indexOf(q) !== -1) s += 25;
    });
    return s;
  }

  function render(q) {
    if (!q) {
      results.innerHTML = '<div class="doc-search-empty">输入关键词，搜索教程、指南、规范与错误码。</div>';
      hits = [];
      return;
    }
    if (!idx) { loadIndex(); results.innerHTML = '<div class="doc-search-empty">索引加载中…</div>'; return; }
    hits = idx
      .map(function (e) { return { e: e, s: score(e, q) }; })
      .filter(function (r) { return r.s > 0; })
      .sort(function (a, b) { return b.s - a.s; })
      .slice(0, 12)
      .map(function (r) { return r.e; });
    sel = 0;
    if (!hits.length) {
      results.innerHTML = '<div class="doc-search-empty">没有匹配「' + escapeHtml(q) + '」的结果。</div>';
      return;
    }
    results.innerHTML = hits.map(function (h, i) {
      var url = base + h.url.replace(/^\//, "");
      return '<a class="doc-search-hit' + (i === 0 ? " is-sel" : "") + '" href="' + url + '">' +
        '<div class="doc-search-hit-title">' + escapeHtml(h.title) + '</div>' +
        '<div class="doc-search-hit-url">' + escapeHtml(h.url) + '</div>' +
        (h.desc ? '<div class="doc-search-hit-text">' + escapeHtml(h.desc) + '</div>' : '') +
        '</a>';
    }).join("");
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function open() {
    modal.classList.add("is-open");
    input.value = "";
    render("");
    loadIndex();
    setTimeout(function () { input.focus(); }, 30);
  }
  function close() { modal.classList.remove("is-open"); }

  openBtn.addEventListener("click", open);
  modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
  input.addEventListener("input", function () { render(input.value.trim().toLowerCase()); });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { close(); return; }
    if (!hits.length) return;
    var nodes = results.querySelectorAll(".doc-search-hit");
    if (e.key === "ArrowDown") {
      e.preventDefault();
      sel = Math.min(sel + 1, hits.length - 1);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      sel = Math.max(sel - 1, 0);
    } else if (e.key === "Enter") {
      e.preventDefault();
      window.location.href = base + hits[sel].url.replace(/^\//, "");
      return;
    }
    if (nodes[sel]) {
      nodes.forEach(function (n) { n.classList.remove("is-sel"); });
      nodes[sel].classList.add("is-sel");
      nodes[sel].scrollIntoView({ block: "nearest" });
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && document.activeElement !== input && !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) {
      e.preventDefault();
      open();
    } else if (e.key === "Escape" && modal.classList.contains("is-open")) {
      close();
    }
  });
})();
