"""Read site-text.txt, the file of page words Jak edits in Notepad, and turn its lines into safe HTML.

Format: a line [section name] starts a section; lines starting with # are notes and never appear on the site;
a blank line ends a paragraph; a line starting with "- " is one list item; [words](address) is a link.
"""
import html
import re
from pathlib import Path

HEADER = re.compile(r"^\[(.+)\]$")
LINK = re.compile(r"\[([^\[\]]+)\]\(([^()\s]+)\)")
LONG_DASHES = (chr(0x2013), chr(0x2014))
ABSOLUTE = ("http:", "https:", "mailto:", "#", "/")


class SiteTextError(Exception):
    """A problem in site-text.txt, as one plain sentence that names the line when there is one."""


def key(name):
    """The lookup form of a section name: lower case, single spaces."""
    return " ".join(name.split()).lower()


def _sections(text, fname="site-text.txt"):
    """Section key -> (display name, header line number, paragraphs, [(line number, text line)])."""
    out, cur, para = {}, None, []

    def end_paragraph():
        if para and cur is not None:
            out[cur][2].append(" ".join(para))
        para.clear()

    for n, raw in enumerate(text.split("\n"), 1):
        line = raw.rstrip()
        if line.lstrip().startswith("#"):
            continue
        m = HEADER.match(line.strip())
        if m:
            end_paragraph()
            name = " ".join(m.group(1).split())
            cur = key(name)
            if cur in out:
                raise SiteTextError(f"{fname} line {n}: section [{name}] appears twice (also on line {out[cur][1]}).")
            out[cur] = (name, n, [], [])
            continue
        if not line.strip():
            end_paragraph()
            continue
        if cur is None:
            raise SiteTextError(f"{fname} line {n}: these words are not under any [section] heading.")
        out[cur][3].append((n, line))
        if line.startswith("- "):
            end_paragraph()
            para.append(line[2:].strip())
        else:
            para.append(line.strip())
    end_paragraph()
    return out


def parse(text):
    """Section key -> list of paragraphs (list items are paragraphs too)."""
    return {k: v[2] for k, v in _sections(text).items()}


def load(path, sections, optional=()):
    """Read and check the file; every name in `sections` must be present and non-empty, and no other names but those
    in `optional`, which may be missing or empty (they come back as empty lists)."""
    path = Path(path)
    fname = path.name
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        raise SiteTextError(f"{fname}: the file is missing (looked for {path}).") from None
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        line = raw[:e.start].count(b"\n") + 1
        raise SiteTextError(f"{fname} line {line}: the file is not saved as UTF-8; in Notepad use File, Save as, "
                            "and choose Encoding: UTF-8.") from None
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    found = _sections(text, fname)
    wanted = {key(s): s for s in list(sections) + list(optional)}
    may_be_empty = {key(s) for s in optional}
    for k, (name, n, paras, lines) in found.items():
        if k not in wanted:
            raise SiteTextError(f"{fname} line {n}: unknown section [{name}]. The sections are: {', '.join(wanted.values())}.")
    for k, name in wanted.items():
        if k not in found and k not in may_be_empty:
            raise SiteTextError(f"{fname}: section [{name}] is missing.")
    for k, (name, n, paras, lines) in found.items():
        if not paras and k not in may_be_empty:
            raise SiteTextError(f"{fname} line {n}: section [{name}] is empty.")
        for ln, line in lines:
            if any(d in line for d in LONG_DASHES):
                raise SiteTextError(f"{fname} line {ln}: a long dash in [{name}]; use a comma, a colon or parentheses instead.")
    out = {k: v[2] for k, v in found.items()}
    for k in may_be_empty:
        out.setdefault(k, [])
    return out


def inline(text, root=""):
    """Escape a line of site text for HTML and turn [words](address) into links."""
    out, pos = [], 0
    for m in LINK.finditer(text):
        out.append(html.escape(text[pos:m.start()], quote=False))
        words, addr = m.group(1), m.group(2)
        if not addr.startswith(ABSOLUTE):
            addr = root + addr
        out.append(f'<a href="{html.escape(addr, quote=True)}">{html.escape(words, quote=False)}</a>')
        pos = m.end()
    out.append(html.escape(text[pos:], quote=False))
    return "".join(out)


def split_item(paragraph):
    """A list item "title | description" -> (title, description)."""
    if " | " not in paragraph:
        raise SiteTextError(f'site-text.txt: the list item "{paragraph[:40]}" needs " | " between its title and its description.')
    title, desc = paragraph.split(" | ", 1)
    return title.strip(), desc.strip()
