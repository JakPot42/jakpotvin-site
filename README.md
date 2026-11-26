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
images.py           writes the small and blurred copies of each plate for build.py
tools/browser.py    drives headless Microsoft Edge for the browser tests
tests/              the tests (python -m pytest)
site/               the published site
  index.html        home: the first screen, the album, the ten subject rooms, projects, contact
  plates.html       list of plates: full picture credits
  atoms/index.html  the atoms project page
  atoms/calculator/ the calculator
  assets/site.css   all styles
  assets/home.js    the home page's slideshow, shrink, album caption, project reveal and rooms
  assets/img/       the plates (these are source files; build.py reads their sizes)
  assets/img/small/ and assets/img/blur/  copies of each plate written by the build (images.py); do not edit
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

Tests: `pip install pytest`, then `python -m pytest` (the browser tests need Microsoft Edge).

The build overwrites `site/index.html`, `site/plates.html`, `site/atoms/index.html` and `site/atoms/calculator/index.html`. A build with no changes to `build.py`, `data/` or `site/assets/` produces identical files.

## Editing the words

The words on the home page, the description search engines show, and the footer are in `site-text.txt`.

1. Open `site-text.txt` in Notepad.
2. Change the words under the `[section]` lines. Keep the `[section]` lines as they are. Lines starting with `#` are notes and never appear on the site.
3. Save, then ask Claude to push. Claude rebuilds the pages, runs the tests and the private-name scan, and pushes.

If something in the file is wrong (a section renamed, a long dash), the build stops with one sentence saying which line to fix.

## How the home page works

- **First screen.** One plate at a time fills the screen behind the name, tagline and bio, oldest first, about 5 seconds each with a slow zoom and a crossfade, with the plate's year, event and credit in the corner. A pause button stops it; it also stops while the tab is hidden and once the visitor scrolls. Plates that are tall, square or too small to fill the screen sharply (`images.show_whole`) are shown whole on the right, over a blurred copy of themselves. Only the current and the next image are loaded. The behaviour is in `site/assets/home.js`.
- **Album.** `PLATES` in `build.py` lists every picture in date order of what it shows. Plate numbers (I, II, III...) follow that order and are assigned by the build, so adding or removing a plate renumbers everything, including captions, room labels and the list of plates. The build lays the plates out in four columns, each plate going to the shortest column, using the small copies in `assets/img/small/`. On desktop, in browsers with scroll-driven animations, scrolling off the first screen shrinks the painting into its own frame in the album while the other plates settle in around it. Elsewhere the album simply follows the first screen. The caption line under the album names the plate pointed at, focused, or (on a phone) first tapped. On phones the album is one row you swipe sideways.
- **Rooms.** `SUBJECTS` lists the ten writing subjects in order. Each plate's anchor (for example `#s-politics`) puts it in that subject's room. `ROOM_BG` sets each room's wall colour, picked from its painting. The page background fades between room colours on scroll. On desktop the room's plates stay pinned on the right while the room names scroll past on the left.
- **Projects.** The items rise into place once as they come into view, and the project count (`[projects count]` in `site-text.txt`) counts up from zero.
- **Reduced motion.** A visitor whose device asks for less motion sees the first plate held still, the album finished, and everything else in place.
- **Short captions** come from `SHORT_BY_FILE`; full credits from the plate's credit field, plus `NOTE_BY_FILE`, appear on `plates.html`.

### Adding a plate

1. Put the image in `site/assets/img/` (JPEG, about 1,200 to 2,000 pixels on the long side).
2. Add a tuple to `PLATES` at its place in date order. Leave the number empty (`""`); the build fills it in.
3. Add its short caption to `SHORT_BY_FILE`, and a note to `NOTE_BY_FILE` if the licence asks for one.
4. Rebuild and look at the album, the room and `plates.html`.

A plate whose image file is missing is skipped, not an error.

## Before launch (15 December)

- The first essays, and a page format for them.
- Links for the bottleneck map and mechdb, both currently "Published 15 December".
- Image sources to confirm. Paintings and drawings are faithful reproductions of public-domain works; photographs are credited on `plates.html`. These files came from copies Jak saved, so confirm the source and whether a photographer credit is wanted: Vitruvian Man (possibly Luc Viatour's photograph on Wikimedia Commons), School of Athens, Coronation of Charlemagne, Washington Crossing the Delaware, Napoleon Crossing the Alps (a small copy; a larger one would be better).
- On launch day, recheck the facts about other people's work against their sources: on the atoms page, that the three preprints are from CBN Nano Technologies, that none is peer reviewed, and that none has been repeated by a second lab.
- Optional: a larger ENIAC scan (the current file is 630 pixels wide).

## Rules for this site

- Run the private-name scan over the whole folder and its history before any push.
- Every picture is public domain or credited under its licence. No stock-agency copies.
