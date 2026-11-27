"""Essays and papers: a source file in texts/ is a header block, then the text in a small Markdown subset.

Header, between two lines of ---:  key: value, one per line, every key in KEYS.
Text, in blocks separated by a blank line:
  ## Heading            a section heading (h2);  ### Heading  a subsection heading (h3)
  - item                a bulleted list, one item per line
  1. item               a numbered list, one item per line (it may start at any number)
  | a | b |             a table: a header row, then |---|---|, then one row per line, the same number of cells in each
  anything else         a paragraph; its lines are joined with a space
Inside a block: **bold**, *italic*, [words](/address/) for a page of this site, [words](https://...), and a bare
https://... address, which becomes a link to itself.
Anything else (a deeper heading, a quote, an HTML tag, a code fence, an unclosed mark, a ragged table) stops the build
with its line number, so nothing in a source is dropped without a word."""
import html
import re

KEYS = ("title", "short", "kind", "date", "published", "place", "summary", "pdf", "orcid")


class TextError(ValueError):
    """A problem in a source file; the message starts with 'line N:'."""


_MARK = re.compile(r"\*\*(.+?)\*\*|\*([^*]+?)\*|\[([^\[\]]+)\]\(([^()\s]+)\)|(https?://[^\s<>]+)")
_TRAIL = ".,;:"


def _url(addr):
    """Split a bare address from punctuation that follows it: trailing . , ; : and a closing bracket it did not open."""
    tail = ""
    while addr and (addr[-1] in _TRAIL or (addr[-1] == ")" and addr.count(")") > addr.count("("))):
        tail, addr = addr[-1] + tail, addr[:-1]
    return addr, tail


def inline(s, root):
    """One line of text as HTML: escaped, with bold, italic and links. A stray * is a mistake, not text."""
    out, pos = [], 0
    for m in _MARK.finditer(s):
        out.append(_plain(s[pos:m.start()]))
        if m.group(1) is not None:
            out.append(f"<strong>{inline(m.group(1), root)}</strong>")
        elif m.group(2) is not None:
            out.append(f"<em>{inline(m.group(2), root)}</em>")
        elif m.group(3) is not None:
            addr = m.group(4)
            if addr.startswith("/"):
                addr = root + addr[1:]
            elif not addr.startswith("https://"):
                raise ValueError(f"a link must go to /a/page/ of this site or to https://: {addr}")
            out.append(f'<a href="{html.escape(addr, quote=True)}">{inline(m.group(3), root)}</a>')
        else:
            addr, tail = _url(m.group(5))
            out.append(f'<a href="{html.escape(addr, quote=True)}">{html.escape(addr, quote=False)}</a>{html.escape(tail, quote=False)}')
        pos = m.end()
    out.append(_plain(s[pos:]))
    return "".join(out)


def _plain(s):
    if "*" in s:
        raise ValueError(f"an unclosed * or ** near: {s.strip()[:40]}")
    return html.escape(s, quote=False)


def _slug(words, taken):
    base = re.sub(r"[^a-z0-9]+", "-", words.lower()).strip("-") or "section"
    slug, n = base, 2
    while slug in taken:
        slug, n = f"{base}-{n}", n + 1
    taken.add(slug)
    return slug


_CELLS = re.compile(r"^\|(.*)\|$")
_RULE = re.compile(r"^\|(\s*:?-+:?\s*\|)+$")
_OL = re.compile(r"^(\d+)\. (.*)$")


def _cells(line, n):
    m = _CELLS.match(line.strip())
    if not m:
        raise TextError(f"line {n}: a table row must start and end with |")
    return [c.strip() for c in m.group(1).split("|")]


def parse(source):
    """(header fields, text as HTML) from a source file's contents."""
    lines = source.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---" or "---" not in [x.strip() for x in lines[1:]]:
        raise TextError("line 1: a source starts with a header between two lines of ---")
    end = 1 + [x.strip() for x in lines[1:]].index("---")
    meta = {}
    for n in range(1, end):
        k, sep, v = lines[n].partition(": ")
        if not sep or k not in KEYS or k in meta or not v.strip():
            raise TextError(f"line {n + 1}: a header line is 'key: value', one of {', '.join(KEYS)}, each once")
        meta[k] = v.strip()
    missing = [k for k in KEYS if k not in meta]
    if missing:
        raise TextError(f"line 1: the header lacks {', '.join(missing)}")

    blocks, block = [], []
    for n in range(end + 1, len(lines)):
        if lines[n].strip():
            block.append((n + 1, lines[n].rstrip()))
        elif block:
            blocks.append(block)
            block = []
    if block:
        blocks.append(block)

    out, ids, tables = [], set(), 0
    for block in blocks:
        first_no, first = block[0]
        try:
            if first.startswith("## ") or first.startswith("### "):
                if len(block) > 1:
                    raise TextError(f"line {block[1][0]}: a heading stands alone, with a blank line after it")
                level, words = (2, first[3:]) if first.startswith("## ") else (3, first[4:])
                out.append(f'<h{level} id="{_slug(words, ids)}">{inline(words.strip(), ROOT)}</h{level}>')
            elif first.startswith("#") or first.startswith(">") or first.startswith("<") or first.startswith("```"):
                raise TextError(f"line {first_no}: this kind of block is not part of the format")
            elif first.startswith("- "):
                items = []
                for n, line in block:
                    if not line.startswith("- "):
                        raise TextError(f"line {n}: every line of a bulleted list starts with '- '")
                    items.append(f"<li>{_inline_at(line[2:], n)}</li>")
                out.append("<ul>" + "".join(items) + "</ul>")
            elif _OL.match(first):
                items, start = [], int(_OL.match(first).group(1))
                for n, line in block:
                    m = _OL.match(line)
                    if not m:
                        raise TextError(f"line {n}: every line of a numbered list starts with a number and '. '")
                    items.append(f"<li>{_inline_at(m.group(2), n)}</li>")
                out.append(("<ol>" if start == 1 else f'<ol start="{start}">') + "".join(items) + "</ol>")
            elif first.startswith("|"):
                if len(block) < 3 or not _RULE.match(block[1][1].strip()):
                    raise TextError(f"line {first_no}: a table is a header row, a |---| row, then its rows")
                head = _cells(first, first_no)
                rows = []
                for n, line in block[2:]:
                    cells = _cells(line, n)
                    if len(cells) != len(head):
                        raise TextError(f"line {n}: this row has {len(cells)} cells; the table has {len(head)} columns")
                    rows.append("<tr>" + "".join(f"<td>{_inline_at(c, n)}</td>" for c in cells) + "</tr>")
                tables += 1
                out.append(f'<div class="table" role="region" tabindex="0" aria-label="Table {tables}"><table>'
                           "<thead><tr>" + "".join(f'<th scope="col">{_inline_at(c, first_no)}</th>' for c in head)
                           + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")
            else:
                for n, line in block:
                    if line.startswith(("#", ">", "<", "```", "|")):
                        raise TextError(f"line {n}: this line starts a different kind of block; leave a blank line before it")
                out.append("<p>" + _inline_at(" ".join(line.strip() for _, line in block), first_no) + "</p>")
        except ValueError as e:
            if isinstance(e, TextError):
                raise
            raise TextError(f"line {first_no}: {e}") from None
    return meta, "\n".join(out)


ROOT = "../../"  # every text page sits two folders down: essays/<name>/ or research/<name>/


def _inline_at(s, n):
    try:
        return inline(s, ROOT)
    except ValueError as e:
        raise TextError(f"line {n}: {e}") from None
