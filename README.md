# jakpotvin.com

Jak Potvin's personal site. Static HTML, no framework, served from the `site/` folder.

## Layout

```
build.py            writes the HTML pages in site/ from the lists inside it and the words in site-text.txt
site-text.txt       the words on the home page, the page description and the footer: edit these in Notepad
sitetext.py         reads and checks site-text.txt for build.py
texts/              each essay and paper: its PDF and its words (<name>.md), made into a page by build.py
texts.py            reads and checks a texts/ source for build.py
tools/check_text.py checks that an essay or paper page says what its PDF says (see Adding an essay or a paper)
data/counts.json    mechdb export (format mechdb-counts-2) used for the chart on the atoms page
data/calculator.html  the Atom Factory Calculator, copied to site/atoms/calculator/ with a back link
.github/workflows/pages.yml  publishes site/ to GitHub Pages on every push to main (it does not run build.py)
images.py           writes the blurred copy of each plate for build.py
tools/browser.py    drives headless Microsoft Edge for the browser tests
tests/              the tests (python -m pytest)
site/               the published site
  index.html        home: the first screen, the ten subject rooms, projects, contact
  plates.html       picture credits: the full credit for every picture
  404.html          the page GitHub Pages shows for an address that does not exist (every link in it starts with /)
  robots.txt, sitemap.xml  tell search engines the site's pages (the list is ADDRESSES in build.py)
  atoms/index.html  the atoms project page
  atoms/calculator/ the calculator
  assets/site.css   all styles
  assets/home.js    the home page's project reveal, and the rooms' changing paintings and pause buttons
  assets/card.jpg   the link preview picture (1200 by 630), written by the build; do not edit
  assets/orcid-id.svg  ORCID's green iD icon, ORCID's own file (orcid.org/assets/vectors/orcid.logo.icon.svg); never edit it
  assets/img/       the plates (these are source files; build.py reads their sizes)
  assets/img/blur/  a blurred copy of each plate, written by the build (images.py); do not edit
  assets/fonts/     the fonts, served from the site itself (woff2: IBM Plex from IBM's own release,
                    the others Latin subsets from Google Fonts), fonts.css with their @font-face rules,
                    each family's OFL licence, SOURCES.txt
  CNAME             jakpotvin.com
  favicon.svg, favicon.ico
  .nojekyll
```

## Build

```
pip install pillow
python build.py data/counts.json data/calculator.html
```

Two more arguments are optional, for tests: another words file in place of `site-text.txt`, then another texts folder in place of `texts/`.

Rebuild after editing `site.css`, `home.js` or `fonts.css` too: the pages ask for those files by an address with `?v=` and a fingerprint of the file (`asset_v` in `build.py`), so a browser never runs a new page with an old copy it kept. GitHub Pages lets browsers keep files for 10 minutes.

Tests: `pip install pytest`, then `python -m pytest` (the browser tests need Microsoft Edge).

The build overwrites `site/index.html`, `site/plates.html`, `site/atoms/index.html`, `site/atoms/calculator/index.html` and remakes `site/essays/` and `site/research/` from `texts/` each time: anything else put there is removed. A build with no changes to `build.py`, `data/` or `site/assets/` produces identical files.

## Editing the words

The words on the home page, the description search engines show, and the footer are in `site-text.txt`.

1. Open `site-text.txt` in Notepad.
2. Change the words under the `[section]` lines. Keep the `[section]` lines as they are. Lines starting with `#` are notes and never appear on the site.
3. Save, then ask Claude to push. Claude rebuilds the pages, runs the tests and the private-name scan, and pushes.

If something in the file is wrong (a section renamed, a long dash), the build stops with one sentence saying which line to fix.

## Adding an essay or a paper

Each essay and paper is two files in `texts/`: its PDF, as Jak made it, and a source with the same words (`texts/<name>.md`). The build gives each a page in the site's style, puts the PDF beside it, and lists it: an essay in its room, in place of "Coming soon"; a paper at the top of Research's Papers list. The page's address comes from the file name: `essays/<name>/` for an essay, `research/<name>/` for a paper.

