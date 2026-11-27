"""Build-level tests: these run build.py, which rewrites site/ (the result is deterministic)."""
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORCID = "https://orcid.org/0009-0000-1700-0435"
DOI_PLAN, DOI_AMENDMENT = "https://doi.org/10.17605/OSF.IO/NAWZD", "https://doi.org/10.17605/OSF.IO/AGFY9"
ORCID_ICON_SHA256 = "195be086656233fc1a0089086d9190d28dc6abce39c2290612d1893233e1f166"  # orcid.org/assets/vectors/orcid.logo.icon.svg
SITE = ROOT / "site"


def run_build(text_path=None, texts_dir=None):
    args = [sys.executable, "build.py", "data/counts.json", "data/calculator.html"]
    if text_path is not None or texts_dir is not None:
        args.append(str(text_path or ROOT / "site-text.txt"))
    if texts_dir is not None:
        args.append(str(texts_dir))
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


def test_every_plate_has_a_blurred_copy():
    assert run_build().returncode == 0
    plates = sorted(p.name for p in (SITE / "assets/img").glob("*.jpg"))
    assert len(plates) == 49  # 30 in the rooms and Washington, fifteen more on the first screen, and Research's three
    assert sorted(p.name for p in (SITE / "assets/img/blur").glob("*.jpg")) == plates
    assert not (SITE / "assets/img/small").exists()


def test_missing_plate_file_is_skipped(tmp_path):
    src = SITE / "assets/img/eniac.jpg"
    parked = tmp_path / "eniac.jpg"
    shutil.move(src, parked)
    try:
        r = run_build()
        assert r.returncode == 0, r.stderr
        index = (SITE / "index.html").read_text(encoding="utf-8")
        assert "eniac" not in index
        tech = re.search(r'<section class="room" id="s-tech"[^>]*>.*?</section>', index, re.S).group(0)
        assert tech.count('<figure class="slide') == 2  # the room keeps the two it has
        assert not (SITE / "assets/img/small/eniac.jpg").exists()
        assert not (SITE / "assets/img/blur/eniac.jpg").exists()
    finally:
        shutil.move(parked, src)
        assert run_build().returncode == 0


def test_room_with_no_paintings_still_lays_out(tmp_path):  # Review Focus 1: every file of a room missing
    names = ["antikythera.jpg", "eniac.jpg", "summit-supercomputer.jpg"]
    for n in names:
        shutil.move(SITE / "assets/img" / n, tmp_path / n)
    try:
        r = run_build()
        assert r.returncode == 0, r.stderr
        index = (SITE / "index.html").read_text(encoding="utf-8")
        section = re.search(r'<section class="room" id="s-tech"[^>]*>.*?</section>', index, re.S).group(0)
        assert '<figure class="slide' not in section and 'class="caption"' not in section
        assert '<h2 id="s-tech-h">Technology and AI</h2>' in section
    finally:
        for n in names:
            shutil.move(tmp_path / n, SITE / "assets/img" / n)
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
                   "Jacques-Louis David, The Death of Socrates, 1787", "The top layer of a silicon crystal, drawn for this site.",
                   "Rembrandt van Rijn, The Anatomy Lesson of Dr Nicolaes Tulp, 1632", "Francisco Goya, The Madhouse"):
        assert needed in credits, needed


# ---------------------------------------------------------------- the paintings Jak chose (26 November 2026)

