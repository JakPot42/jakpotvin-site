# Rooms that change by themselves, with every painting filling the screen

Changes the room part of `2026-11-26-banner-and-room-backgrounds-design.md` (goals 2 and 5, and the "no timed cycling" non-goal). The banner is unchanged.

## Why

Jak, after seeing the live rooms: "we should have the photos change automatically when on the subject and also i thought we were gonna find pantings that fits the whole background".

On laptops 13 of the 30 room paintings are tall, so they sat whole in a box beside the title instead of filling the screen. A side-by-side test of all 13 cropped to fill a laptop screen showed 11 look as good or better filled. Two do not: Vitruvian Man loses his head and the circle, and Goya's etching turns grainy. Jak chose option A: fill the screen with the tall ones too, and replace those two with wide paintings. His picks (Claude's recommendations):

- Biology and medicine, the old painting: Rembrandt, The Anatomy Lesson of Dr Nicolaes Tulp (1632), Mauritshuis. Commons file "Rembrandt van Rijn - The Anatomy Lesson of Dr Nicolaes Tulp - 146 - Mauritshuis.jpg", 6000 by 4520, public domain. Downloaded with his OK; SHA-1 matches Commons.
- Psychology, the middle painting: Goya, The Madhouse (La casa de locos), Real Academia de Bellas Artes de San Fernando. Commons file "Francisco de Goya - La casa de locos - Google Art Project.jpg", 4480 by 2752, public domain. Downloaded with his OK; SHA-1 matches. Commons dates it 1808 to 1812; other sources say 1812 to 1819. The caption's year follows the museum's own page.

## Goals

1. **Paintings change by themselves.** While a room is on screen, its painting cross-fades to the next every 6 seconds and loops. The timer runs only while at least half of the room is on screen and the browser tab is visible; it picks up where it stopped when the visitor comes back. The caption changes with the painting.
2. **Each room is one screen tall.** The three and a half screens of scrolling existed only to drive the paintings by scroll; they go.
3. **A way to stop it.** Each room has a small pause button (the look of the old banner pause button). Pressing it pauses every room on the page, and it becomes a play button. Anything that moves by itself for more than 5 seconds needs a way to stop it (WCAG 2.2.2). Visitors who ask their device for less motion start paused.
4. **Every room painting fills the screen on laptops too,** cropped around its focal point, as on phones. The layout that showed tall paintings whole beside the title leaves the rooms.
5. **The two new paintings replace Vitruvian Man and Goya's Sleep of Reason,** whose files leave the site. Each room keeps old, middle, modern in date order.
6. **Sharp on big screens.** A room painting's site copy is 1,920 pixels wide where its source allows, made from the full-size originals already downloaded. Two exceptions: the Verne engraving's biggest scan is 1,338 wide, so it stays a little soft on big monitors; Adam Smith's statue needs the cropped Commons file (1925 by 2884, 1.1 MB, CC BY-SA 4.0, the same photographer), a download that waits for Jak's OK.
7. **Focal points checked for the laptop crop,** starting with Freud, whose head the first test cut off.
8. **Text stays readable:** every line of room text measures at least 4.5 to 1 against the painting behind it, on laptops and phones, for all 30 paintings.

## Not in this change

- The banner: still one still painting.
- No scroll-driven changes in rooms; no parallax.
- Screen readers are not told each time a painting changes (that would interrupt every 6 seconds).

## Would make it a failure

- A painting fading in half-loaded: the next painting is loaded before the fade starts.
- Paintings changing in a room nobody is looking at, or with no way to stop them.

## Approaches

- **A timer per room, rooms one screen tall (chosen).** Simple to follow; the visitor sees each painting without scrolling.
- **A timer and scroll together, rooms kept tall.** Rejected: two things would move the picture and fight each other.
- **Fill vs replace (Jak chose fill, option A).** Replacing all 13 tall paintings would have kept everything uncropped but needed 13 new picks and emptied Psychology.

The trade-off the first design named still holds: when essays go up, people read over a changing picture. The pause button is the answer to that.

## Claude's calls (Jak can change any of them)

- 6 seconds per painting; the 0.6 second cross-fade stays.
- One pause button pauses all rooms, not one room.
- Less-motion visitors start paused and can press play.
- The timer counts only while half the room is on screen.
- The blurred backdrop copies stay only if something still uses them.

## Left to the builder

The pause button's exact place and size (it must not cover the caption), the focal point values, JPEG quality, and which tests the scroll-driven design leaves behind.
