"""Check that a text's web page says what its PDF says, word for word.

usage: python tools/check_text.py PDF PAGE [--allow OLD=NEW ...] [--order]
  PDF   the text's PDF, read with pdftotext (Git for Windows ships it; set PDFTOTEXT to use another copy)
  PAGE  the built page (site/.../index.html: the words inside <article class="text">, less anything marked
        data-added), or the source (texts/<name>.md: the header's title, name, ORCID and kind line, then the text)
  --allow OLD=NEW  a difference that is meant: the PDF says OLD and the page says NEW. Use it for an approved
        correction, and for a real hyphen pdftotext drops at the end of a line (selfdetermination=self-determination).
  --order  also list where the running order differs (in tables pdftotext reads across columns, so expect some there)

From the PDF it drops the running header at the top of each page after the first and the page number at the foot
of each page, and the bullet marks. It counts every word, punctuation included, on both sides: it exits 0 only when
the counts match, and prints every word that is missing or extra."""
import collections
import html.parser
import os
import pathlib
import re
import shutil
import subprocess
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import texts  # noqa: E402

GIT_PDFTOTEXT = r"C:\Program Files\Git\ucrt64\bin\pdftotext.exe"
BLOCKS = {"p", "li", "td", "th", "tr", "h1", "h2", "h3", "div", "br", "ul", "ol", "table", "section", "header"}


def pdf_words(pdf, short, kind, allow, table_heads=()):
    """The PDF's words. A table that runs onto the next page repeats its header row there; that repeat is dropped
    (table_heads: each table's header row as a list of words, from the source)."""
    exe = os.environ.get("PDFTOTEXT") or shutil.which("pdftotext") or GIT_PDFTOTEXT
    raw = subprocess.run([exe, "-enc", "UTF-8", str(pdf), "-"], capture_output=True, check=True).stdout.decode("utf-8")
    raw = unicodedata.normalize("NFKC", raw).replace("\r", "")
    kept, printed = [], []  # each page's words as kept, and as printed
    for no, page in enumerate(raw.split("\f"), 1):
        lines = [x.strip() for x in page.split("\n") if x.strip()]
        if no > 1:
            while lines and lines[0] in (f"Potvin, {short}", kind, f"Potvin, {short} {kind}"):
                lines.pop(0)
        if lines and lines[-1] == str(no):
            lines.pop()
        words = " ".join(lines).split()
        printed.append(list(words))
        if no > 1:
            # A repeat only: this page opens with the header's first word, the header's words all appear on the page
            # before (where the table began), and all appear again near the top of this one (pdftotext reads a header
            # of several columns across them, mixed in with the first cells).
            before = collections.Counter(printed[-2]) if len(printed) > 1 else collections.Counter()
            for head in table_heads:
                window = words[:len(head) + 300]
                need = collections.Counter(head)
                if head and words[:1] == head[:1] and not need - before and not need - collections.Counter(window):
                    for w in head:
                        window.remove(w)
                    words = window + words[len(head) + 300:]
                    break
        kept.append(" ".join(words))
    text = "\n".join(kept)
    for old, new in allow:
        if old not in text:
            sys.exit(f"--allow {old}={new}: the PDF never says {old!r}")
        text = text.replace(old, new)
    return [w for w in text.split() if w != "•"]


