# Banner and Room Backgrounds Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The home page's first screen shows one still painting (Washington Crossing the Delaware), and each of the ten rooms shows its three paintings full screen behind its title, one at a time, changing only as the visitor scrolls through the room.

**Architecture:** `build.py` renders the banner and every room painting with the existing `slide()` markup (figure.slide, img.art, blurred img.bg for tall paintings), so the first screen and the rooms share one set of CSS rules. Each room is a tall section with a sticky full-screen layer; `home.js` picks the painting from how far the room has been scrolled, and loads a room's paintings only when the visitor nears it. The slideshow, its pause button, the pinned rooms stage and the room wall colours are removed.

**Tech Stack:** Python 3.14 + Pillow (build.py), plain CSS, plain JavaScript (no framework), pytest with headless Edge over CDP (`tools/browser.py`).

**Spec:** `docs/superpowers/specs/2026-11-26-banner-and-room-backgrounds-design.md` (approved; its section "Paintings chosen" and the note after it are already built: commits e576051 and 048f457).

## Global Constraints

- Python: `C:/Users/jakpo/AppData/Local/Python/pythoncore-3.14-64/python.exe` (written `PY` below). Run everything from `C:\Users\jakpo\Projects\jakpotvin-site`.
- Rebuild after every change to `build.py`, `site/assets/site.css` or `site/assets/home.js`: `PY build.py data/counts.json data/calculator.html` (the build stamps `?v=` hashes on css and js). A second build must change nothing.
- No em or en dashes in site output, README or commit messages; LF line endings (the existing test `test_outputs_lf_and_no_long_dashes` checks the site).
- No requests to any other host (`test_pages_load_cleanly` checks).
- A room is about one screen of scrolling per painting plus half a screen: height `(n * 100 + 50)svh` for n paintings.
- Every room painting at least 1,600 pixels on its long side; the banner at least 3,000 wide (already tested).
- Room titles and captions keep at least 4.5 to 1 contrast over every painting, measured with the text hidden.
- Visitors whose device asks for less motion: paintings change without the fade.
- Room paintings are decoration for screen readers: `aria-hidden="true"` on the painting layer, `alt=""` on every painting; the title and caption carry the meaning.
- The banner is the only large picture loaded at first; each room's paintings load only as the visitor nears the room.
- Commits stay local; nothing is pushed. Stage each file with its own `git add -- <path>`, check `git status --porcelain`, and chain the commit with `&&` so a failed add stops it. End every commit message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; no 19xx or 20xx tokens in commit messages.

## Review Focus

1. A room with fewer than three painting files (a file missing, even all three): the room still lays out, `--n` is its real count (at least 1), and no caption shows for an empty room. Test in Task 2.
2. A jump past rooms (a deep link to `#projects`, the End key, a fast fling) and then back into a room: the painting shown is the one for that position, not a leftover. Test in Task 2.
3. A resize or phone rotation in the middle of a room: one painting stays on, the right one for the new height, and nothing overflows sideways. Test in Task 2.
4. Short landscape screens (a phone turned sideways, 915 by 412; a 1280 by 600 laptop window): the room title and note never overlap the caption. Test in Task 2.
5. A deep link to a room (`#s-economics`): the room's top lands at the top of the screen with no strip of the room before it, its first painting loads and shows. Test in Task 2.

---

### Task 1: The banner: one still painting

**Files:**
- Modify: `build.py` (`slide()`, the `home` hero markup, `make_card()`, `CARD_ALT`, move `BANNER_FILE` up next to `PLATES`)
- Modify: `site/assets/site.css` (first-screen block, lines 123 to 189)
- Modify: `site/assets/home.js` (remove the slideshow)
- Modify: `README.md` (First screen, Link previews and Reduced motion bullets)
- Test: `tests/test_home_browser.py`, `tests/test_build.py`

