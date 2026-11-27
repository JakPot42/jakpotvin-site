import pytest

from sitetext import SiteTextError, inline, load, papers, parse, split_item

SAMPLE = """# A note for Jak
[Name]
Jak Potvin

[bio]
First line of a paragraph
continues here.

Second paragraph.

[areas]
- Space | Satellites
- Law | Courts
"""


def write(tmp_path, text, name="site-text.txt", encoding="utf-8"):
    p = tmp_path / name
    p.write_bytes(text.encode(encoding))
    return p


def test_parse_sections_and_paragraphs():
    got = parse(SAMPLE)
    assert got["name"] == ["Jak Potvin"]
    assert got["bio"] == ["First line of a paragraph continues here.", "Second paragraph."]


def test_comment_lines_ignored():
    got = parse("[bio]\n# not shown\nShown\n")
    assert got == {"bio": ["Shown"]}


def test_list_items_are_paragraphs():
    assert parse(SAMPLE)["areas"] == ["Space | Satellites", "Law | Courts"]


def test_section_names_normalised():
    assert list(parse("[  Room   Note:  The future ]\nx\n")) == ["room note: the future"]


def test_bom_and_crlf(tmp_path):
    lf = load(write(tmp_path, SAMPLE), ["name", "bio", "areas"])
    crlf = load(write(tmp_path, chr(0xFEFF) + SAMPLE.replace("\n", "\r\n") + "   \r\n\r\n", "b.txt"), ["name", "bio", "areas"])
    assert crlf == lf


def test_missing_section_message(tmp_path):
    with pytest.raises(SiteTextError) as e:
        load(write(tmp_path, "[name]\nJak\n"), ["name", "bio"])
    assert str(e.value) == "site-text.txt: section [bio] is missing."


def test_unknown_section_names_line(tmp_path):
    with pytest.raises(SiteTextError) as e:
        load(write(tmp_path, "[name]\nJak\n\n[bioo]\nText\n"), ["name", "bio"])
    assert str(e.value).startswith("site-text.txt line 4: unknown section [bioo]")
    assert "bio" in str(e.value).split("[bioo]", 1)[1]


def test_empty_section_names_line(tmp_path):
    with pytest.raises(SiteTextError) as e:
        load(write(tmp_path, "[name]\nJak\n[bio]\n# only a note\n"), ["name", "bio"])
    assert str(e.value) == "site-text.txt line 3: section [bio] is empty."


@pytest.mark.parametrize("dash", [chr(0x2013), chr(0x2014)])
def test_long_dash_rejected(tmp_path, dash):
    with pytest.raises(SiteTextError) as e:
        load(write(tmp_path, f"[name]\nJak\n\n[bio]\nOne {dash} two\n"), ["name", "bio"])
    msg = str(e.value)
    assert msg.startswith("site-text.txt line 5:")
    assert "[bio]" in msg and "comma" in msg


def test_text_outside_a_section_names_line(tmp_path):
    with pytest.raises(SiteTextError) as e:
        load(write(tmp_path, "Stray words\n[name]\nJak\n"), ["name"])
    assert str(e.value).startswith("site-text.txt line 1:")


def test_duplicate_section_names_both_lines(tmp_path):
    with pytest.raises(SiteTextError) as e:
        load(write(tmp_path, "[name]\nJak\n[name]\nJak again\n"), ["name"])
    assert str(e.value).startswith("site-text.txt line 3:") and "line 1" in str(e.value)


def test_typographic_quotes_allowed(tmp_path):
    text = "I" + chr(0x2019) + "m " + chr(0x201C) + "quoted" + chr(0x201D) + " " + chr(0xA9) + " 2026"
    got = load(write(tmp_path, f"[bio]\n{text}\n"), ["bio"])
    assert got["bio"] == [text]
    assert inline(text) == text


PAPERS = """[research papers]
- A title (Study 1)
Preregistered November 2026 · Paper in preparation
# a note for Jak
First line of the summary
continues here.

Plan: [https://doi.org/10.1/A](https://doi.org/10.1/A)
Amendment: [https://doi.org/10.1/B](https://doi.org/10.1/B)

- Second paper
Published
Its summary.
"""


def test_papers_reads_each_block(tmp_path):
    assert papers(write(tmp_path, PAPERS)) == [
        {"title": "A title (Study 1)", "status": "Preregistered November 2026 " + chr(0xB7) + " Paper in preparation",
         "summary": "First line of the summary continues here.",
         "links": ["Plan: [https://doi.org/10.1/A](https://doi.org/10.1/A)",
                   "Amendment: [https://doi.org/10.1/B](https://doi.org/10.1/B)"]},
        {"title": "Second paper", "status": "Published", "summary": "Its summary.", "links": []}]


def test_papers_without_the_section_is_no_papers(tmp_path):
    assert papers(write(tmp_path, "[bio]\nx\n")) == []
    assert papers(write(tmp_path, "[research papers]\n")) == []


