# Essay and Paper Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Jak's essay "Offshoring the Mind" and his three Research papers each get a web page in the site's style plus their PDF, listed in the War, strategy and defense room and in Research's Papers.

**Architecture:** Each text is `texts/<slug>.md` (a header block plus a small Markdown subset) with its PDF beside it. `texts.py` renders the subset to HTML and refuses anything else with a line number. `build.py` writes the pages through the shared `page()` template, copies the PDFs, lists the texts in their room or in Papers, and adds the pages to the sitemap. `tools/check_text.py` compares a built page's words with its PDF's words.

**Tech Stack:** Python 3.14 (the build), pytest, headless Edge through `tools/browser.py`, pdftotext (Git for Windows, ucrt64) for the word check only.

**Spec:** `docs/superpowers/specs/2026-11-27-essay-and-paper-pages-design.md`

## Global Constraints

- Every word on a page as in its PDF; the one approved change is "analyzes" to "analyses" in the siege paper, Section 6.
- No long dashes (U+2013, U+2014) in any file, page or commit message; no 19xx/20xx tokens in commit messages.
- Nothing about the startup: the private-name scan runs over every new file before any push.
- Files are written with LF line endings (`newline="\n"`); the build stays deterministic.
- Commit author is the repo's noreply address; stage files by name; never `--no-verify`; trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push without Jak's "push".

## Review Focus