class _Article(html.parser.HTMLParser):
    """The words of <article class="text">, skipping elements marked data-added; a numbered list's numbers included."""

    def __init__(self):
        super().__init__()
        self.depth, self.skip, self.out, self.ols = 0, 0, [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "article" and "text" in (a.get("class") or "").split():
            self.depth = 1
            return
        if not self.depth:
            return
        if tag not in ("br", "img", "meta", "link", "input", "hr"):
            self.depth += 1
            if self.skip or "data-added" in a:
                self.skip += 1
        if tag == "ol":
            self.ols.append(int(a.get("start") or 1))
        elif tag == "li" and self.ols and not self.skip:
            self.out.append(f" {self.ols[-1]}. ")
            self.ols[-1] += 1
        elif tag in BLOCKS:
            self.out.append(" ")

    def handle_endtag(self, tag):
        if not self.depth:
            return
        if tag == "ol" and self.ols:
            self.ols.pop()
        self.depth -= 1
        if self.skip:
            self.skip -= 1
        if tag in BLOCKS:  # a word never runs across a block's edge; inline marks (strong, em, a) add no space
            self.out.append(" ")

    def handle_data(self, data):
        if self.depth and not self.skip:
            self.out.append(data)


def page_words(page):
    page = pathlib.Path(page)
    if page.suffix == ".md":
        meta, body = texts.parse(page.read_text(encoding="utf-8"))
        doc = (f'<article class="text"><h1>{meta["title"]}</h1><p>Jak Potvin</p><p>ORCID: {meta["orcid"]}</p>'
               f'<p>{meta["kind"]}</p>{body}</article>')
    else:
        doc = page.read_text(encoding="utf-8")
    p = _Article()
    p.feed(doc)
    return unicodedata.normalize("NFKC", "".join(p.out)).split()


def blocks(page):
    """The words of each paragraph, heading and list item outside the tables, one string each."""
    page = pathlib.Path(page)
    if page.suffix == ".md":
        meta, body = texts.parse(page.read_text(encoding="utf-8"))
        doc = f'<h1>{meta["title"]}</h1><p>Jak Potvin</p><p>ORCID: {meta["orcid"]}</p><p>{meta["kind"]}</p>{body}'
    else:
        t = page.read_text(encoding="utf-8")
        doc = t[t.index('<article class="text"'):t.index("</article>")]
    doc = re.sub(r'<div class="table".*?</div>', " ", doc, flags=re.S)
    doc = re.sub(r"<(p|h\d|li)\b[^>]*\bdata-added\b[^>]*>.*?</\1>", " ", doc, flags=re.S)
    out = []
    for m in re.finditer(r"<(p|h1|h2|h3|li)\b[^>]*>(.*?)</\1>", doc, flags=re.S):
        words = unicodedata.normalize("NFKC", html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))).split()
        if words:
            out.append(" ".join(words))
    return out


def main(argv):
    args, allow, order = [], [], False
    it = iter(argv)
    for a in it:
        if a == "--allow":
            old, _, new = next(it).partition("=")
            allow.append((old, new))
        elif a == "--order":
            order = True
        else:
            args.append(a)
    pdf, page = args
    src = pathlib.Path(page)
    md = src if src.suffix == ".md" else pathlib.Path(__file__).resolve().parent.parent / "texts" / (src.parent.name + ".md")
    meta, body = texts.parse(md.read_text(encoding="utf-8"))
    heads = []
    for thead in re.findall(r"<thead>(.*?)</thead>", body):
        p = _Article()
        p.feed(f'<article class="text">{thead}</article>')
        heads.append(unicodedata.normalize("NFKC", "".join(p.out)).split())
    a, b = pdf_words(pdf, meta["short"], meta["kind"], allow, heads), page_words(page)
    ca, cb = collections.Counter(a), collections.Counter(b)
    missing, extra = ca - cb, cb - ca
    for w, n in sorted(missing.items()):
        print(f"missing from the page: {w!r} x{n}")
    for w, n in sorted(extra.items()):
        print(f"extra on the page: {w!r} x{n}")
    if order:  # every paragraph, heading and list item outside the tables reads in the PDF as one run of words
        whole = " " + " ".join(a) + " "
        for block in blocks(page):
            if f" {block} " not in whole:
                print(f"order: not one run in the PDF: {block[:150]!r}")
    print(f"{pathlib.Path(pdf).name}: {len(a)} words in the PDF, {len(b)} on the page, "
          + ("the same words" if not missing and not extra else f"{sum(missing.values())} missing, {sum(extra.values())} extra"))
    return 0 if not missing and not extra else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
