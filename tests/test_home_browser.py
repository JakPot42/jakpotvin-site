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


def current(page):
    return page.eval("document.querySelector('.slides').dataset.current")


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


def test_slideshow_advances(browser, site):
    page = open_home(browser, site, DESKTOP)
    assert current(page) == "0"
    page.wait(6.2)
    assert current(page) == "1"
    assert page.eval("document.querySelector('.intro .caption .yr').textContent") == \
        page.eval("document.querySelector('.slide[data-i=\"1\"]').dataset.yr")


def test_pause_stops_slideshow(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.click(".pause")
    assert page.eval("document.querySelector('.pause').getAttribute('aria-pressed')") == "true"
    before = current(page)
    page.wait(7)
    assert current(page) == before
    page.click(".pause")
    assert page.eval("document.querySelector('.pause').getAttribute('aria-pressed')") == "false"
    page.wait(6.2)
    assert current(page) != before


def test_hidden_tab_stops_slideshow(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.eval("Object.defineProperty(document, 'hidden', {value: true, configurable: true});"
              " document.dispatchEvent(new Event('visibilitychange')); 1")
    before = current(page)
    page.wait(7)
    assert current(page) == before


def test_reduced_motion_holds_plate_one(browser, site):
    page = open_home(browser, site, {**DESKTOP, "reduced_motion": True})
    assert page.eval("document.documentElement.dataset.motion") == "reduced"
    page.wait(7)
    assert current(page) == "0"
    assert page.eval("document.querySelector('.intro .caption .credit b').textContent") == "Plate I."
    assert page.eval("[...document.querySelectorAll('.slide .art')].every(i => ['none', 'matrix(1, 0, 0, 1, 0, 0)']"
                     ".includes(getComputedStyle(i).transform))")
    assert not page.eval("!!document.querySelector('.pause') && getComputedStyle(document.querySelector('.pause')).display !== 'none'")


def test_only_current_and_next_images_load(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(1)
    assert page.eval("document.querySelectorAll('.slide .art[src]').length") <= 2
    assert page.eval("document.querySelectorAll('.slide .art[data-src]').length") >= 18


def test_whole_plates_have_backdrop(browser, site):
    page = open_home(browser, site, DESKTOP)
    q = ("(() => { const img = [...document.querySelectorAll('.slide .art')].find(i => (i.getAttribute('src') || i.dataset.src).endsWith('/%s'));"
         " const s = img.closest('.slide'); return [s.classList.contains('whole'), !!s.querySelector('.bg')]; })()")
    for f in ("vitruvian-man.jpg", "eniac.jpg", "earthrise.jpg"):
        assert page.eval(q % f) == [True, True], f
    assert page.eval(q % "school-of-athens.jpg") == [False, False]


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


# ---------------------------------------------------------------- Task 7: the rooms

ROOM_IDS = "[...document.querySelectorAll('.rooms .room')].map(r => r.id)"
ON_ROOMS = "[...document.querySelectorAll('.room-plates.on')].map(p => p.dataset.room)"
HEX_TO_RGB = "(h => 'rgb(' + [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)).join(', ') + ')')"


def center_room(page, rid):
    page.eval("document.getElementById(%s).scrollIntoView({block: 'center'}); 1" % json.dumps(rid))
    page.wait(1)


def test_rooms_pin_and_swap(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(0.5)
    assert page.eval("document.querySelector('.rooms').classList.contains('pinned')")
    ids = page.eval(ROOM_IDS)
    for k in (0, 3, 9):
        center_room(page, ids[k])
        assert page.eval(ON_ROOMS) == [ids[k]], k
    center_room(page, ids[3])
    first = rect(page, ".rooms-stage")["top"]
    page.scroll_to(page.eval("scrollY") + 200)
    page.wait(0.3)
    second = rect(page, ".rooms-stage")["top"]
    assert abs(first) <= 2 and abs(second) <= 2, (first, second)


def test_room_wall_colours(browser, site):
    page = open_home(browser, site, DESKTOP)
    for rid in page.eval(ROOM_IDS):
        center_room(page, rid)
        want = page.eval(HEX_TO_RGB + "(document.getElementById(%s).dataset.bg)" % json.dumps(rid))
        assert page.eval("getComputedStyle(document.querySelector('.rooms')).backgroundColor") == want, rid


def test_room_deep_link_shows_its_plates(browser, site):
    page = open_home(browser, site, DESKTOP, hash="#s-economics")
    page.wait(1)
    h = rect(page, "#s-economics-h")
    assert 0 <= h["top"] and h["bottom"] <= page.eval("innerHeight")
    assert page.eval(ON_ROOMS) == ["s-economics"]


@pytest.mark.parametrize("cfg", [PHONE, {**DESKTOP, "reduced_motion": True}], ids=["phone", "desktop-rm"])
def test_rooms_unpinned_on_phone_and_reduced_motion(browser, site, cfg):
    page = open_home(browser, site, cfg)
    page.wait(0.5)
    assert not page.eval("document.querySelector('.rooms').classList.contains('pinned')")
    assert page.eval("[...document.querySelectorAll('.rooms .room')].every(r => { const p = r.querySelector('.room-plates'), t = r.querySelector('.room-text');"
                     " return p && p.getBoundingClientRect().top >= t.getBoundingClientRect().top - 1 || r.querySelector('.room-plates') && getComputedStyle(r.querySelector('.room-in')).display === 'grid'; })")
    assert page.eval("document.querySelectorAll('.rooms .room .room-plates').length") == page.eval("document.querySelectorAll('.rooms .room').length")


def test_rooms_repin_after_resize(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(0.5)
    assert page.eval("document.querySelector('.rooms').classList.contains('pinned')")
    page.resize(700, 900, settle=0.6)
    assert not page.eval("document.querySelector('.rooms').classList.contains('pinned')")
    assert page.eval("document.querySelectorAll('.rooms .room .room-plates').length") == 10
    page.resize(1440, 900, settle=0.6)
    assert page.eval("document.querySelector('.rooms').classList.contains('pinned')")
    assert page.eval("document.querySelectorAll('.rooms-stage .room-plates').length") == 10


# ---------------------------------------------------------------- final review fixes

def test_slides_hidden_from_screen_readers(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(1.2)
    assert page.eval("document.querySelector('.slides').getAttribute('aria-hidden')") == "true"
    assert page.eval("[...document.querySelectorAll('.slide .art')].every(i => i.getAttribute('alt') === '')")
    assert page.eval("[...document.querySelectorAll('.slide:not(.on):not(.leaving)')].every(s => getComputedStyle(s).visibility === 'hidden')")
    assert page.eval("document.querySelector('.intro .caption .what').textContent.length") > 0


@pytest.mark.parametrize("w, h, mobile", [(915, 412, True), (1280, 600, False), (800, 600, False)])
def test_text_clears_caption_on_short_screens(browser, site, w, h, mobile):
    page = open_home(browser, site, dict(width=w, height=h, mobile=mobile))
    page.wait(0.8)
    assert rect(page, ".intro-text")["bottom"] <= rect(page, ".hero .caption")["top"]
    assert page.eval("document.documentElement.scrollWidth <= innerWidth")


ZOOM = r"(m => m ? Math.hypot(+m[1], +m[2]) : 1)(getComputedStyle(document.querySelector('.slide.on .art')).transform.match(/matrix\(([^,]+), ([^,]+)/))"


def test_pause_stops_the_zoom(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(1)
    page.click(".pause")
    a = page.eval(ZOOM)
    page.wait(2)
    assert abs(page.eval(ZOOM) - a) < 0.002


def test_pause_button_keeps_its_name(browser, site):
    page = open_home(browser, site, DESKTOP)
    name = page.eval("document.querySelector('.pause').getAttribute('aria-label')")
    page.click(".pause")
    assert page.eval("document.querySelector('.pause').getAttribute('aria-label')") == name
    assert page.eval("document.querySelector('.pause').getAttribute('aria-pressed')") == "true"


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
