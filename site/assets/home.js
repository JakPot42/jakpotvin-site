/* jakpotvin.com home page: the first-screen slideshow, the shrink into the album, the album caption,
   and the rooms' wall colour. With prefers-reduced-motion nothing moves: the first plate stays, still. */
(() => {
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const desktop = matchMedia('(min-width: 761px)');
  root.dataset.motion = reduced ? 'reduced' : 'full';

  // Year, event, subject link and credit of a plate (data-* of a slide or a tile) into a caption element.
  function fillCaption(cap, d) {
    cap.querySelector('.yr').textContent = d.yr;
    cap.querySelector('.what').textContent = d.what;
    const subj = cap.querySelector('.subj');
    subj.textContent = d.subj; subj.setAttribute('href', d.href);
    const b = document.createElement('b'); b.textContent = `Plate ${d.no}.`;
    cap.querySelector('.credit').replaceChildren(b, ' ' + d.credit);
  }

  // One plate at a time: 5 s each, 1 s crossfade; only the current and the next image are loaded.
  function initSlideshow(intro) {
    const box = intro.querySelector('.slides');
    const slides = [...box.querySelectorAll('.slide')];
    const cap = intro.querySelector('.caption');
    const btn = intro.querySelector('.pause');
    let cur = 0, timer = null, paused = false, stopped = false;

    const art = i => slides[(i + slides.length) % slides.length].querySelector('.art');
    const load = i => { const img = art(i); if (img.dataset.src) { img.src = img.dataset.src; img.removeAttribute('data-src'); } };
    const show = i => {
      const prev = slides[cur];
      cur = (i + slides.length) % slides.length;
      const next = slides[cur];
      load(cur + 1);
      prev.classList.remove('on'); prev.classList.add('leaving');
      setTimeout(() => prev.classList.remove('leaving'), 1100);
      next.classList.add('on');
      box.dataset.current = String(cur);
      fillCaption(cap, next.dataset);
      box.dispatchEvent(new Event('slidechange'));
    };
    const tick = () => {
      if (document.hidden || paused || stopped) return;
      const img = art(cur + 1);
      if (img.dataset.src) { load(cur + 1); return; }
      if (!img.complete) return;  // a slow connection: try again on the next tick
      show(cur + 1);
    };
    const start = () => { clearInterval(timer); timer = setInterval(tick, 5000); };
    const setPaused = p => {
      paused = p;
      btn.setAttribute('aria-pressed', String(p));
      btn.setAttribute('aria-label', p ? 'Play the slideshow' : 'Pause the slideshow');
      if (!p) start();
    };

    load(1);
    btn.addEventListener('click', () => setPaused(!paused));
    document.addEventListener('visibilitychange', () => { if (!document.hidden) start(); });
    start();
    return {
      current: () => cur,
      pause: () => setPaused(true),
      play: () => setPaused(false),
      stop: () => { stopped = true; },
      resume: () => { if (stopped) { stopped = false; start(); } },
    };
  }

  // Scrolling off the first screen: the slideshow stops and the zoom eases out; on desktop with scroll-driven
  // animation support (html.sda) CSS then shrinks the current painting into its tile, using the box measured here.
  function initIntroScroll(intro, show) {
    const stage = intro.querySelector('.intro-stage');
    const box = intro.querySelector('.slides');
    const supported = CSS.supports('animation-timeline: scroll()');
    const offset = (el) => { let x = 0, y = 0; for (let n = el; n && n !== stage; n = n.offsetParent) { x += n.offsetLeft; y += n.offsetTop; } return [x, y]; };
    const reset = a => { for (const k of ['top', 'left', 'width', 'height', 'right', 'bottom', 'margin']) a.style[k] = ''; };

    const measure = () => {
      const on = supported && !reduced && desktop.matches;
      root.classList.toggle('sda', on);
      intro.querySelectorAll('.tile.current').forEach(t => t.classList.remove('current'));
      intro.querySelectorAll('.slide .art').forEach(reset);
      if (!on) return;
      const slide = box.querySelector('.slide.on');
      const tile = intro.querySelector(`.tile[data-i="${box.dataset.current}"]`);
      if (!slide || !tile) return;
      tile.classList.add('current');
      const [tx, ty] = offset(tile);
      stage.style.setProperty('--tx', tx + 'px');
      stage.style.setProperty('--ty', ty + 'px');
      stage.style.setProperty('--tw', tile.offsetWidth + 'px');
      stage.style.setProperty('--th', tile.offsetHeight + 'px');
      const a = slide.querySelector('.art');
      a.style.animation = 'none';  // measure the box the shrink starts from, without the animation applied
      const [ax, ay] = offset(a);
      const start = {top: ay + 'px', left: ax + 'px', width: a.offsetWidth + 'px', height: a.offsetHeight + 'px', right: 'auto', bottom: 'auto', margin: '0'};
      a.style.animation = '';
      Object.assign(a.style, start);
    };

    let still = false;
    const freeze = () => {
      const s = box.querySelector('.slide.on');
      if (!s) return;
      const a = s.querySelector('.art');
      a.style.transform = getComputedStyle(a).transform;
      s.classList.add('still');
      requestAnimationFrame(() => { a.style.transition = 'transform .3s ease'; a.style.transform = 'none'; });
    };
    const thaw = () => box.querySelectorAll('.slide').forEach(s => {
      s.classList.remove('still');
      const a = s.querySelector('.art'); a.style.transform = ''; a.style.transition = '';
    });
    const onScroll = () => {
      if (scrollY > 0 && !still) { still = true; show && show.stop(); freeze(); }
      else if (scrollY <= 0 && still) { still = false; thaw(); show && show.resume(); }
    };

    let queued = false;
    const later = () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; measure(); }); } };
    box.addEventListener('slidechange', () => { thaw(); measure(); if (still) freeze(); });
    addEventListener('resize', later);
    desktop.addEventListener('change', later);
    addEventListener('scroll', onScroll, {passive: true});
    measure();
    onScroll();
  }

  // The caption under the album names the tile pointed at, focused, or (on touch) first tapped; a second tap follows the link.
  function initAlbumCaption(wall, cap) {
    let armed = null, touch = false;
    const pick = e => e.target.closest && e.target.closest('.tile');
    wall.addEventListener('pointerdown', e => { touch = e.pointerType === 'touch'; });
    wall.addEventListener('mouseover', e => { const t = pick(e); if (t) fillCaption(cap, t.dataset); });
    wall.addEventListener('focusin', e => { const t = pick(e); if (t) fillCaption(cap, t.dataset); });
    wall.addEventListener('click', e => {
      const t = pick(e);
      if (!t || !touch) return;
      if (armed !== t) { e.preventDefault(); armed = t; fillCaption(cap, t.dataset); }
    });
  }

  // Without the shrink, tiles fade in once as they come into view (full motion only).
  function initTileReveal(wall) {
    if (reduced || !('IntersectionObserver' in window)) return;
    const tiles = [...wall.querySelectorAll('.tile')];
    const io = new IntersectionObserver(es => {
      for (const e of es) if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }, {threshold: 0.1});
    tiles.forEach(t => io.observe(t));
    wall.classList.add('reveal-tiles');
  }

  // Projects: each item rises into place once, the first time it is 15% visible, 90 ms after the one before it.
  function initReveal(items) {
    const list = [...items];
    list.forEach(el => el.classList.add('reveal'));
    if (reduced || !('IntersectionObserver' in window)) { list.forEach(el => el.classList.add('in')); return; }
    const io = new IntersectionObserver(es => {
      let k = 0;
      for (const e of es) {
        if (!e.isIntersecting) continue;
        const el = e.target, delay = el.classList.contains('count') ? 0 : k++ * 90;  // the count never waits its turn
        io.unobserve(el);
        el.style.transitionDelay = delay + 'ms';
        el.classList.add('in');
        const n = el.querySelector('.n[data-to]');
        if (n) countUp(n, delay);
      }
    }, {threshold: 0.15});
    list.forEach(el => io.observe(el));
  }

  // The project count runs from 0 to its number in 1.2 s, easing out, and ends on the page's own text.
  function countUp(n, delay) {
    const to = +n.dataset.to, text = n.textContent, start = performance.now() + delay;
    n.textContent = '0';
    const step = now => {
      const t = Math.min(1, Math.max(0, (now - start) / 1200));
      n.textContent = t >= 1 ? text : String(Math.round(to * (1 - (1 - t) ** 3)));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  // Each room's wall colour, taken from its painting, fills the page as the room comes into view.
  function initRooms(wrap) {
    const rooms = [...wrap.querySelectorAll('.room')];
    if (!rooms.length || !('IntersectionObserver' in window)) return;
    wrap.classList.add('live');
    wrap.style.backgroundColor = rooms[0].dataset.bg;
    const io = new IntersectionObserver(es => {
      for (const e of es) if (e.isIntersecting) wrap.style.backgroundColor = e.target.dataset.bg;
    }, {rootMargin: '-45% 0px -45% 0px'});
    rooms.forEach(r => io.observe(r));
  }

  const intro = document.querySelector('.intro');
  if (intro) {
    const show = reduced ? null : initSlideshow(intro);
    window.slideshow = show;
    initIntroScroll(intro, show);
    const wall = intro.querySelector('.wall'), cap = intro.querySelector('.album-caption');
    if (wall && cap) { initAlbumCaption(wall, cap); initTileReveal(wall); }
  }
  const projects = document.querySelectorAll('#projects li, #projects h3, #projects .count');
  if (projects.length) initReveal(projects);
  const rooms = document.querySelector('.rooms');
  if (rooms) initRooms(rooms);
})();