ROOM_PAINTINGS = {  # old, middle, modern, by the date of what each shows
    "s-philosophy": ["death-of-socrates.jpg", "botticelli-augustine.jpg", "wanderer-sea-of-fog.jpg"],
    "s-psychology": ["bosch-cure-of-folly.jpg", "goya-madhouse.jpg", "freud-halberstadt.jpg"],
    "s-sociology": ["bruegel-harvesters.jpg", "seurat-grande-jatte.jpg", "shibuya-crossing.jpg"],
    "s-politics": ["death-of-caesar.jpg", "magna-carta.jpg", "berlin-wall-1989.jpg"],
    "s-economics": ["massys-moneylender.jpg", "adam-smith-statue.jpg", "ford-assembly-line.jpg"],
    "s-warfare": ["alexander-mosaic.jpg", "napoleon-alps.jpg", "iwo-jima.jpg"],
    "s-physics": ["alchemist-full.jpg", "faraday-lecture.jpg", "atlas-detector.jpg"],
    "s-biology": ["rembrandt-anatomy-lesson.jpg", "jenner-hillemacher.jpg", "sars-cov-2.jpg"],
    "s-tech": ["antikythera.jpg", "eniac.jpg", "summit-supercomputer.jpg"],
    "s-future": ["verne-earth-to-moon.jpg", "kennedy-von-braun.jpg", "webb-cosmic-cliffs.jpg"],
}
BANNER = "washington-crossing.jpg"
BANNER_FILES = ["washington-crossing.jpg", "newton-prism.jpg", "gaspee-burning.jpg", "balloon-1783.jpg", "constitution-guerriere.jpg",
                "ether-first-operation.jpg", "london-sewers-1859.jpg", "wright-first-flight.jpg", "fleming-gabain.jpg",
                "marshall-plan-france.jpg", "laika-1957.jpg", "von-braun-office.jpg", "earthrise-apollo8.jpg", "iphone-2007.jpg",
                "f22-raptor.jpg", "starship-booster-catch.jpg"]  # the first screen, Washington first, then by date
BANNER_CREDITS = [
    "Charles DeWolf Brownell, The Burning of the Gaspee, 1892. Rhode Island Historical Society, Providence.",
    "Thomas Birch, Engagement Between the Constitution and the Guerri" + chr(0xE8) + "re, 1813. Museum of Fine Arts, Boston.",
    "John T. Daniels, First flight of the Wright Flyer, Kill Devil Hills, North Carolina, 17 December 1903. Library of Congress.",
    "William Anders, Earthrise, from Apollo 8 in orbit around the Moon, 24 December 1968. NASA.",
    "Newton décompose la lumière au moyen d'un prisme de verre, wood engraving in Louis Figuier, Vies des savants illustres, 1876 edition. Wellcome Collection copy, scanned for the Internet Archive.",
    "The main drainage of the Metropolis: the tunnels from Wick Lane, near Old Ford, Bow, wood engraving, The Illustrated London News, 1859. Wellcome Collection, licensed CC BY 4.0.",
    "Laika before her orbital flight, 1957. Museum of Cosmonautics and the Moscow Main Archive, via Mos.ru, licensed CC BY 4.0.",
    "NASA photograph, Marshall Space Flight Center, Huntsville, Alabama, September 1960.",
    "Tech. Sgt. Steven Tucker, U.S. Air National Guard, an F-22 Raptor at Thunder Over New Hampshire, Pease Air National Guard Base, 11 September 2021.",
    "Expérience du globe aérostatique de MM. Charles et Robert au jardin des Thuilleries, le 1er décembre 1783, coloured print. Bibliothèque nationale de France.",
    "Robert C. Hinckley, The First Operation Under Ether, 1882 to 1893. Boston Medical Library in the Francis A. Countway Library of Medicine, Boston.",
    "Ethel Gabain, Sir Alexander Fleming, FRS, the Discoverer of Penicillin, 1944. Imperial War Museums, London.",
    "Marshall Plan aid arriving in France, 1949. Economic Cooperation Administration photograph, U.S. National Archives.",
    "Steve Jobs introduces the iPhone at Macworld, San Francisco, 9 January 2007. Photograph by Blake Patterson, licensed CC BY 2.0.",
    "The Super Heavy booster caught by the launch tower on Starship's fifth flight test, Starbase, Texas, 13 October 2024. Photograph by Steve Jurvetson, licensed CC BY 2.0."]
TAKEN_OUT = ["school-of-athens.jpg", "charcot-salpetriere.jpg", "coronation-charlemagne.jpg", "iron-rolling-mill.jpg",
             "newton-romney.jpg", "first-flight.jpg", "earthrise.jpg", "caesar-coustou.jpg", "alchemist-phosphorus.jpg",
             "vitruvian-man.jpg", "goya-sleep-of-reason.jpg"]
ROOM_SECTION = re.compile(r'<section class="room" id="([^"]+)".*?</section>', re.S)


def room_files():
    index = (SITE / "index.html").read_text(encoding="utf-8")
    # the <noscript> copy of a room's first painting (for visitors without JavaScript) is not another painting
    return {m.group(1): re.findall(r'assets/img/([^"/]+\.jpg)', re.sub(r"<noscript>.*?</noscript>", "", m.group(0)))
            for m in ROOM_SECTION.finditer(index)}


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
        named = re.compile(r'["/]' + re.escape(f))  # the whole file name: wright-first-flight.jpg is not first-flight.jpg
        assert not any(named.search(page) for page in pages), f


