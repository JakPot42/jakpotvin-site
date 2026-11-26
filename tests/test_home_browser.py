"""Browser tests: the built site in headless Edge (see tools/browser.py). Run: python -m pytest"""
import pytest

from tools.browser import DESKTOP, PHONE


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
