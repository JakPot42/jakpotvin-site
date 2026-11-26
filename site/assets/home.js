/* jakpotvin.com home page: the projects reveal and count, and the rooms (wall colour, pinned plates).
   The first screen is one still painting and needs no script. With prefers-reduced-motion nothing moves. */
(() => {
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const desktop = matchMedia('(min-width: 761px)');
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

  const projects = document.querySelectorAll('#projects li, #projects h3, #projects .count');
  if (projects.length) initReveal(projects);
  const rooms = document.querySelector('.rooms');
  if (rooms) initRooms(rooms);
})();