SMALL_SOURCES = {"verne-earth-to-moon.jpg": 1338, "botticelli-augustine.jpg": 1775,  # the biggest scans there are
                 "freud-halberstadt.jpg": 1625}  # the photograph itself, inside its mount, in the biggest scan


def test_room_paintings_are_big_enough_to_fill_a_screen():
    from PIL import Image
    for files in ROOM_PAINTINGS.values():
        for f in files:
            with Image.open(SITE / "assets/img" / f) as im:
                w, h = im.size
            assert w >= min(1600, SMALL_SOURCES.get(f, 1600)), (f, im.size)  # every painting fills a laptop screen's width
            if h > w:  # a tall painting fills the screen by its width, so it is made 1,920 wide where its source allows
                assert w >= SMALL_SOURCES.get(f, 1900), (f, im.size)
    with Image.open(SITE / "assets/img" / BANNER) as im:
        assert im.width >= 3000, im.size


def test_site_pictures_stay_light():
    heavy = [(p.name, p.stat().st_size) for p in (SITE / "assets/img").glob("*.jpg") if p.stat().st_size > 1_250_000]
    assert heavy == []


def test_rooms_are_built_to_change_by_themselves():
    assert run_build().returncode == 0
    index = (SITE / "index.html").read_text(encoding="utf-8")
    assert "<noscript><style>" not in index  # a room is one screen tall with or without JavaScript
    for rid, files in ROOM_PAINTINGS.items():
        section = re.search(r'<section class="room" id="%s"[^>]*>.*?</section>' % rid, index, re.S).group(0)
        assert "style=" not in section.split(">", 1)[0], rid  # no per-room length any more
        assert section.count('<figure class="slide') == 3 and len(re.findall(r'<figure class="slide[^"]* on"', section)) == 1, rid
        lazy = re.sub(r"<noscript>.*?</noscript>", "", section)  # the copy for visitors without JavaScript is the only eager one
        assert 'data-src="assets/img/%s"' % files[0] in lazy and ' src="assets/img/%s"' % files[0] not in lazy, rid
        assert section.count("<noscript>") == 1 and '<noscript><img class="art" src="assets/img/%s"' % files[0] in section, rid
        assert '<div class="room-bg" aria-hidden="true">' in section and '<div class="caption">' in section, rid
        assert not re.search(r'<figure class="slide[^"]* whole', section) and 'class="bg"' not in section, rid  # every one fills
    assert "rooms-stage" not in index and "data-bg=" not in index


