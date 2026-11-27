/* jakpotvin.com home page: the projects reveal and count, and the rooms (each room's paintings change by themselves
   every 6 seconds while half the room is on screen, with a pause button that holds every room; a room's paintings load
   as the visitor nears it). The first screen is one still painting and needs no script.
   With prefers-reduced-motion the projects stay in place, the rooms start paused and the paintings change without the
   fade (site.css). */
(() => {
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  root.dataset.motion = reduced ? 'reduced' : 'full';

  // Year, event, subject link (if the caption has one) and credit of a painting (data-* of a slide) into a caption.
  function fillCaption(cap, d) {
    cap.querySelector('.yr').textContent = d.yr;
    cap.querySelector('.what').textContent = d.what;
    const subj = cap.querySelector('.subj');
    if (subj) { subj.textContent = d.subj; subj.setAttribute('href', d.href); }
    cap.querySelector('.credit').textContent = d.credit;
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

  const EVERY = 6000;  // milliseconds between a room's paintings

  // The rooms: each room is one screen and its paintings fill it behind the title, one at a time. While at least half
  // of a room is on screen, and the page is neither hidden nor paused, its painting moves on every EVERY ms and loops,
  // picking up where it stopped; a painting whose image failed is skipped, and one still loading is waited for. A room's
  // paintings load when it is on screen, or, once the banner has loaded, when it comes within one screen. Each room with
  // two or more paintings gets a pause button, and every button holds or lets go of every room.
  function initRooms(wrap) {
    const rooms = [...wrap.querySelectorAll('.room')].map(el => ({
      el, slides: [...el.querySelectorAll('.slide')], cap: el.querySelector('.caption'), cur: 0, loaded: false, seen: false, timer: 0}));
    const load = room => {
      if (room.loaded) return;
      room.loaded = true;
      room.el.querySelectorAll('.art[data-src]').forEach(img => { img.src = img.dataset.src; img.removeAttribute('data-src'); });
    };
    if (!('IntersectionObserver' in window)) { rooms.forEach(load); return; }  // every first painting, nothing moves
    let paused = reduced;
    const buttons = [];
    const show = (room, i) => {
      room.slides[room.cur].classList.remove('on');
      room.slides[i].classList.add('on');
      room.cur = i;
      if (room.cap) fillCaption(room.cap, room.slides[i].dataset);
    };
    const step = room => {
      const n = room.slides.length;
      for (let k = 1; k < n; k++) {
        const i = (room.cur + k) % n, img = room.slides[i].querySelector('.art');
        if (img.dataset.src || !img.complete) return;  // not loaded yet: try again at the next tick
        if (img.naturalWidth > 0) { show(room, i); return; }
      }  // the others failed: stay
    };
    const stop = room => { clearInterval(room.timer); room.timer = 0; };
    const start = room => {
      if (room.timer || !room.seen || paused || document.hidden || room.slides.length < 2) return;
      room.timer = setInterval(() => step(room), EVERY);
    };
    const setPaused = p => {
      paused = p;
      buttons.forEach(b => b.setAttribute('aria-pressed', String(p)));
      rooms.forEach(room => (p ? stop(room) : start(room)));
    };
    for (const room of rooms) {
      if (room.slides.length < 2) continue;
      const b = document.createElement('button');
      b.className = 'pause';
      b.type = 'button';
      b.setAttribute('aria-label', 'Pause the paintings');  // a toggle: its name stays, aria-pressed says whether it holds them
      b.setAttribute('aria-pressed', String(paused));
      b.appendChild(document.createElement('span'));
      b.addEventListener('click', () => setPaused(!paused));
      room.el.querySelector('.room-stick').appendChild(b);
      buttons.push(b);
    }
    const io = new IntersectionObserver(es => {
      for (const e of es) {
        const room = rooms.find(r => r.el === e.target);
        if (e.isIntersecting) load(room);
        room.seen = e.intersectionRatio >= 0.499;  // half on screen (a hair under, for rounding at the threshold)
        if (room.seen) start(room); else stop(room);
      }
    }, {threshold: [0, 0.45, 0.5, 0.75]});  // 0.45: a room that slips just under half on a slow scroll is told again
    rooms.forEach(room => io.observe(room.el));
    document.addEventListener('visibilitychange', () => rooms.forEach(room => (document.hidden ? stop(room) : start(room))));
    const lookAhead = () => {
      const near = new IntersectionObserver(es => {
        for (const e of es) if (e.isIntersecting) {
          load(rooms.find(room => room.el === e.target));
          near.unobserve(e.target);
        }
      }, {rootMargin: '100% 0px'});
      rooms.forEach(room => { if (!room.loaded) near.observe(room.el); });
    };
    if (document.readyState === 'complete') lookAhead(); else addEventListener('load', lookAhead);
  }

  const projects = document.querySelectorAll('#projects li, #projects h3, #projects .count');
  if (projects.length) initReveal(projects);
  const rooms = document.querySelector('.rooms');
  if (rooms) initRooms(rooms);
})();
