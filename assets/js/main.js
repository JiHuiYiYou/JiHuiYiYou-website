// ============================================================
// JHYY landing — interactions
// ============================================================
(() => {
  'use strict';

  // 「减少动态效果」是**硬要求**，不是可选项：
  // 命中时不建碎片、不跑雾气物理、不跑打字机、不做磁吸 ——
  // 只保留入场 reveal 与 hover 反馈。
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  let REDUCED = motionQuery.matches;
  try {
    motionQuery.addEventListener('change', (e) => { REDUCED = e.matches; });
  } catch (_) { /* 老浏览器没有 addEventListener，忽略 */ }

  // ---- 1. Scroll reveal via IntersectionObserver ------------
  const reveal = (el, delay = 0) => {
    el.style.transitionDelay = delay + 'ms';
    el.classList.add('in');
  };

  const ioReveal = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const d = parseInt(e.target.dataset.revealDelay || '0', 10);
      reveal(e.target, d);
      ioReveal.unobserve(e.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

  document.querySelectorAll('.reveal, .reveal-card, .reveal-scale').forEach((el) => ioReveal.observe(el));

  // ---- 2. Line reveal ---------------------------------------
  const ioLine = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const lines = e.target.querySelectorAll('.reveal-line');
      lines.forEach((l) => l.classList.add('in'));
      ioLine.unobserve(e.target);
    });
  }, { threshold: 0.2 });
  document.querySelectorAll('.hero-title, .section-title, .cta-title').forEach((el) => ioLine.observe(el));

  // ---- 3. Pointer: 光点拖影 + 玻璃碎片 + 雾气（共用一套循环） ----
  //
  // 原生光标**保留** —— 之前全局 cursor:none 让全站没有文本 I 形光标。
  // 光点继续跟着鼠标跑，但它是**拖影装饰**，不是指针替身。
  const lastMouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
  const dot = document.querySelector('.cursor-dot');
  const cracksSvg = document.getElementById('cracks');
  const layer = cracksSvg && cracksSvg.querySelector('.cracks-layer');

  // 光点位置（弹簧跟随）
  let cx = window.innerWidth / 2;
  let cy = window.innerHeight / 2;
  if (dot) dot.style.transform = 'translate3d(' + (cx - 2) + 'px,' + (cy - 2) + 'px,0)';

  // 碎片状态
  const shards = [];
  let lastSampleX = -9999;
  let lastSampleY = -9999;
  const SHARD_COLORS = [
    '#00d4aa', '#1de9c0', '#34d399', '#66e9cc',
    '#00ffd0', '#00a886', '#5eead4',
  ];
  const MAX_SHARDS = 80;
  const SHARD_LIFE = 1200; // ms (与 CSS --shard-life 一致)
  const SAMPLE_STEP = 22;  // px — 鼠标每 22 像素扎 1 个

  // 雾气状态
  const mists = Array.from(document.querySelectorAll('.mist'));
  const PUSH_RADIUS = 420;   // px — 鼠标进入半径开始施冲量
  const PUSH_IMPULSE = 2.6;  // 单次冲量大小（累加到速度）
  const MAX_V = 14;          // 速度上限，防止无限加速
  const SPRING_K = 0.0011;   // 弹簧系数（小 → 慢慢拉回）
  const DAMPING = 0.010;     // 阻尼（小 → 漂很久 + 多次过冲）
  const MAX_OFFSET = 480;    // 位置上限，避免飞出视野
  const REST_EPS = 0.05;     // 静止阈值：offset+vel 小于此就跳过 tick

  mists.forEach((m) => {
    const rect = m.getBoundingClientRect();
    m._cx = rect.left + rect.width / 2;
    m._cy = rect.top + rect.height / 2;
    m._px = 0; m._py = 0;    // current offset
    m._vx = 0; m._vy = 0;    // velocity
  });

  // 生成 3-5 个顶点的多边形（锋利、有角）
  const polyPoints = (cx0, cy0, baseR) => {
    const n = 3 + ((Math.random() * 3) | 0);
    const start = Math.random() * Math.PI * 2;
    const pts = [];
    for (let i = 0; i < n; i++) {
      const a = start + (i / n) * Math.PI * 2 + (Math.random() - 0.5) * 0.7;
      const r = baseR * (0.55 + Math.random() * 0.7);
      pts.push((cx0 + Math.cos(a) * r).toFixed(1) + ',' + (cy0 + Math.sin(a) * r).toFixed(1));
    }
    return pts.join(' ');
  };

  function spawnShard(vx, vy) {
    const r1 = 10 + Math.random() * 22;
    const r2 = r1 * (0.55 + Math.random() * 0.35);
    const dx = (Math.random() - 0.5) * 4;
    const dy = (Math.random() - 0.5) * 4;

    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', 'shard');
    g.setAttribute('style', '--shard-life:' + SHARD_LIFE + 'ms;');
    // 用 SVG transform 属性，不被 CSS animation 的 transform 覆盖
    g.setAttribute('transform', 'translate(' + dx + ' ' + dy + ')');

    const body = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    body.setAttribute('class', 's-body');
    body.setAttribute('points', polyPoints(vx, vy, r1));
    body.setAttribute('stroke', SHARD_COLORS[(Math.random() * SHARD_COLORS.length) | 0]);
    g.appendChild(body);

    // 1 条内部短裂纹（少元素，降 GPU 负载）
    const a1 = Math.random() * Math.PI * 2;
    const a2 = a1 + (Math.random() - 0.5) * 1.4;
    const lr = r1 * (0.5 + Math.random() * 0.4);
    const x1 = vx + Math.cos(a1) * (r1 * 0.3);
    const y1 = vy + Math.sin(a1) * (r1 * 0.3);
    const x2 = x1 + Math.cos(a2) * lr;
    const y2 = y1 + Math.sin(a2) * lr;
    const ln = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    ln.setAttribute('class', 's-line');
    ln.setAttribute('x1', x1.toFixed(1));
    ln.setAttribute('y1', y1.toFixed(1));
    ln.setAttribute('x2', x2.toFixed(1));
    ln.setAttribute('y2', y2.toFixed(1));
    ln.setAttribute('stroke', SHARD_COLORS[(Math.random() * SHARD_COLORS.length) | 0]);
    g.appendChild(ln);

    layer.appendChild(g);
    shards.push({ el: g, born: performance.now() });

    if (shards.length > MAX_SHARDS) {
      const old = shards.shift();
      old.el.remove();
    }
  }

  // 在线段 (x0,y0)→(x1,y1) 上按 SAMPLE_STEP 等距撒 shards
  const burstBetween = (x0, y0, x1, y1) => {
    const dx = x1 - x0, dy = y1 - y0;
    const dist = Math.hypot(dx, dy);
    if (dist < 1) { spawnShard(x1, y1); return; }
    const n = Math.max(1, Math.floor(dist / SAMPLE_STEP));
    for (let i = 0; i <= n; i++) {
      const t = i / n;
      spawnShard(x0 + dx * t, y0 + dy * t);
    }
  };

  // ---- 4. 磁吸按钮 ------------------------------------------------
  if (!REDUCED) {
    document.querySelectorAll('[data-magnetic]').forEach((btn) => {
      const strength = 0.35;
      btn.addEventListener('mousemove', (e) => {
        const r = btn.getBoundingClientRect();
        const x = e.clientX - (r.left + r.width / 2);
        const y = e.clientY - (r.top + r.height / 2);
        btn.style.transform = `translate(${x * strength}px, ${y * strength}px)`;
      });
      btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
    });
  }

  // ---- 5. 指针事件（一次监听，三个消费者） --------------------------
  let pendingMx = 0, pendingMy = 0, pendingMove = false;

  window.addEventListener('mousemove', (e) => {
    lastMouse.x = e.clientX;
    lastMouse.y = e.clientY;
    pendingMx = e.clientX;
    pendingMy = e.clientY;
    pendingMove = true;

    // 玻璃碎片
    if (!REDUCED && layer) {
      if (lastSampleX < -9000) {
        lastSampleX = e.clientX;
        lastSampleY = e.clientY;
        spawnShard(e.clientX, e.clientY);
      } else {
        burstBetween(lastSampleX, lastSampleY, e.clientX, e.clientY);
        lastSampleX = e.clientX;
        lastSampleY = e.clientY;
      }
    }
  }, { passive: true });

  window.addEventListener('resize', () => {
    if (cracksSvg) {
      cracksSvg.setAttribute('width', window.innerWidth);
      cracksSvg.setAttribute('height', window.innerHeight);
      cracksSvg.setAttribute('viewBox', '0 0 ' + window.innerWidth + ' ' + window.innerHeight);
    }
    mists.forEach((m) => {
      const rect = m.getBoundingClientRect();
      m._cx = rect.left + rect.width / 2;
      m._cy = rect.top + rect.height / 2;
    });
  }, { passive: true });

  // ---- 6. 唯一的 rAF 循环：光点 + 碎片清理 + 雾气弹簧 ---------------
  let tickCount = 0;
  const frame = () => {
    // 光点：弹簧跟随（拖影，比原生光标慢一拍）
    cx += (lastMouse.x - cx) * 0.35;
    cy += (lastMouse.y - cy) * 0.35;
    if (dot) dot.style.transform = 'translate3d(' + (cx - 2) + 'px,' + (cy - 2) + 'px,0)';

    // 碎片：每帧清掉过期的
    const now = performance.now();
    while (shards.length > 0 && now - shards[0].born > SHARD_LIFE + 80) {
      shards[0].el.remove();
      shards.shift();
    }

    // 雾气：鼠标冲量 + 弹簧回位（隔帧跑，省 GPU）
    if (!REDUCED && mists.length) {
      tickCount++;
      const doTick = (tickCount & 1) === 0;
      if (pendingMove) {
        const mx = pendingMx, my = pendingMy;
        pendingMove = false;
        for (let i = 0; i < mists.length; i++) {
          const m = mists[i];
          const dx = m._cx - mx;
          const dy = m._cy - my;
          const d = Math.hypot(dx, dy);
          if (d > 0 && d < PUSH_RADIUS) {
            const f = (1 - d / PUSH_RADIUS);
            const force = f * f * PUSH_IMPULSE;
            m._vx += (dx / d) * force;
            m._vy += (dy / d) * force;
            const v = Math.hypot(m._vx, m._vy);
            if (v > MAX_V) {
              m._vx = (m._vx / v) * MAX_V;
              m._vy = (m._vy / v) * MAX_V;
            }
          }
        }
      }
      if (doTick) {
        for (let i = 0; i < mists.length; i++) {
          const m = mists[i];
          if (Math.abs(m._px) + Math.abs(m._py) + Math.abs(m._vx) + Math.abs(m._vy) < REST_EPS) continue;
          m._vx += -SPRING_K * m._px;
          m._vy += -SPRING_K * m._py;
          m._vx *= (1 - DAMPING);
          m._vy *= (1 - DAMPING);
          m._px += m._vx;
          m._py += m._vy;
          const off = Math.hypot(m._px, m._py);
          if (off > MAX_OFFSET) {
            m._px = (m._px / off) * MAX_OFFSET;
            m._py = (m._py / off) * MAX_OFFSET;
            m._vx *= 0.7;
            m._vy *= 0.7;
          }
          m.style.transform = 'translate3d(' + m._px.toFixed(2) + 'px,' + m._py.toFixed(2) + 'px,0)';
        }
      }
    }

    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);

  // ---- 7. Nav scroll state -----------------------------------
  const nav = document.querySelector('.floating-nav');
  const onScroll = () => {
    if (!nav) return;
    if (window.scrollY > 8) nav.classList.add('is-scrolled');
    else nav.classList.remove('is-scrolled');
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // ---- 8. Stats counter -------------------------------------
  const ioCount = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const el = e.target;
      const target = parseFloat(el.dataset.target || '0');
      const suffix = el.dataset.suffix || '';
      const dur = 1100;
      const start = performance.now();
      const step = (now) => {
        const t = Math.min(1, (now - start) / dur);
        const eased = 1 - Math.pow(1 - t, 3);
        const val = Math.round(target * eased);
        el.textContent = val + suffix;
        if (t < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
      ioCount.unobserve(el);
    });
  }, { threshold: 0.4 });
  document.querySelectorAll('[data-counter]').forEach((el) => ioCount.observe(el));

  // ---- 9. Code showcase tabs --------------------------------
  const tabs = document.querySelectorAll('.stab');
  const panels = document.querySelectorAll('.panel-code');
  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const id = tab.dataset.tab;
      tabs.forEach((t) => t.classList.toggle('active', t === tab));
      panels.forEach((p) => p.classList.toggle('active', p.dataset.tab === id));
      // Update file tab + cmd/out
      const fname = tab.querySelector('.stab-name')?.textContent || '';
      const fnameEl = document.querySelector('.panel-filename');
      const cmdEl = document.getElementById('panelCmd');
      const outEl = document.getElementById('panelOut');
      if (fnameEl) fnameEl.textContent = fname;
      if (cmdEl) cmdEl.textContent = '$ jhyy run ' + fname;
      // Out strings keyed by tab id (kept in HTML data attrs)
      // v1.8.3.2 sync: tab 04 wrapper now calls `unwrap(Option::Some(99))`,
      // so the displayed exit value is 99 not 7. (Tab 02 wrapper uses
      // `dist_sq(Point { x: 3, y: 4 }, Point { x: 0, y: 0 })` = 25 — unchanged.)
      const outs = {
        '01': 'Hello, world!',
        '02': 'point · dist² = 25',
        '03': 'fib(10) = 55',
        '04': 'unwrap(Some(99)) = 99',
      };
      if (outEl) outEl.textContent = outs[id] || '';
    });
  });

  // ---- 10. Copy button feedback ------------------------------
  const setCopied = (btn, label = 'Copied') => {
    if (!btn) return;
    const original = btn.querySelector('span')?.textContent || btn.textContent;
    btn.classList.add('copied');
    const span = btn.querySelector('span');
    if (span) span.textContent = label;
    setTimeout(() => {
      btn.classList.remove('copied');
      if (span) span.textContent = original;
    }, 1400);
  };

  document.querySelectorAll('.copy-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const code = document.querySelector('.panel-code.active')?.innerText || '';
      try {
        await navigator.clipboard.writeText(code);
        setCopied(btn, 'Copied');
      } catch {
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = code;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); setCopied(btn, 'Copied'); }
        catch { setCopied(btn, 'Failed'); }
        ta.remove();
      }
    });
  });

  document.querySelectorAll('.ci-copy').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const text =
        btn.dataset.copyText ||
        btn.closest('.cta-install, .community-value')?.querySelector('.ci-line')?.innerText ||
        '';
      try {
        await navigator.clipboard.writeText(text);
        setCopied(btn, 'OK');
      } catch {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); setCopied(btn, 'OK'); }
        catch { setCopied(btn, 'No'); }
        ta.remove();
      }
    });
  });

  // ---- 11. Smooth scroll for in-page anchors -----------------
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const href = a.getAttribute('href');
      if (!href || href === '#') return;
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth', block: 'start' });
    });
  });

  // ---- 12. Hero code typewriter (one-shot) -------------------
  const heroCode = document.getElementById('heroCode');
  if (heroCode) {
    const src = heroCode.dataset.src || '';
    if (src) {
      if (REDUCED) {
        // 减少动态效果：直接给全文，不逐字写
        heroCode.textContent = src;
      } else {
        heroCode.textContent = '';
        let i = 0;
        const type = () => {
          if (i >= src.length) return;
          heroCode.textContent = src.slice(0, i + 1);
          i++;
          const ch = src[i - 1];
          const delay = ch === '\n' ? 60 : (ch === ' ' ? 12 : 18);
          setTimeout(type, delay);
        };
        // Start after a short delay so reveal completes first
        setTimeout(type, 900);
      }
    }
  }
})();