CREATIVE_COMMONS = {  # file: (its credit names the maker and the licence, the licence's own page)
    "shibuya-crossing.jpg": ("Photograph by Mark D, licensed CC BY-SA 2.0", "https://creativecommons.org/licenses/by-sa/2.0/"),
    "adam-smith-statue.jpg": ("Photograph by Stefan Schäfer, Lich, licensed CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "atlas-detector.jpg": ("Photograph by SimonWaldherr, licensed CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "antikythera.jpg": ("Photograph by Peulle, licensed CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "jenner-hillemacher.jpg": ("Wellcome Collection, licensed CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "sars-cov-2.jpg": ("NIAID, licensed CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/"),
    "summit-supercomputer.jpg": ("Photograph by Carlos Jones, ORNL, licensed CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/"),
    "london-sewers-1859.jpg": ("Wellcome Collection, licensed CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "laika-1957.jpg": ("Museum of Cosmonautics and the Moscow Main Archive, via Mos.ru, licensed CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "iphone-2007.jpg": ("Photograph by Blake Patterson, licensed CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/"),
    "starship-booster-catch.jpg": ("Photograph by Steve Jurvetson, licensed CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/"),
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


def test_card_is_drawn_from_the_banner_with_the_name_on_a_dark_band():
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    assert "Leutze, Washington Crossing the Delaware" in meta(t, "property", "og:image:alt")
    from PIL import Image, ImageStat
    with Image.open(SITE / "assets/card.jpg") as im:
        band = im.convert("L").crop((60, 630 - 215, 700, 630 - 40))
        assert ImageStat.Stat(band).median[0] <= 80  # the band behind the name


def test_sitemap_robots_and_404():
    assert run_build().returncode == 0
    sm = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    assert locs[:len(PAGES)] == list(PAGES.values())  # the site's own pages, then each essay and paper
    assert sorted(locs[len(PAGES):]) == sorted(f"https://jakpotvin.com/{f}/" for f in TEXT_PAGES)
    robots = (SITE / "robots.txt").read_text(encoding="utf-8")
    assert "User-agent: *" in robots and "Sitemap: https://jakpotvin.com/sitemap.xml" in robots
    nf = (SITE / "404.html").read_text(encoding="utf-8")
    assert 'href="/index.html"' in nf and "/assets/site.css" in nf and '<meta name="robots" content="noindex">' in nf


def test_orcid_sits_in_contact_with_its_icon_and_rel_me():
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    start = t.index('<section id="contact"')
    contact = t[start:t.index("</section>", start)]
    assert (f'<a class="orcid" href="{ORCID}" rel="me"><img src="assets/orcid-id.svg" width="16" height="16" alt="">'
            f'{ORCID}</a>') in contact
    for page in ("index.html", "plates.html", "atoms/index.html", "atoms/calculator/index.html", "404.html"):  # every page
        page_text = (SITE / page).read_text(encoding="utf-8")
        assert page_text[:page_text.index("</head>")].count(f'<link rel="me" href="{ORCID}">') == 1, page  # the same person
    icon = (SITE / "assets/orcid-id.svg").read_bytes()
    assert hashlib.sha256(icon).hexdigest() == ORCID_ICON_SHA256  # ORCID's own file, as provided, never changed


def intro_slides(t):
    start = t.index('<section class="intro"')
    intro = t[start:t.index("</section>", start)]
    return re.findall(r'<figure class="([^"]*)"[^>]*>(?:<img class="bg"[^>]*>)?<img class="art" ([^>]*)>', intro)


def test_banner_pictures_in_order_washington_first():
    assert run_build().returncode == 0
    slides = intro_slides((SITE / "index.html").read_text(encoding="utf-8"))
    assert [re.search(r'src="assets/img/([^"]+)"', a).group(1) for _, a in slides] == BANNER_FILES
    first_cls, first = slides[0]
    assert first_cls.split() == ["slide", "on"] and first.startswith('src="assets/img/washington-crossing.jpg" fetchpriority="high"')
    for cls, attrs in slides[1:]:  # the rest wait in data-src: home.js loads one ahead
        assert cls.split() == ["slide"] and attrs.startswith('data-src="') and " src=" not in " " + attrs.replace("data-src", ""), attrs


def test_banner_pictures_belong_to_no_room():
    assert run_build().returncode == 0
    rooms = "".join(m.group(0) for m in ROOM_SECTION.finditer((SITE / "index.html").read_text(encoding="utf-8")))
    assert rooms and not [f for f in BANNER_FILES if f in rooms]


def test_banner_pictures_are_credited():
    assert run_build().returncode == 0
    plates = re.sub(r" ([.,])", r"\1", visible_text(SITE / "plates.html"))  # the words a visitor reads (a licence name is a link)
    assert [c for c in BANNER_CREDITS if c not in plates] == []

def test_research_sits_between_the_rooms_and_projects():
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    r = t.index('<section class="room research-room" id="research"')
    p = t.index('<section class="research-papers"')
    assert t.index('<section id="writing"') < t.index('<section class="room" id="s-future"') < r < p < t.index('<section id="projects"')
    screen = t[r:t.index("</section>", r)]
    assert '<h2 id="research-h">Research</h2>' in screen
    assert screen.index("research-h") < screen.index(f'<a class="orcid" href="{ORCID}" rel="me">')  # ORCID right under the heading
    research = t[p:t.index("</section>", p)]
    assert "<h3>Predicting the adopted organisation before simulating it (Study 2A)</h3>" in research
    assert "Preregistered November 2026 " + chr(0xB7) + " Paper in preparation" in research
    assert "Earlier work found that chemistries grown from lifeless conditions" in research
    assert "which is what a law has to do." in research
    assert f'Plan: <a href="{DOI_PLAN}">{DOI_PLAN}</a>' in research
    assert f'Amendment: <a href="{DOI_AMENDMENT}">{DOI_AMENDMENT}</a>' in research
    for page, root in (("index.html", ""), ("plates.html", ""), ("atoms/index.html", "../"), ("atoms/calculator/index.html", "../../")):
        nav = re.search(r'<nav aria-label="Site"[^>]*>(.*?)</nav>', (SITE / page).read_text(encoding="utf-8")).group(1)  # the calculator styles its own
        assert re.findall(r">([A-Za-z]+)</a>", nav) == ["Writing", "Research", "Projects", "Contact"], page
        assert f'href="{root}index.html#research"' in nav, page


def test_the_war_room_takes_in_strategy():
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    assert '<h2 id="s-warfare-h">War, strategy and defense</h2>' in t  # one room for war and the thinking behind it
    assert "War and defense" not in t  # the old name, in no heading and in no painting's caption data


def test_research_opens_with_the_air_pump_like_a_room():
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    r = t.index('<section class="room research-room" id="research"')
    screen = t[r:t.index("</section>", r)]
    assert re.findall(r'data-src="assets/img/([^"]+)"', screen) == [  # by date, each loading as the room nears
        "wright-air-pump.jpg", "edelfelt-pasteur.jpg", "solvay-1927.jpg"]
    assert '<noscript><img class="art" src="assets/img/wright-air-pump.jpg"' in screen  # and shows without JavaScript
    assert '<span class="yr">1768</span> <span class="what">A lecturer pumps the air from a glass flask</span>' in screen
    assert '<span class="credit">Wright of Derby, An Experiment on a Bird in the Air Pump</span>' in screen
    plates = visible_text(SITE / "plates.html")
    assert "Joseph Wright of Derby, An Experiment on a Bird in the Air Pump, 1768. The National Gallery, London." in plates
    assert "Albert Edelfelt, Louis Pasteur, 1885. Musée d'Orsay, Paris." in plates
    assert ("Benjamin Couprie, the Fifth Solvay Conference on Electrons and Photons, Brussels, October 1927. "
            "Institut International de Physique Solvay. Public domain in the United States: published in 1927.") in plates
    intro = t[t.index('<nav class="intro-links"'):t.index("</nav>", t.index('<nav class="intro-links"'))]
    assert re.findall(r'href="(#[a-z]+)"', intro) == ["#projects", "#writing", "#research"]  # the first screen's buttons


def test_research_stays_hidden_until_it_has_a_paper(tmp_path):
    text = (ROOT / "site-text.txt").read_text(encoding="utf-8")
    start = text.index(chr(10) + "[research papers]" + chr(10)) + 1  # the heading line, not a note that names it
    empty = tmp_path / "site-text.txt"
    empty.write_text(text[:start] + "[research papers]\n" + text[text.index("\n[", start + 1):], encoding="utf-8")
    no_texts = tmp_path / "texts"
    no_texts.mkdir()
    try:
        r = run_build(empty, no_texts)
        assert r.returncode == 0, r.stderr
        for page in ("index.html", "plates.html", "atoms/index.html", "atoms/calculator/index.html"):
            t = (SITE / page).read_text(encoding="utf-8")
            assert 'id="research"' not in t and "#research" not in t and "research-papers" not in t, page
    finally:
        assert run_build().returncode == 0


def test_home_says_who_the_site_belongs_to():
    import json as _json
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    found = [_json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
    person = next(d for d in found if d["@type"] == "Person")
    assert person["name"] == "Jak Potvin" and person["url"] == "https://jakpotvin.com/"
    assert person["jobTitle"] == "Researcher and software designer"  # his choice; search engines only, never on the page
    assert person["sameAs"] == ["https://github.com/JakPot42", ORCID]  # the https links in [contact line]; never the email
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


# ---------------------------------------------------------------- essays and papers (27 November 2026)

TEXT_PAGES = {  # address folder: (title, kind line, summary)
    "essays/offshoring-the-mind": (
        "Offshoring the Mind: AI Dependence, Lost Capability and the Risk of a Cold Standoff Between Humans and AI",
        "Version 1.0, November 2026",
        "Handing thinking over to AI resembles handing manufacturing over to another country."),
    "research/measuring-cognitive-hollowing": (
        "Measuring Cognitive Hollowing: A Study Design for Unassisted Skill After AI Adoption",
        "Research proposal, version 1.0, November 2026",
        "Professionals in several fields complete standardized tasks with the AI switched off, before AI adoption and at "
        "intervals of up to two years afterwards."),
    "research/measuring-siege-mentality-in-ai": (
        "Measuring Siege Mentality in AI Systems: A Calibration-Based Test",
        "Research proposal, version 1.0, November 2026",
        "Four studies are proposed: calibration of beliefs about human intentions; rigidity of those beliefs under evidence; "
        "the effect of explained versus unexplained monitoring on beliefs, behavior and internal states; and the effect of "
        "training text that depicts cooperation or hostility between humans and AI."),
    "research/labeling-claims-by-kind-of-support": (
        "Labeling Claims by Kind of Support: A Claim Table for Philosophical Writing",
        "Method note, version 1.0, November 2026",
        "This note sets out a simple discipline, used throughout the Universal Inquiry research program: every main claim in a "
        "paper is listed in a table with its kind, its basis and its status, and no main claim may rest only on opinion."),
}


def test_text_pages_are_written_with_their_pdfs():
    assert run_build().returncode == 0
    for folder, (title, kind, _) in TEXT_PAGES.items():
        slug = folder.split("/")[1]
        t = (SITE / folder / "index.html").read_text(encoding="utf-8")
        assert f"<h1>{title}</h1>" in t, folder
        assert f">{kind}</p>" in t, folder
        assert f'<a class="orcid" href="{ORCID}" rel="me">' in t, folder  # his ORCID line, as in the PDF
        assert (SITE / folder / f"{slug}.pdf").read_bytes() == (ROOT / "texts" / f"{slug}.pdf").read_bytes(), folder
        assert t.count('<nav aria-label="Site">') == 1 and ('aria-current=page>Research<' in t) == folder.startswith("research")


def test_text_pages_tell_search_engines_what_they_are():
    assert run_build().returncode == 0
    for folder, (title, kind, summary) in TEXT_PAGES.items():
        t = (SITE / folder / "index.html").read_text(encoding="utf-8")
        head = t[:t.index("</head>")]
        assert meta(head, "name", "description") == summary, folder  # its own description, not the site's
        assert f'<link rel="canonical" href="https://jakpotvin.com/{folder}/">' in head, folder
        assert meta(head, "property", "og:type") == "article", folder
        assert '"datePublished":"2026-11-27"' in head and f'"sameAs":["{ORCID}"]' in head, folder
    sm = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    for folder in TEXT_PAGES:
        assert f"<loc>https://jakpotvin.com/{folder}/</loc>" in sm, folder


def test_every_link_on_a_text_page_resolves():
    assert run_build().returncode == 0
    for folder in TEXT_PAGES:
        page = SITE / folder / "index.html"
        for ref in re.findall(r'(?:href|src)="([^"]+)"', page.read_text(encoding="utf-8")):
            if ref.startswith(("https://", "http://", "mailto:", "#")):
                continue
            path = ref.split("#")[0].split("?")[0]
            target = page.parent / path
            if path.endswith("/"):
                target = target / "index.html"
            assert target.exists(), (folder, ref)


def test_the_war_room_lists_its_essay():
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    r = t.index('<section class="room" id="s-warfare"')
    room = t[r:t.index("</section>", r)]
    assert '<ul class="room-essays">' in room and '<a href="essays/offshoring-the-mind/">Offshoring the Mind</a>' in room
    assert "Handing thinking over to AI resembles handing manufacturing over to another country." in room
    assert "November 2026" in room and "Coming soon" not in room
    for anchor in ROOM_PAINTINGS:
        if anchor != "s-warfare":
            r = t.index(f'id="{anchor}"')
            assert "Coming soon" in t[r:t.index("</section>", r)], anchor  # the other rooms wait


def test_papers_lists_the_three_texts_first():
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    p = t.index('<section class="research-papers"')
    papers = t[p:t.index("</section>", p)]
    at = [papers.index(x) for x in ("Measuring Cognitive Hollowing:", "Measuring Siege Mentality in AI Systems:",
                                     "Labeling Claims by Kind of Support:", "Predicting the adopted organisation")]
    assert at == sorted(at)  # newest first; on the same day, the two proposals before the method note
    for slug in ("measuring-cognitive-hollowing", "measuring-siege-mentality-in-ai", "labeling-claims-by-kind-of-support"):
        assert f'href="research/{slug}/"' in papers and f'href="research/{slug}/{slug}.pdf"' in papers, slug


def test_writing_note_says_more_are_coming():
    assert run_build().returncode == 0
    assert "More essays are coming soon." in (SITE / "index.html").read_text(encoding="utf-8")
