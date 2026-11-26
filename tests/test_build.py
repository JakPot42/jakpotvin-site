"""Build-level tests: these run build.py, which rewrites site/ (the result is deterministic)."""
import hashlib
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