1. Put the PDF in `texts/`.
2. Write `texts/<name>.md`. It starts with a header between two lines of `---`:
   - `title`, `short` (the title before its colon), `kind` (the version line, as the PDF has it), `date` (as the room shows it, for example November 2026), `published` (for search engines, for example 2026-11-27), `orcid`, `pdf` (the PDF's file name);
   - `place`: `research` for a paper, or the room's anchor for an essay (`s-warfare`, `s-philosophy`, and so on: `SUBJECTS` in `build.py`);
   - `summary`: one of the text's own sentences that makes sense alone. It shows in the room or the Papers list, and as the description search engines show.
3. Then the text, in the small set of marks `texts.py` describes at its top: `##` and `###` headings, paragraphs, `**bold**`, `*italic*`, lists, tables, links. Anything else stops the build with its line number.
4. Make the words from the PDF, never retyped: `pdftotext` (it comes with Git for Windows) gives the words; bold, italic and tables follow the PDF's pages.
5. Rebuild, then check the page against its PDF: `python tools/check_text.py texts/<name>.pdf site/<essays or research>/<name>/index.html --order`. It counts every word on both sides and must say "the same words", and with `--order` it checks that every paragraph, heading and list item is one run of the PDF's words, each after the one before. The tests run this check on every text.
6. A difference that is meant goes in `texts/<name>.allow`, one per line, with a `#` line saying why: `OLD=NEW` for a correction Jak approved, or for a real hyphen `pdftotext` joins at the end of a line (it reads "self-determination" split over two lines as "selfdetermination"); `order: <start of a paragraph>` for a paragraph `pdftotext` reads out of the PDF's order (check the PDF page first).

On a phone a wide table scrolls sideways in its own box; the page itself never does.

## How the home page works

- **First screen.** The pictures in `BANNER_FILES` (`build.py`) fill the screen behind the name, tagline and bio, one at a time, Washington Crossing the Delaware first and the rest by date, with each one's year, event and credit in the corner. While at least half of the first screen is on screen it changes every 4 seconds (`BANNER_EVERY` in `home.js`) and loops, with the same pause button as the rooms; one pause holds the first screen and every room. Only Washington loads with the page; once the page has loaded the second picture loads, and each change starts loading the one after, so a visitor who scrolls straight past fetches one picture more. Without JavaScript the first screen is Washington alone, and the link-preview card is drawn from Washington. To add a picture: a `PLATES` entry with an empty subject and anchor, a short name in `SHORT_BY_FILE`, and its file name in `BANNER_FILES` in the order it should show; there is no limit.
- **Plates.** `PLATES` in `build.py` lists every picture in date order of what it shows. The first screen's pictures (`BANNER_FILES`) are credited and captioned but in no room; each other painting is a background in its subject's room. The site shows no plate numbers; the build still numbers the plates internally (I, II, III...) to key captions and credits. Scrolling off the first screen goes straight into Writing.
- **Rooms.** `SUBJECTS` lists the ten writing subjects in order. Each plate's anchor (for example `#s-politics`) puts it in that subject's room. Each room is one screen tall. Its paintings fill the screen behind the title, one at a time, with a caption naming the one showing. While at least half of the room is on screen, the painting changes every 6 seconds and loops (`EVERY` in `home.js`); it stops when the visitor scrolls away or switches tabs, and picks up where it stopped. A painting still loading is waited for; one that failed to load is skipped. Each room has a pause button, and pressing any of them holds or restarts every room. Screen readers are not told each time a painting changes. Every painting fills the screen on phones and laptops, tall ones too, cropped around its focal point (the last field of its `PLATES` tuple). A room's paintings load only when the visitor is within a screen of it, after the banner has loaded. Without JavaScript each room shows its first painting (a `<noscript>` copy) and nothing changes.
- **Research.** Between the rooms and Projects, once `[research papers]` in `site-text.txt` has a paper; with none, nothing of it appears: not the section, not `Research` in the menu (the same on every page, the calculator's too), not the first screen's Research button. It opens with a screen like the rooms: three pictures by date, Joseph Wright of Derby's An Experiment on a Bird in the Air Pump (1768), Albert Edelfelt's Louis Pasteur (1885) and the Solvay Conference photograph (1927) (their `PLATES` entries have the anchor `#research`), behind the heading, `[research line]` under it (the ORCID link today) and the dated caption of the picture showing; the papers follow on the light background, under a `Papers` heading the size of the other sections' headings. Each paper is a block: a line `- ` and its title, the next line saying where it stands, then its summary, and last one line per link written `Label: [address](address)`. A paper's full text lives only here; the rooms get new writing for each field, never copies or excerpts of a paper. Check each link before a push.
- **Featured projects.** Lines under `[featured projects]` in `site-text.txt` (one per project: `- [name](address) | one line`) show as a list under the atoms part, headed by `[featured heading]`. With no lines there, nothing about it appears. Check each link before a push.
- **Projects.** The items rise into place once as they come into view, and the project count (`[projects count]` in `site-text.txt`) counts up from zero.
- **Reduced motion.** A visitor whose device asks for less motion sees the projects in place, and the first screen and the rooms start paused; pressing play starts them, and the paintings then change without the fade.
- **Short captions** come from `SHORT_BY_FILE`; full credits from the plate's credit field, plus `NOTE_BY_FILE`, appear on `plates.html`.

## Link previews and search engines

- **Link previews.** Every page carries its address (`canonical`) and the tags that texts, LinkedIn, Slack and the like read to show a card: the page's title, `[page description]` from `site-text.txt`, and `assets/card.jpg`. The build draws the card from the banner painting, darkened at the left and at the bottom, with `[name]` and the site address. `SITE_URL` in `build.py` holds the address.
- **Who the site belongs to.** The home page tells search engines, in a form they read, the name, a job title (`JOB_TITLE` in `build.py`, never shown on the page), the address and the https links in `[contact line]` (the GitHub and ORCID links today; never the email). An ORCID link also gets a `rel="me"` line in every page's head, the calculator's too, which tells search engines the site and the ORCID record are the same person.
- **ORCID links.** Any link in `site-text.txt` to an address starting `https://orcid.org/` shows ORCID's green iD icon, 16 pixels, just before the link, as ORCID's display guidelines ask (the full https address, with the icon). The icon and the link never part on a narrow screen.
- **Sitemap.** `sitemap.xml` lists the site's four pages and every essay and paper; `robots.txt` points to it. Another new page needs its address added to `ADDRESSES` in `build.py`. Each essay and paper page also has its own description (its `summary`) and tells search engines it is an article by Jak, with his ORCID.
- **Google Search Console** (Jak's step, after the push that publishes these files): sign in at search.google.com/search-console, add jakpotvin.com as a Domain property, and copy the TXT record Google shows. Adding it in Cloudflare is the one DNS change this needs; Claude enters it only when Jak asks for that record. Once Google says verified, submit `https://jakpotvin.com/sitemap.xml` under Sitemaps.

### Adding a plate

1. Put the image in `site/assets/img/` (progressive JPEG in sRGB, at least 1,600 pixels wide so it can fill a screen: a tall painting 1,920 wide where its source allows, a wide one about 2,000; at most 1,250,000 bytes).
2. Add a tuple to `PLATES` at its place in date order. Leave the number empty (`""`); the build fills it in.
3. Add its short caption to `SHORT_BY_FILE`, and a note to `NOTE_BY_FILE` if the licence asks for one.
4. Rebuild and look at the first screen, the room and `plates.html`.

A plate whose image file is missing is skipped, not an error.

## Before launch

- Links for the bottleneck map and mechdb, both currently "Coming soon".
- On launch day, recheck the facts about other people's work against their sources: on the atoms page, that the three preprints are from CBN Nano Technologies, that none is peer reviewed, and that none has been repeated by a second lab.

## Rules for this site

- Run the private-name scan over the whole folder and its history before any push.
- Every picture is public domain or credited under its licence, with the licence linked on `plates.html`. No stock-agency copies. On 26 November 2026 the pictures that came from copies Jak saved were replaced with Wikimedia Commons files whose licences were checked, or taken out. Later that day Rembrandt's Anatomy Lesson of Dr Tulp and Goya's Madhouse (dated by the Real Academia de San Fernando, c. 1814 to 1816) replaced Vitruvian Man and the Sleep of Reason etching, which could not fill a laptop screen.