1. A long DOI or address in a reference on a 320 px phone: it wraps; the page never scrolls sideways (Task 4 test).
2. A four-column claims table on a phone: it scrolls inside its own box, which a keyboard can reach and a screen reader names (Task 4 test).
3. A markup slip in a source file (an unclosed `**`, a table row with the wrong number of cells, an unknown block): the build stops and names the file and line (Task 1 tests).
4. The War room with its essay list: the list stays readable over each of the three paintings, and the room keeps its pause button (Task 4 test, through the existing contrast test's selector list).
5. A link from one text to another, or to a PDF: it resolves to a file the build wrote (Task 3 test).

---

### Task 0: Save the Research pictures

- [ ] Full suite green (run in progress when this plan was written), then commit build.py, README.md, site/index.html, site/plates.html, tests/test_build.py, tests/test_home_browser.py and the four new image files by name. Message: "Research shows three pictures: the Air Pump, Pasteur in his laboratory and the Solvay Conference".

### Task 1: The text format (`texts.py`)

**Files:** Create `texts.py`, `tests/test_texts.py`.

**Interfaces:**
- Produces: `class TextError(ValueError)` whose message starts with `line N:`; `parse(source: str) -> tuple[dict[str, str], str]` returning the header fields and the body HTML; `inline(s: str, root: str) -> str`.
- Header: lines `key: value` between two `---` lines; required keys `title, short, kind, date, published, place, summary, pdf, orcid`; `place` is `research` or a room anchor such as `s-warfare`.
- Body blocks: `## ` gives `<h2>`, `### ` gives `<h3>` (each with an id from its words); a blank line ends a block; `- ` items give `<ul>`; `N. ` items give `<ol>` (with `start` when not 1); pipe tables (`| a | b |` then `|---|---|`) give `<div class="table" role="region" tabindex="0" aria-label="Table N"><table>` with `<th scope="col">`; anything else is a paragraph, its lines joined with spaces.
- Inline: HTML-escaped text; `**x**` gives `<strong>`, `*x*` gives `<em>`; `[x](/path/)` gives a link to `root + path` without the leading slash; `[x](https://...)` gives an outside link; a bare `https://...` gives a link to itself, trailing `.`, `,`, `;` and `)` left outside.

- [ ] **Step 1: Write the failing tests** in `tests/test_texts.py`:
  - `test_header_and_heading`: `parse(HEAD + "## 1. Introduction\n\nText.\n")` gives `meta["short"] == "Offshoring the Mind"` and html containing `<h2 id="1-introduction">1. Introduction</h2>` and `<p>Text.</p>`.
  - `test_inline_marks_and_links`: `inline("**Short answer.** The *order* of use, see https://doi.org/10.1016/S2468-1253(25)00133-5.", "../../")` contains `<strong>Short answer.</strong>`, `<em>order</em>`, `<a href="https://doi.org/10.1016/S2468-1253(25)00133-5">https://doi.org/10.1016/S2468-1253(25)00133-5</a>.`; `inline("[Offshoring the Mind](/essays/offshoring-the-mind/)", "../../")` gives `href="../../essays/offshoring-the-mind/"`; `inline("a < b & c", "")` gives `a &lt; b &amp; c`.
  - `test_lists`: `- a\n- b` gives `<ul><li>a</li><li>b</li></ul>`; `3. x\n4. y` gives `<ol start="3">`.
  - `test_table`: a 2-column table gives one `<th scope="col">` per header cell, `role="region"`, `tabindex="0"`, `aria-label="Table 1"`.
  - `test_slips_stop_the_build`: each of an unclosed `**`, a row with 3 cells in a 2-column table, a `> quote` line, a missing header key raises `TextError` whose message starts with the right `line N:`.
- [ ] **Step 2:** `pytest tests/test_texts.py -q`; Expected: fails (no module `texts`).
- [ ] **Step 3:** Implement `texts.py`.
- [ ] **Step 4:** `pytest tests/test_texts.py -q`; Expected: all pass.
- [ ] **Step 5:** Commit `texts.py tests/test_texts.py`: "A text format for essays and papers: a header and a small Markdown subset, refusing anything else".

### Task 2: The four sources and the word check

**Files:** Create `texts/offshoring-the-mind.md`, `texts/measuring-cognitive-hollowing.md`, `texts/measuring-siege-mentality-in-ai.md`, `texts/labeling-claims-by-kind-of-support.md`, the four PDFs beside them (copied from the 4:02 PM Downloads versions; SHA-256 recorded in the ledger), `tools/check_text.py`.

**Interfaces:**
- Consumes: Task 1's format.
- Produces: header values used by Task 3: `place` (`s-warfare` for the essay, `research` for the papers), `short`, `summary` (the abstract's first sentence; for the method note, its sentence beginning "This note sets out"), `date: November 2026`, `published: 2026-11-27`.
- `tools/check_text.py PDF HTML [--allow OLD=NEW]...` prints every word-level difference between the PDF text (pdftotext; the running header lines at the top of each page after the first and the page number at the end of each page dropped; NFKC) and the words inside `<article class="text">` minus elements marked `data-added`; exit 0 only when every difference is allowed.

- [ ] **Step 1:** Write each source from pdftotext's words (never retyped), restoring the real hyphens pdftotext joins at line ends (found by listing every line-end hyphen in the PDF), tables rebuilt from the page images, bold and italic from the page images, references' addresses as bare `https://` links, and cross-references linked: Potvin (2026) to `/essays/offshoring-the-mind/`, 2026a, b, c to the three papers.
- [ ] **Step 2:** Write `tools/check_text.py`.
- [ ] **Step 3:** After Task 3 builds the pages, run it on each pair. Expected: no differences, except `analyzes=analyses` for the siege paper.
- [ ] **Step 4:** Commit the sources, PDFs and tool: "The essay and three papers as sources, with a tool that checks a page's words against its PDF".

### Task 3: The pages, the room list and the Papers list (`build.py`)

**Files:** Modify `build.py` (`social`, `page`, `room`, the Papers block, writers, `ADDRESSES`), `site-text.txt` (`[writing note]`), `tests/test_build.py`.

**Interfaces:**
- Consumes: `texts.parse`, the headers from Task 2.
- Produces: `site/essays/offshoring-the-mind/index.html` and `.pdf`, `site/research/<slug>/index.html` and `.pdf` for the three papers; `page(..., description=None, og_type="website")`; `social(title, url, description=None, og_type="website")`.
- Page body: `<article class="text">` holding `<p class="text-place" data-added>` (link back to the room, or to `#research`), `<h1>`, `Jak Potvin`, the ORCID line through `sitetext.inline` (icon and rel=me), the kind line, a `<p class="text-pdf small" data-added>` PDF link, then the body. Menu current item: `writing` for the essay, `research` for papers. Head: description = summary; canonical = page address; `og:type` `article`; JSON-LD `Article` (essay) or `ScholarlyArticle` (papers) with `headline`, `author` (Person, name, url, sameAs [orcid]), `datePublished`, `url`.

- [ ] **Step 1: Write the failing tests** in `tests/test_build.py`:
  - `test_text_pages_are_written_with_their_pdfs`: for the four addresses, `index.html` exists, holds `<h1>` with the full title, the kind line, the ORCID link with `rel="me"`, and the PDF beside it is byte-identical to `texts/<slug>.pdf`.
  - `test_text_pages_tell_search_engines_what_they_are`: each head has its own `<meta name="description" content="` + summary, `<link rel="canonical" href="https://jakpotvin.com/<folder>/<slug>/">`, `og:type` `article`, a JSON-LD `datePublished` of `2026-11-27`; `sitemap.xml` lists all four addresses.
  - `test_every_link_on_a_text_page_resolves`: every relative `href` and `src` on the four pages names a file the build wrote (Review Focus 5).
  - `test_the_war_room_lists_its_essay`: the `#s-warfare` room has `<ul class="room-essays">` with a link to `essays/offshoring-the-mind/`, the summary and `November 2026`, and no `Coming soon`; the other nine rooms still say `Coming soon`.
  - `test_papers_lists_the_three_texts_first`: in `.research-papers`, the titles appear in the order hollowing, siege, labeling, then Study 2A, each new one linking to its page and its PDF.
  - `test_writing_note`: the home page says `More essays are coming soon.`
- [ ] **Step 2:** `pytest tests/test_build.py -q -k "text_ or war_room_lists or papers_lists or writing_note"`; Expected: fail.
- [ ] **Step 3:** Implement in `build.py` and `site-text.txt`.
- [ ] **Step 4:** Same command; Expected: pass. Then `tools/check_text.py` on all four (Task 2 Step 3).
- [ ] **Step 5:** Commit `build.py site-text.txt tests/test_build.py` and the written `site/` files by name: "Essay and paper pages: the essay in the war room, three papers in Research, each with its PDF".

### Task 4: How the pages look (`site.css`)

**Files:** Modify `site/assets/site.css`, `tests/test_home_browser.py` (or a new `tests/test_text_pages_browser.py`).

- [ ] **Step 1: Write the failing browser tests:**
  - `test_text_pages_fit_a_small_phone` (320 x 640, each page): `document.documentElement.scrollWidth <= innerWidth` (Review Focus 1).
  - `test_wide_tables_scroll_in_their_own_box` (320 x 640, essay): every `.table` has `scrollWidth > clientWidth` or fits, has `tabindex="0"`, `role="region"` and an `aria-label` (Review Focus 2).
  - `test_text_pages_read_without_javascript`: with JavaScript off the essay's `h1` and its first table are visible.
  - The existing room contrast test's selector list gains `.room-essays a` and `.room-essays .d` (Review Focus 4).
- [ ] **Step 2:** Run them; Expected: the phone and table tests fail before the CSS (the tables widen the page).
- [ ] **Step 3:** CSS: a reading column of about 68ch; `h1` `clamp(32px, 4.4vw, 52px)`; section `h2` `clamp(24px, 2.6vw, 32px)`; `.table` `overflow-x: auto` with a hairline border and small sans cells; references wrap anywhere; `.room-essays` in the room's light-on-dark colours.
- [ ] **Step 4:** Run the browser tests; Expected: pass. Screenshots of each page at desktop and phone width compared by eye with the PDF pages for bold, italic and tables.
- [ ] **Step 5:** Commit `site/assets/site.css` and the tests: "Essay and paper pages: a reading column, tables that scroll in their own box".

### Task 5: Documentation and the whole-branch check

- [ ] README: how to add an essay or a paper (source, PDF, header keys, the word check).
- [ ] Full suite green; private-name scan over the folder and every unpushed commit; long-dash check over the new files.
- [ ] Final review of the whole branch by a fresh reviewer; fix Critical and Important findings with a failing test first.
- [ ] Commit "README: adding an essay or a paper". Show Jak the preview; no push without his "push".
