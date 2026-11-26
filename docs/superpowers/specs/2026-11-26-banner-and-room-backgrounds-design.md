# Banner and room backgrounds: design

Date: 26 November 2026. Status: approved by Jak ("looks good", 26 November 2026).

## Why

Jak, after seeing the live site on his phone: "do you think i should even have the photos on the side like that? or have them appear in the background as i scroll? like for example you see napoleon appear in the background when you scroll to war and defense and it goes through the photos like it does at top but just for that category, so i would have to add some more".

On a phone the side photos turn each room into a heading followed by a stack of pictures, which makes the page long and makes the photos feel like the subject. A painting filling the screen behind the room's title feels like walking into a room. A throwaway build of War and defense (26 November) confirmed the look with Washington Crossing the Delaware, and showed that small files cannot fill a screen.

Jak then chose a single still banner for the top ("A") and liked "1 old 1 middle 1 modern" per room.

## Goals

1. **Banner.** The first screen shows one still painting, Leutze's Washington Crossing the Delaware, behind the name, tagline, bio and quick links. The slideshow and its pause button go. The caption stays, fixed to this painting (year, event, the War and defense link, credit). The link preview card is drawn from the banner painting. Washington also stays in War and defense.
2. **Room backgrounds.** In each of the ten rooms, the room's paintings fill the screen behind the room's title, one at a time. Which painting shows follows how far the visitor has scrolled through the room, not a timer: entering the room shows the first, and scrolling on fades to the next. A caption at the bottom names the painting showing (year, event, credit). Nothing changes while the visitor is not scrolling.
3. **Three paintings per room, old to modern.** One old, one middle, one modern in each room, in date order: 30 paintings. Eight rooms need one more (Philosophy and Political science have three).
4. **Files big enough to fill a screen.** Every room painting at least 1,600 pixels, ideally about 2,000, on its long side. Napoleon was replaced on 26 November (1674 by 2000). Still too small: ENIAC (630 wide), Vitruvian Man (753), Caesar (924), Goya (1,000), First Flight (1,024). The banner should be bigger still (about 3,000 pixels wide) to stay sharp on large laptop screens; the Metropolitan Museum's public-domain scan of Washington Crossing the Delaware is the candidate.
5. **How a painting fills the screen.** On phones every painting fills the screen, cropped around its focal point (tall paintings lose a little at the sides; the throwaway build showed Napoleon this way, and it was far better than fitting it whole). On laptops, wide paintings fill the screen; tall ones are shown whole beside the title over a darkened, blurred copy, as the first screen does now.

## Non-goals

- No timed cycling in rooms; no parallax.
- Projects, Contact, the featured projects list and the credits page keep their layout (the credits page gains the new paintings).
- Essay pages (from 15 December) are a separate piece of work.

## Anti-goals (would make this a failure even if it works)

- A picture changing behind text someone is reading.
- A painting stretched past its pixels until it looks blurry.
- Room titles or captions that fail contrast over a painting (keep the measured 4.5 to 1 minimum the first screen meets).
- A heavy page: each room's paintings load only as the visitor nears the room; the banner is the only large picture loaded at first.

## Approaches considered

