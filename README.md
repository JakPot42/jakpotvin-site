# jakpotvin.com

Jak Potvin's personal site. Static HTML, no framework, served from the `site/` folder.

## Layout

```
build.py            writes the HTML pages in site/ from the lists inside it and the words in site-text.txt
site-text.txt       the words on the home page, the page description and the footer: edit these in Notepad
sitetext.py         reads and checks site-text.txt for build.py
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

Rebuild after editing `site.css`, `home.js` or `fonts.css` too: the pages ask for those files by an address with `?v=` and a fingerprint of the file (`asset_v` in `build.py`), so a browser never runs a new page with an old copy it kept. GitHub Pages lets browsers keep files for 10 minutes.

Tests: `pip install pytest`, then `python -m pytest` (the browser tests need Microsoft Edge).

The build overwrites `site/index.html`, `site/plates.html`, `site/atoms/index.html` and `site/atoms/calculator/index.html`. A build with no changes to `build.py`, `data/` or `site/assets/` produces identical files.

## Editing the words

The words on the home page, the description search engines show, and the footer are in `site-text.txt`.

1. Open `site-text.txt` in Notepad.
2. Change the words under the `[section]` lines. Keep the `[section]` lines as they are. Lines starting with `#` are notes and never appear on the site.
3. Save, then ask Claude to push. Claude rebuilds the pages, runs the tests and the private-name scan, and pushes.

If something in the file is wrong (a section renamed, a long dash), the build stops with one sentence saying which line to fix.

## How the home page works

- **First screen.** One still painting, Washington Crossing the Delaware (`BANNER_FILE` in `build.py`), fills the screen behind the name, tagline and bio, with its year, event, a link to the War and defense room and its credit in the corner. There is no slideshow; the first screen needs no script.
- **Plates.** `PLATES` in `build.py` lists every picture in date order of what it shows. The banner painting (`BANNER_FILE`) is the first screen, credited and captioned but in no room; each other painting is a background in its subject's room. The site shows no plate numbers; the build still numbers the plates internally (I, II, III...) to key captions and credits. Scrolling off the first screen goes straight into Writing.
- **Rooms.** `SUBJECTS` lists the ten writing subjects in order. Each plate's anchor (for example `#s-politics`) puts it in that subject's room. Each room is one screen tall. Its paintings fill the screen behind the title, one at a time, with a caption naming the one showing. While at least half of the room is on screen, the painting changes every 6 seconds and loops (`EVERY` in `home.js`); it stops when the visitor scrolls away or switches tabs, and picks up where it stopped. A painting still loading is waited for; one that failed to load is skipped. Each room has a pause button, and pressing any of them holds or restarts every room. Screen readers are not told each time a painting changes. Every painting fills the screen on phones and laptops, tall ones too, cropped around its focal point (the last field of its `PLATES` tuple). A room's paintings load only when the visitor is within a screen of it, after the banner has loaded. Without JavaScript each room shows its first painting (a `<noscript>` copy) and nothing changes.
- **Featured projects.** Lines under `[featured projects]` in `site-text.txt` (one per project: `- [name](address) | one line`) show as a list under the atoms part, headed by `[featured heading]`. With no lines there, nothing about it appears. Check each link before a push.
- **Projects.** The items rise into place once as they come into view, and the project count (`[projects count]` in `site-text.txt`) counts up from zero.
- **Reduced motion.** Nothing on the first screen moves for anyone. A visitor whose device asks for less motion sees the projects in place, and the rooms start paused; pressing play starts them, and the paintings then change without the fade.
- **Short captions** come from `SHORT_BY_FILE`; full credits from the plate's credit field, plus `NOTE_BY_FILE`, appear on `plates.html`.

## Link previews and search engines

- **Link previews.** Every page carries its address (`canonical`) and the tags that texts, LinkedIn, Slack and the like read to show a card: the page's title, `[page description]` from `site-text.txt`, and `assets/card.jpg`. The build draws the card from the banner painting, darkened at the left and at the bottom, with `[name]` and the site address. `SITE_URL` in `build.py` holds the address.
- **Who the site belongs to.** The home page tells search engines, in a form they read, the name, the address and the https links in `[contact line]` (the GitHub link today; never the email).
- **Sitemap.** `sitemap.xml` lists the four pages; `robots.txt` points to it. A new page needs its address added to `ADDRESSES` in `build.py`.
- **Google Search Console** (Jak's step, after the push that publishes these files): sign in at search.google.com/search-console, add jakpotvin.com as a Domain property, and copy the TXT record Google shows. Adding it in Cloudflare is the one DNS change this needs; Claude enters it only when Jak asks for that record. Once Google says verified, submit `https://jakpotvin.com/sitemap.xml` under Sitemaps.

### Adding a plate

1. Put the image in `site/assets/img/` (progressive JPEG in sRGB, at least 1,600 pixels wide so it can fill a screen: a tall painting 1,920 wide where its source allows, a wide one about 2,000; at most 1,250,000 bytes).
2. Add a tuple to `PLATES` at its place in date order. Leave the number empty (`""`); the build fills it in.
3. Add its short caption to `SHORT_BY_FILE`, and a note to `NOTE_BY_FILE` if the licence asks for one.
4. Rebuild and look at the first screen, the room and `plates.html`.

A plate whose image file is missing is skipped, not an error.

## Before launch

- The first essays, and a page format for them.
- Links for the bottleneck map and mechdb, both currently "Coming soon".
- On launch day, recheck the facts about other people's work against their sources: on the atoms page, that the three preprints are from CBN Nano Technologies, that none is peer reviewed, and that none has been repeated by a second lab.

## Rules for this site

- Run the private-name scan over the whole folder and its history before any push.
- Every picture is public domain or credited under its licence, with the licence linked on `plates.html`. No stock-agency copies. On 26 November 2026 the pictures that came from copies Jak saved were replaced with Wikimedia Commons files whose licences were checked, or taken out. Later that day Rembrandt's Anatomy Lesson of Dr Tulp and Goya's Madhouse (dated by the Real Academia de San Fernando, c. 1814 to 1816) replaced Vitruvian Man and the Sleep of Reason etching, which could not fill a laptop screen.
