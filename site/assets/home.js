/* jakpotvin.com home page: the first-screen slideshow, the projects reveal and count,
   and the rooms (wall colour, pinned plates). With prefers-reduced-motion nothing moves: the first plate stays, still. */
(() => {
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const desktop = matchMedia('(min-width: 761px)');
  root.dataset.motion = reduced ? 'reduced' : 'full';

  // Year, event, subject link and credit of a plate (data-* of a slide) into a caption element.
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
      load(cur); load(cur + 1);
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
      btn.setAttribute('aria-pressed', String(p));  // a toggle: its name stays "Pause the slideshow"
      box.classList.toggle('paused', p);           // CSS also freezes the slow zoom
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
      goto: i => { if (i !== cur) show(i); },
    };
  }

  // Scrolling off the first screen: the slideshow stops and the zoom eases out; back at the top it plays again (unless paused).
  function initIntroScroll(intro, show) {
    const box = intro.querySelector('.slides');
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
    box.addEventListener('slidechange', () => { thaw(); if (still) freeze(); });
    addEventListener('scroll', onScroll, {passive: true});
    onScroll();
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

  // The rooms: each room's wall colour, taken from its painting, fills the page as the room reaches the middle of
  // the screen. On desktop with full motion the plates move into the pinned stage and cross-fade room by room.
  function initRooms(wrap) {
    const rooms = [...wrap.querySelectorAll('.room')];
    const stage = wrap.querySelector('.rooms-stage');
    if (!rooms.length || !('IntersectionObserver' in window)) return;
    const plates = new Map(rooms.map(r => [r.id, r.querySelector('.room-plates')]));
    plates.forEach((p, id) => { if (p) p.dataset.room = id; });
    let current = rooms[0].id;
    const mark = () => plates.forEach((p, id) => p && p.classList.toggle('on', id === current));
    const pin = () => {
      const want = !reduced && desktop.matches && !!stage;
      if (want === wrap.classList.contains('pinned')) return;
      wrap.classList.toggle('pinned', want);
      rooms.forEach(r => {
        const p = plates.get(r.id);
        if (p) (want ? stage : r.querySelector('.room-in')).appendChild(p);
      });
      mark();
    };
    wrap.classList.add('live');
    wrap.style.backgroundColor = rooms[0].dataset.bg;
    const io = new IntersectionObserver(es => {
      for (const e of es) if (e.isIntersecting) {
        wrap.style.backgroundColor = e.target.dataset.bg;
        current = e.target.id;
        mark();
      }
    }, {rootMargin: '-45% 0px -45% 0px'});
    rooms.forEach(r => io.observe(r));
    desktop.addEventListener('change', pin);
    pin();
    mark();
  }

  const intro = document.querySelector('.intro');
  if (intro) {
    const show = reduced ? null : initSlideshow(intro);
    window.slideshow = show;
    initIntroScroll(intro, show);
  }
  const projects = document.querySelectorAll('#projects li, #projects h3, #projects .count');
  if (projects.length) initReveal(projects);
  const rooms = document.querySelector('.rooms');
  if (rooms) initRooms(rooms);
})();
