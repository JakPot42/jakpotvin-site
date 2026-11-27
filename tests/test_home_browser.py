"""Browser tests: the built site in headless Edge (see tools/browser.py). Run: python -m pytest"""
import json
from pathlib import Path

import pytest

from tools.browser import DESKTOP, PHONE, open_home

ROOT = Path(__file__).resolve().parent.parent


def site_text(name):
    import sitetext
    return " ".join(sitetext.parse((ROOT / "site-text.txt").read_text(encoding="utf-8"))[name])


def rect(page, selector):
    return page.eval("(() => { const el = document.querySelector(%s); if (!el) return null; const r = el.getBoundingClientRect();"
                     " return {left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height}; })()"
                     % json.dumps(selector))


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE, {**DESKTOP, "reduced_motion": True}, {**PHONE, "reduced_motion": True}],
                         ids=["desktop", "phone", "desktop-rm", "phone-rm"])
@pytest.mark.parametrize("path", ["index.html", "plates.html", "atoms/index.html", "atoms/calculator/index.html"])
def test_pages_load_cleanly(browser, site, cfg, path):
    page = browser.open(site.url(path), **cfg)
    page.wait(1.5)
    assert page.console_problems() == []
    assert page.outside_requests() == []
    assert page.failed_requests() == []
    assert page.eval("document.documentElement.scrollWidth <= innerWidth")


# ---------------------------------------------------------------- Task 4: the first screen

BANNER = "washington-crossing.jpg"
STILL = ("none", "matrix(1, 0, 0, 1, 0, 0)")


BANNER_FILES = ["washington-crossing.jpg", "newton-prism.jpg", "gaspee-burning.jpg", "constitution-guerriere.jpg",
                "london-sewers-1859.jpg", "wright-first-flight.jpg", "laika-1957.jpg", "von-braun-office.jpg", "earthrise-apollo8.jpg",
                "f22-raptor.jpg"]
BANNER_EVERY = 4.0  # the first screen changes every 4 s while half of it is on screen
BANNER_TICK = 4.7  # one change and a margin
ARTS_WITH_SRC = "[...document.querySelectorAll('.intro .art')].map(a => !!a.getAttribute('src'))"


def test_banner_caption_names_the_painting_and_no_room(browser, site):  # the banner is the background, not a room's
    page = open_home(browser, site, DESKTOP)
    q = "document.querySelector('.hero .caption %s').%s"
    assert page.eval(q % (".yr", "textContent")) == "1776"
    assert page.eval(q % (".what", "textContent")) == "Washington crosses the Delaware"
    assert page.eval("document.querySelector('.hero .caption .subj')") is None
    assert page.eval(q % (".credit", "textContent")) == "Leutze, Washington Crossing the Delaware"


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_first_screen_without_scrolling(browser, site, cfg):
    page = open_home(browser, site, cfg)
    page.wait(1)
    assert page.eval("scrollY") == 0
    assert page.eval("document.querySelector('.intro h1').textContent.trim()") == site_text("name")
    whole = page.eval("document.querySelector('.slide.on').classList.contains('whole')")
    assert page.eval("(() => { const i = document.querySelector('.slide.on .art'); return i.complete && i.naturalWidth > 0; })()")
    cover = rect(page, ".slide.on .bg" if whole else ".slide.on .art")
    vw, vh = page.eval("innerWidth"), page.eval("innerHeight")
    assert cover["left"] <= 0 and cover["top"] <= 0 and cover["right"] >= vw - 1 and cover["bottom"] >= vh - 1
    for sel in (".intro h1", ".intro .lede"):
        r = rect(page, sel)
        assert r["top"] >= 0 and r["bottom"] <= vh, sel


def test_phone_first_screen_contents_fit(browser, site):
    page = open_home(browser, site, PHONE)
    page.wait(0.5)
    for sel in (".intro h1", ".intro .lede", ".intro .note", ".intro .intro-links"):
        r = rect(page, sel)
        assert r is not None and r["height"] > 0 and r["bottom"] <= 915, sel
    assert page.eval("parseFloat(getComputedStyle(document.querySelector('.intro .caption .yr')).fontSize)") <= 16
    assert page.eval("[...document.querySelectorAll('.intro-links a')].map(a => a.getAttribute('href'))") == ["#projects", "#writing"]


