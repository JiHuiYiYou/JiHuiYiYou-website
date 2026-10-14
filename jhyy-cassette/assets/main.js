/* ═══════════════════════════════════════════════════════════════
   JHYY 介绍页 — 卡带未来主义动效
   规则：打字机、步进、开机闪烁、换台雪花。不做顺滑缓动。
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── 频道选择 ─────────────────────────────────────────────── */
  var screen    = document.querySelector('.crt__screen');
  var snow      = document.getElementById('crtSnow');
  var buttons   = Array.prototype.slice.call(document.querySelectorAll('.chanbtn'));
  var channels  = Array.prototype.slice.call(document.querySelectorAll('.chan'));
  var current   = 1;
  var typeTimer = null;

  function playSnow() {
    if (reduced) return;
    snow.classList.remove('is-on');
    void snow.offsetWidth;          // 强制重排，让动画能重播
    snow.classList.add('is-on');
  }

  /* 逐行打字：按 \n 切开原 HTML，一行一行补上去 */
  function typeInto(term, done) {
    if (!term) { done(); return; }
    var lines = term.dataset.src.split('\n');
    clearTimeout(typeTimer);
    term.textContent = '';

    if (reduced) { term.innerHTML = term.dataset.src; done(); return; }

    var i = 0;
    (function step() {
      term.innerHTML = lines.slice(0, i).join('\n') + '<span class="cursor">▊</span>';
      i += 1;
      if (i <= lines.length) {
        typeTimer = setTimeout(step, 52);
      } else {
        term.innerHTML = term.dataset.src;
        done();
      }
    })();
  }

  function tuneChannel(n, instant) {
    var chan = document.querySelector('.chan[data-chan="' + n + '"]');
    if (!chan) return;
    var term = chan.querySelector('.term');

    channels.forEach(function (c) { c.classList.remove('is-active'); });
    buttons.forEach(function (b) {
      var on = b.dataset.goto === String(n);
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });

    playSnow();
    // 重播开机闪烁
    chan.classList.remove('is-active');
    void chan.offsetWidth;
    chan.classList.add('is-active');

    if (instant) {
      clearTimeout(typeTimer);
      if (term) term.innerHTML = term.dataset.src;
    } else {
      typeInto(term, function () {});
    }
  }

  // 缓存原始内容，供打字机重放
  channels.forEach(function (chan) {
    var term = chan.querySelector('.term');
    if (term) term.dataset.src = term.innerHTML;
  });

  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      stopAutoCycle();
      current = Number(btn.dataset.goto);
      tuneChannel(current, false);
    });
  });

  /* ── 自动轮播（像没关的电视） ───────────────────────────────── */
  var autoTimer = null;
  var autoOn = !reduced;

  function stopAutoCycle() {
    autoOn = false;
    clearInterval(autoTimer);
  }

  function startAutoCycle() {
    if (!autoOn) return;
    autoTimer = setInterval(function () {
      current = current % channels.length + 1;
      tuneChannel(current, false);
    }, 15000);
  }

  ['pointerdown', 'keydown', 'wheel', 'touchstart'].forEach(function (evt) {
    window.addEventListener(evt, function (e) {
      if (evt === 'wheel' || (evt === 'keydown' && e.key === 'Tab')) return;
      stopAutoCycle();
    }, { once: true, passive: true });
  });

  /* ── 滚动入场：12 帧步进 ───────────────────────────────────── */
  var reveals = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));

  if (!('IntersectionObserver' in window) || reduced) {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, i) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        // 同屏内按顺序错开，模拟逐格点亮
        setTimeout(function () { el.classList.add('is-in'); }, i * 70);
        io.unobserve(el);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    reveals.forEach(function (el) { io.observe(el); });
  }

  /* ── 读数条 ───────────────────────────────────────────────── */
  var bars = Array.prototype.slice.call(document.querySelectorAll('.readout__bar'));

  if ('IntersectionObserver' in window && !reduced) {
    var bio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var bar = entry.target;
        var target = bar.style.getPropertyValue('--v');
        setTimeout(function () { bar.style.setProperty('--shown', target || '0%'); }, 80);
        bio.unobserve(bar);
      });
    }, { threshold: 0.4 });
    bars.forEach(function (b) { bio.observe(b); });
  } else {
    bars.forEach(function (b) { b.style.setProperty('--shown', b.style.getPropertyValue('--v') || '0%'); });
  }

  /* ── 启动 ─────────────────────────────────────────────────── */
  // 首屏：雪花一下 + 打完 CH-01
  tuneChannel(1, false);
  startAutoCycle();
})();
