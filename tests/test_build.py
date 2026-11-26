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
    for needed in ("Photograph by Stefan Schäfer, Lich, licensed CC BY-SA 4.0", "Photograph by Marie-Lan Nguyen",
                   "Jacques-Louis David, The Death of Socrates, 1787", "The top layer of a silicon crystal, drawn for this site."):
        assert needed in credits, needed
