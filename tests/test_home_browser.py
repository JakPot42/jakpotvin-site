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
