"""The text format for essays and papers (texts.py): a header block, then a small Markdown subset; anything else stops."""
import pytest

from texts import TextError, inline, parse

HEAD = """---
title: Offshoring the Mind: AI Dependence, Lost Capability and the Risk of a Cold Standoff Between Humans and AI
short: Offshoring the Mind
kind: Version 1.0, November 2026
date: November 2026
published: 2026-11-27
place: s-warfare
summary: Handing thinking over to AI resembles handing manufacturing over to another country.
pdf: offshoring-the-mind.pdf
orcid: https://orcid.org/0009-0000-1700-0435
---
"""


def test_header_and_heading():
    meta, body = parse(HEAD + "## 1. Introduction\n\nText.\n")
    assert meta["short"] == "Offshoring the Mind"
    assert meta["title"].endswith("Between Humans and AI")  # a colon inside a value stays in it
    assert '<h2 id="1-introduction">1. Introduction</h2>' in body
    assert "<p>Text.</p>" in body
    _, body = parse(HEAD + "### 2.1 Three documented effects\n\nOne\ntwo.\n")
    assert '<h3 id="2-1-three-documented-effects">2.1 Three documented effects</h3>' in body
    assert "<p>One two.</p>" in body  # a paragraph's lines are joined with a space


def test_inline_marks_and_links():
    got = inline("**Short answer.** The *order* of use, see https://doi.org/10.1016/S2468-1253(25)00133-5.", "../../")
    assert "<strong>Short answer.</strong>" in got and "<em>order</em>" in got
    assert ('<a href="https://doi.org/10.1016/S2468-1253(25)00133-5">https://doi.org/10.1016/S2468-1253(25)00133-5</a>.'
            in got)  # the full stop stays outside the link; the brackets inside the address stay in it
    assert inline("(see https://example.org/a)", "") == '(see <a href="https://example.org/a">https://example.org/a</a>)'
    assert inline("[Offshoring the Mind](/essays/offshoring-the-mind/)", "../../") == (
        '<a href="../../essays/offshoring-the-mind/">Offshoring the Mind</a>')
    assert inline("a < b & c", "") == "a &lt; b &amp; c"
    assert inline("**What follows from *all five*.**", "") == "<strong>What follows from <em>all five</em>.</strong>"


def test_lists():
    _, body = parse(HEAD + "- a\n- b\n")
    assert "<ul><li>a</li><li>b</li></ul>" in body
    _, body = parse(HEAD + "3. x\n4. y\n")
    assert '<ol start="3"><li>x</li><li>y</li></ol>' in body
    _, body = parse(HEAD + "1. x\n2. **y**\n")
    assert "<ol><li>x</li><li><strong>y</strong></li></ol>" in body


def test_table():
    _, body = parse(HEAD + "| Part | Carries over? |\n|---|---|\n| Moved | **Yes** |\n\n| a | b |\n|---|---|\n| c | d |\n")
    assert body.count('<th scope="col">') == 4
    assert '<div class="table" role="region" tabindex="0" aria-label="Table 1"><table>' in body
    assert 'aria-label="Table 2"' in body
    assert "<td>Moved</td><td><strong>Yes</strong></td>" in body


@pytest.mark.parametrize("source, line", [
    (HEAD + "Para with **no end.\n", 12),
    (HEAD + "\n| a | b |\n|---|---|\n| c | d | e |\n", 15),
    (HEAD + "Text.\n\n> a quote\n", 14),
    (HEAD + "#### Too deep\n", 12),
    (HEAD.replace("short: Offshoring the Mind\n", ""), 1),
])
def test_slips_stop_the_build(source, line):
    with pytest.raises(TextError) as e:
        parse(source)
    assert str(e.value).startswith(f"line {line}:"), str(e.value)