- **Rooms: timed slideshow per room** (Jak's first idea). Rejected: once essays go up, people read over these paintings, and a timer changes the picture under the text.
- **Rooms: scroll-driven** (chosen). Nothing moves unless the visitor scrolls; nobody misses a painting; the room's length sets the pace.
- **Rooms: keep the side photos.** Rejected for the phone reasons above.
- **Banner: one still painting** (chosen, Jak's "A"). Every painting now has its own full-screen moment in its room, so the top no longer needs to cycle through all of them; one strong picture makes a clearer first impression and the page loads faster.
- **Banner: keep the slideshow, starting on Washington** ("B"). Not chosen.

## Decided details

- A room is about one screen of scrolling per painting plus half a screen, so three paintings make a room about three and a half screens long.
- The room's text (title and note, later its essays) sits over the painting: on laptops on the left, as on the first screen; on phones near the bottom, above the caption.
- Visitors whose device asks for less motion: paintings change without the fade.
- The room paintings are decoration for screen readers (the title and caption carry the meaning); full credits stay on the credits page.
- The pinned side column on laptops (the rooms stage) goes away; each room has its own full-screen background.
- New paintings: Claude searches Wikimedia Commons for public-domain or credit-only images, big enough per goal 4, and lists two or three options per room with year, source and licence. Jak picks. Nothing is downloaded before he picks; each file's name, source and size is stated before download. Modern pictures are mostly U.S. government photographs or credit-only licences, since most modern work is still under copyright.

## Left to the builder

The exact shade gradients, the fade length, where each painting's focal point sits, the loading distance for room paintings, and whether the room wall colours (`ROOM_BG`) survive as the colour between paintings.

## Order of work

1. Banner and room backgrounds, built with the paintings the site has now (tests first, as before).
2. Painting options for each room, then the downloads Jak picks, added as they come.

## Paintings chosen (26 November 2026)

Jak's picks after two rounds of options (Claude proposed; Jak swapped Martin Luther King Jr., the Yalta Conference and Migrant Mother for the Wanderer, the Shibuya crossing and the fall of the Berlin Wall; D-Day for Iwo Jima; Earthrise for Kennedy and von Braun, whose date is 16 November 1963, not 1962 as the site said). Old, middle, modern per room, by the date of what each shows. New files and bigger copies come from Wikimedia Commons; the file name is given for each.

- **Philosophy and religion**
  - old: David, The Death of Socrates (399 BC), the site's current file.
  - middle: Botticelli, Saint Augustine in His Study (c. 400), the site's current file.
  - modern: Friedrich, Wanderer above the Sea of Fog (c. 1818). New: `Caspar David Friedrich - Wanderer above the Sea of Fog.jpeg` (Public domain).
- **Psychology**
  - old: Bosch, The Cure of Folly (c. 1501). New: `The Cure of Folly, ca. 1501-05FXD.jpg` (Public domain).
  - middle: Goya, The Sleep of Reason Produces Monsters (1799). Bigger copy: `Goya - Caprichos (43) - Sleep of Reason.jpg` (Public domain).
  - modern: Sigmund Freud, photograph by Max Halberstadt (c. 1921). New: `Sigmund Freud, by Max Halberstadt.jpg` (Public domain).
- **Sociology**
  - old: Bruegel, The Harvesters (1565), the site's current file.
  - middle: Seurat, A Sunday on La Grande Jatte (1884), the site's current file.
  - modern: Shibuya crossing, Tokyo (2017). New: `Shibuya Crossing, Tokyo; December 2017.jpg` (CC BY-SA 2.0).
- **Political science**
  - old: Coustou, Julius Caesar (49 BC). Bigger copy: `Julius Caesar Coustou Louvre MR1798 - 01a.jpg` (CC BY-SA 2.0).
  - middle: Magna Carta (1215), the site's current file.
  - modern: Fall of the Berlin Wall, Brandenburg Gate (1989). New: `Crane removed part of Wall Brandenburg Gate.jpg` (Public domain).
- **Economics**
  - old: Massys, The Moneylender and His Wife (1514). New: `Le prêteur et sa femme - Quentin Metsys - Musée du Louvre Peintures INV 1444 ; MR 821.jpg` (Public domain).
  - middle: Stoddart, Adam Smith (1776), the site's current file.
  - modern: Ford's moving assembly line (1913). New: `Ford assembly line - 1913.jpg` (Public domain).
- **War and defense**
  - old: Alexander Mosaic, Pompeii (333 BC). New: `Battle of Issus in 333 BC, between Alexander the Great & Darius III, from House of the Faun, Pompeii; closeup of Alexander on his horse Bucephalus (48452981692).jpg` (Public domain).
  - middle: David, Napoleon Crossing the Alps (1800; replaced 26 Nov), the site's current file.
  - modern: Rosenthal, Raising the Flag on Iwo Jima (1945). New: `Photograph of Flag Raising on Iwo Jima - NARA - 520748.tif` (Public domain).
- **Physics and chemistry**
  - old: Wright of Derby, The Alchemist (1669). Bigger copy: `Joseph Wright of Derby The Alchemist.jpg` (Public domain).
  - middle: Faraday lecturing at the Royal Institution (1855). New: `Professor Faraday lecturing at the Royal Institution, 27th December, 1855 RIIC 0006 20110213 BAL EP.jpg` (Public domain).
  - modern: The ATLAS detector, CERN (2008). New: `CERN LHC ATLAS Detector.jpg` (CC BY-SA 4.0).
- **Biology and medicine**
  - old: Leonardo, Vitruvian Man (c. 1490). Bigger copy: `Uomo Vitruviano.jpg` (Public domain).
  - middle: Hillemacher, Jenner vaccinating a boy (1796). Bigger copy: `Edward Jenner vaccinating a boy. Oil painting by E.-E. Hille Wellcome L0029093.jpg` (CC BY 4.0).
  - modern: SARS-CoV-2 under the electron microscope (2020). New: `Novel Coronavirus SARS-CoV-2 (51267393817).png` (CC BY 2.0).
- **Technology and AI**
  - old: The Antikythera mechanism (c. 100 BC). New: `Antikythera Mechanism (NAMA) 2017.jpg` (CC BY-SA 4.0).
  - middle: ENIAC and two of its programmers (1946). Bigger copy: `Two women operating ENIAC (full resolution).jpg` (Public domain).
  - modern: Summit supercomputer, Oak Ridge (2018). New: `Summit (supercomputer).jpg` (CC BY 2.0).
- **The future**
  - old: Verne, From the Earth to the Moon (1865). New: `From the Earth to the Moon (151481087).jpg` (Public domain).
  - middle: Von Braun and Kennedy at Cape Canaveral (1963). Bigger copy: `Werner Von Braun and President John F. Kennedy at Cape Canaveral Missile Test Annex - 1963 - 63PC-0095.jpg` (Public domain).
  - modern: Webb telescope, Cosmic Cliffs (2022). New: `NASA’s Webb Reveals Cosmic Cliffs, Glittering Landscape of Star Birth.jpg` (Public domain).
- **Banner**: Leutze, Washington Crossing the Delaware (1776). Bigger copy: `Washington Crossing the Delaware by Emanuel Leutze, MMA-NYC, 1851.jpg` (Public domain).

Coming out: Raphael, The School of Athens; Brouillet, A Clinical Lesson; Kaulbach, The Coronation of Charlemagne; Menzel, The Iron Rolling Mill; Newton with the Prism; First Flight; Anders, Earthrise. Washington Crossing the Delaware leaves War and defense and becomes the banner (it would otherwise show twice, and it is 24 years from Napoleon); this changes goal 1 above.