**Interfaces:**
- Produces: `BANNER` (the PLATES tuple whose file is `BANNER_FILE`); `slide(p, on=False, eager=False) -> str` returning `<figure class="slide[ whole][ on]" {plate_data(p)}>[<img class="bg" src="assets/img/blur/{f}" alt="">]<img class="art" src|data-src="assets/img/{f}" alt="" style="--w:..;--h:..;--pos:..;object-position:..">` with `src` plus `fetchpriority="high"` when `eager`, else `data-src`; the blurred `.bg` always uses `src` (each is about 4 KB). `data-i` is dropped.
- Produces (CSS): `.slide` cross-fade by opacity and visibility, 0.6 s, no `.leaving` class; on screens up to 760 px wide `.slide.whole .art` covers the screen at its focal point (`object-fit: cover; object-position: var(--pos)`).
- Produces (JS): `fillCaption(cap, d)` kept, with the `.subj` link optional (room captions have none).

- [ ] **Step 1: Write the failing tests.** In `tests/test_home_browser.py` delete `test_slideshow_advances`, `test_pause_stops_slideshow`, `test_hidden_tab_stops_slideshow`, `test_reduced_motion_holds_plate_one`, `test_only_current_and_next_images_load`, `test_whole_plates_have_backdrop` (Task 2 covers tall paintings), `test_pause_stops_the_zoom`, `test_pause_button_keeps_its_name` and the `current()` helper, and add:

```python
BANNER = "washington-crossing.jpg"
STILL = ("none", "matrix(1, 0, 0, 1, 0, 0)")


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE, {**DESKTOP, "reduced_motion": True}], ids=["desktop", "phone", "desktop-rm"])
def test_banner_is_one_still_painting(browser, site, cfg):
    page = open_home(browser, site, cfg)
    assert page.eval("document.querySelectorAll('.intro .slide').length") == 1
    assert page.eval("document.querySelector('.intro .slide.on .art').getAttribute('src')") == "assets/img/" + BANNER
    assert page.eval("document.querySelector('.pause')") is None
    caption = "document.querySelector('.hero .caption').textContent"
    zoom = "getComputedStyle(document.querySelector('.intro .slide .art')).transform"
    before = page.eval(caption)
    assert page.eval(zoom) in STILL
    page.wait(6.5)
    assert page.eval(caption) == before and page.eval(zoom) in STILL


def test_banner_caption_names_the_painting_and_links_its_room(browser, site):
    page = open_home(browser, site, DESKTOP)
    q = "document.querySelector('.hero .caption %s').%s"
    assert page.eval(q % (".yr", "textContent")) == "1776"
    assert page.eval(q % (".what", "textContent")) == "Washington crosses the Delaware"
    assert page.eval(q % (".subj", "getAttribute('href')")) == "#s-warfare"
    assert page.eval(q % (".subj", "textContent")) == "War and defense"
    assert page.eval(q % (".credit", "textContent")) == "Leutze, Washington Crossing the Delaware"
```