@pytest.mark.parametrize("text, says", [
    ("[research papers]\nWords before any title\n", "line 2"),
    ("[research papers]\n- Title only\n", "line 2.*needs"),
    ("[research papers]\n- Title\nWhere it stands\n", "line 2.*needs"),
    ("[research papers]\n- T\nS\nSummary\nPlan: [a](https://a.b)\nMore words after the links\n", "line 6"),
])
def test_papers_errors_name_the_line(tmp_path, text, says):
    with pytest.raises(SiteTextError, match=says):
        papers(write(tmp_path, text))


def test_inline_escapes_html():
    assert inline("a < b & c") == "a &lt; b &amp; c"
    assert inline("<b>x</b>") == "&lt;b&gt;x&lt;/b&gt;"


def test_inline_link_relative_gets_root():
    assert inline("[list](plates.html)", "../") == '<a href="../plates.html">list</a>'


def test_inline_absolute_and_mailto_untouched():
    assert inline("[GitHub](https://github.com/JakPot42)", "../") == '<a href="https://github.com/JakPot42">GitHub</a>'
    assert inline("[me](mailto:jak@jakpotvin.com)", "../") == '<a href="mailto:jak@jakpotvin.com">me</a>'
    assert inline("[top](#projects)", "../") == '<a href="#projects">top</a>'


def test_inline_orcid_link_shows_the_id_icon():  # ORCID asks for its green iD icon beside the full https link
    addr = "https://orcid.org/0009-0000-1700-0435"
    assert inline(f"ORCID: [{addr}]({addr})", "../") == (
        f'ORCID: <a class="orcid" href="{addr}" rel="me"><img src="../assets/orcid-id.svg" width="16" height="16" alt="">{addr}</a>')
    assert inline("[x](https://orcid.org.example.com/a)") == '<a href="https://orcid.org.example.com/a">x</a>'  # only orcid.org itself


def test_inline_link_inside_sentence():
    assert inline("Email: [jak@jakpotvin.com](mailto:jak@jakpotvin.com). Code: [x](https://a.b/?q=1&r=2)") == (
        'Email: <a href="mailto:jak@jakpotvin.com">jak@jakpotvin.com</a>. Code: <a href="https://a.b/?q=1&amp;r=2">x</a>')


def test_inline_quote_in_address_escaped():
    assert inline('[x](a"b.html)') == '<a href="a&quot;b.html">x</a>'


def test_inline_malformed_link_left_as_text():
    assert inline("[words](address") == "[words](address"
    assert inline("[words] (address)") == "[words] (address)"


def test_split_item():
    assert split_item("[Atom Factory Calculator](atoms/calculator/index.html) | How many good parts") == (
        "[Atom Factory Calculator](atoms/calculator/index.html)", "How many good parts")
    assert split_item("A | b | c") == ("A", "b | c")
    with pytest.raises(SiteTextError) as e:
        split_item("No separator in this list item at all, sorry")
    assert "No separator in this list item at all," in str(e.value)


def test_not_utf8_names_line(tmp_path):
    p = tmp_path / "site-text.txt"
    p.write_bytes("[name]\nJak\n[bio]\nCafé au lait\n".encode("cp1252"))
    with pytest.raises(SiteTextError) as e:
        load(p, ["name", "bio"])
    assert str(e.value).startswith("site-text.txt line 4:") and "UTF-8" in str(e.value)


def test_utf16_file_message(tmp_path):
    p = tmp_path / "site-text.txt"
    p.write_bytes("[name]\nJak\n".encode("utf-16"))
    with pytest.raises(SiteTextError) as e:
        load(p, ["name"])
    assert "UTF-8" in str(e.value)


def test_missing_file_message(tmp_path):
    with pytest.raises(SiteTextError) as e:
        load(tmp_path / "site-text.txt", ["name"])
    assert str(e.value).startswith("site-text.txt: the file is missing")


def test_optional_section_may_be_empty_or_missing(tmp_path):
    p = write(tmp_path, "[name]\nJak\n\n[featured projects]\n# none yet\n")
    assert load(p, ["name"], optional=["featured projects"])["featured projects"] == []
    p = write(tmp_path, "[name]\nJak\n")
    assert load(p, ["name"], optional=["featured projects"])["featured projects"] == []
    p = write(tmp_path, "[name]\nJak\n\n[featured projects]\n- [A](https://example.org/a) | Does a\n")
    assert load(p, ["name"], optional=["featured projects"])["featured projects"] == ["[A](https://example.org/a) | Does a"]


def test_optional_section_is_known_and_required_ones_still_checked(tmp_path):
    p = write(tmp_path, "[featured projects]\n\n[name]\n")
    with pytest.raises(SiteTextError, match=r"line 3: section \[name\] is empty"):
        load(p, ["name"], optional=["featured projects"])
