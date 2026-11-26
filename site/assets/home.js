/* jakpotvin.com home page: the projects reveal and count, and the rooms (each room's paintings, chosen by scrolling,
   loaded as the visitor nears them). The first screen is one still painting and needs no script.
   With prefers-reduced-motion the projects stay in place and the paintings change without the fade (site.css). */
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

  // Which of a room's n paintings shows: the share of the room scrolled past, from its top at the top of the screen
  // to its bottom at the bottom of the screen, cut into n equal parts.
  const paintingIndex = (top, height, view, n) =>
    n < 2 ? 0 : Math.min(n - 1, Math.floor(Math.max(0, -top) / Math.max(1, height - view) * n));

  // The rooms: each room's paintings fill the screen behind its title, one at a time, and change only as the visitor
  // scrolls through the room. A room's paintings load when it is on screen, or, once the banner has loaded, when it
  // comes within one screen.
  function initRooms(wrap) {
    const rooms = [...wrap.querySelectorAll('.room')].map(el => ({
      el, slides: [...el.querySelectorAll('.slide')], cap: el.querySelector('.caption'), cur: 0, loaded: false}));
    const load = room => {
      if (room.loaded) return;
      room.loaded = true;
      room.el.querySelectorAll('.art[data-src]').forEach(img => { img.src = img.dataset.src; img.removeAttribute('data-src'); });
    };
    const update = () => {
      const view = innerHeight;
      for (const room of rooms) {
        if (!room.slides.length) continue;
        const r = room.el.getBoundingClientRect();
        if (r.top < view && r.bottom > 0) load(room);
        const i = paintingIndex(r.top, r.height, view, room.slides.length);
        if (i === room.cur) continue;
        room.slides[room.cur].classList.remove('on');
        room.slides[i].classList.add('on');
        room.cur = i;
        if (room.cap) fillCaption(room.cap, room.slides[i].dataset);
      }
    };
    let queued = false;
    addEventListener('scroll', () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => { queued = false; update(); });
    }, {passive: true});
    addEventListener('resize', update);
    update();
    const lookAhead = () => {
      if (!('IntersectionObserver' in window)) { rooms.forEach(load); return; }
      const io = new IntersectionObserver(es => {
        for (const e of es) if (e.isIntersecting) {
          load(rooms.find(room => room.el === e.target));
          io.unobserve(e.target);
        }
      }, {rootMargin: '100% 0px'});
      rooms.forEach(room => { if (!room.loaded) io.observe(room.el); });
    };
    if (document.readyState === 'complete') lookAhead(); else addEventListener('load', lookAhead);
  }

  const projects = document.querySelectorAll('#projects li, #projects h3, #projects .count');
  if (projects.length) initReveal(projects);
  const rooms = document.querySelector('.rooms');
  if (rooms) initRooms(rooms);
})();
