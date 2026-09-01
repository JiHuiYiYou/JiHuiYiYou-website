// ============================================================
// JHYY landing — interactions
// ============================================================
(() => {
  'use strict';

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

  // Word-level reveal lines (used in H1 / H2)
  const ioLine = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      // Reveal each line with a stagger
      const lines = e.target.querySelectorAll('.reveal-line');
      lines.forEach((l) => l.classList.add('in'));
      ioLine.unobserve(e.target);
    });
  }, { threshold: 0.2 });
  document.querySelectorAll('.hero-title, .section-title, .cta-title').forEach((el) => ioLine.observe(el));

  // ---- 2. Cursor glass-shard crack effect --------------------
  // DISABLED (user: 滚轮无特效 — wheel burst + mousemove shards 太花)
  if (false) {
  {
    document.body.classList.add('has-cursor');
    // lastMouse 必须在外层作用域,follow 循环在外面要访问
    const lastMouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
    const dot = document.querySelector('.cursor-dot');
    const cracksSvg = document.getElementById('cracks');
    const layer = cracksSvg && cracksSvg.querySelector('.cracks-layer');

    if (layer && cracksSvg) {
      // 容器 = viewport 尺寸(viewport 锚定,100% 100% 有效)
      const sizeCracks = () => {
        cracksSvg.setAttribute('width', window.innerWidth);
        cracksSvg.setAttribute('height', window.innerHeight);
        cracksSvg.setAttribute('viewBox', '0 0 ' + window.innerWidth + ' ' + window.innerHeight);
      };
      sizeCracks();
      window.addEventListener('resize', sizeCracks, { passive: true });

      // 玻璃碎片的 7 种绿色
      const SHARD_COLORS = [
        '#00d4aa', '#1de9c0', '#34d399', '#66e9cc',
        '#00ffd0', '#00a886', '#5eead4',
      ];

      const MAX_SHARDS = 80;
      const SHARD_LIFE = 1200; // ms (与 CSS --shard-life 一致)
      const SAMPLE_STEP = 22;  // px — 鼠标每 22 像素扎 1 个
      const WHEEL_BURST = 3;

      const shards = [];
      let lastSampleX = -9999, lastSampleY = -9999;
      // lastMouse 提上去了,这里不再声明

      // 生成 3-5 个顶点的多边形(锋利、有角)
      const polyPoints = (cx, cy, baseR) => {
        const n = 3 + ((Math.random() * 3) | 0);
        const start = Math.random() * Math.PI * 2;
        const pts = [];
        for (let i = 0; i < n; i++) {
          const a = start + (i / n) * Math.PI * 2 + (Math.random() - 0.5) * 0.7;
          const r = baseR * (0.55 + Math.random() * 0.7);
          pts.push((cx + Math.cos(a) * r).toFixed(1) + ',' + (cy + Math.sin(a) * r).toFixed(1));
        }
        return pts.join(' ');
      };

      const spawnShard = (vx, vy) => {
        // viewport 坐标(SVG 跟 viewport 走,shards 实时跟鼠标)
        const x = vx;
        const y = vy;
        const color = SHARD_COLORS[(Math.random() * SHARD_COLORS.length) | 0];
        const r1 = 10 + Math.random() * 22;
        const r2 = r1 * (0.55 + Math.random() * 0.35);
        const dx = (Math.random() - 0.5) * 4;
        const dy = (Math.random() - 0.5) * 4;

        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'shard');
        g.setAttribute('style', '--shard-life:' + SHARD_LIFE + 'ms;');
        // 用 SVG transform 属性,不被 CSS animation 的 transform 覆盖
        g.setAttribute('transform', 'translate(' + dx + ' ' + dy + ')');

        // 主轮廓 polygon
        const body = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        body.setAttribute('class', 's-body');
        body.setAttribute('points', polyPoints(x, y, r1));
        body.setAttribute('stroke', color);
        g.appendChild(body);

        // 1 条内部短裂纹(更少元素,降 GPU 负载)
        const a1 = Math.random() * Math.PI * 2;
        const a2 = a1 + (Math.random() - 0.5) * 1.4;
        const lr = r1 * (0.5 + Math.random() * 0.4);
        const x1 = x + Math.cos(a1) * (r1 * 0.3);
        const y1 = y + Math.sin(a1) * (r1 * 0.3);
        const x2 = x1 + Math.cos(a2) * lr;
        const y2 = y1 + Math.sin(a2) * lr;
        const ln = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        ln.setAttribute('class', 's-line');
        ln.setAttribute('x1', x1.toFixed(1));
        ln.setAttribute('y1', y1.toFixed(1));
        ln.setAttribute('x2', x2.toFixed(1));
        ln.setAttribute('y2', y2.toFixed(1));
        ln.setAttribute('stroke', color);
        g.appendChild(ln);

        layer.appendChild(g);
        shards.push({ el: g, born: performance.now() });

        if (shards.length > MAX_SHARDS) {
          const old = shards.shift();
          old.el.remove();
        }
      };

      // 在线段 (x0,y0)→(x1,y1) 上按 SAMPLE_STEP 等距撒 shards
      // 这样直着走也能密集产生,不会因为 mousemove 步长太大而漏
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

      window.addEventListener('mousemove', (e) => {
        lastMouse.x = e.clientX;
        lastMouse.y = e.clientY;
        if (lastSampleX < -9000) {
          lastSampleX = e.clientX;
          lastSampleY = e.clientY;
          spawnShard(e.clientX, e.clientY);
          return;
        }
        burstBetween(lastSampleX, lastSampleY, e.clientX, e.clientY);
        lastSampleX = e.clientX;
        lastSampleY = e.clientY;
      }, { passive: true });

      window.addEventListener('wheel', () => {
        for (let i = 0; i < WHEEL_BURST; i++) {
          spawnShard(
            lastMouse.x + (Math.random() - 0.5) * 70,
            lastMouse.y + (Math.random() - 0.5) * 70,
          );
        }
        lastSampleX = lastMouse.x;
        lastSampleY = lastMouse.y;
      }, { passive: true });

      // 每帧清理过期的 shard
      const cleanup = () => {
        const now = performance.now();
        while (shards.length > 0 && now - shards[0].born > SHARD_LIFE + 80) {
          shards[0].el.remove();
          shards.shift();
        }
        requestAnimationFrame(cleanup);
      };
      requestAnimationFrame(cleanup);
    }

    // 光标尖点 spring lag
    let cx = window.innerWidth / 2, cy = window.innerHeight / 2;
    if (!dot) {
      console.error('[JHYY] cursor-dot NOT FOUND — querying all .cursor-dot:', document.querySelectorAll('.cursor-dot').length);
    }
    // 立即把 dot 摆到屏幕中央,避免看不见
    if (dot) dot.style.transform = 'translate3d(' + (cx - 2) + 'px,' + (cy - 2) + 'px,0)';
    const follow = () => {
      // lastMouse 由 mousemove 实时更新;初次 (-100,-100) → spring 平滑滑入
      cx += (lastMouse.x - cx) * 0.35;
      cy += (lastMouse.y - cy) * 0.35;
      if (dot) dot.style.transform = 'translate3d(' + (cx - 2) + 'px,' + (cy - 2) + 'px,0)';
      requestAnimationFrame(follow);
    };
    requestAnimationFrame(follow);

    // Hover 状态
    document.querySelectorAll('a, button, [data-magnetic]').forEach((el) => {
      el.addEventListener('mouseenter', () => dot && dot.classList.add('is-hover'));
      el.addEventListener('mouseleave', () => dot && dot.classList.remove('is-hover'));
    });
  }
  } // end if(false) — DISABLED cursor effect

  // ---- 4. Magnetic button effect ----------------------------
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

  // ---- 5. Nav scroll state ----------------------------------
  const nav = document.querySelector('.floating-nav');
  const onScroll = () => {
    if (!nav) return;
    if (window.scrollY > 8) nav.classList.add('is-scrolled');
    else nav.classList.remove('is-scrolled');
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // ---- 6. Stats counter -------------------------------------
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

  // ---- 7. Code showcase tabs --------------------------------
  const tabs = document.querySelectorAll('.stab');
  const panels = document.querySelectorAll('.panel-code');
  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const id = tab.dataset.tab;
      tabs.forEach((t) => t.classList.toggle('active', t === tab));
      panels.forEach((p) => p.classList.toggle('active', p.dataset.tab === id));
      // Update file tab + cmd/out
      const fname = tab.querySelector('.stab-name')?.textContent || '';
      const sub = tab.querySelector('.stab-sub')?.textContent || '';
      const fnameEl = document.querySelector('.panel-filename');
      const cmdEl = document.getElementById('panelCmd');
      const outEl = document.getElementById('panelOut');
      if (fnameEl) fnameEl.textContent = fname;
      if (cmdEl) cmdEl.textContent = '$ jhyy run ' + fname;
      // Out strings keyed by tab id (kept in HTML data attrs)
      const outs = {
        '01': 'Hello, world!',
        '02': 'point · dist² = 25',
        '03': 'fib(10) = 55',
        '04': 'unwrap(Some(7)) = 7',
      };
      if (outEl) outEl.textContent = outs[id] || '';
    });
  });

  // ---- 8. Copy button feedback ------------------------------
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

  // ---- 9. Smooth scroll for in-page anchors -----------------
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const href = a.getAttribute('href');
      if (!href || href === '#') return;
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'auto', block: 'start' });
    });
  });

  // ---- 10. Hero code typewriter (one-shot) -------------------
  const heroCode = document.getElementById('heroCode');
  if (heroCode) {
    const src = heroCode.dataset.src || '';
    if (src) {
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

  // ---- 11. Purple mist — mouse pushes blobs with momentum ---
  //  弹簧物理:每个 blob 有 vx/vy 速度,鼠标施加冲量(累加),弹簧慢慢拉回
  //  - mousemove 用 rAF 合并(每帧最多 1 次冲量,降 CPU)
  //  - 静止 blob (|offset|+|vel|<eps) 跳过 spring tick
  //  - 极低 SPRING_K + 极小 DAMPING = 飘很久 + 过冲
  const mists = document.querySelectorAll('.mist');
  if (mists.length) {
    const PUSH_RADIUS = 420;   // px — 鼠标进入半径开始施冲量
    const PUSH_IMPULSE = 2.6;  // 单次冲量大小(累加到速度)
    const MAX_V = 14;          // 速度上限,防止无限加速
    const SPRING_K = 0.0011;   // 弹簧系数(小 → 慢慢拉回)
    const DAMPING = 0.010;     // 阻尼(小 → 漂很久 + 多次过冲)
    const MAX_OFFSET = 480;    // 位置上限,避免飞出视野
    const REST_EPS = 0.05;     // 静止阈值:offset+vel 小于此则跳过 tick

    mists.forEach((m) => {
      const rect = m.getBoundingClientRect();
      m._cx = rect.left + rect.width / 2;
      m._cy = rect.top + rect.height / 2;
      m._px = 0; m._py = 0;    // current offset
      m._vx = 0; m._vy = 0;    // velocity
    });

    // mousemove 合并:rAF 频率,不每事件都算
    let pendingMx = 0, pendingMy = 0, pendingMove = false;
    window.addEventListener('mousemove', (e) => {
      pendingMx = e.clientX; pendingMy = e.clientY; pendingMove = true;
    }, { passive: true });

    window.addEventListener('resize', () => {
      mists.forEach((m) => {
        const rect = m.getBoundingClientRect();
        m._cx = rect.left + rect.width / 2;
        m._cy = rect.top + rect.height / 2;
      });
    }, { passive: true });

    // tick 降到 ~30fps (隔帧跑) 省 GPU
    let tickCount = 0;
    const tickMist = () => {
      tickCount++;
      const doTick = (tickCount & 1) === 0;  // 偶数帧才跑
      // 一帧最多 apply 一次 pending mousemove
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
              m._vx = m._vx / v * MAX_V;
              m._vy = m._vy / v * MAX_V;
            }
          }
        }
      }

      if (doTick) {
        // spring tick;静止 blob 跳过
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
            m._px = m._px / off * MAX_OFFSET;
            m._py = m._py / off * MAX_OFFSET;
            m._vx *= 0.7; m._vy *= 0.7;
          }
          m.style.transform = 'translate3d(' + m._px.toFixed(2) + 'px,' + m._py.toFixed(2) + 'px,0)';
        }
      }
      requestAnimationFrame(tickMist);
    };
    requestAnimationFrame(tickMist);
  }
})();
