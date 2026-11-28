"""The essay and paper pages in a real browser (headless Edge): they fit a small phone, a wide table scrolls inside its own
box, and they read without JavaScript."""
import pytest

from tools.browser import DESKTOP

PAGES = ["essays/offshoring-the-mind/index.html", "research/measuring-cognitive-hollowing/index.html",
         "research/measuring-siege-mentality-in-ai/index.html", "research/labeling-claims-by-kind-of-support/index.html"]
SMALL = dict(width=320, height=640, mobile=True)


@pytest.mark.parametrize("path", PAGES)
def test_text_pages_fit_a_small_phone(browser, site, path):  # Review Focus 1: long DOIs, wide tables
    page = browser.open(site.url(path), **SMALL)
    page.wait(0.3)
    # a phone widens its layout (and so shrinks the text) to take in anything wider than the screen; it must not
    assert page.eval("innerWidth") == SMALL["width"], path
    assert page.eval("document.documentElement.scrollWidth <= innerWidth"), path
    # the page clips what overflows (overflow-x: clip), so look at each element: outside a table's own scrolling box,
    # nothing ends past the screen's right edge, not a long DOI and not a table
    wide = page.eval("[...document.querySelectorAll('article.text *')].filter(e => !e.parentElement.closest('.table'))"
                     ".flatMap(e => [...e.getClientRects()].filter(r => r.right > innerWidth + 0.5)"
                     ".map(r => e.tagName + ' ' + (e.textContent || '').slice(0, 40)))")
    assert wide == [], (path, wide[:5])


def test_wide_tables_scroll_in_their_own_box(browser, site):  # Review Focus 2
    page = browser.open(site.url(PAGES[0]), **SMALL)
    page.wait(0.3)
    boxes = page.eval("[...document.querySelectorAll('.table')].map(b => [b.getAttribute('role'), b.getAttribute('tabindex'),"
                      " b.getAttribute('aria-label'), getComputedStyle(b).overflowX, b.getBoundingClientRect().right,"
                      " b.scrollWidth > b.clientWidth])")
    assert len(boxes) == 5  # the essay's five tables
    for role, tabindex, label, overflow, right, _ in boxes:
        assert role == "region" and tabindex == "0" and label.startswith("Table ")  # a keyboard reaches it; a reader names it
        assert overflow in ("auto", "scroll") and right <= 320.5
    assert any(wide for *_, wide in boxes)  # the claims table is wider than a small phone, and scrolls in its box


def test_text_pages_read_without_javascript(browser, site):
    page = browser.open(site.url(PAGES[0]), **DESKTOP, javascript=False)
    page.wait(0.3)
    assert page.eval("document.querySelector('article.text h1').getBoundingClientRect().height") > 0
    assert page.eval("document.querySelector('.table table').getBoundingClientRect().height") > 0


def test_tables_are_set_apart_from_the_prose(browser, site):
    page = browser.open(site.url(PAGES[0]), **DESKTOP)
    page.wait(0.3)
    cell = "getComputedStyle(document.querySelector('.table td'))"
    assert "Plex" in page.eval(f"{cell}.fontFamily")  # small sans in the cells, as in the site's captions and lists
    assert page.eval("getComputedStyle(document.querySelector('.table th')).borderBottomStyle") == "solid"


CPL = """(() => { const p = [...document.querySelectorAll('.text-body p')].find(p => p.textContent.length > 700);
  const lines = Math.round(p.getBoundingClientRect().height / parseFloat(getComputedStyle(p).lineHeight));
  return p.textContent.length / lines; })()"""


def test_reading_column_holds_about_68_characters_a_line(browser, site):  # the plan's measure, for comfortable reading
    page = browser.open(site.url(PAGES[0]), **DESKTOP)
    page.wait(0.3)
    cpl = page.eval(CPL)
    assert 58 <= cpl <= 75, cpl
