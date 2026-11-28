"""tools/check_text.py: the check that a text's page says what its PDF says. Unit tests on small made-up pages, and the
check itself run on every text in texts/ (skipped where pdftotext is missing)."""
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import check_text  # noqa: E402

PDFTOTEXT = os.environ.get("PDFTOTEXT") or shutil.which("pdftotext") or check_text.GIT_PDFTOTEXT


def words(html, tmp_path):
    page = tmp_path / "index.html"
    page.write_text(html, encoding="utf-8")
    return check_text.page_words(page)


def test_page_words_leave_out_what_the_site_adds(tmp_path):
    got = words('<p>Menu</p><article class="text"><p data-added><a href="x">Research</a></p><h1>A title</h1>'
                '<p>One <strong>two</strong>, three.</p></article><footer>x</footer>', tmp_path)
    assert got == ["A", "title", "One", "two,", "three."]  # a mark adds no space; data-added and the outside are left out


def test_page_words_count_a_numbered_list_s_numbers(tmp_path):
    got = words('<article class="text"><ol start="3"><li>x</li><li>y</li></ol><ul><li>z</li></ul></article>', tmp_path)
    assert got == ["3.", "x", "4.", "y", "z"]  # the PDF prints the numbers; bullets it prints as marks the check drops


def test_order_problems_find_a_paragraph_out_of_sequence():
    whole = "a b c d e f".split()
    assert check_text.order_problems(["a b", "c d", "e f"], whole, []) == []
    assert check_text.order_problems(["c d", "a b"], whole, []) == ["out of order: 'a b'"]
    assert check_text.order_problems(["b a"], whole, []) == ["not one run in the PDF: 'b a'"]
    assert check_text.order_problems(["b a"], whole, ["b a"]) == []  # a known reading-order artifact, allowed by name


def test_allow_file_is_read_beside_the_source(tmp_path):
    src = tmp_path / "x.md"
    (tmp_path / "x.allow").write_text("# a real hyphen pdftotext joins\nselfdetermination=self-determination\n"
                                      "order: Anthropic (2026).\n", encoding="utf-8")
    assert check_text.read_allow(src) == ([("selfdetermination", "self-determination")], ["Anthropic (2026)."])


@pytest.mark.skipif(not pathlib.Path(PDFTOTEXT).exists() and not shutil.which("pdftotext"), reason="pdftotext not found")
@pytest.mark.parametrize("src", sorted((ROOT / "texts").glob("*.md")), ids=lambda p: p.stem)
def test_every_text_page_says_what_its_pdf_says(src):
    from test_build import run_build
    assert run_build().returncode == 0
    head = src.read_text(encoding="utf-8")
    folder = "research" if "\nplace: research\n" in head else "essays"
    page = ROOT / "site" / folder / src.stem / "index.html"
    r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "check_text.py"), str(src.with_suffix(".pdf")),
                        str(page), "--order"], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr  # the same words, every paragraph in the PDF's order
    assert "the same words" in r.stdout
