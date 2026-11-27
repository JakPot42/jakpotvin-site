# Rooms That Change by Themselves, Every Painting Filling the Screen: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Each room's three paintings fill the screen on every device and cross-fade by themselves every 6 seconds while the room is on screen, with a pause button; Rembrandt's Anatomy Lesson and Goya's Madhouse replace Vitruvian Man and the Sleep of Reason.

**Architecture:** build.py writes the rooms (one screen tall, every painting a full-screen slide with no "whole" layout); home.js runs one timer per room, started and stopped by an IntersectionObserver (half the room on screen), the page's visibility and one shared pause state, and adds the pause buttons. Site copies of the paintings are made once from the originals in the session scratchpad and committed, as before.

**Tech Stack:** Python 3.14 + Pillow (build.py, images.py), plain JavaScript (home.js), CSS (site.css), pytest with headless Edge over CDP (tools/browser.py), tools/contrast.py.

**Spec:** `docs/superpowers/specs/2026-11-26-rooms-autoplay-and-fill-design.md` (amends `docs/superpowers/specs/2026-11-26-banner-and-room-backgrounds-design.md`, goals 2 and 5).

## Global Constraints

- Paintings change every 6 seconds; the cross-fade stays 0.6 s; with less motion there is no fade and rooms start paused.
- The timer runs only while at least half of the room is on screen and the tab is visible; it picks up where it stopped.
- One pause button per room with two or more paintings; pressing any of them pauses or plays every room.
- Each room is one screen tall (100svh).
- Every room painting fills the screen on laptops and phones, cropped around its focal point (`pos`).
- Room painting site copies: at least 1,600 px wide (the Verne engraving's biggest scan is 1,338 wide and is the one exception); tall paintings 1,920 wide where the source allows; new wide paintings 2,000 wide; progressive JPEG, sRGB, no metadata, each file at most 1,250,000 bytes.
- Every line of room text measures at least 4.5 to 1 over every painting on laptops and phones; the pause icon at least 3 to 1.
- No em or en dashes in the site or in commit messages; no 19xx/20xx numbers in commit messages; LF line endings; a second build changes nothing.
- Screen readers are not told when a painting changes (the caption is not a live region).
- Nothing is pushed without Jak's "push"; commits by the noreply author already in the repo config; stage files by name.

## Review Focus

1. **A slow connection:** the next painting is still downloading when the timer fires. Expected: the room waits for a later tick and never fades in a half-drawn painting. (No test: the test server cannot slow one request.)
2. **The tab hidden and shown again.** Expected: no change while hidden, no burst of catch-up changes on return. Test: `test_hidden_tab_holds_the_rooms` (Task 2).
3. **A keyboard visitor.** Expected: each pause button is a real, named, focusable button outside the hidden painting layer. Test: `test_pause_button_is_a_named_button_clear_of_the_words` (Task 2).
4. **A room less than half on screen** (between two rooms, a short window). Expected: it does not change unseen. Test: `test_room_waits_while_off_screen` (Task 2).
5. **Coming back to a room again and again.** Expected: one timer, never several stacked ones. Test: `test_coming_back_does_not_speed_up_a_room` (Task 2).

---

### Task 1: The paintings: two swaps, bigger copies, every one filling the screen

**Files:**
- Modify: `build.py` (PLATES, SHORT_BY_FILE, slide(), room())
- Modify: `site/assets/site.css` (rooms: no "whole" layout)
- Create: `site/assets/img/rembrandt-anatomy-lesson.jpg`, `site/assets/img/goya-madhouse.jpg`
- Replace: the 11 tall room paintings' site copies (all but Verne)
- Delete: `site/assets/img/vitruvian-man.jpg`, `site/assets/img/goya-sleep-of-reason.jpg` (their blur copies go with the next build)
- Test: `tests/test_build.py`, `tests/test_home_browser.py`
- Modify: `README.md` (picture notes, "Adding a plate" sizes)

**Interfaces:**
- Produces: `slide(p, on=False, eager=False, fill=False)`: with `fill=True` the figure never has the `whole` class or a `.bg` image. `room()` calls it with `fill=True`. The banner keeps `slide(BANNER, on=True, eager=True)`.
- Produces (tests): `set_painting(page, rid, k)` in tests/test_home_browser.py: shows painting k of room rid by switching the `on` class and filling the caption from the slide's data, then waits for it to load. Task 2's tests and the readability test use it.

- [ ] **Step 1: Write the failing build tests**

In tests/test_build.py:
- `ROOM_PAINTINGS["s-biology"] = ["rembrandt-anatomy-lesson.jpg", "jenner-hillemacher.jpg", "sars-cov-2.jpg"]` and `ROOM_PAINTINGS["s-psychology"] = ["bosch-cure-of-folly.jpg", "goya-madhouse.jpg", "freud-halberstadt.jpg"]`.
- `TAKEN_OUT` gains `"vitruvian-man.jpg"` and `"goya-sleep-of-reason.jpg"`.
- `test_room_paintings_are_big_enough_to_fill_a_screen`: every room painting `width >= 1600`, except `verne-earth-to-moon.jpg` (`>= 1338`); every tall one (`height > width`) `width >= 1900` unless it is Verne or `botticelli-augustine.jpg` (source 1,775 wide: `>= 1775`); new test `test_site_pictures_stay_light`: every file in `site/assets/img/*.jpg` is at most 1,250,000 bytes.
- In the rooms markup test: no room section contains ` whole` in a figure class or `class="bg"`.
- `test_picture_credits_page_keeps_every_credit` also needs `"Rembrandt van Rijn, The Anatomy Lesson of Dr Nicolaes Tulp, 1632"` and `"Francisco Goya, The Madhouse"`.

- [ ] **Step 2: Run them, expect FAIL**

Run: `python -m pytest tests/test_build.py -q`
Expected: the room list, taken-out, size, whole/bg and credit tests fail.

- [ ] **Step 3: Write the failing browser test**

Add `set_painting(page, rid, k)` and rewrite `test_every_room_painting_fills_the_screen` (DESKTOP, PHONE): for every room and k in 0..2, `set_painting`, then the `.art` of `.slide.on` covers the viewport (`left <= 0`, `top <= 0`, `right >= width - 1`, `bottom >= height - 1`) with `object-fit: cover`, and the room has no `.bg`.

Run: `python -m pytest tests/test_home_browser.py -q -k fills_the_screen`
Expected: desktop FAIL (tall paintings are shown whole beside the title), phone may pass.

- [ ] **Step 4: Make the site copies**

From the originals in the scratchpad (`dl/*/source.*`, `botticelli-orig/00.jpg`, `napoleon-orig/belvedere.jpg`), with ICC profiles converted to sRGB and no metadata, progressive JPEG, quality 80 (step down to no lower than 72 if a file passes 1,250,000 bytes):
- Tall paintings at 1,920 wide (Botticelli at its full 1,775): Wanderer, Bosch, Massys, Adam Smith (from the new cropped file, `dl/economics-middle-smith`), Napoleon, Alchemist, SARS-CoV-2, Kennedy. Same framing as the current copy: check each ratio against the current file; Freud's current copy was trimmed from its source, so find that crop box by matching the current copy against the source and reuse it.
- Rembrandt (`dl/biology-and-medicine-old-rembrandt`) and the Madhouse (`dl/psychology-middle-madhouse`) at 2,000 wide; trim the Madhouse's dark edge and the museum stamp at its bottom right.
- Verne stays as it is.
- Delete the two retired files.

- [ ] **Step 5: Update build.py**

- PLATES: replace the Vitruvian Man and Sleep of Reason tuples with:
  - `("", "rembrandt-anatomy-lesson.jpg", "Dr Tulp, in a black hat, lifts the muscles of a dead man's forearm with forceps while seven surgeons in white ruffs lean in to watch.", "1632", "Dr Tulp shows Amsterdam's surgeons the muscles of the arm", "Biology and medicine", "#s-biology", "Rembrandt van Rijn, The Anatomy Lesson of Dr Nicolaes Tulp, 1632. Mauritshuis, The Hague.", 0, 0, "<pos>")`
  - `("", "goya-madhouse.jpg", "<alt>", "<year>", "Goya paints the inmates of a madhouse", "Psychology", "#s-psychology", "Francisco Goya, The Madhouse, <dates>. Real Academia de Bellas Artes de San Fernando, Madrid.", 0, 0, "<pos>")`, its dates from the Academia's own page (Commons says 1808 to 1812); if that page cannot be read, `c. 1810` and "1808 to 1812" from Commons. The alt describes what is visible, in the same plain style as the others.
  - Both in date order within PLATES.
- SHORT_BY_FILE: `"rembrandt-anatomy-lesson.jpg": "Rembrandt, The Anatomy Lesson of Dr Tulp"`, `"goya-madhouse.jpg": "Goya, The Madhouse"`; drop the two retired entries.
- `slide(..., fill=False)`; `room()` passes `fill=True`.

- [ ] **Step 6: Update site.css**

Rooms never get the whole layout, so no CSS change is needed for that beyond keeping `.slide.whole` rules for the banner; update the rooms comment block to say every painting fills the screen.

- [ ] **Step 7: Focal points**

Screenshot every room painting on a laptop (1440x900) and a phone (412x915) with `set_painting` and lay them out as contact sheets (scratchpad). Set each `pos` so the subject stays in view and clear of the title where the painting allows: Freud's head whole, Napoleon's face, the Wanderer's figure, Augustine's face, Kennedy and von Braun, Dr Tulp and the forearm, the Madhouse's figures.

- [ ] **Step 8: Run the tests, expect PASS, and measure readability**

Run: `python -m pytest tests/test_build.py -q` then `python -m pytest tests/test_home_browser.py -q -k "fills_the_screen or readable"`
Expected: PASS. If a room text line drops under 4.5 to 1 over a newly filled painting, fix it with that painting's `pos` first, then the shade; record each fix.

- [ ] **Step 9: README and commit**

README: the picture notes name the two new paintings; "Adding a plate" says tall room paintings are made 1,920 wide and wide ones 2,000, at most 1,250,000 bytes. Run the whole suite, then commit the changed files by name.

```
git commit -m "Every room painting fills the screen; Rembrandt and Goya's Madhouse replace Vitruvian Man and the etching"
```

### Task 2: Rooms change by themselves, with a pause button

**Files:**
- Modify: `build.py` (room(): no `--n`; NO_SCRIPT goes)
- Modify: `site/assets/home.js` (initRooms rewritten)
- Modify: `site/assets/site.css` (room height, the pause button)
- Test: `tests/test_home_browser.py`, `tests/test_build.py`
- Modify: `README.md` (Rooms and Reduced motion bullets, home.js line)

**Interfaces:**
- Consumes: `set_painting(page, rid, k)` (Task 1).
- Produces (DOM): in each room with two or more paintings, home.js adds `<button class="pause" type="button" aria-label="Pause the paintings" aria-pressed="false"><span></span></button>` as the last child of `.room-stick`. `aria-pressed="true"` means paused; every button shows the same state.
- Produces (JS): `const EVERY = 6000` in home.js.

- [ ] **Step 1: Write the failing tests**

Remove the scroll-driven tests and helper (`show_painting`, `test_room_painting_follows_scroll`, `test_room_painting_holds_still_without_scrolling`, `test_room_is_three_and_a_half_screens_long`, `test_jumps_land_on_the_right_painting`); tests that used `show_painting` only to reach a room now scroll the room to the top of the screen (`room_on_screen(page, rid)`). New tests (waits are real time; `TICK = 6.8` s):
- `test_room_is_one_screen_tall` (DESKTOP, PHONE): every room `offsetHeight` within 2 px of `innerHeight`.
- `test_room_paintings_change_by_themselves` (DESKTOP: 0, then 1, 2, 0 after each TICK, caption matching each time; PHONE: 0 then 1).
- `test_room_waits_while_off_screen`: a room scrolled 30% onto the screen, wait TICK, still 0; scrolled fully away, wait TICK, back on screen and checked at once: still 0.
- `test_coming_back_does_not_speed_up_a_room`: on and off a room four times within a second, then on it: after 3 s still 0, after TICK exactly 1.
- `test_pause_stops_every_room_and_play_resumes`: press `#s-philosophy .pause`: every `.pause` has `aria-pressed="true"`; after TICK still 0; another room after TICK still 0; press its button: all `"false"`, and after TICK that room shows 1.
- `test_less_motion_starts_paused`: with reduced motion every button is pressed and after TICK the room still shows 0; pressing play makes it change after TICK.
- `test_hidden_tab_holds_the_rooms`: make `document.hidden` report true and fire `visibilitychange`: after TICK still 0; report false and fire it again: after TICK exactly 1.
- `test_room_skips_a_painting_that_failed_to_load`: point slide 1's image of `#s-tech` at a missing file: after TICK the room shows 2.
- `test_pause_button_is_a_named_button_clear_of_the_words` (DESKTOP, PHONE, 915x412, 1280x600): one per room, a BUTTON, named "Pause the paintings", focusable, not inside `[aria-hidden]`, its box clear of `.room-text` and `.caption`.
- Rewrite `test_resize_mid_room_keeps_one_right_painting`: a phone turned sideways in a room: one `.on`, caption matching, room one screen tall, no sideways scroll.
- Readability: `test_room_text_is_readable_over_every_painting` uses `set_painting` after pressing pause, and also measures `.room .pause span` against 3 to 1.
- tests/test_build.py: the rooms markup test has no `--n:` style; `test_room_with_no_paintings_still_lays_out` and `test_missing_plate_file_is_skipped` check slide counts instead of `--n`; the home page has no `<noscript><style>`.

Run: `python -m pytest tests -q -k "room or pause or hidden or less_motion"`
Expected: the new tests FAIL (no timer, no button, rooms 3.5 screens tall).

- [ ] **Step 2: build.py**

`room()` drops `style="--n:..."` and its docstring says the paintings change by themselves; `NO_SCRIPT` and its use in the home page head go (the room is one screen tall without it).

- [ ] **Step 3: site.css**

`.room { height: 100svh; }` (no `--n`); `.room-stick { position: relative; height: 100%; overflow: hidden; }`. The pause button reuses the old banner button's look: 42 px circle, `border: 1px solid rgba(244, 241, 234, .5)`, `background: rgba(10, 9, 8, .6)`, two bars or a triangle drawn in `currentColor`, a focus ring `2px solid #9fd3da`. Laptops: bottom right (`right: max(4vw, 18px); bottom: max(28px, 6svh)`); phones: top right (`top: 18px; right: 18px`).

- [ ] **Step 4: home.js**

Rewrite `initRooms` (paintingIndex, the scroll listener and the resize listener go):
- State per room: slides, caption, current index, loaded, timer id, half on screen.
- One shared `paused`, starting `true` with less motion.
- An IntersectionObserver with thresholds `[0, 0.5]`: any intersection loads the room; a ratio of at least 0.5 marks it seen and starts its timer, less stops it. The existing look-ahead loading after the window load event stays.
- `start(room)` only when seen, not paused, `!document.hidden`, two or more paintings, and no timer already running; `stop(room)` clears it.
- Each tick: the next painting after the current one, in a loop, whose image has loaded (`complete && naturalWidth > 0`); a painting whose image failed (`complete`, `naturalWidth === 0`, no `data-src`) is skipped; one still loading means wait for the next tick. Showing it moves `on` and fills the caption.
- `visibilitychange` stops every timer or restarts the seen ones; the buttons set `paused` for all, update every button's `aria-pressed`, then stop or start.
- Without IntersectionObserver: load every room, no timer, no buttons.

- [ ] **Step 5: Run the tests, expect PASS**

Run: `python -m pytest tests -q`
Expected: all pass, including the readability tests and the no-JavaScript test.

- [ ] **Step 6: README and commit**

README: Rooms (one screen each, change every 6 seconds while half on screen, pause button, less motion starts paused, without JavaScript the first painting), the home.js layout line. Commit the changed files by name.

```
git commit -m "Rooms change by themselves every six seconds while on screen, with a pause button"
```
