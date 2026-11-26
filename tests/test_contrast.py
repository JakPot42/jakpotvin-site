"""The contrast measure used by the readability tests (tools/contrast.py)."""
from tools.browser import Browser, Site
from tools.contrast import contrast, luminance, over, text_contrast


def test_luminance_and_contrast_match_wcag():
    assert luminance((255, 255, 255)) == 1.0 and luminance((0, 0, 0)) == 0.0
    assert round(contrast((255, 255, 255), (0, 0, 0)), 2) == 21.0
    assert contrast((0, 0, 0), (255, 255, 255)) == contrast((255, 255, 255), (0, 0, 0))
    assert over((255, 255, 255, 0.5), (0, 0, 0)) == (127.5, 127.5, 127.5)


def test_text_contrast_measures_the_background_behind_the_text(tmp_path):
    (tmp_path / "index.html").write_text(
        '<!DOCTYPE html><body style="margin:0;font:40px sans-serif">'
        '<p id="a" style="margin:0;background:#000;color:#fff">white on black</p>'
        '<p id="b" style="margin:0;background:#fff;color:rgba(255,255,255,.9)">white on white</p>', encoding="utf-8")
    with Site(root=tmp_path) as site, Browser() as b:
        page = b.open(site.url("index.html"), width=800, height=400)
        got = text_contrast(page, ["#a", "#b", "#missing"])
    assert got["#a"] > 20 and got["#b"] < 1.1 and "#missing" not in got
