# The first screen: a changing set of pictures from history

Approved by Jak in chat on 27 November 2026: "every 6 seconds, the gaspee is a good one, they are all good, maybe the top one shouldnt be limted to 3?", then "you have my ok, maybe make it less then 6 seconds for this one".

## Why

The first screen held one still painting, Washington Crossing the Delaware. Jak wants it to show more moments from history that he likes, changing by themselves, with no cap on how many.

## Goals

- The first screen shows the banner pictures in order, Washington first, then by the date of what each shows, and loops. It changes every 4 seconds (`BANNER_EVERY`, shorter than the rooms' 6, at Jak's ask) while at least half of it is on screen and the tab is visible.
- The same round pause button as the rooms. One pause state holds the first screen and every room; a visitor who asks for less motion starts paused.
- The caption follows the picture: year, what happens, credit. No room link (the banner pictures belong to no room).
- The name, tagline, bio and caption stay readable over every picture (4.5 to 1, measured), the pause icon 3 to 1.
- Only the next picture loads ahead: Washington paints first; once the page has loaded, the second loads; each change starts loading the one after. A picture still loading is waited for; one that failed is skipped.
- Without JavaScript: Washington only. The link-preview card stays Washington.
- Adding a picture later is a `PLATES` entry plus its file name in `BANNER_FILES`. No cap.
- Every picture is credited on the plates page.

## Non-goals

- No next or previous controls; no random picture per visit.
- Jak's eight downloads are not used as files: they are website copies (cropped, filtered, small, sources unknown). Their free originals are being found; each joins through the same list once Jak approves its download.

## Approaches

- **A, chosen:** the first screen joins the rooms' code in `home.js` (one IntersectionObserver, one pause state, one rule for waiting on a loading picture), with its own interval and one-ahead loading. One set of rules, one pause.
- **B:** a separate banner script. Rejected: two pause states to keep in step.
- **C:** a CSS animation. Rejected: it cannot wait for a picture to load, pause with the rooms, or stop when the tab is hidden.

## Decided

- Order: Washington (1776), then The Burning of the Gaspee (1772), USS Constitution and HMS Guerriere (1812), the Wright brothers' first flight (1903), Earthrise (1968). Later additions go by date after Washington.
- Pictures: site copies up to 3,000 px wide, progressive sRGB JPEG, at most 1,250,000 bytes. The Constitution scan loses 3 px at the left and 4 px at the bottom (light scan edges); Earthrise is cropped from its square to 3,000 by 1,924, keeping the Earth and the lunar horizon. New file names (`earthrise-apollo8.jpg`, `wright-first-flight.jpg`) so no browser shows a retired copy of the same name.
- Credits: Charles DeWolf Brownell, The Burning of the Gaspee, 1892, Rhode Island Historical Society, Providence; Thomas Birch, Engagement Between the Constitution and the Guerrière, 1813, Museum of Fine Arts, Boston; John T. Daniels, the first flight of the Wright Flyer, Kill Devil Hills, North Carolina, 17 December 1903, Library of Congress; William Anders, Earthrise, Apollo 8, 24 December 1968, NASA.
- The pause button sits bottom right on laptops, as in the rooms. On phones and short screens it sits bottom right beside the caption, which is narrowed to make room.

## Left to the builder

Focal points; the exact pause offsets on phones; the shade's strength if a picture fails the readability test.