LUMINANCE = (r"(() => { const c = getComputedStyle(document.querySelector(%s)).color.match(/[\d.]+/g).map(Number);"
             " const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };"
             " return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); })()")


def test_header_over_slide_on_home_only(browser, site):
    page = open_home(browser, site, DESKTOP)
    assert page.eval("getComputedStyle(document.querySelector('.top .name')).display") == "none"
    assert page.eval("getComputedStyle(document.querySelector('.top nav')).display") != "none"
    assert page.eval(LUMINANCE % json.dumps(".top nav a")) > 0.7
    assert rect(page, ".top")["top"] < 40 and rect(page, ".intro")["top"] <= 0
    other = browser.open(site.url("plates.html"), **DESKTOP)
    assert other.eval("getComputedStyle(document.querySelector('.top .name')).display") != "none"


# ---------------------------------------------------------------- Task 5 (album removed 26 Nov): scrolling, deep links, widths

def test_scroll_back_restores_first_screen(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.scroll_to(page.eval("innerHeight"))
    page.wait(0.5)
    page.scroll_to(0)
    page.wait(0.6)
    r = rect(page, ".slide.on .art")
    assert r["left"] <= 0 and r["top"] <= 0 and r["right"] >= 1439 and r["bottom"] >= 899
    assert page.eval("getComputedStyle(document.querySelector('.intro-text')).opacity") == "1"


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_deep_link_lands_on_section(browser, site, cfg):
    page = open_home(browser, site, cfg, hash="#projects")
    page.wait(1)
    vh = page.eval("innerHeight")
    top = rect(page, "#projects-h")["top"]
    assert 0 <= top <= 0.4 * vh, top
    text = rect(page, ".intro-text")
    assert text["bottom"] <= top or text["top"] >= vh or page.eval("getComputedStyle(document.querySelector('.intro-text')).visibility") == "hidden"


@pytest.mark.parametrize("w, h", [(800, 1280), (1024, 768)])
def test_no_sideways_overflow_between_breakpoints(browser, site, w, h):
    page = open_home(browser, site, dict(width=w, height=h, mobile=False))
    for k in range(4):
        page.scroll_to(k * h)
        page.wait(0.3)
        assert page.eval("document.documentElement.scrollWidth <= innerWidth"), k


# ---------------------------------------------------------------- Task 6: projects arrive

def count_number(page):
    return page.eval("document.querySelector('#projects .count .n').textContent")


def test_projects_rise_in_once(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(0.5)
    assert page.eval("[...document.querySelectorAll('#projects li')].every(li => li.classList.contains('reveal') && !li.classList.contains('in'))")
    page.eval("document.querySelector('#projects').scrollIntoView(); 1")
    page.wait(0.3)
    page.eval("document.querySelector('#projects .links.areas').scrollIntoView({block: 'center'}); 1")
    page.wait(1.5)
    assert page.eval("[...document.querySelectorAll('#projects li')].every(li => li.classList.contains('in') && getComputedStyle(li).opacity === '1')")
    page.scroll_to(0)
    page.wait(0.3)
    page.eval("document.querySelector('#projects').scrollIntoView(); 1")
    assert page.eval("[...document.querySelectorAll('#projects li')].every(li => li.classList.contains('in'))")


def test_counter_counts_to_80(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(0.5)
    page.eval("document.querySelector('#projects .count').scrollIntoView({block: 'center'}); 1")
    page.wait(0.3)
    mid = int(count_number(page))
    assert 1 <= mid <= 79, mid
    page.wait(1.7)
    assert count_number(page) == "80"


def test_counter_text_without_motion(browser, site):
    page = open_home(browser, site, {**DESKTOP, "reduced_motion": True})
    assert page.eval(r"document.querySelector('#projects .count').textContent.replace(/\s+/g, ' ').trim()") == "80+ projects"
    assert page.eval("[...document.querySelectorAll('#projects *')].every(el => getComputedStyle(el).opacity === '1')")


# ---------------------------------------------------------------- the rooms: three paintings, full screen, changing by themselves

TICK = 6.8  # a room changes every 6 s while half of it is on screen; this is one change plus the fade and a margin


def room_on_screen(page, rid, share=1.0):
    """Scroll so that `share` of room rid is on screen: 1.0 puts its top at the top of the screen, 0.3 its top 70% down."""
    page.eval("(() => { const r = document.getElementById(%s);"
              " scrollTo(0, Math.round(r.getBoundingClientRect().top + scrollY - innerHeight * (1 - %s)));"
              " return new Promise(f => requestAnimationFrame(() => requestAnimationFrame(f))); })()" % (json.dumps(rid), share))


def loaded(page, rid):
    """Wait until every painting of room rid has loaded (or failed)."""
    return page.eval("Promise.all([...document.querySelectorAll('#%s .art')].map(a => a.complete && !a.dataset.src ? 1 :"
                     " new Promise(f => { a.addEventListener('load', () => f(1)); a.addEventListener('error', () => f(0)); setTimeout(() => f(0), 8000); })))" % rid)


def all_pressed(page, value):
    return page.eval("[...document.querySelectorAll('.room .pause')].every(b => b.getAttribute('aria-pressed') === %s)" % json.dumps(value))


def set_painting(page, rid, k):
    """Show painting k of room rid directly (its caption filled from the painting's data), scroll the room to the top of
    the screen and wait until the painting has loaded: for measuring what a painting looks like, not how rooms change."""
    page.eval("(() => { const r = document.getElementById(%s), k = %d; r.scrollIntoView();"
              " r.querySelectorAll('.art[data-src]').forEach(i => { i.src = i.dataset.src; i.removeAttribute('data-src'); });"
              " r.querySelectorAll('.slide').forEach((s, i) => s.classList.toggle('on', i === k));"
              " const d = r.querySelectorAll('.slide')[k].dataset, c = r.querySelector('.caption');"
              " c.querySelector('.yr').textContent = d.yr; c.querySelector('.what').textContent = d.what; c.querySelector('.credit').textContent = d.credit;"
              " const a = r.querySelector('.slide.on .art');"
              " return a.complete && a.naturalWidth ? 1 : new Promise(f => { a.onload = () => f(1); a.onerror = () => f(0); setTimeout(() => f(0), 8000); }); })()"
              % (json.dumps(rid), k))
    page.eval("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")


def on_index(page, rid):
    return page.eval("[...document.getElementById(%s).querySelectorAll('.slide')].findIndex(s => s.classList.contains('on'))" % json.dumps(rid))


def caption_matches(page, rid):
    return page.eval("(r => { const s = r.querySelector('.slide.on').dataset, c = r.querySelector('.caption');"
                     " return c.querySelector('.yr').textContent === s.yr && c.querySelector('.what').textContent === s.what"
                     " && c.querySelector('.credit').textContent === s.credit; })(document.getElementById(%s))" % json.dumps(rid))


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_banner_changes_every_four_seconds(browser, site, cfg):
    page = open_home(browser, site, cfg)
    assert page.eval("document.querySelectorAll('.intro .slide').length") == len(BANNER_FILES)
    assert page.eval("document.querySelector('.intro .slide.on .art').getAttribute('src')") == "assets/img/" + BANNER
    page.wait(1)
    assert on_index(page, "intro") == 0
    page.wait(BANNER_TICK - 1)
    assert on_index(page, "intro") == 1 and caption_matches(page, "intro")
    page.wait(BANNER_EVERY)
    assert on_index(page, "intro") == 2 and caption_matches(page, "intro")
    zoom = "getComputedStyle(document.querySelector('.intro .slide.on .art')).transform"
    assert page.eval(zoom) in STILL  # it fades from one to the next; nothing zooms


def test_banner_loads_one_picture_ahead(browser, site):  # Review Focus 2: a visitor who never waits fetches one more
    page = open_home(browser, site, DESKTOP)
    page.wait(1.5)
    assert page.eval(ARTS_WITH_SRC) == [True, True] + [False] * (len(BANNER_FILES) - 2)
    page.wait(BANNER_TICK - 1.5)
    assert on_index(page, "intro") == 1
    assert page.eval(ARTS_WITH_SRC) == [True, True, True] + [False] * (len(BANNER_FILES) - 3)


def test_banner_waits_for_the_page_on_a_slow_connection(browser, site):  # final review: nothing starts ahead of Washington
    page = browser.open(site.url("index.html"), **DESKTOP, kbps=1500, latency=100)  # the page takes longer than one change
    entries = page.eval("performance.getEntriesByType('resource').filter(e => e.name.includes('/assets/img/') && !e.name.includes('/blur/'))"
                        ".map(e => [e.name.split('/').pop(), e.startTime, e.responseEnd])")
    washington = [e for e in entries if e[0] == BANNER]
    assert len(washington) == 1
    assert [name for name, start, _ in entries if name != BANNER and start < washington[0][2] - 1] == []
    assert on_index(page, "intro") == 0


def test_banner_skips_a_picture_that_failed_to_load(browser, site):  # Review Focus 1
    page = open_home(browser, site, DESKTOP)
    page.eval("(a => new Promise(f => { a.onerror = () => f(1); a.removeAttribute('data-src'); a.src = 'assets/img/missing.jpg'; }))"
              "(document.querySelectorAll('.intro .art')[1])")
    page.wait(BANNER_TICK + BANNER_EVERY)
    assert on_index(page, "intro") == 2 and caption_matches(page, "intro")


def test_one_pause_holds_the_banner_and_the_rooms(browser, site):  # Review Focus 3
    pressed = "[...document.querySelectorAll('.pause')].map(b => b.getAttribute('aria-pressed'))"
    page = open_home(browser, site, DESKTOP)
    page.wait(0.5)
    page.click(".intro .pause")
    assert set(page.eval(pressed)) == {"true"} and len(page.eval(pressed)) == 11
    page.wait(BANNER_TICK)
    assert on_index(page, "intro") == 0
    room_on_screen(page, "s-economics")
    loaded(page, "s-economics")
    page.wait(TICK)
    assert on_index(page, "s-economics") == 0
    page.click("#s-economics .pause")
    assert set(page.eval(pressed)) == {"false"}
    page.scroll_to(0)
    page.wait(BANNER_TICK)
    assert on_index(page, "intro") == 1 and caption_matches(page, "intro")


def test_less_motion_starts_the_banner_paused(browser, site):
    page = open_home(browser, site, {**DESKTOP, "reduced_motion": True})
    assert page.eval("document.querySelector('.intro .pause').getAttribute('aria-pressed')") == "true"
    page.wait(BANNER_TICK)
    assert on_index(page, "intro") == 0


@pytest.mark.parametrize("w, h, mobile", [(1440, 900, False), (412, 915, True), (320, 640, True), (915, 412, True), (1280, 600, False)])
def test_banner_pause_is_a_named_button_clear_of_the_words(browser, site, w, h, mobile):  # Review Focus 4
    page = open_home(browser, site, dict(width=w, height=h, mobile=mobile))
    page.wait(0.5)
    assert page.eval("(b => b.tagName === 'BUTTON' && b.type === 'button' && b.getAttribute('aria-label') === 'Pause the paintings'"
                     " && !b.closest('[aria-hidden]') && getComputedStyle(b).pointerEvents !== 'none')(document.querySelector('.intro .pause'))")
    b, hero = rect(page, ".intro .pause"), rect(page, ".hero")
    assert b["left"] >= 0 and b["right"] <= w and b["top"] >= hero["top"] and b["bottom"] <= hero["bottom"], (b, hero)
    for other in (".intro-text", ".hero .caption", ".hero .cue", ".top nav"):
        o = rect(page, other)
        assert b["right"] <= o["left"] or b["left"] >= o["right"] or b["bottom"] <= o["top"] or b["top"] >= o["bottom"], (other, b, o)


def test_banner_without_javascript_is_washington_alone(browser, site):  # Review Focus 5
    page = browser.open(site.url("index.html"), **DESKTOP, javascript=False)
    page.wait(1)
    assert page.eval("[...document.querySelectorAll('.intro .art')].filter(a => a.getAttribute('src')).map(a => a.getAttribute('src'))") == [
        "assets/img/" + BANNER]
    assert page.eval("document.querySelector('.intro .slide.on .art').complete")
    assert page.eval("document.querySelector('.intro .pause')") is None


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_room_is_one_screen_tall(browser, site, cfg):
    page = open_home(browser, site, cfg)
    assert page.eval("[...document.querySelectorAll('.room')].every(r => Math.abs(r.offsetHeight - innerHeight) <= 2)")


@pytest.mark.parametrize("cfg, steps", [(DESKTOP, (1, 2, 0)), (PHONE, (1,))], ids=["desktop", "phone"])
def test_room_paintings_change_by_themselves(browser, site, cfg, steps):
    page = open_home(browser, site, cfg)
    room_on_screen(page, "s-philosophy")
    loaded(page, "s-philosophy")
    assert on_index(page, "s-philosophy") == 0 and caption_matches(page, "s-philosophy")
    for n, want in enumerate(steps):
        page.wait(TICK if n == 0 else 6.0)
        assert on_index(page, "s-philosophy") == want and caption_matches(page, "s-philosophy"), want
    assert page.eval("document.getElementById('s-philosophy').querySelectorAll('.slide.on').length") == 1


def test_room_waits_while_off_screen(browser, site):  # Review Focus 4
    page = open_home(browser, site, DESKTOP)
    room_on_screen(page, "s-economics", share=0.3)
    loaded(page, "s-economics")
    page.wait(TICK)
    assert on_index(page, "s-economics") == 0  # less than half of it on screen: it waits
    room_on_screen(page, "s-economics")
    page.wait(3)
    page.scroll_to(0)  # gone before its first change
    page.wait(TICK)
    room_on_screen(page, "s-economics")
    assert on_index(page, "s-economics") == 0


def test_coming_back_does_not_speed_up_a_room(browser, site):  # Review Focus 5
    page = open_home(browser, site, DESKTOP)
    room_on_screen(page, "s-sociology")
    loaded(page, "s-sociology")
    for _ in range(4):
        page.scroll_to(0)
        page.wait(0.1)
        room_on_screen(page, "s-sociology")
        page.wait(0.1)
    page.wait(3)
    assert on_index(page, "s-sociology") == 0
    page.wait(TICK - 3)
    assert on_index(page, "s-sociology") == 1



def test_room_stops_when_it_slips_under_half(browser, site):  # final review: a slow scroll out of a room
    page = open_home(browser, site, DESKTOP)
    room_on_screen(page, "s-economics")
    loaded(page, "s-economics")
    room_on_screen(page, "s-economics", share=0.495)  # just under half: the first frame past the 0.5 line
    room_on_screen(page, "s-economics", share=0.2)
    page.wait(TICK)
    assert on_index(page, "s-economics") == 0


def test_one_timer_per_room_however_often_it_starts(browser, site):  # final review: Review Focus 5, the guard itself
    import time
    page = open_home(browser, site, DESKTOP)
    room_on_screen(page, "s-sociology")
    loaded(page, "s-sociology")
    t0 = time.monotonic()
    for _ in range(4):  # across the 0.75 line and back, always more than half on screen: start() is asked again each time
        room_on_screen(page, "s-sociology", share=0.6)
        page.wait(0.1)
        room_on_screen(page, "s-sociology", share=0.95)
        page.wait(0.1)
    page.wait(3)
    assert on_index(page, "s-sociology") == 0
    page.wait(max(0.5, t0 + TICK - time.monotonic()))
    assert on_index(page, "s-sociology") == 1  # stacked timers would have moved it on several times
    page.scroll_to(0)
    page.wait(TICK)
    room_on_screen(page, "s-sociology")
    assert on_index(page, "s-sociology") == 1  # and an orphaned one would have kept going off screen

def test_pause_stops_every_room_and_play_resumes(browser, site):
    page = open_home(browser, site, DESKTOP)
    room_on_screen(page, "s-philosophy")
    loaded(page, "s-philosophy")
    page.click("#s-philosophy .pause")
    assert all_pressed(page, "true")
    page.wait(TICK)
    assert on_index(page, "s-philosophy") == 0
    room_on_screen(page, "s-warfare")
    loaded(page, "s-warfare")
    page.wait(TICK)
    assert on_index(page, "s-warfare") == 0
    page.click("#s-warfare .pause")
    assert all_pressed(page, "false")
    page.wait(TICK)
    assert on_index(page, "s-warfare") == 1 and caption_matches(page, "s-warfare")


def test_less_motion_starts_paused(browser, site):
    page = open_home(browser, site, {**DESKTOP, "reduced_motion": True})
    room_on_screen(page, "s-physics")
    loaded(page, "s-physics")
    assert all_pressed(page, "true")
    page.wait(TICK)
    assert on_index(page, "s-physics") == 0
    page.click("#s-physics .pause")
    page.wait(TICK)
    assert on_index(page, "s-physics") == 1


def test_hidden_tab_holds_the_rooms(browser, site):  # Review Focus 2
    page = open_home(browser, site, DESKTOP)
    room_on_screen(page, "s-biology")
    loaded(page, "s-biology")
    hide = "Object.defineProperty(document, 'hidden', {configurable: true, get: () => %s}); document.dispatchEvent(new Event('visibilitychange')); 1"
    page.eval(hide % "true")
    page.wait(TICK)
    assert on_index(page, "s-biology") == 0
    page.eval(hide % "false")
    page.wait(3)
    assert on_index(page, "s-biology") == 0  # no catching up
    page.wait(TICK - 3)
    assert on_index(page, "s-biology") == 1


def test_room_skips_a_painting_that_failed_to_load(browser, site):
    page = open_home(browser, site, DESKTOP)
    room_on_screen(page, "s-tech")
    loaded(page, "s-tech")
    page.eval("(a => new Promise(f => { a.onerror = () => f(1); a.src = 'assets/img/missing.jpg'; }))(document.querySelectorAll('#s-tech .art')[1])")
    page.wait(TICK)
    assert on_index(page, "s-tech") == 2 and caption_matches(page, "s-tech")


@pytest.mark.parametrize("w, h, mobile", [(1440, 900, False), (412, 915, True), (915, 412, True), (1280, 600, False)])
def test_pause_button_is_a_named_button_clear_of_the_words(browser, site, w, h, mobile):  # Review Focus 3
    page = open_home(browser, site, dict(width=w, height=h, mobile=mobile))
    assert page.eval("document.querySelectorAll('.room .pause').length") == 10
    assert page.eval("[...document.querySelectorAll('.room .pause')].every(b => b.tagName === 'BUTTON' && b.type === 'button'"
                     " && b.getAttribute('aria-label') === 'Pause the paintings' && !b.closest('[aria-hidden]'))")
    assert page.eval("(b => { b.focus(); return document.activeElement === b; })(document.querySelector('#s-politics .pause'))")
    assert page.eval("document.querySelector('.room .caption').getAttribute('aria-live')") is None  # changes are not announced
    for rid in ("s-politics", "s-tech"):
        room_on_screen(page, rid)
        b = rect(page, f"#{rid} .pause")
        assert b["top"] >= 0 and b["bottom"] <= h and b["left"] >= 0 and b["right"] <= w, (rid, b)
        for other in (f"#{rid} .room-text", f"#{rid} .caption"):
            o = rect(page, other)
            assert b["right"] <= o["left"] or b["left"] >= o["right"] or b["bottom"] <= o["top"] or b["top"] >= o["bottom"], (rid, other, b, o)


def test_resize_mid_room_keeps_one_right_painting(browser, site):  # a phone turned sideways in a room
    page = open_home(browser, site, PHONE)
    room_on_screen(page, "s-biology")
    loaded(page, "s-biology")
    page.wait(TICK)
    assert on_index(page, "s-biology") == 1
    page.resize(915, 412, settle=0.8)
    assert page.eval("document.getElementById('s-biology').querySelectorAll('.slide.on').length") == 1
    assert on_index(page, "s-biology") == 1 and caption_matches(page, "s-biology")
    assert abs(page.eval("document.getElementById('s-biology').offsetHeight") - 412) <= 2
    assert page.eval("document.documentElement.scrollWidth <= innerWidth")


@pytest.mark.parametrize("w, h, mobile", [(1440, 900, False), (412, 915, True), (915, 412, True), (1280, 600, False), (800, 600, False)])
def test_room_words_never_overlap_the_caption(browser, site, w, h, mobile):  # Review Focus 4
    page = open_home(browser, site, dict(width=w, height=h, mobile=mobile))
    for rid in ("s-politics", "s-tech"):
        room_on_screen(page, rid)
        assert rect(page, f"#{rid} .room-text")["bottom"] <= rect(page, f"#{rid} .caption")["top"], rid
        assert rect(page, f"#{rid} .room-text h2")["top"] >= 0, rid


def test_room_deep_link_lands_on_its_first_painting(browser, site):  # Review Focus 5
    page = open_home(browser, site, DESKTOP, hash="#s-economics")
    page.wait(1.5)
    assert abs(rect(page, "#s-economics")["top"]) <= 1
    assert on_index(page, "s-economics") == 0
    assert page.eval("(a => a.complete && a.naturalWidth > 0)(document.querySelector('#s-economics .slide.on .art'))")


def test_text_sits_left_on_laptops_and_low_on_phones(browser, site):
    page = open_home(browser, site, DESKTOP)
    room_on_screen(page, "s-sociology")
    t = rect(page, "#s-sociology .room-text")
    assert t["left"] <= 0.25 * 1440 and t["right"] <= 0.55 * 1440 and 0.2 * 900 <= (t["top"] + t["bottom"]) / 2 <= 0.8 * 900
    page = open_home(browser, site, PHONE)
    room_on_screen(page, "s-sociology")
    assert rect(page, "#s-sociology .room-text")["top"] >= 0.45 * 915


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_every_room_painting_fills_the_screen(browser, site, cfg):  # tall ones too, cropped around their focal point
    page = open_home(browser, site, cfg)
    page.eval(NO_FADE)
    for rid in page.eval("[...document.querySelectorAll('.room')].map(r => r.id)"):
        assert page.eval(f"document.querySelectorAll('#{rid} .bg').length") == 0, rid
        for k in range(3):
            set_painting(page, rid, k)
            s = f"#{rid} .slide.on .art"
            cover = rect(page, s)
            assert cover["left"] <= 1 and cover["top"] <= 1 and cover["right"] >= cfg["width"] - 1 and cover["bottom"] >= cfg["height"] - 1, (rid, k, cover)
            assert page.eval(f"getComputedStyle(document.querySelector('{s}')).objectFit") == "cover", (rid, k)


@pytest.mark.parametrize("cfg, want", [(DESKTOP, "0.6s"), ({**DESKTOP, "reduced_motion": True}, "0s")], ids=["fade", "no-fade"])
def test_paintings_fade_unless_less_motion(browser, site, cfg, want):
    page = open_home(browser, site, cfg)
    assert page.eval("getComputedStyle(document.querySelector('.room .slide')).transitionDuration").split(",")[0] == want


def test_banner_loads_before_any_room_painting(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(2)
    entries = page.eval("performance.getEntriesByType('resource').filter(e => e.name.includes('/assets/img/') && !e.name.includes('/blur/'))"
                        ".map(e => [e.name.split('/').pop(), e.startTime, e.responseEnd])")
    banner = [e for e in entries if e[0] == "washington-crossing.jpg"]
    assert len(banner) == 1
    assert all(start >= banner[0][2] - 1 for name, start, _ in entries if name != "washington-crossing.jpg")


def test_far_rooms_wait_until_the_visitor_nears_them(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(2)
    assert page.eval("document.querySelectorAll('#s-future .art[data-src]').length") == 3
    page.scroll_to(page.eval("document.getElementById('s-future').getBoundingClientRect().top + scrollY - innerHeight * 0.9"))
    page.wait(0.8)
    assert page.eval("document.querySelectorAll('#s-future .art[data-src]').length") == 0


# ---------------------------------------------------------------- final review fixes

def test_slides_hidden_from_screen_readers(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(1.2)
    assert page.eval("document.querySelector('.slides').getAttribute('aria-hidden')") == "true"
    assert page.eval("document.querySelectorAll('.room-bg[aria-hidden=\"true\"]').length") == 10
    assert page.eval("[...document.querySelectorAll('.slide .art, .slide .bg')].every(i => i.getAttribute('alt') === '')")
    assert page.eval("[...document.querySelectorAll('.slide:not(.on):not(.leaving)')].every(s => getComputedStyle(s).visibility === 'hidden')")
    assert page.eval("document.querySelector('.intro .caption .what').textContent.length") > 0


@pytest.mark.parametrize("w, h, mobile", [(915, 412, True), (1280, 600, False), (800, 600, False)])
def test_text_clears_caption_on_short_screens(browser, site, w, h, mobile):
    page = open_home(browser, site, dict(width=w, height=h, mobile=mobile))
    page.wait(0.8)
    assert rect(page, ".intro-text")["bottom"] <= rect(page, ".hero .caption")["top"]
    assert page.eval("document.documentElement.scrollWidth <= innerWidth")


# ---------------------------------------------------------------- 26 Nov: Jak dropped the album from the home page

@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_writing_follows_the_first_screen(browser, site, cfg):
    page = open_home(browser, site, cfg)
    page.wait(0.5)
    assert page.eval("document.querySelectorAll('.album, .tile, .wall').length") == 0
    top = page.eval("document.querySelector('#writing').getBoundingClientRect().top + scrollY")
    assert abs(top - page.eval("document.querySelector('.hero').getBoundingClientRect().bottom + scrollY")) <= 2
    page.scroll_to(page.eval("innerHeight"))
    page.wait(0.5)
    assert page.eval("document.querySelector('#writing').getBoundingClientRect().top") <= 2


# ---------------------------------------------------------------- readable text over every painting (4.5 to 1, text hidden)

HERO_TEXT = [".intro h1", ".intro .lede", ".intro .note", ".hero .caption .yr", ".hero .caption .what", ".hero .caption .credit"]
ROOM_TEXT = [".room-text h2", ".room-soon", ".caption .yr", ".caption .what", ".caption .credit"]
NO_FADE = "document.head.insertAdjacentHTML('beforeend', '<style>.slide { transition: none !important; }</style>'); 1"
LOADED = "(a => a.complete && a.naturalWidth ? 1 : new Promise(f => { a.onload = () => f(1); setTimeout(() => f(0), 5000); }))(document.querySelector('#%s .slide.on .art'))"


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_banner_text_is_readable_over_every_picture(browser, site, cfg):
    from tools.contrast import text_contrast
    page = open_home(browser, site, cfg)
    page.eval(NO_FADE)
    page.click(".intro .pause")  # the first screen holds still while it is measured
    low = []
    for k in range(len(BANNER_FILES)):
        set_painting(page, "intro", k)
        got = text_contrast(page, HERO_TEXT + [".intro .pause span"])
        assert len(got) >= 5, (k, got)
        low += [(BANNER_FILES[k], sel, round(v, 2)) for sel, v in got.items() if v < (3 if sel.endswith(".pause span") else 4.5)]
    assert low == []  # text 4.5 to 1, the pause icon 3 to 1


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_room_text_is_readable_over_every_painting(browser, site, cfg):
    from tools.contrast import text_contrast
    page = open_home(browser, site, cfg)
    page.eval(NO_FADE)
    room_on_screen(page, "s-philosophy")
    page.click("#s-philosophy .pause")  # every room holds still while it is measured
    low = []
    for rid in page.eval("[...document.querySelectorAll('.room')].map(r => r.id)"):
        for k in range(3):
            set_painting(page, rid, k)
            assert page.eval(LOADED % rid) == 1, (rid, k)
            got = text_contrast(page, [f"#{rid} {s}" for s in ROOM_TEXT + [".pause span"]])
            assert len(got) == len(ROOM_TEXT) + 1, (rid, k, got)
            low += [(rid, k, s, round(v, 2)) for s, v in got.items() if v < (3 if s.endswith(".pause span") else 4.5)]
    assert low == []  # text 4.5 to 1, the pause icon 3 to 1



def test_orcid_link_stays_whole_on_a_small_phone(browser, site):  # the iD icon never parts from its link
    page = open_home(browser, site, dict(width=320, height=640, mobile=True), hash="#contact")
    page.wait(1)
    assert page.eval("document.querySelector('#contact a.orcid').getClientRects().length") == 1
    assert page.eval("(i => i.complete && i.naturalWidth > 0)(document.querySelector('#contact a.orcid img'))")
    assert page.eval("document.documentElement.scrollWidth <= innerWidth")



def test_research_fits_a_small_phone(browser, site):  # long doi.org addresses, and a menu of four
    page = open_home(browser, site, dict(width=320, height=640, mobile=True), hash="#research")
    page.wait(1)
    assert page.eval("document.documentElement.scrollWidth <= innerWidth")
    assert page.eval("[...document.querySelectorAll('#research a, .top a')].every(a => a.getBoundingClientRect().right <= innerWidth)")
    assert page.eval("document.querySelector('#research h3').getBoundingClientRect().top") < 640


# ---------------------------------------------------------------- final review: JavaScript turned off

def test_rooms_without_javascript_show_their_first_painting(browser, site):
    page = browser.open(site.url("index.html"), **DESKTOP, javascript=False)
    page.wait(1)
    assert page.eval("[...document.querySelectorAll('.room')].every(r => Math.abs(r.offsetHeight - innerHeight) <= 2)")
    page.eval("document.getElementById('s-future').scrollIntoView(); 1")
    page.wait(1)
    assert page.eval("(a => !!a && a.complete && a.naturalWidth > 0)(document.querySelector('#s-future .slide.on .art[src]'))")
    assert page.eval("document.querySelector('#s-future .caption .credit').textContent") == "De Montaut, From the Earth to the Moon"
