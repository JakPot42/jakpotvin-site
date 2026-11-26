/* jakpotvin.com home page: the first-screen slideshow and the rooms' wall colour.
   With prefers-reduced-motion nothing moves: the first plate stays, still. */
(() => {
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  root.dataset.motion = reduced ? 'reduced' : 'full';

  // One plate at a time: 5 s each, 1 s crossfade; only the current and the next image are loaded.
  function initSlideshow(intro) {
    const box = intro.querySelector('.slides');
    const slides = [...box.querySelectorAll('.slide')];
    const cap = intro.querySelector('.caption');
    const btn = intro.querySelector('.pause');
    const f = {yr: cap.querySelector('.yr'), what: cap.querySelector('.what'), subj: cap.querySelector('.subj'), credit: cap.querySelector('.credit')};
    let cur = 0, timer = null, paused = false, stopped = false;

    const art = i => slides[(i + slides.length) % slides.length].querySelector('.art');
    const load = i => { const img = art(i); if (img.dataset.src) { img.src = img.dataset.src; img.removeAttribute('data-src'); } };
    const caption = d => {
      f.yr.textContent = d.yr; f.what.textContent = d.what;
      f.subj.textContent = d.subj; f.subj.setAttribute('href', d.href);
      const b = document.createElement('b'); b.textContent = `Plate ${d.no}.`;
      f.credit.replaceChildren(b, ' ' + d.credit);
    };
    const show = i => {
      const prev = slides[cur];
      cur = (i + slides.length) % slides.length;
      const next = slides[cur];
      load(cur + 1);
      prev.classList.remove('on'); prev.classList.add('leaving');
      setTimeout(() => prev.classList.remove('leaving'), 1100);
      next.classList.add('on');
      box.dataset.current = String(cur);
      caption(next.dataset);
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
  if (intro && !reduced) window.slideshow = initSlideshow(intro);
  const rooms = document.querySelector('.rooms');
  if (rooms) initRooms(rooms);
})();
