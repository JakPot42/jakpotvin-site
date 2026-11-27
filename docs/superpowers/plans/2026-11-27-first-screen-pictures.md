# The first screen's pictures: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** the first screen shows Washington, then four more pictures from history, changing every 4 seconds, with the rooms' pause button.

**Architecture:** `build.py` gains `BANNER_FILES` (Washington first) and writes one slide per banner picture (the first eager, the rest lazy). `home.js` treats the first screen as one more room with its own interval and one-ahead loading, so one pause state and one set of rules hold everything.

**Tech stack:** Python build (`build.py`, Pillow), plain JavaScript (`home.js`), CSS, pytest with headless Edge (`tools/browser.py`).

**Spec:** `docs/superpowers/specs/2026-11-27-first-screen-pictures-design.md`

## Global constraints

- No long dashes in site text, code comments shown on the site, or commit messages; no 19xx/20xx tokens in commit messages.
- Pictures at most 1,250,000 bytes, progressive sRGB, at least 1,600 px wide (the existing size tests).
- Text 4.5 to 1 over every picture, the pause icon 3 to 1 (`tools/contrast.py`).
- The site copies are already made (`site/assets/img/gaspee-burning.jpg`, `constitution-guerriere.jpg`, `wright-first-flight.jpg`, `earthrise-apollo8.jpg`).

## Review focus

1. A slow connection: the next picture is still loading when its turn comes. Expected: the first screen waits, never shows a blank.
2. A visitor who scrolls straight past the first screen: no more than one picture ahead is fetched.
3. Pause on the first screen, then scroll to a room: the room is held too (one state), and play on either button restarts both.
4. A phone, a short laptop window, a phone turned sideways: the pause button never covers the name, the words or the caption.
5. The link-preview card and the page without JavaScript still show Washington alone.

---

### Task 1: the pictures and the markup

**Files:** modify `build.py`; test `tests/test_build.py`.

**Interfaces:** produces `BANNER_FILES` (list of file names, Washington first) and, in `index.html`, `.intro .slides` holding one `figure.slide` per banner picture in that order: the first `class="slide on"` with `src` and `fetchpriority="high"`, the others with `data-src` only, each with `data-yr`, `data-what`, `data-credit`.

- [ ] Write the failing tests: `test_banner_pictures_in_order_washington_first` (slide files in `.intro` equal `BANNER_FILES`; the first has `src` and is `on`; the others have `data-src` and no `src`), `test_banner_pictures_belong_to_no_room` (no banner file inside any `<section class="room"`), `test_banner_pictures_are_credited` (plates.html names Brownell, Birch, Daniels and Anders with the credits in the spec).
- [ ] Run them: they fail (one slide, no new plates).
- [ ] Add the four `PLATES` entries by date (subject and anchor empty), their `SHORT_BY_FILE` names, `BANNER_FILES`, and build the banner slides from it; rooms leave out every banner file.
- [ ] Run them and `tests/test_build.py`: pass.
- [ ] Commit.

### Task 2: the motion, the pause button and the readability

**Files:** modify `site/assets/home.js`, `site/assets/site.css`, `README.md`; test `tests/test_home_browser.py`.

**Interfaces:** consumes Task 1's slides. Produces `BANNER_EVERY = 4000` in `home.js`; the first screen gets the same `button.pause` as the rooms, appended to `.hero`.

- [ ] Write the failing tests: `test_banner_changes_every_four_seconds` (desktop and phone: the shown picture moves on about every 4 s and the caption matches it), `test_banner_loads_one_picture_ahead` (after load only the first two have `src`; after a change, the third), `test_one_pause_holds_the_banner_and_the_rooms`, `test_less_motion_starts_the_banner_paused`, the banner in the pause-clear-of-the-words sizes, and readability over every banner picture. The old `test_banner_is_one_still_painting` is replaced.
- [ ] Run them: they fail.
- [ ] `home.js`: the intro joins the rooms list with its interval and one-ahead loading; `site.css`: the banner pause position on laptops, phones and short screens, the caption narrowed beside it.
- [ ] Run them, then the whole suite: pass. Fix any picture that fails readability with its focal point or the shade.
- [ ] README: the first screen's paragraph; commit.
