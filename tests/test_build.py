"""Build-level tests: these run build.py, which rewrites site/ (the result is deterministic)."""
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"


def run_build(text_path=None):
    args = [sys.executable, "build.py", "data/counts.json", "data/calculator.html"]
    if text_path is not None:
        args.append(str(text_path))
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")


def site_hashes():
    return {p.relative_to(SITE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(SITE.rglob("*")) if p.is_file()}


def git_status_site():
    return subprocess.run(["git", "status", "--porcelain", "site/"], cwd=ROOT, capture_output=True, text=True).stdout


def test_build_twice_identical():
    assert run_build().returncode == 0
    first = site_hashes()
    assert run_build().returncode == 0
    assert site_hashes() == first


def test_outputs_lf_and_no_long_dashes():
    assert run_build().returncode == 0
    for p in SITE.rglob("*"):
        if p.suffix in (".html", ".css", ".js"):
            b = p.read_bytes()
            assert b"\r" not in b, p
            assert chr(0x2013).encode() not in b and chr(0x2014).encode() not in b, p


SLIDE_IMG = re.compile(r'<img class="art" (?:src|data-src)="assets/img/([^"/]+)"')


def slide_files():
    return SLIDE_IMG.findall((SITE / "index.html").read_text(encoding="utf-8"))


def test_every_plate_has_a_blurred_copy():
    assert run_build().returncode == 0
    files = slide_files()
    assert len(files) >= 20
    for f in files:
        assert (SITE / "assets/img/blur" / f).is_file(), f
    assert sorted(p.name for p in (SITE / "assets/img/blur").glob("*.jpg")) == sorted(files)
    assert not (SITE / "assets/img/small").exists()


def test_missing_plate_file_is_skipped(tmp_path):
    src = SITE / "assets/img/eniac.jpg"
    parked = tmp_path / "eniac.jpg"
    shutil.move(src, parked)
    try:
        r = run_build()
        assert r.returncode == 0, r.stderr
        assert "eniac" not in (SITE / "index.html").read_text(encoding="utf-8")
        assert not (SITE / "assets/img/small/eniac.jpg").exists()
        assert not (SITE / "assets/img/blur/eniac.jpg").exists()
    finally:
        shutil.move(parked, src)
        assert run_build().returncode == 0


def test_build_reports_text_error_plainly(tmp_path):
    assert run_build().returncode == 0
    before = git_status_site()
    bad = tmp_path / "site-text.txt"
    bad.write_text((ROOT / "site-text.txt").read_text(encoding="utf-8").replace("[bio]", "[bioo]"), encoding="utf-8")
    r = run_build(bad)
    assert r.returncode == 2
    assert r.stderr.startswith("site-text.txt line")
    assert "Traceback" not in r.stderr
    assert git_status_site() == before


def test_intro_has_one_slide_per_plate():
    assert run_build().returncode == 0
    index = (SITE / "index.html").read_text(encoding="utf-8")
    plates = (SITE / "plates.html").read_text(encoding="utf-8")
    assert index.count('<figure class="slide') == plates.count('<li><span class="pl">') - 1  # the drawing on the atoms page is credited too


def test_projects_count_text_error(tmp_path):
    text = (ROOT / "site-text.txt").read_text(encoding="utf-8")
    start = text.index("[projects count]\n") + len("[projects count]\n")
    end = text.index("\n", start)
    bad = tmp_path / "site-text.txt"
    bad.write_text(text[:start] + "lots of projects" + text[end:], encoding="utf-8")
    r = run_build(bad)
    assert r.returncode == 2
    assert "[projects count]" in r.stderr and "Traceback" not in r.stderr


def test_build_reports_missing_text_file_plainly(tmp_path):
    r = run_build(tmp_path / "site-text.txt")
    assert r.returncode == 2
    assert r.stderr.startswith("site-text.txt") and "Traceback" not in r.stderr


PLATE_NUMBER = re.compile(r"\bPlates? [IVXL]+\b")


def visible_text(path):
    import html.parser

    class P(html.parser.HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.out, self.skip = [], 0

        def handle_starttag(self, tag, attrs):
            self.skip += tag in ("script", "style")

        def handle_endtag(self, tag):
            self.skip -= tag in ("script", "style")

        def handle_data(self, d):
            if not self.skip:
                self.out.append(d)
    p = P()
    p.feed(path.read_text(encoding="utf-8"))
    return " ".join(" ".join(p.out).split())


def test_no_plate_numbers_shown():
    assert run_build().returncode == 0
    for page in ("index.html", "plates.html", "atoms/index.html"):
        found = PLATE_NUMBER.findall(visible_text(SITE / page))
        assert found == [], (page, found[:5])
    assert "Plate " not in (SITE / "assets/home.js").read_text(encoding="utf-8")


def test_picture_credits_page_keeps_every_credit():
    assert run_build().returncode == 0
    credits = visible_text(SITE / "plates.html")
    raw = (SITE / "plates.html").read_text(encoding="utf-8")
    assert re.search(r"<h1[^>]*>Picture credits</h1>", raw) and "<title>Picture credits | Jak Potvin</title>" in raw
    for needed in ("Photograph by Stefan Schäfer, Lich, licensed CC BY-SA 4.0", "Photograph by Mark D, licensed CC BY-SA 2.0",
                   "Jacques-Louis David, The Death of Socrates, 1787", "The top layer of a silicon crystal, drawn for this site."):
        assert needed in credits, needed


# ---------------------------------------------------------------- the paintings Jak chose (26 November 2026)

ROOM_PAINTINGS = {  # old, middle, modern, by the date of what each shows
    "s-philosophy": ["death-of-socrates.jpg", "botticelli-augustine.jpg", "wanderer-sea-of-fog.jpg"],
    "s-psychology": ["bosch-cure-of-folly.jpg", "goya-sleep-of-reason.jpg", "freud-halberstadt.jpg"],
    "s-sociology": ["bruegel-harvesters.jpg", "seurat-grande-jatte.jpg", "shibuya-crossing.jpg"],
    "s-politics": ["death-of-caesar.jpg", "magna-carta.jpg", "berlin-wall-1989.jpg"],
    "s-economics": ["massys-moneylender.jpg", "adam-smith-statue.jpg", "ford-assembly-line.jpg"],
    "s-warfare": ["alexander-mosaic.jpg", "napoleon-alps.jpg", "iwo-jima.jpg"],
    "s-physics": ["alchemist-full.jpg", "faraday-lecture.jpg", "atlas-detector.jpg"],
    "s-biology": ["vitruvian-man.jpg", "jenner-hillemacher.jpg", "sars-cov-2.jpg"],
    "s-tech": ["antikythera.jpg", "eniac.jpg", "summit-supercomputer.jpg"],
    "s-future": ["verne-earth-to-moon.jpg", "kennedy-von-braun.jpg", "webb-cosmic-cliffs.jpg"],
}
BANNER = "washington-crossing.jpg"
TAKEN_OUT = ["school-of-athens.jpg", "charcot-salpetriere.jpg", "coronation-charlemagne.jpg", "iron-rolling-mill.jpg",
             "newton-romney.jpg", "first-flight.jpg", "earthrise.jpg", "caesar-coustou.jpg", "alchemist-phosphorus.jpg"]
ROOM_SECTION = re.compile(r'<section class="room" id="([^"]+)".*?</section>', re.S)


def room_files():
    index = (SITE / "index.html").read_text(encoding="utf-8")
    return {m.group(1): re.findall(r'assets/img/([^"/]+\.jpg)', m.group(0)) for m in ROOM_SECTION.finditer(index)}


def test_each_room_shows_its_three_paintings_oldest_first():
    assert run_build().returncode == 0
    assert room_files() == ROOM_PAINTINGS


def test_banner_painting_is_credited_but_in_no_room():
    assert run_build().returncode == 0
    assert all(BANNER not in files for files in room_files().values())
    assert "Emanuel Leutze, Washington Crossing the Delaware, 1851" in visible_text(SITE / "plates.html")


def test_paintings_taken_out_are_gone():
    assert run_build().returncode == 0
    pages = [p.read_text(encoding="utf-8") for p in SITE.rglob("*.html")]
    for f in TAKEN_OUT:
        assert not (SITE / "assets/img" / f).exists(), f
        assert not any(f in page for page in pages), f


def test_room_paintings_are_big_enough_to_fill_a_screen():
    from PIL import Image
    for files in ROOM_PAINTINGS.values():
        for f in files:
            with Image.open(SITE / "assets/img" / f) as im:
                assert max(im.size) >= 1600, (f, im.size)
    with Image.open(SITE / "assets/img" / BANNER) as im:
        assert im.width >= 3000, im.size


CREATIVE_COMMONS = {  # file: (its credit names the maker and the licence, the licence's own page)
    "shibuya-crossing.jpg": ("Photograph by Mark D, licensed CC BY-SA 2.0", "https://creativecommons.org/licenses/by-sa/2.0/"),
    "adam-smith-statue.jpg": ("Photograph by Stefan Schäfer, Lich, licensed CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "atlas-detector.jpg": ("Photograph by SimonWaldherr, licensed CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "antikythera.jpg": ("Photograph by Peulle, licensed CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "jenner-hillemacher.jpg": ("Wellcome Collection, licensed CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "sars-cov-2.jpg": ("NIAID, licensed CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/"),
    "summit-supercomputer.jpg": ("Photograph by Carlos Jones, ORNL, licensed CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/"),
}


def test_creative_commons_credits_name_the_maker_and_link_the_licence():
    assert run_build().returncode == 0
    raw = (SITE / "plates.html").read_text(encoding="utf-8")
    text = visible_text(SITE / "plates.html")
    for needed, _ in CREATIVE_COMMONS.values():
        assert needed in text, needed
    links = re.findall(r'<a href="(https://creativecommons\.org/licenses/[^"]+)">(CC [^<]+)</a>', raw)
    assert len(links) == text.count("licensed CC") == len(CREATIVE_COMMONS)
    for url, words in links:  # "CC BY-SA 2.0" goes to .../by-sa/2.0/
        kind, version = words[3:].lower().split()
        assert url == f"https://creativecommons.org/licenses/{kind}/{version}/", (url, words)
    assert {deed for _, deed in CREATIVE_COMMONS.values()} == {url for url, _ in links}


# ---------------------------------------------------------------- link previews and search engines

PAGES = {"index.html": "https://jakpotvin.com/", "atoms/index.html": "https://jakpotvin.com/atoms/",
         "atoms/calculator/index.html": "https://jakpotvin.com/atoms/calculator/", "plates.html": "https://jakpotvin.com/plates.html"}


def meta(html_text, attr, name):
    m = re.search(r'<meta %s="%s" content="([^"]*)">' % (attr, re.escape(name)), html_text)
    return m and m.group(1)


def test_every_page_has_a_link_preview_card():
    assert run_build().returncode == 0
    for page, url in PAGES.items():
        t = (SITE / page).read_text(encoding="utf-8")
        assert '<link rel="canonical" href="%s">' % url in t, page
        assert meta(t, "property", "og:url") == url, page
        assert meta(t, "property", "og:title") and meta(t, "property", "og:description"), page
        assert meta(t, "property", "og:image") == "https://jakpotvin.com/assets/card.jpg", page
        assert meta(t, "property", "og:type") == "website", page
        assert meta(t, "name", "twitter:card") == "summary_large_image", page
    from PIL import Image
    with Image.open(SITE / "assets/card.jpg") as im:
        assert im.size == (1200, 630)


def test_sitemap_robots_and_404():
    assert run_build().returncode == 0
    sm = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    assert re.findall(r"<loc>([^<]+)</loc>", sm) == list(PAGES.values())
    robots = (SITE / "robots.txt").read_text(encoding="utf-8")
    assert "User-agent: *" in robots and "Sitemap: https://jakpotvin.com/sitemap.xml" in robots
    nf = (SITE / "404.html").read_text(encoding="utf-8")
    assert 'href="/index.html"' in nf and "/assets/site.css" in nf and '<meta name="robots" content="noindex">' in nf


def test_home_says_who_the_site_belongs_to():
    import json as _json
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    found = [_json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
    person = next(d for d in found if d["@type"] == "Person")
    assert person["name"] == "Jak Potvin" and person["url"] == "https://jakpotvin.com/"
    assert person["sameAs"] == ["https://github.com/JakPot42"]  # the https links in [contact line]; never the email
    site = next(d for d in found if d["@type"] == "WebSite")
    assert site["name"] == "Jak Potvin" and site["url"] == "https://jakpotvin.com/"
    for page in ("plates.html", "atoms/index.html", "404.html"):
        assert "application/ld+json" not in (SITE / page).read_text(encoding="utf-8"), page


# ---------------------------------------------------------------- featured projects (Jak lists them in site-text.txt)

def with_featured(tmp_path, items):
    text = (ROOT / "site-text.txt").read_text(encoding="utf-8")
    assert text.count("[featured projects]\n") == 1
    p = tmp_path / "site-text.txt"
    p.write_text(text.replace("[featured projects]\n", "[featured projects]\n" + "".join(i + "\n" for i in items), 1),
                 encoding="utf-8", newline="\n")
    return p


def test_featured_projects_hidden_until_listed():
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    assert 'class="links featured"' not in t and "Featured projects" not in t


def test_featured_projects_listed(tmp_path):
    items = ["- [Sample tracker](https://github.com/JakPot42/sample-tracker) | Tracks samples, & more",
             "- Plain title | No link yet"]
    try:
        r = run_build(with_featured(tmp_path, items))
        assert r.returncode == 0, r.stderr
        t = (SITE / "index.html").read_text(encoding="utf-8")
        block = re.search(r'<ul class="links featured">(.*?)</ul>', t, re.S).group(1)
        assert '<a class="t" href="https://github.com/JakPot42/sample-tracker">Sample tracker</a>' in block
        assert "Tracks samples, &amp; more" in block
        assert '<span class="t">Plain title</span>' in block
        assert t.index('id="projects-h"') < t.index("Featured projects") < t.index('class="count"')
    finally:
        assert run_build().returncode == 0


def test_featured_item_without_bar_is_a_plain_error(tmp_path):
    try:
        r = run_build(with_featured(tmp_path, ["- [Sample](https://example.org) no bar"]))
        assert r.returncode == 2 and 'needs " | "' in r.stderr and "Traceback" not in r.stderr, r.stderr
    finally:
        assert run_build().returncode == 0


# ---------------------------------------------------------------- 26 Nov: Jak's phone showed the new page with an old site.css it had kept

def test_style_and_script_addresses_change_with_their_files():
    assert run_build().returncode == 0
    def v(rel):
        return hashlib.sha256((SITE / rel).read_bytes()).hexdigest()[:10]
    css, fonts, js = v("assets/site.css"), v("assets/fonts/fonts.css"), v("assets/home.js")
    for page, root in (("index.html", ""), ("plates.html", ""), ("atoms/index.html", "../"), ("404.html", "/")):
        t = (SITE / page).read_text(encoding="utf-8")
        assert f'href="{root}assets/site.css?v={css}"' in t, page
        assert f'href="{root}assets/fonts/fonts.css?v={fonts}"' in t, page
        assert not re.search(r'assets/(site|fonts/fonts)\.css"', t), page
    assert f'src="assets/home.js?v={js}"' in (SITE / "index.html").read_text(encoding="utf-8")
    assert f'href="../../assets/fonts/fonts.css?v={fonts}"' in (SITE / "atoms/calculator/index.html").read_text(encoding="utf-8")
