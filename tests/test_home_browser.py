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


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE, {**DESKTOP, "reduced_motion": True}], ids=["desktop", "phone", "desktop-rm"])
def test_banner_is_one_still_painting(browser, site, cfg):
    page = open_home(browser, site, cfg)
    assert page.eval("document.querySelectorAll('.intro .slide').length") == 1
    assert page.eval("document.querySelector('.intro .slide.on .art').getAttribute('src')") == "assets/img/" + BANNER
    assert page.eval("document.querySelector('.pause')") is None
    caption = "document.querySelector('.hero .caption').textContent"
    zoom = "getComputedStyle(document.querySelector('.intro .slide .art')).transform"
    before = page.eval(caption)
    assert page.eval(zoom) in STILL
    page.wait(6.5)
    assert page.eval(caption) == before and page.eval(zoom) in STILL


def test_banner_caption_names_the_painting_and_links_its_room(browser, site):
    page = open_home(browser, site, DESKTOP)
    q = "document.querySelector('.hero .caption %s').%s"
    assert page.eval(q % (".yr", "textContent")) == "1776"
    assert page.eval(q % (".what", "textContent")) == "Washington crosses the Delaware"
    assert page.eval(q % (".subj", "getAttribute('href')")) == "#s-warfare"
    assert page.eval(q % (".subj", "textContent")) == "War and defense"
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


# ---------------------------------------------------------------- the rooms: three paintings, full screen, changed by scrolling

def show_painting(page, rid, k, settle=0.8):
    """Scroll to the middle of the stretch of room rid where painting k shows."""
    page.eval("(() => { const r = document.getElementById(%s), n = r.querySelectorAll('.slide').length;"
              " const top = r.getBoundingClientRect().top + scrollY, span = r.offsetHeight - innerHeight;"
              " scrollTo(0, Math.round(top + span * (%d + 0.5) / n)); return new Promise(f => requestAnimationFrame(() => requestAnimationFrame(f))); })()"
              % (json.dumps(rid), k))
    page.wait(settle)


def on_index(page, rid):
    return page.eval("[...document.getElementById(%s).querySelectorAll('.slide')].findIndex(s => s.classList.contains('on'))" % json.dumps(rid))


def caption_matches(page, rid):
    return page.eval("(r => { const s = r.querySelector('.slide.on').dataset, c = r.querySelector('.caption');"
                     " return c.querySelector('.yr').textContent === s.yr && c.querySelector('.what').textContent === s.what"
                     " && c.querySelector('.credit').textContent === s.credit; })(document.getElementById(%s))" % json.dumps(rid))


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE, {**DESKTOP, "reduced_motion": True}], ids=["desktop", "phone", "desktop-rm"])
def test_room_painting_follows_scroll(browser, site, cfg):
    page = open_home(browser, site, cfg)
    for rid in ("s-philosophy", "s-warfare", "s-future"):
        for k in (0, 1, 2, 1):
            show_painting(page, rid, k)
            assert on_index(page, rid) == k and caption_matches(page, rid), (rid, k)
    assert page.eval("[...document.querySelectorAll('.room')].every(r => r.querySelectorAll('.slide.on').length === 1)")


def test_room_painting_holds_still_without_scrolling(browser, site):
    page = open_home(browser, site, DESKTOP)
    show_painting(page, "s-biology", 1)
    page.wait(3)
    assert on_index(page, "s-biology") == 1


def test_room_is_three_and_a_half_screens_long(browser, site):
    page = open_home(browser, site, DESKTOP)
    assert page.eval("[...document.querySelectorAll('.room')].every(r => Math.abs(r.offsetHeight - 3.5 * innerHeight) <= 2)")


def test_jumps_land_on_the_right_painting(browser, site):  # Review Focus 2
    page = open_home(browser, site, DESKTOP, hash="#projects")
    page.wait(0.5)
    show_painting(page, "s-warfare", 1)
    assert on_index(page, "s-warfare") == 1
    page.scroll_to(page.eval("document.documentElement.scrollHeight"))
    show_painting(page, "s-philosophy", 0)
    assert on_index(page, "s-philosophy") == 0 and caption_matches(page, "s-philosophy")


def test_resize_mid_room_keeps_one_right_painting(browser, site):  # Review Focus 3
    page = open_home(browser, site, DESKTOP)
    show_painting(page, "s-biology", 2)
    page.resize(700, 900, settle=0.8)
    top, height, view = page.eval("(r => [r.getBoundingClientRect().top, r.offsetHeight, innerHeight])(document.getElementById('s-biology'))")
    want = min(2, int(max(0, -top) / max(1, height - view) * 3))
    assert on_index(page, "s-biology") == want
    assert page.eval("document.getElementById('s-biology').querySelectorAll('.slide.on').length") == 1
    assert page.eval("document.documentElement.scrollWidth <= innerWidth")


@pytest.mark.parametrize("w, h, mobile", [(1440, 900, False), (412, 915, True), (915, 412, True), (1280, 600, False), (800, 600, False)])
def test_room_words_never_overlap_the_caption(browser, site, w, h, mobile):  # Review Focus 4
    page = open_home(browser, site, dict(width=w, height=h, mobile=mobile))
    for rid in ("s-politics", "s-tech"):
        show_painting(page, rid, 0, settle=0.3)
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
    show_painting(page, "s-sociology", 0)
    t = rect(page, "#s-sociology .room-text")
    assert t["left"] <= 0.25 * 1440 and t["right"] <= 0.55 * 1440 and 0.2 * 900 <= (t["top"] + t["bottom"]) / 2 <= 0.8 * 900
    page = open_home(browser, site, PHONE)
    show_painting(page, "s-sociology", 0)
    assert rect(page, "#s-sociology .room-text")["top"] >= 0.45 * 915


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_every_room_painting_fills_the_screen(browser, site, cfg):
    page = open_home(browser, site, cfg)
    for rid in page.eval("[...document.querySelectorAll('.room')].map(r => r.id)"):
        for k in range(3):
            show_painting(page, rid, k, settle=0.2)
            s = f"#{rid} .slide.on"
            whole = page.eval(f"document.querySelector('{s}').classList.contains('whole')")
            cover = rect(page, f"{s} .bg" if whole and cfg is DESKTOP else f"{s} .art")
            assert cover["left"] <= 0 and cover["top"] <= 0 and cover["right"] >= cfg["width"] - 1 and cover["bottom"] >= cfg["height"] - 1, (rid, k)
            if cfg is PHONE or not whole:
                assert page.eval(f"getComputedStyle(document.querySelector('{s} .art')).objectFit") == "cover", (rid, k)
            else:  # a tall painting on a laptop: shown whole, beside the title
                assert rect(page, f"{s} .art")["left"] >= rect(page, f"#{rid} .room-words")["right"] - 1, (rid, k)


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
