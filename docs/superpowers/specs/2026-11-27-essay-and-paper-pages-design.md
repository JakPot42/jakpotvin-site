# Essay and paper pages: design

Approved by Jak on 27 November 2026, in answers to three questions: "Web page + PDF" for the essay, "Web page + PDF each" for the three Research papers, "No, use the PDF" (he has no Markdown source), "Universal Inquiry" may be published, and the siege paper's page says "analyses" where the PDF says "analyzes".

## Intent

Jak's first essay and his first three research write-ups go on the site. They must read well on a phone, be found by search engines, and match the rest of the site, while staying word for word what he wrote. The PDF he made stays available for anyone who wants the typeset copy or wants to cite it.

## The four texts (final versions: Downloads, 27 Nov 2026, 4:02 PM)

| Text | Kind (as the PDF says) | Where it goes | Address |
|---|---|---|---|
| Offshoring the Mind: AI Dependence, Lost Capability and the Risk of a Cold Standoff Between Humans and AI | Version 1.0, November 2026 | War, strategy and defense room | /essays/offshoring-the-mind/ |
| Measuring Cognitive Hollowing: A Study Design for Unassisted Skill After AI Adoption | Research proposal, version 1.0, November 2026 | Research, Papers | /research/measuring-cognitive-hollowing/ |
| Measuring Siege Mentality in AI Systems: A Calibration-Based Test | Research proposal, version 1.0, November 2026 | Research, Papers | /research/measuring-siege-mentality-in-ai/ |
| Labeling Claims by Kind of Support: A Claim Table for Philosophical Writing | Method note, version 1.0, November 2026 | Research, Papers | /research/labeling-claims-by-kind-of-support/ |

Each folder also serves the PDF under its own file name, for example /essays/offshoring-the-mind/offshoring-the-mind.pdf.

## Goals

- Every word as in the PDF, with one approved change ("analyses"). Checked by script: the page's words against pdftotext's words, in order for running text and as a count of every word overall, with each difference explained.
- Bold and italic as in the PDF. pypdf mislabels fonts where the style changes, so emphasis is applied from the page images and checked against them by eye.
- Tables as real tables. On a narrow screen a table scrolls sideways inside its own box; the page itself never scrolls sideways.
- Addresses and DOIs printed in the references become links. References to each other (Potvin 2026, 2026a, 2026b, 2026c) link the title to that text's page. No other wording changes.
- Works without JavaScript; light and dark colours; the same menu, footer and same-person (rel=me) line as every page.
- Search engines: each page has its own description (the abstract's first sentence), its own canonical address and link preview title, an Article record naming Jak with his ORCID, and a line in the sitemap.

## Non-goals

- No rewriting, summarising or shortening of Jak's text on these pages.
- No new fonts, no JavaScript, no comment system, no table of contents (later, if he wants one).
- Research's existing Study 2A entry is unchanged.

## Anti-goals

- A page that differs from the PDF in any word other than the approved one.
- A page that scrolls sideways on a phone.
- Anything about the startup (the private-name scan runs over every new file).

## How it is built

- Each text is a source file Jak can read and edit: `texts/<slug>.md`, a small Markdown subset with a header block (title, kind line, where it goes, summary line, PDF name). The PDF sits next to it as `texts/<slug>.pdf`.
- `texts.py` turns the subset into HTML: headings, paragraphs, bold, italic, links, bullet and numbered lists, pipe tables. Anything else in a source file stops the build with the line number, so nothing is silently dropped.
- `build.py` writes one page per text with the shared `page()` template, copies its PDF beside it, and adds the address to the sitemap.
- The War, strategy and defense room lists the essay under its heading in place of "Coming soon": the short title as a link, the abstract's first sentence, and "November 2026". Rooms without an essay still say "Coming soon".
- Research's Papers list gains the three papers above Study 2A, newest first and, among equals, the two proposals before the method note: title (link to the page), the kind line, a summary sentence from the abstract, and a PDF link.
- `[writing note]` changes from "The first essays are coming soon." to "More essays are coming soon." (Claude's call, as it would otherwise be untrue once an essay is up.)

## Approaches considered

1. Web page plus PDF (chosen by Jak): readable on phones, indexed, linkable; costs a careful conversion and a word-by-word check.
2. PDF only: exact and quick, but poor on phones and unlike the site.

## Left to the builder

The exact CSS of the reading column, the table box and the reference list; how the abstract block is set off; the order of head tags.