In `tests/test_build.py` delete `test_intro_has_one_slide_per_plate` (Task 2's `test_rooms_are_built_for_scrolling` replaces it) and rewrite `test_every_plate_has_a_blurred_copy` so it no longer counts slideshow slides (after this task the rooms are not slides yet): every `site/assets/img/*.jpg` has a copy of the same name in `site/assets/img/blur/`, the two name sets are equal and number 31, and `assets/img/small` does not exist; drop the then unused `SLIDE_IMG` and `slide_files`. After `test_every_page_has_a_link_preview_card`, add:

```python
def test_card_is_drawn_from_the_banner_with_the_name_on_a_dark_band():
    assert run_build().returncode == 0
    t = (SITE / "index.html").read_text(encoding="utf-8")
    assert "Leutze, Washington Crossing the Delaware" in meta(t, "property", "og:image:alt")
    from PIL import Image
    with Image.open(SITE / "assets/card.jpg") as im:
        band = im.convert("L").crop((60, 630 - 215, 700, 630 - 40))
        assert sorted(band.getdata())[band.width * band.height // 2] <= 80  # median of the band behind the name
```

(Grey level 80 is relative luminance of about 0.08; white text on it is above 7 to 1.)

- [ ] **Step 2: Run them and watch them fail.**
Run: `PY -m pytest tests/test_home_browser.py tests/test_build.py -q -k "banner or card_is_drawn"`
Expected: FAIL: 31 slides in `.intro`, the pause button exists, the caption is Socrates', the card alt names David.

- [ ] **Step 3: Implement in `build.py`.** Move `BANNER_FILE = "washington-crossing.jpg"` (with its comment) to just after the `PLATES = [(roman(i + 1),) + p[1:] ...]` renumbering line and add `BANNER = next(p for p in PLATES if p[1] == BANNER_FILE)`. Give `slide()` the signature and output in Interfaces. In the hero: `<div class="slides" aria-hidden="true">{slide(BANNER, on=True, eager=True)}</div>` (no `data-current`), the caption from `BANNER` (`first = BANNER`), and no pause button. `make_card()` opens `BANNER[1]` and shades with the darker of two masks, alpha `200 * max(0, 1 - x / (0.55 * w))` from the left and `235 * clamp((y - 0.4 * h) / (0.35 * h), 0, 1)` from the bottom (combine two L masks with `ImageChops.lighter`), so Washington, at about a third of the width and the middle of the height, stays bright. `CARD_ALT` uses `SHORT[BANNER[0]]`.

- [ ] **Step 4: Implement in `site.css` and `home.js`.** CSS: delete the `.pause` rules, `html[data-motion=full] .pause`, the `intro-zoom` keyframes and the rule that runs them, `.slides.paused`, and `.slide:not(.on):not(.leaving)`. Replace `.slide`'s transition with `.slide { opacity: 0; visibility: hidden; transition: opacity .6s ease, visibility 0s linear .6s; }` and `.slide.on { opacity: 1; visibility: visible; transition: opacity .6s ease; }`; keep `@media (prefers-reduced-motion: reduce) { .slide { transition: none; } }`. In the 760 px block change the `.slide.whole .art` rule to `object-fit: cover; object-position: var(--pos) !important;` (keep `inset: 0; margin: 0; width: 100%; height: 100%`). JS: delete `initSlideshow`, `initIntroScroll`, `window.slideshow` and the `intro` block that calls them; make `fillCaption` skip `.subj` when the caption has none; update the file's header comment.

- [ ] **Step 5: Rebuild and run the tests.**
Run: `PY build.py data/counts.json data/calculator.html` then `PY -m pytest tests/test_home_browser.py tests/test_build.py -q`
Expected: all pass. If `test_first_screen_without_scrolling`, `test_scroll_back_restores_first_screen` or `test_text_clears_caption_on_short_screens` fail, the hero markup lost a class it needs; fix the markup, not the test.

- [ ] **Step 6: Look at the card.** Open `site/assets/card.jpg`. Washington and the flag must read clearly above the name. If the shade buries him, lower the left mask's 200 and record the value.

- [ ] **Step 7: README.** First screen bullet: one still painting (`BANNER_FILE`, Washington Crossing the Delaware) fills the screen behind the name, tagline and bio, with its year, event, the War and defense link and its credit in the corner; no slideshow. Link previews: the card is drawn from the banner painting, darkened at the left and the bottom. Reduced motion: nothing on the first screen moves for anyone now; the rooms change paintings without the fade.

- [ ] **Step 8: Commit.** Stage `build.py`, `site/assets/site.css`, `site/assets/home.js`, `README.md`, `tests/test_home_browser.py`, `tests/test_build.py`, `site/index.html`, `site/plates.html`, `site/404.html`, `site/atoms/index.html`, `site/atoms/calculator/index.html`, `site/assets/card.jpg` (each that `git status` lists), then commit "The banner: Washington Crossing the Delaware, one still painting; the slideshow and pause button go".

### Task 2: The rooms: three paintings, full screen, changed by scrolling

**Files:**
- Modify: `build.py` (`room()`, `ROOMS`; delete `ROOM_TEXT`, `ROOM_BG`, `room_colour()`, `aspect()`, `row()`, `index`, and the `colorsys` and second `PIL.Image` imports if nothing else uses them)
- Modify: `site/assets/site.css` (the rooms block, lines 207 to 243 and 248 to 250; the header comment, which still describes Newton)
- Modify: `site/assets/home.js` (`initRooms` rewritten)
- Modify: `README.md` (Plates and Rooms bullets)
- Test: `tests/test_home_browser.py`, `tests/test_build.py`

**Interfaces:**
- Consumes: `slide(p, on, eager)`, `BANNER_FILE`, `fillCaption(cap, d)`, the `.slide` cross-fade (Task 1).
- Produces (markup, one per subject): `<section class="room" id="{anchor}" style="--n:{max(n, 1)}" aria-labelledby="{anchor}-h"><div class="room-stick"><div class="room-bg" aria-hidden="true"><div class="slides">{slides, the first with class on, all lazy}</div><div class="room-shade"></div></div><div class="room-words"><div class="room-text"><h2 id="{anchor}-h">{title}</h2><p class="room-soon">{room note}</p></div>{caption}</div></div></section>`, where caption is `<div class="caption"><span class="yr">..</span> <span class="what">..</span> <span class="credit">{short credit}</span></div>` for the room's first painting, and nothing when the room has none. `ROOMS = '<div class="rooms">' + rooms + '</div>'` (no `.rooms-stage`, no `data-bg`).
- Produces (JS): `paintingIndex(top, height, view, n)` in `home.js`:

```js
// Which of a room's n paintings shows: the share of the room scrolled past, from its top at the top of the screen
// to its bottom at the bottom of the screen, cut into n equal parts.
const paintingIndex = (top, height, view, n) =>
  n < 2 ? 0 : Math.min(n - 1, Math.floor(Math.max(0, -top) / Math.max(1, height - view) * n));
```

- [ ] **Step 1: Write the failing tests.** In `tests/test_home_browser.py` delete `test_rooms_pin_and_swap`, `test_room_wall_colours`, `test_room_deep_link_shows_its_plates`, `test_rooms_unpinned_on_phone_and_reduced_motion`, `test_rooms_repin_after_resize`, `ON_ROOMS`, `HEX_TO_RGB` and `center_room`; change `test_slides_hidden_from_screen_readers` to also require `document.querySelectorAll('.room-bg[aria-hidden="true"]').length === 10` and `alt === ''` on every `.slide .art` and `.slide .bg`. Add the helpers and tests below.

```python
def show_painting(page, rid, k, settle=0.8):
    """Scroll to the middle of the stretch of room rid where painting k shows."""
    page.eval("(() => { const r = document.getElementById(%s), n = r.querySelectorAll('.slide').length;"
              " const top = r.getBoundingClientRect().top + scrollY, span = r.offsetHeight - innerHeight;"
              " scrollTo(0, Math.round(top + span * (%d + 0.5) / n)); return new Promise(f => requestAnimationFrame(() => requestAnimationFrame(f))); })()"
              % (json.dumps(rid), k))
    page.wait(settle)


def on_index(page, rid):
    return page.eval("[...document.getElementById(%s).querySelectorAll('.slide')].findIndex(s => s.classList.contains('on'))" % json.dumps(rid))


def caption_matches(page, rid):
    return page.eval("(r => { const s = r.querySelector('.slide.on').dataset, c = r.querySelector('.caption');"
                     " return c.querySelector('.yr').textContent === s.yr && c.querySelector('.what').textContent === s.what"
                     " && c.querySelector('.credit').textContent === s.credit; })(document.getElementById(%s))" % json.dumps(rid))


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE, {**DESKTOP, "reduced_motion": True}], ids=["desktop", "phone", "desktop-rm"])
def test_room_painting_follows_scroll(browser, site, cfg):
    page = open_home(browser, site, cfg)
    for rid in ("s-philosophy", "s-warfare", "s-future"):
        for k in (0, 1, 2, 1):
            show_painting(page, rid, k)
            assert on_index(page, rid) == k and caption_matches(page, rid), (rid, k)
    assert page.eval("[...document.querySelectorAll('.room')].every(r => r.querySelectorAll('.slide.on').length === 1)")


def test_room_painting_holds_still_without_scrolling(browser, site):
    page = open_home(browser, site, DESKTOP)
    show_painting(page, "s-biology", 1)
    page.wait(3)
    assert on_index(page, "s-biology") == 1


def test_room_is_three_and_a_half_screens_long(browser, site):
    page = open_home(browser, site, DESKTOP)
    assert page.eval("[...document.querySelectorAll('.room')].every(r => Math.abs(r.offsetHeight - 3.5 * innerHeight) <= 2)")


def test_jumps_land_on_the_right_painting(browser, site):  # Review Focus 2
    page = open_home(browser, site, DESKTOP, hash="#projects")
    page.wait(0.5)
    show_painting(page, "s-warfare", 1)
    assert on_index(page, "s-warfare") == 1
    page.scroll_to(page.eval("document.documentElement.scrollHeight"))
    show_painting(page, "s-philosophy", 0)
    assert on_index(page, "s-philosophy") == 0 and caption_matches(page, "s-philosophy")


def test_resize_mid_room_keeps_one_right_painting(browser, site):  # Review Focus 3
    page = open_home(browser, site, DESKTOP)
    show_painting(page, "s-biology", 2)
    page.resize(700, 900, settle=0.8)
    top, height, view = page.eval("(r => [r.getBoundingClientRect().top, r.offsetHeight, innerHeight])(document.getElementById('s-biology'))")
    want = min(2, int(max(0, -top) / max(1, height - view) * 3))
    assert on_index(page, "s-biology") == want
    assert page.eval("document.getElementById('s-biology').querySelectorAll('.slide.on').length") == 1
    assert page.eval("document.documentElement.scrollWidth <= innerWidth")


@pytest.mark.parametrize("w, h, mobile", [(1440, 900, False), (412, 915, True), (915, 412, True), (1280, 600, False), (800, 600, False)])
def test_room_words_never_overlap_the_caption(browser, site, w, h, mobile):  # Review Focus 4
    page = open_home(browser, site, dict(width=w, height=h, mobile=mobile))
    for rid in ("s-politics", "s-tech"):
        show_painting(page, rid, 0, settle=0.3)
        assert rect(page, f"#{rid} .room-text")["bottom"] <= rect(page, f"#{rid} .caption")["top"], rid
        assert rect(page, f"#{rid} .room-text h2")["top"] >= 0, rid


def test_room_deep_link_lands_on_its_first_painting(browser, site):  # Review Focus 5
    page = open_home(browser, site, DESKTOP, hash="#s-economics")
    page.wait(1.5)
    assert abs(rect(page, "#s-economics")["top"]) <= 1
    assert on_index(page, "s-economics") == 0
    assert page.eval("(a => a.complete && a.naturalWidth > 0)(document.querySelector('#s-economics .slide.on .art'))")


def test_text_sits_left_on_laptops_and_low_on_phones(browser, site):
    page = open_home(browser, site, DESKTOP)
    show_painting(page, "s-sociology", 0)
    t = rect(page, "#s-sociology .room-text")
    assert t["left"] <= 0.25 * 1440 and t["right"] <= 0.55 * 1440 and 0.2 * 900 <= (t["top"] + t["bottom"]) / 2 <= 0.8 * 900
    page = open_home(browser, site, PHONE)
    show_painting(page, "s-sociology", 0)
    assert rect(page, "#s-sociology .room-text")["top"] >= 0.45 * 915


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_every_room_painting_fills_the_screen(browser, site, cfg):
    page = open_home(browser, site, cfg)
    for rid in page.eval("[...document.querySelectorAll('.room')].map(r => r.id)"):
        for k in range(3):
            show_painting(page, rid, k, settle=0.2)
            s = f"#{rid} .slide.on"
            whole = page.eval(f"document.querySelector('{s}').classList.contains('whole')")
            cover = rect(page, f"{s} .bg" if whole and cfg is DESKTOP else f"{s} .art")
            assert cover["left"] <= 0 and cover["top"] <= 0 and cover["right"] >= cfg["width"] - 1 and cover["bottom"] >= cfg["height"] - 1, (rid, k)
            if cfg is PHONE or not whole:
                assert page.eval(f"getComputedStyle(document.querySelector('{s} .art')).objectFit") == "cover", (rid, k)
            else:  # a tall painting on a laptop: shown whole, beside the title
                assert rect(page, f"{s} .art")["left"] >= rect(page, f"#{rid} .room-words")["right"] - 1, (rid, k)


@pytest.mark.parametrize("cfg, want", [(DESKTOP, "0.6s"), ({**DESKTOP, "reduced_motion": True}, "0s")], ids=["fade", "no-fade"])
def test_paintings_fade_unless_less_motion(browser, site, cfg, want):
    page = open_home(browser, site, cfg)
    assert page.eval("getComputedStyle(document.querySelector('.room .slide')).transitionDuration").split(",")[0] == want


def test_banner_loads_before_any_room_painting(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(2)
    entries = page.eval("performance.getEntriesByType('resource').filter(e => e.name.includes('/assets/img/') && !e.name.includes('/blur/'))"
                        ".map(e => [e.name.split('/').pop(), e.startTime, e.responseEnd])")
    banner = [e for e in entries if e[0] == "washington-crossing.jpg"]
    assert len(banner) == 1
    assert all(start >= banner[0][2] - 1 for name, start, _ in entries if name != "washington-crossing.jpg")


def test_far_rooms_wait_until_the_visitor_nears_them(browser, site):
    page = open_home(browser, site, DESKTOP)
    page.wait(2)
    assert page.eval("document.querySelectorAll('#s-future .art[data-src]').length") == 3
    page.scroll_to(page.eval("document.getElementById('s-future').getBoundingClientRect().top + scrollY - innerHeight * 0.9"))
    page.wait(0.8)
    assert page.eval("document.querySelectorAll('#s-future .art[data-src]').length") == 0
```

In `tests/test_build.py` extend `test_missing_plate_file_is_skipped`: while `eniac.jpg` is parked, `re.search(r'<section class="room" id="s-tech" style="--n:2"', index)` matches (Review Focus 1). Add:

```python
def test_rooms_are_built_for_scrolling():
    assert run_build().returncode == 0
    index = (SITE / "index.html").read_text(encoding="utf-8")
    for rid, files in ROOM_PAINTINGS.items():
        section = re.search(r'<section class="room" id="%s" style="--n:3".*?</section>' % rid, index, re.S).group(0)
        assert section.count('class="slide') == 3 and section.count('class="slide on') == 1, rid
        assert 'data-src="assets/img/%s"' % files[0] in section and ' src="assets/img/%s"' % files[0] not in section, rid
        assert '<div class="room-bg" aria-hidden="true">' in section and '<div class="caption">' in section, rid
    assert "rooms-stage" not in index and "data-bg=" not in index
```

- [ ] **Step 2: Run them and watch them fail.**
Run: `PY -m pytest tests/test_home_browser.py tests/test_build.py -q -k "room or jumps or resize_mid or banner_loads or far_rooms or fade or fills_the_screen or missing_plate or screen_readers or text_sits"`
Expected: FAIL: no `.room-stick`, rooms are one screen tall, the stage is pinned, `--n` absent.

- [ ] **Step 3: Implement `room(anchor, title) -> str` and `ROOMS` in `build.py`** to the markup in Interfaces: the room's paintings are `[p for p in PLATES if p[6] == "#" + anchor and p[1] != BANNER_FILE]`, each through `slide(p, on=(k == 0))` (lazy); the caption uses `p[3]`, `p[4]` and `SHORT[p[0]]` of the first. Delete the dead room code listed under Files.

- [ ] **Step 4: Implement the CSS.** Replace the rooms block with: `.rooms` full width, light text colour, no background transition; `.room { height: calc((var(--n) * 100 + 50) * 1svh); padding: 0; border: 0; background: #0e0d0c; }` plus whatever cancels `html { scroll-padding-top: 24px }` for rooms (for example `scroll-margin-top: -24px`) so a deep link puts the room's top at 0; `.room-stick { position: sticky; top: 0; height: 100svh; overflow: hidden; }`; `.room-bg` and `.room-bg .slides` fill it; `.room-shade` uses the first screen's two gradients; `.room-words` is absolute at `left: var(--edge)`, `top` and `bottom` `max(28px, 6svh)`, `width: min(540px, 44vw)`, a flex column; `.room-text` has `margin-block: auto` (so it centres in the space above the caption and can never cover it) and the first screen's text shadow; the room caption takes the first screen's caption look but sits in the flex flow (`flex: none`). Up to 760 px wide: `.room-shade` becomes `linear-gradient(180deg, rgba(10, 9, 8, .2) 0%, rgba(10, 9, 8, .55) 38%, rgba(10, 9, 8, .8) 100%)`; `.room-words` runs from `left: 18px; right: 18px; width: auto; top: 76px; bottom: 22px`; `.room-text` gets `margin: auto 0 0`; the room caption shows its credit on its own line (the first screen's caption hides it on phones; the room caption must not). Keep `.room h2` and `.room-soon` as they are. Delete `.rooms-stage`, `.rooms.pinned`, `.room-in`, `.room-plates`, `.rp`, `.room-row`, `.room-empty`, `.room-pl`, `.room-d`. Rewrite the header comment's PICTURE line (Washington on the first screen; each room's three paintings behind it).

- [ ] **Step 5: Implement `initRooms(wrap)` in `home.js`.** For each `.room`: its slides, its caption, its current index (0). `update()`: for every room with slides, `i = paintingIndex(top, height, innerHeight, n)` from `getBoundingClientRect()`; when `i` changes, move `.on` to slide `i` and `fillCaption(caption, slide.dataset)`; any room on screen whose images are not loaded is loaded now. Run `update` on `scroll` (passive, at most once per animation frame), on `resize`, and once at start. Loading a room sets `src` from `data-src` on its `.art` images and removes `data-src`. Look-ahead loading starts only after the window's `load` event (at once if `document.readyState === 'complete'`): an `IntersectionObserver` with `rootMargin: '100% 0px'` loads each room as it comes within one screen and stops watching it; without `IntersectionObserver`, load every room at the `load` event. Delete the old pin, stage and wall-colour code and `desktop`.

- [ ] **Step 6: Rebuild and run the whole suite.**
Run: `PY build.py data/counts.json data/calculator.html` then `PY -m pytest -q -p no:cacheprovider`
Expected: all pass, including `test_pages_load_cleanly` (no console errors), `test_no_sideways_overflow_between_breakpoints`, `test_deep_link_lands_on_section` and `test_writing_follows_the_first_screen`.

- [ ] **Step 7: README.** Plates bullet: the banner painting is on the first screen; each other painting is a background in its subject's room. Rooms bullet: each room is about one screen of scrolling per painting plus half a screen; its paintings fill the screen behind the title, one at a time, chosen by how far the room has been scrolled (`paintingIndex` in `home.js`); on phones every painting fills the screen around its focal point (the last field of its `PLATES` tuple); on laptops tall ones are shown whole beside the title over a blurred copy; a room's paintings load only when the visitor is within a screen of it, after the banner. Remove the sentences about `ROOM_BG`, wall colours and the pinned plates.

- [ ] **Step 8: Commit.** Stage `build.py`, `site/assets/site.css`, `site/assets/home.js`, `README.md`, both test files and the rebuilt pages (each path `git status` lists), then commit "The rooms: each room's three paintings fill the screen behind its title and change as you scroll through it".

### Task 3: Readable text over every painting

**Files:**
- Create: `tools/contrast.py`
- Modify: `tools/browser.py` (add `Page.screenshot_png`)
- Modify: `site/assets/site.css` (only if a measurement fails)
- Test: `tests/test_contrast.py` (new), `tests/test_home_browser.py`

**Interfaces:**
- Consumes: the room markup and `show_painting(page, rid, k, settle)` from Task 2; `.hero` markup from Task 1.
- Produces: `Page.screenshot_png() -> bytes` (CDP `Page.captureScreenshot` with `format: "png"`, after `document.fonts.ready`); in `tools/contrast.py`: `luminance(rgb) -> float` (WCAG relative luminance, sRGB 0 to 255), `contrast(a, b) -> float` (WCAG ratio, order-free), `over(rgba, rgb) -> tuple` (alpha composite, alpha 0 to 1), `text_contrast(page, selectors) -> dict[str, float]`.
- `text_contrast` method: read each selector's box (`getBoundingClientRect`) and computed `color`; skip selectors with no element or a zero-size box; inject a style that makes all text transparent with no text shadow and no caption border; take one PNG screenshot; remove the style; for each box take the pixel at the 90th percentile of luminance as the background; composite the text colour over it; return the ratio per selector.

- [ ] **Step 1: Write the failing tests.** `tests/test_contrast.py`:

```python
from tools.browser import Browser, Site
from tools.contrast import contrast, luminance, over, text_contrast


def test_luminance_and_contrast_match_wcag():
    assert luminance((255, 255, 255)) == 1.0 and luminance((0, 0, 0)) == 0.0
    assert round(contrast((255, 255, 255), (0, 0, 0)), 2) == 21.0
    assert contrast((0, 0, 0), (255, 255, 255)) == contrast((255, 255, 255), (0, 0, 0))
    assert over((255, 255, 255, 0.5), (0, 0, 0)) == (127.5, 127.5, 127.5)


def test_text_contrast_measures_the_background_behind_the_text(tmp_path):
    (tmp_path / "index.html").write_text(
        '<!DOCTYPE html><body style="margin:0;font:40px sans-serif">'
        '<p id="a" style="margin:0;background:#000;color:#fff">white on black</p>'
        '<p id="b" style="margin:0;background:#fff;color:rgba(255,255,255,.9)">white on white</p>', encoding="utf-8")
    with Site(root=tmp_path) as site, Browser() as b:
        page = b.open(site.url("index.html"), width=800, height=400)
        got = text_contrast(page, ["#a", "#b", "#missing"])
    assert got["#a"] > 20 and got["#b"] < 1.1 and "#missing" not in got
```

In `tests/test_home_browser.py`:

```python
HERO_TEXT = [".intro h1", ".intro .lede", ".intro .note", ".hero .caption .yr", ".hero .caption .what", ".hero .caption .subj", ".hero .caption .credit"]
ROOM_TEXT = [".room-text h2", ".room-soon", ".caption .yr", ".caption .what", ".caption .credit"]
NO_FADE = "document.head.insertAdjacentHTML('beforeend', '<style>.slide { transition: none !important; }</style>'); 1"
LOADED = "(a => a.complete && a.naturalWidth ? 1 : new Promise(f => { a.onload = () => f(1); setTimeout(() => f(0), 5000); }))(document.querySelector('#%s .slide.on .art'))"


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_banner_text_is_readable(browser, site, cfg):
    from tools.contrast import text_contrast
    page = open_home(browser, site, cfg)
    page.wait(1)
    got = text_contrast(page, HERO_TEXT)
    assert len(got) >= 4 and min(got.values()) >= 4.5, got


@pytest.mark.parametrize("cfg", [DESKTOP, PHONE], ids=["desktop", "phone"])
def test_room_text_is_readable_over_every_painting(browser, site, cfg):
    from tools.contrast import text_contrast
    page = open_home(browser, site, cfg)
    page.eval(NO_FADE)
    low = []
    for rid in page.eval("[...document.querySelectorAll('.room')].map(r => r.id)"):
        for k in range(3):
            show_painting(page, rid, k, settle=0.1)
            assert page.eval(LOADED % rid) == 1, (rid, k)
            got = text_contrast(page, [f"#{rid} {s}" for s in ROOM_TEXT])
            assert len(got) == len(ROOM_TEXT), (rid, k, got)
            low += [(rid, k, s, round(v, 2)) for s, v in got.items() if v < 4.5]
    assert low == []
```

- [ ] **Step 2: Run them and watch them fail.**
Run: `PY -m pytest tests/test_contrast.py tests/test_home_browser.py -q -k "contrast or readable"`
Expected: FAIL with `ModuleNotFoundError: tools.contrast`.

- [ ] **Step 3: Implement `Page.screenshot_png` and `tools/contrast.py`** to the Interfaces. Run `test_contrast.py` until it passes.

- [ ] **Step 4: Run the readability tests and fix what they find.**
Run: `PY -m pytest tests/test_home_browser.py -q -k readable`
Expected: PASS. If a painting fails, darken the shade where the failing text sits (`.room-shade` or `.hero .shade` alphas, in steps of .05) or raise that text's opacity (`.room-soon`, `.caption .credit`, at most .85), never lighten anything; rerun; record the final values in the commit message.

- [ ] **Step 5: Look at every room.** With a throwaway script in the session scratchpad (not the repo), screenshot each room's three paintings on DESKTOP and PHONE through `show_painting` and lay them out as two contact sheets. Check each: on phones the focal point (the person or object the caption names) is on screen; on laptops tall paintings sit whole beside the title; nothing looks stretched or soft. Fix a bad crop by changing that painting's focal point (the last field of its `PLATES` tuple), rebuild, and look again.

- [ ] **Step 6: Run the whole suite, the name scan, and commit.**
Run: `PY -m pytest -q -p no:cacheprovider`; then the private-name scan over the folder (`name_scan.py` with the list in `C:\Users\jakpo\Projects\mechdb\local\private-names.txt`).
Expected: all pass; the scan prints PASS.
Stage `tools/contrast.py`, `tools/browser.py`, `tests/test_contrast.py`, `tests/test_home_browser.py` and, if changed, `site/assets/site.css`, `build.py` and the rebuilt pages; commit "Text over every painting measured at 4.5 to 1 or better, on laptops and phones".
