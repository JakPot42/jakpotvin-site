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
ORCID = "https://orcid.org/"  # a link here shows ORCID's green iD icon (assets/orcid-id.svg, ORCID's own file) and says rel="me"


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


def _read(path):
    """The file's words, with Windows line ends made plain, or a SiteTextError saying what is wrong with the file."""
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
    return text.replace("\r\n", "\n").replace("\r", "\n")


def load(path, sections, optional=()):
    """Read and check the file; every name in `sections` must be present and non-empty, and no other names but those
    in `optional`, which may be missing or empty (they come back as empty lists)."""
    path = Path(path)
    fname = path.name
    found = _sections(_read(path), fname)
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
        href, shown = html.escape(addr, quote=True), html.escape(words, quote=False)
        if addr.startswith(ORCID):
            out.append(f'<a class="orcid" href="{href}" rel="me"><img src="{root}assets/orcid-id.svg" width="16" height="16" alt="">{shown}</a>')
        else:
            out.append(f'<a href="{href}">{shown}</a>')
        pos = m.end()
    out.append(html.escape(text[pos:], quote=False))
    return "".join(out)


LINK_LINE = re.compile(r"^[^\[\]:]+:\s*\[[^\[\]]+\]\([^()\s]+\)$")  # Label: [words](address)


def papers(path, section="research papers"):
    """The papers in [research papers], in order, each a dict: title, status (where it stands), summary, and links (each
    link line as written, Label: [words](address)). A paper starts with a line "- " and its title; the next line says
    where it stands; then comes its summary, and last one line per link. No section, or an empty one: no papers."""
    path = Path(path)
    found = _sections(_read(path), path.name).get(key(section))
    out = []
    for n, line in (found[3] if found else []):
        s = line.strip()
        if line.startswith("- "):
            out.append({"title": s[2:].strip(), "status": "", "summary": [], "links": [], "line": n})
        elif not out:
            raise SiteTextError(f'{path.name} line {n}: in [{found[0]}], each paper starts with a line "- " and its title.')
        elif LINK_LINE.match(s):
            out[-1]["links"].append(s)
        elif out[-1]["links"]:
            raise SiteTextError(f"{path.name} line {n}: in [{found[0]}], a paper's summary goes before its links.")
        elif not out[-1]["status"]:
            out[-1]["status"] = s
        else:
            out[-1]["summary"].append(s)
    for p in out:
        if not p["status"] or not p["summary"]:
            raise SiteTextError(f'{path.name} line {p["line"]}: the paper "{p["title"][:40]}" needs a line saying where '
                                "it stands, then its summary.")
    return [{"title": p["title"], "status": p["status"], "summary": " ".join(p["summary"]), "links": p["links"]} for p in out]


def split_item(paragraph):
    """A list item "title | description" -> (title, description)."""
    if " | " not in paragraph:
        raise SiteTextError(f'site-text.txt: the list item "{paragraph[:40]}" needs " | " between its title and its description.')
    title, desc = paragraph.split(" | ", 1)
    return title.strip(), desc.strip()
