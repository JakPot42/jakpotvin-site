# jakpotvin.com

Jak Potvin's personal site. Static HTML, no framework, served from the `site/` folder.

## Layout

```
build.py            writes the HTML pages in site/ from the lists inside it
data/counts.json    mechdb export (format mechdb-counts-2) used for the chart on the atoms page
data/calculator.html  the Atom Factory Calculator, copied to site/atoms/calculator/ with a back link
site/               the published site
  index.html        home: the album, the ten subject rooms, projects, contact
  plates.html       list of plates: full picture credits
  atoms/index.html  the atoms project page
  atoms/calculator/ the calculator
  assets/site.css   all styles
  assets/img/       the plates (these are source files; build.py reads their sizes)
  assets/fonts/     the fonts, served from the site itself (woff2, Latin subsets from Google Fonts),
                    fonts.css with their @font-face rules, each family's OFL licence, SOURCES.txt
  CNAME             jakpotvin.com
  favicon.svg, favicon.ico
  .nojekyll
```

## Build

```
pip install pillow
python build.py data/counts.json data/calculator.html
```

The build overwrites `site/index.html`, `site/plates.html`, `site/atoms/index.html` and `site/atoms/calculator/index.html`. A build with no changes to `build.py`, `data/` or `site/assets/` produces identical files.

## How the home page works

- **Album.** `PLATES` in `build.py` lists every picture in date order of what it shows. Plate numbers (I, II, III...) follow that order and are assigned by the build, so adding or removing a plate renumbers everything, including captions, room labels and the list of plates. The build lays the plates out in four columns, each plate going to the shortest column. As the visitor scrolls, the plates drop into their frames oldest first; a reader set to reduced motion sees the finished album.
- **Rooms.** `SUBJECTS` lists the ten writing subjects in order. Each plate's anchor (for example `#s-politics`) puts it in that subject's room. `ROOM_BG` sets each room's wall colour, picked from its painting. The page background fades between room colours on scroll.
- **Short captions** come from `SHORT_BY_FILE`; full credits from the plate's credit field, plus `NOTE_BY_FILE`, appear on `plates.html`.

### Adding a plate

1. Put the image in `site/assets/img/` (JPEG, about 1,200 to 2,000 pixels on the long side).
2. Add a tuple to `PLATES` at its place in date order. Leave the number empty (`""`); the build fills it in.
3. Add its short caption to `SHORT_BY_FILE`, and a note to `NOTE_BY_FILE` if the licence asks for one.
4. Rebuild and look at the album, the room and `plates.html`.

A plate whose image file is missing is skipped, not an error.

## Before launch (15 December)

- Contact email address (Contact section; currently "Email address to come").
- The first essays, and a page format for them.
- Links for the bottleneck map and mechdb, both currently "Published 15 December".
- Remove the preview banner: the `DRAFT` constant in `build.py`.
- Image sources to confirm. Paintings and drawings are faithful reproductions of public-domain works; photographs are credited on `plates.html`. These files came from copies Jak saved, so confirm the source and whether a photographer credit is wanted: Vitruvian Man (possibly Luc Viatour's photograph on Wikimedia Commons), School of Athens, Coronation of Charlemagne, Washington Crossing the Delaware, Napoleon Crossing the Alps (a small copy; a larger one would be better).
- On launch day, recheck the facts about other people's work against their sources: on the atoms page, that the three preprints are from CBN Nano Technologies, that none is peer reviewed, and that none has been repeated by a second lab.
- Optional: a larger ENIAC scan (the current file is 630 pixels wide).
- Waiting on one image: Botticelli, Saint Augustine in His Study (save as `site/assets/img/botticelli-augustine.jpg`, about 1,800 pixels tall). Its plate is already in `PLATES`; it appears once the file is there.

## Rules for this site

- Run the private-name scan over the whole folder and its history before any push.
- Every picture is public domain or credited under its licence. No stock-agency copies.
