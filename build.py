"""Build jakpotvin.com. Run from this folder: python build.py data/counts.json data/calculator.html (needs Pillow)."""
import hashlib, html, json, re, sys, pathlib

import sitetext

COUNTS, CALC = sys.argv[1], sys.argv[2]
OUT = pathlib.Path(__file__).parent / "site"


def asset_v(rel):
    """A site file's address suffix: ?v= and the first 10 hex digits of its SHA-256. The address changes whenever the
    file does, so a page never runs with an older copy a browser kept (GitHub Pages lets browsers keep files 10 minutes)."""
    return "?v=" + hashlib.sha256((OUT / rel).read_bytes()).hexdigest()[:10]


SUBJECTS = [("s-philosophy", "Philosophy and religion"), ("s-psychology", "Psychology"), ("s-sociology", "Sociology"),
            ("s-politics", "Political science"), ("s-economics", "Economics"), ("s-warfare", "War and defense"),
            ("s-physics", "Physics and chemistry"), ("s-biology", "Biology and medicine"), ("s-tech", "Technology and AI"), ("s-future", "The future")]

# ---------------------------------------------------------------- the words, from site-text.txt (Jak edits that file)
SECTIONS = (["name", "page description", "tagline", "bio", "first screen links", "scroll cue", "writing intro", "writing note"]
            + [f"room note: {t}" for _, t in SUBJECTS]
            + ["atoms heading", "atoms plate note", "atoms lede", "atoms text", "atoms links", "featured heading", "projects count", "other software heading",
               "other software text", "other software link", "areas", "contact text", "contact line", "footer", "page not found"])
OPTIONAL = ["featured projects"]  # may be empty: nothing about it shows on the site until it has an item
TEXT_FILE = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else pathlib.Path(__file__).parent / "site-text.txt"
try:
    TEXT = sitetext.load(TEXT_FILE, SECTIONS, optional=OPTIONAL)
    FEATURED = [sitetext.split_item(p) for p in TEXT[sitetext.key("featured projects")]]
    ATOMS_LINKS = [sitetext.split_item(p) for p in TEXT[sitetext.key("atoms links")]]
    AREAS = [sitetext.split_item(p) for p in TEXT[sitetext.key("areas")]]
    COUNT = re.match(r"^(\d+)(\+?)\s+(.+)$", " ".join(TEXT["projects count"]))
    if not COUNT:
        raise sitetext.SiteTextError("site-text.txt: [projects count] must start with a number, for example: 80+ projects")
except sitetext.SiteTextError as e:
    print(e, file=sys.stderr)
    sys.exit(2)


SITE_URL = "https://jakpotvin.com/"  # the live address; canonical links, the sitemap and link previews use it
CARD = "assets/card.jpg"  # the picture link previews show (texts, LinkedIn, Slack); written by make_card() below
NAME = " ".join(TEXT["name"])


def social(title, url):
    """Head tags that give a page its address and its link preview card."""
    t, d = html.escape(title), html.escape(" ".join(TEXT["page description"]))
    return (f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="website">\n'
            f'<meta property="og:site_name" content="{html.escape(NAME)}">\n'
            f'<meta property="og:title" content="{t}">\n'
            f'<meta property="og:description" content="{d}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:image" content="{SITE_URL}{CARD}">\n'
            f'<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{{CARD_ALT}}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n')


def one(name, root=""):
    """A section's text as one line of HTML."""
    return sitetext.inline(" ".join(TEXT[sitetext.key(name)]), root)


def link_item(title, desc, plain_cls):
    """<li> for a list item; a title written as [words](address) becomes the link."""
    m = sitetext.LINK.fullmatch(title)
    if m:
        return (f'<li><a class="t" href="{html.escape(m.group(2))}">{html.escape(m.group(1), quote=False)}</a>'
                f'<span class="d">{sitetext.inline(desc)}</span></li>')
    return f'<li><span class="t">{sitetext.inline(title)}</span><span class="{plain_cls}">{sitetext.inline(desc)}</span></li>'
DRAFT = ""  # preview banner text; when empty, no banner is written

MOTION = """<script>{const ps=document.querySelectorAll('figure.plate');
if('IntersectionObserver' in window&&!matchMedia('(prefers-reduced-motion: reduce)').matches){
const io=new IntersectionObserver(es=>{for(const e of es){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}},{threshold:.2});
ps.forEach(p=>{p.classList.add('settle');io.observe(p)})}}</script>"""


def page(title, root, current, body, script="", home=False, url=None, head="", noindex=False):
    nav = [("Writing", f"{root}index.html#writing", "writing"), ("Projects", f"{root}index.html#projects", "projects"),
           ("Contact", f"{root}index.html#contact", "contact")]
    links = "".join(f'<a href="{h}"{" aria-current=page" if k == current else ""}>{t}</a>' for t, h, k in nav)
    banner = f'<div class="draft"><div class="wrap">{DRAFT}</div></div>\n' if DRAFT else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(" ".join(TEXT["page description"]))}">
{social(title, url).replace("{CARD_ALT}", CARD_ALT) if url else ""}{'<meta name="robots" content="noindex">' + chr(10) if noindex else ""}{head}<link rel="stylesheet" href="{root}assets/fonts/fonts.css{asset_v("assets/fonts/fonts.css")}">
<link rel="stylesheet" href="{root}assets/site.css{asset_v("assets/site.css")}">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{root}favicon.ico" sizes="32x32">
</head>
<body{' class="home"' if home else ""}>
{banner}<div class="wrap">
<header class="top"><a class="name" href="{root}index.html">Jak Potvin</a><nav aria-label="Site">{links}</nav></header>
{body}
<footer>{one("footer", root)}</footer>
</div>
{MOTION}
{script}{'<script src="assets/home.js' + asset_v("assets/home.js") + '" defer></script>' if home else ""}
</body>
</html>
"""


def plate(no, src, alt, caption, cls="", ratio=None, pos="50% 50%"):
    if src is None:
        return (f'<figure class="plate pending"><div class="frame" style="aspect-ratio:{ratio}"><span>Image to come</span></div>'
                f'<figcaption><span>{caption}</span></figcaption></figure>')
    style = f' style="aspect-ratio:{ratio}"' if ratio else ""
    img = (f'<img src="{src}" alt="{html.escape(alt)}"{"" if no == "I" else " loading=lazy"}'
           f'{f" style=\"height:100%;object-fit:cover;object-position:{pos}\"" if ratio else ""}>')
    return (f'<figure class="plate {cls}"><div class="frame"{style}>{img}</div>'
            f'<figcaption><span>{caption}</span></figcaption></figure>')


# The atoms page's drawing: an engraved-style silicon surface, two carbon pairs placed between the rows.
W, H = 640, 440
cells = []
for r in range(5):
    y = 52 + r * 84
    for c in range(13):
        x = 26 + c * 49
        cells.append(f'<line x1="{x}" y1="{y - 12}" x2="{x}" y2="{y + 12}" stroke="currentColor" stroke-width="3.2" opacity=".55"/>')
        for dy in (-14, 14):
            cells.append(f'<g transform="translate({x} {y + dy})"><circle r="12.5" fill="var(--paper)"/>'
                         f'<circle r="12.5" fill="url(#hatch)"/><circle r="12.5" fill="url(#lit)"/>'
                         f'<circle r="12.5" fill="none" stroke="currentColor" stroke-width="1"/></g>')
carbon = []
for x in (26 + 4 * 49, 26 + 5 * 49):
    y = 52 + 84 + 42
    carbon.append(f'<g><circle cx="{x}" cy="{y}" r="24" fill="var(--teal)" opacity=".13"/>'
                  f'<line x1="{x}" y1="{y - 10}" x2="{x}" y2="{y + 10}" stroke="var(--teal)" stroke-width="4"/>'
                  f'<circle cx="{x}" cy="{y - 10}" r="9" fill="var(--teal)"/><circle cx="{x}" cy="{y + 10}" r="9" fill="var(--teal)"/>'
                  f'<circle cx="{x - 3}" cy="{y - 13}" r="3" fill="var(--paper)" opacity=".7"/><circle cx="{x - 3}" cy="{y + 7}" r="3" fill="var(--paper)" opacity=".7"/></g>')
lattice = f"""<svg viewBox="0 0 {W} {H}" role="img" aria-label="Drawing of rows of paired silicon atoms seen from above, with two pairs of carbon atoms in teal placed in the trough between two rows." style="color:var(--ink);background:var(--paper)">
<defs><pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(40)"><line x1="0" y1="0" x2="0" y2="4" stroke="currentColor" stroke-width="1.1" opacity=".55"/></pattern>
<radialGradient id="lit" cx="34%" cy="30%" r="72%"><stop offset="0" stop-color="var(--paper)"/><stop offset=".45" stop-color="var(--paper)" stop-opacity=".92"/><stop offset="1" stop-color="var(--paper)" stop-opacity="0"/></radialGradient></defs>
{''.join(cells)}{''.join(carbon)}</svg>"""

LATTICE_CAPTION = 'The top layer of a silicon crystal, drawn for this site: rows of paired silicon atoms, with two carbon pairs (teal) placed between the rows.'

# ---------------------------------------------------------------- home: the plates
OUT_IMG = pathlib.Path(__file__).parent / "site" / "assets" / "img"
PLATES = [  # chronological by what is shown; (no, file, alt, year, what, subject, anchor, credit, column, grow, pos): column and grow are set below
 ("", "death-of-socrates.jpg", "Socrates, seated on his prison bed, reaches for the cup of hemlock with one hand and points upward with the other while his followers grieve.", "399 BC", "Socrates is condemned and drinks the hemlock", "Philosophy and religion", "#s-philosophy", "Jacques-Louis David, The Death of Socrates, 1787. The Metropolitan Museum of Art, New York.", 0, 0, "55% 45%"),
 ("", "alexander-mosaic.jpg", "Mosaic of Alexander the Great charging bareheaded on his horse Bucephalus, wide-eyed, a long spear in his hand and a Gorgon's face on his breastplate.", "333 BC", "Alexander defeats the Persian king Darius at Issus", "War and defense", "#s-warfare", "The Alexander Mosaic (detail), from the House of the Faun, Pompeii, c. 100 BC. National Archaeological Museum, Naples. Photograph by Gary Todd.", 0, 0, "52% 40%"),
 ("", "antikythera.jpg", "Three corroded green bronze fragments of an ancient geared machine, mounted on clear stands in a dark museum case.", "c. 100 BC", "Greek gears model the motions of the Sun and Moon", "Technology and AI", "#s-tech", "The Antikythera mechanism, bronze, c. 100 BC. National Archaeological Museum, Athens. Photograph by Peulle, licensed CC BY-SA 4.0.", 0, 0, "50% 45%"),
 ("", "death-of-caesar.jpg", "Senators in white togas raise daggers as Caesar, in a red cloak, sinks to the marble floor; others flee across the hall beneath a tall statue.", "44 BC", "Caesar is assassinated on the Ides of March", "Political science", "#s-politics", "Vincenzo Camuccini, The Death of Caesar, 1804 to 1805. Galleria Nazionale d&rsquo;Arte Moderna, Rome. Photograph by Daderot.", 0, 0, "40% 62%"),
 ("", "botticelli-augustine.jpg", "Saint Augustine at his desk, one hand on his chest, looking up from his books toward a light, with a clock and an armillary sphere on the shelf behind him.", "c. 400", "Augustine writes the Confessions", "Philosophy and religion", "#s-philosophy", "Sandro Botticelli, Saint Augustine in His Study, fresco, 1480. Church of Ognissanti, Florence.", 0, 0, "50% 30%"),
 ("", "magna-carta.jpg", "The Magna Carta of 1215: a sheet of parchment densely written in medieval Latin.", "1215", "King John seals Magna Carta at Runnymede", "Political science", "#s-politics", "Magna Carta, 1215. Cotton MS Augustus II.106, British Library, London.", 0, 0, "50% 40%"),
 ("", "vitruvian-man.jpg", "Leonardo da Vinci's drawing of a man in two overlapping poses inside a circle and a square.", "c. 1490", "Leonardo measures the human body", "Biology and medicine", "#s-biology", "Leonardo da Vinci, Vitruvian Man, pen and ink, c. 1490. Gallerie dell&rsquo;Accademia, Venice.", 0, 0, "50% 45%"),
 ("", "bosch-cure-of-folly.jpg", "In a round landscape framed by gold lettering, a surgeon in a funnel hat cuts into the head of a seated man, watched by a monk with a jug and a nun with a book balanced on her head.", "c. 1501", "A quack cuts out the stone of madness", "Psychology", "#s-psychology", "Workshop or follower of Hieronymus Bosch, The Cure of Folly (The Extraction of the Stone of Madness), c. 1501 to 1505. Museo del Prado, Madrid.", 0, 0, "50% 50%"),
 ("", "massys-moneylender.jpg", "A moneylender in a fur-collared coat weighs coins on a small balance while his wife, turning the pages of an illuminated book, looks over at the money; a round mirror on the table reflects a window.", "1514", "A moneylender weighs coins as his wife looks on", "Economics", "#s-economics", "Quentin Massys, The Moneylender and His Wife, 1514. Louvre, Paris.", 0, 0, "50% 60%"),
 ("", "bruegel-harvesters.jpg", "Peasants in a golden wheat field at harvest: some cut and bind the grain, others rest and eat together under a pear tree.", "1565", "Bruegel paints a village at harvest time", "Sociology", "#s-sociology", "Pieter Bruegel the Elder, The Harvesters, 1565. The Metropolitan Museum of Art, New York.", 0, 0, "55% 60%"),
 ("", "alchemist-full.jpg", "An old alchemist kneels in a dark, vaulted laboratory, gazing at a glass flask that glows with white light; two assistants work by candlelight in the shadows behind him.", "1669", "Hennig Brand discovers phosphorus", "Physics and chemistry", "#s-physics", "Joseph Wright of Derby, The Alchemist Discovering Phosphorus, 1771, reworked 1795. Derby Museum and Art Gallery.", 0, 0, "60% 70%"),
 ("", "adam-smith-statue.jpg", "Bronze statue of Adam Smith on a stone plinth, with St Giles' Cathedral behind him.", "1776", "Adam Smith publishes The Wealth of Nations", "Economics", "#s-economics", "Alexander Stoddart, statue of Adam Smith, bronze, 2008. Royal Mile, Edinburgh. Photograph by Stefan Schäfer, Lich, licensed CC BY-SA 4.0.", 0, 0, "66% 42%"),
 ("", "washington-crossing.jpg", "George Washington standing in a crowded rowing boat pushing through river ice, a flag behind him.", "1776", "Washington crosses the Delaware", "War and defense", "#s-warfare", "Emanuel Leutze, Washington Crossing the Delaware, 1851. The Metropolitan Museum of Art, New York.", 0, 0, "35% 45%"),
 ("", "jenner-hillemacher.jpg", "A doctor leans in to vaccinate a small child held on its mother's lap in a farmhouse, while a young man and a girl watch.", "1796", "Jenner gives the first vaccination against smallpox", "Biology and medicine", "#s-biology", "Eugène-Ernest Hillemacher, Edward Jenner Vaccinating a Boy, 1884. Wellcome Collection, licensed CC BY 4.0.", 0, 0, "55% 50%"),
 ("", "goya-sleep-of-reason.jpg", "A man slumped asleep over his desk while owls and bats swarm out of the darkness behind him and a lynx watches.", "1799", "Goya: the sleep of reason produces monsters", "Psychology", "#s-psychology", "Francisco Goya, The Sleep of Reason Produces Monsters, plate 43 of Los Caprichos, etching and aquatint, 1799.", 0, 0, "50% 55%"),
 ("", "napoleon-alps.jpg", "Napoleon in a billowing red cloak on a rearing white horse, pointing up toward a mountain pass; soldiers haul a cannon up the slope behind him.", "1800", "Napoleon crosses the Alps", "War and defense", "#s-warfare", "Jacques-Louis David, Napoleon Crossing the Alps, 1802 to 1803, one of five versions. Belvedere, Vienna.", 0, 0, "60% 30%"),
 ("", "wanderer-sea-of-fog.jpg", "A man in a dark coat stands with his back to us on a rocky summit, looking out over a sea of fog with mountains rising through it.", "c. 1817", "Friedrich's wanderer looks out over a sea of fog", "Philosophy and religion", "#s-philosophy", "Caspar David Friedrich, Wanderer above the Sea of Fog, c. 1817. Hamburger Kunsthalle, Hamburg.", 0, 0, "50% 42%"),
 ("", "faraday-lecture.jpg", "Michael Faraday stands at a demonstration table before a packed, tiered lecture theatre, with Prince Albert and two young princes in the front row.", "1855", "Faraday gives a Christmas lecture at the Royal Institution", "Physics and chemistry", "#s-physics", "After Alexander Blaikley, Professor Faraday Lecturing at the Royal Institution, 27 December 1855. Royal Institution, London.", 0, 0, "62% 55%"),
 ("", "verne-earth-to-moon.jpg", "Engraving of a huge cone-shaped shell hung with American flags beside a tall crane, men in top hats looking on.", "1865", "Verne imagines a cannon shot to the Moon", "The future", "#s-future", "Henri de Montaut, illustration for Jules Verne, From the Earth to the Moon (1865), in an 1874 edition. National Library of Poland.", 0, 0, "50% 45%"),
 ("", "seurat-grande-jatte.jpg", "Parisians of every kind, in top hats, bustles and work clothes, resting and strolling on a sunny riverbank, painted in dots.", "1884", "Parisians of every class share a Sunday afternoon", "Sociology", "#s-sociology", "Georges Seurat, A Sunday on La Grande Jatte, 1884 to 1886. The Art Institute of Chicago.", 0, 0, "50% 50%"),
 ("", "ford-assembly-line.jpg", "Rows of workmen in caps bend over a long waist-high line, fitting parts onto round flywheels that slide along it.", "1913", "Ford's moving assembly line begins", "Economics", "#s-economics", "Workers on a Ford Motor Company assembly line, 1913. U.S. National Archives.", 0, 0, "45% 50%"),
 ("", "freud-halberstadt.jpg", "Sigmund Freud, grey-bearded, in a three-piece suit with a watch chain, holds a cigar and looks straight at the camera, one hand on his hip.", "c. 1921", "Freud, the founder of psychoanalysis", "Psychology", "#s-psychology", "Max Halberstadt, photograph of Sigmund Freud, c. 1921.", 0, 0, "50% 25%"),
 ("", "iwo-jima.jpg", "Six servicemen strain together to raise a pole flying the American flag on a rubble-strewn hilltop.", "1945", "Marines raise the flag on Iwo Jima", "War and defense", "#s-warfare", "Joe Rosenthal, Associated Press, Raising the Flag on Iwo Jima, 23 February 1945. U.S. National Archives.", 0, 0, "45% 50%"),
 ("", "eniac.jpg", "Two women stand at ENIAC's tall panels of switches, dials and cables, one reaching up to a setting.", "1946", "ENIAC, the first general-purpose electronic computer, is unveiled", "Technology and AI", "#s-tech", "Betty Jennings (left) and Frances Bilas prepare ENIAC for its public unveiling, February 1946. U.S. Army photograph.", 0, 0, "45% 50%"),
 ("", "kennedy-von-braun.jpg", "Wernher von Braun and President Kennedy look and point upward beside a model rocket, officials crowding around them.", "1963", "Von Braun shows Kennedy the Saturn rocket", "The future", "#s-future", "NASA photograph, Cape Canaveral, 16 November 1963.", 0, 0, "55% 35%"),
 ("", "berlin-wall-1989.jpg", "At night, floodlights show a graffiti-covered stretch of the Berlin Wall beside the Brandenburg Gate; a crane rises over a new gap in the wall where people gather.", "1989", "The Berlin Wall is opened at the Brandenburg Gate", "Political science", "#s-politics", "East and West Germans meet at a new opening in the Berlin Wall beside the Brandenburg Gate, after a crane lifted out a section, 21 December 1989. Photograph by SSgt F. Lee Corkran, U.S. Air Force.", 0, 0, "55% 55%"),
 ("", "atlas-detector.jpg", "The ATLAS particle detector in its underground hall: a huge cylinder of metal plates, pipes and cables, ringed by scaffolding and yellow walkways.", "2012", "ATLAS helps find the Higgs boson", "Physics and chemistry", "#s-physics", "The ATLAS detector at CERN&rsquo;s Large Hadron Collider, 2019. Photograph by SimonWaldherr, licensed CC BY-SA 4.0.", 0, 0, "60% 55%"),
 ("", "shibuya-crossing.jpg", "Seen from above, crowds stream in every direction across a scramble crossing between tall buildings covered in signs and screens.", "2017", "Crowds cross at Shibuya, Tokyo", "Sociology", "#s-sociology", "Shibuya Crossing, Tokyo, December 2017. Photograph by Mark D, licensed CC BY-SA 2.0.", 0, 0, "55% 65%"),
 ("", "summit-supercomputer.jpg", "A long row of black computer cabinets with blue panels and green lights, the nearest marked Summit, Oak Ridge and IBM.", "2018", "Summit becomes the world's fastest computer", "Technology and AI", "#s-tech", "The Summit supercomputer, Oak Ridge National Laboratory, 2018. Photograph by Carlos Jones, ORNL, licensed CC BY 2.0.", 0, 0, "50% 45%"),
 ("", "sars-cov-2.jpg", "Colourized electron microscope image: countless small gold virus particles cluster on and stream from the blue surface of a cell.", "2020", "The virus behind COVID-19, under the microscope", "Biology and medicine", "#s-biology", "SARS-CoV-2 particles (gold) emerging from a cell grown in the lab; scanning electron micrograph, colourized, Rocky Mountain Laboratories. NIAID, licensed CC BY 2.0.", 0, 0, "50% 45%"),
 ("", "webb-cosmic-cliffs.jpg", "Glowing orange clouds of gas and dust rise like a mountain range under a deep blue sky full of bright, spiked stars.", "2022", "Webb's first images show stars being born", "The future", "#s-future", "The Cosmic Cliffs in the Carina Nebula, James Webb Space Telescope, July 2022. NASA, ESA, CSA and STScI.", 0, 0, "50% 50%"),
]
# each plate's column and height share (from the old album wall; kept so the plate tuples keep their shape)
from PIL import Image as _Img
_cols, _h, _ps = 4, [0.0] * 4, []
PLATES = [_p for _p in PLATES if (OUT_IMG / _p[1]).exists()]
for _p in PLATES:
    _w, _hh = _Img.open(OUT_IMG / _p[1]).size; _g = min(max(_hh / _w, 0.55), 1.3)
    _c = min(range(_cols), key=lambda i: _h[i]); _h[_c] += _g
    _ps.append(_p[:8] + (_c, round(_g, 3), _p[10]))
PLATES = _ps
# blurred copy of each plate (images.py), the backdrop of plates shown whole on the first screen
import images
SIZE = {}
for _p in PLATES:
    images.write_copies(OUT_IMG / _p[1], None, OUT_IMG / "blur")
    with _Img.open(OUT_IMG / _p[1]) as _im:
        SIZE[_p[1]] = _im.size
WHOLE = {f: images.show_whole(*wh) for f, wh in SIZE.items()}
for _stale in (OUT_IMG / "blur").glob("*.jpg"):  # a plate removed from PLATES, or whose file is gone, leaves no copy behind
    if _stale.name not in SIZE:
        _stale.unlink()
import shutil
shutil.rmtree(OUT_IMG / "small", ignore_errors=True)  # the album's small copies; the home page no longer has an album
def roman(n):
    out = ""
    for v, s in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v: out += s; n -= v
    return out
PLATES = [(roman(i + 1),) + p[1:] for i, p in enumerate(PLATES)]
BANNER_FILE = "washington-crossing.jpg"  # the first screen's painting: credited, captioned with its room's link, shown in no room
BANNER = next(p for p in PLATES if p[1] == BANNER_FILE)
NO = {p[1]: p[0] for p in PLATES}
LATTICE_NO = roman(len(PLATES) + 1)
SHORT_BY_FILE = {"death-of-socrates.jpg": "David, The Death of Socrates", "alexander-mosaic.jpg": "The Alexander Mosaic, Pompeii",
    "antikythera.jpg": "The Antikythera mechanism", "death-of-caesar.jpg": "Camuccini, The Death of Caesar",
    "botticelli-augustine.jpg": "Botticelli, Saint Augustine in His Study", "magna-carta.jpg": "Magna Carta, 1215", "vitruvian-man.jpg": "Leonardo, Vitruvian Man",
    "bosch-cure-of-folly.jpg": "Bosch workshop or follower, The Cure of Folly", "massys-moneylender.jpg": "Massys, The Moneylender and His Wife",
    "bruegel-harvesters.jpg": "Bruegel, The Harvesters", "alchemist-full.jpg": "Wright of Derby, The Alchemist",
    "adam-smith-statue.jpg": "Stoddart, Adam Smith", "washington-crossing.jpg": "Leutze, Washington Crossing the Delaware",
    "jenner-hillemacher.jpg": "Hillemacher, Jenner Vaccinating a Boy", "goya-sleep-of-reason.jpg": "Goya, The Sleep of Reason Produces Monsters",
    "napoleon-alps.jpg": "David, Napoleon Crossing the Alps", "wanderer-sea-of-fog.jpg": "Friedrich, Wanderer above the Sea of Fog",
    "faraday-lecture.jpg": "After Blaikley, Faraday Lecturing", "verne-earth-to-moon.jpg": "De Montaut, From the Earth to the Moon",
    "seurat-grande-jatte.jpg": "Seurat, A Sunday on La Grande Jatte", "ford-assembly-line.jpg": "Ford assembly line, 1913",
    "freud-halberstadt.jpg": "Halberstadt, Sigmund Freud", "iwo-jima.jpg": "Rosenthal, Raising the Flag on Iwo Jima",
    "eniac.jpg": "U.S. Army, ENIAC", "kennedy-von-braun.jpg": "NASA, Kennedy and von Braun", "berlin-wall-1989.jpg": "U.S. Air Force, The Berlin Wall opened",
    "atlas-detector.jpg": "The ATLAS detector, CERN", "shibuya-crossing.jpg": "Shibuya Crossing, Tokyo", "summit-supercomputer.jpg": "Summit, Oak Ridge",
    "sars-cov-2.jpg": "NIAID, SARS-CoV-2", "webb-cosmic-cliffs.jpg": "NASA, Webb's Cosmic Cliffs"}
SHORT = {p[0]: SHORT_BY_FILE[p[1]] for p in PLATES}
def plate_data(p):
    """The data-* attributes home.js reads for a painting's caption."""
    no, f, alt, yr, what, subj, href, credit, col, grow, pos = p
    return " ".join(f'data-{k}="{html.escape(v, quote=True)}"' for k, v in
                    (("yr", yr), ("what", what), ("subj", subj), ("href", href), ("credit", SHORT[no]), ("no", no)))
def slide(p, on=False, eager=False):
    """One painting filling the screen: the banner, or one of a room's paintings. An eager one has its image address
    set; the others keep it in data-src until home.js loads them. A tall or small painting (images.show_whole) also
    gets its blurred copy behind it (about 4 KB, always loaded)."""
    no, f, alt, yr, what, subj, href, credit, col, grow, pos = p
    w, h = SIZE[f]
    whole = WHOLE[f]
    src = f'src="assets/img/{f}" fetchpriority="high"' if eager else f'data-src="assets/img/{f}"'
    bg = f'<img class="bg" src="assets/img/blur/{f}" alt="">' if whole else ""
    cls = "slide" + (" whole" if whole else "") + (" on" if on else "")
    return (f'<figure class="{cls}" {plate_data(p)}>{bg}'
            f'<img class="art" {src} alt="" style="--w:{w};--h:{h};--pos:{pos};object-position:{pos}"></figure>')
first = BANNER

# ---------------------------------------------------------------- writing: one room per subject
def room(anchor, title):
    """A subject's room: about one screen of scrolling per painting plus half a screen. Its paintings (lazy; home.js
    loads them as the visitor nears the room) fill the screen behind the title, one at a time, chosen by how far the
    room has been scrolled; the caption names the painting showing, starting with the first."""
    ps = [p for p in PLATES if p[6] == "#" + anchor and p[1] != BANNER_FILE]
    slides = "".join(slide(p, on=(k == 0)) for k, p in enumerate(ps))
    cap = (f'<div class="caption"><span class="yr">{ps[0][3]}</span> <span class="what">{ps[0][4]}</span> '
           f'<span class="credit">{SHORT[ps[0][0]]}</span></div>') if ps else ""
    return (f'<section class="room" id="{anchor}" style="--n:{max(len(ps), 1)}" aria-labelledby="{anchor}-h"><div class="room-stick">'
            f'<div class="room-bg" aria-hidden="true"><div class="slides">{slides}</div><div class="room-shade"></div></div>'
            f'<div class="room-words"><div class="room-text"><h2 id="{anchor}-h">{title}</h2>'
            f'<p class="room-soon">{one("room note: " + title)}</p></div>{cap}</div></div></section>')
OUT.mkdir(exist_ok=True)
ROOMS = '<div class="rooms">' + "".join(room(a, t) for a, t in SUBJECTS) + '</div>'

BIO = one("bio")
def make_card():
    """The 1200x630 link preview picture: the banner painting, darkened at the left and at the bottom, with the name."""
    from PIL import Image, ImageChops, ImageDraw, ImageFont
    w, h = 1200, 630
    with Image.open(OUT_IMG / BANNER[1]) as im:
        im = im.convert("RGB")
        im = im.crop((round(im.width * .01), round(im.height * .01), round(im.width * .99), round(im.height * .99)))  # drop the photo's dark edge
        scale = max(w / im.width, h / im.height)
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        left, top = (im.width - w) // 2, (im.height - h) // 2
        im = im.crop((left, top, left + w, top + h))
    left = Image.new("L", (w, 1))
    left.putdata([round(200 * max(0.0, 1 - x / (w * 0.55))) for x in range(w)])
    bottom = Image.new("L", (1, h))
    bottom.putdata([round(235 * min(1.0, max(0.0, (y - 0.4 * h) / (0.35 * h)))) for y in range(h)])
    shade = ImageChops.lighter(left.resize((w, h)), bottom.resize((w, h)))  # the darker of the two shades at each point
    im = Image.composite(Image.new("RGB", (w, h), (10, 9, 8)), im, shade)
    d = ImageDraw.Draw(im)
    fonts = OUT / "assets" / "fonts"
    d.text((72, h - 132), NAME, font=ImageFont.truetype(str(fonts / "libre-caslon-display-normal-400-latin.woff2"), 100),
           fill=(245, 241, 234), anchor="ls")
    d.text((76, h - 76), SITE_URL.split("//")[1].rstrip("/"), font=ImageFont.truetype(str(fonts / "IBMPlexSans-Regular-Latin1.woff2"), 30),
           fill=(220, 213, 202), anchor="ls")
    im.save(OUT / CARD, "JPEG", quality=85, optimize=True, progressive=True)


make_card()
CARD_ALT = html.escape(f"{NAME}, over a detail of {SHORT[BANNER[0]]}")
# who the site belongs to, for search engines: the name, the address, and the https links in [contact line]
_same = [a for _, a in sitetext.LINK.findall(" ".join(TEXT[sitetext.key("contact line")])) if a.startswith("https://")]


def ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>\n"


PERSON_LD = (ld({"@context": "https://schema.org", "@type": "Person", "name": NAME, "url": SITE_URL, "sameAs": _same})
             + ld({"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE_URL}))

FEATURED_BLOCK = "" if not FEATURED else f"""<div class="split" style="margin-top:clamp(32px,4vw,56px)">
<div class="stack">
<h3>{one("featured heading")}</h3>
</div>
<ul class="links featured">
{chr(10).join(link_item(t, d, "d") for t, d in FEATURED)}
</ul>
</div>
"""

home = page("Jak Potvin", "", "home", f"""
<section class="intro" aria-label="Introduction">
<div class="intro-stage">
<div class="hero">
<div class="slides" aria-hidden="true">
{slide(BANNER, on=True, eager=True)}
</div>
<div class="shade" aria-hidden="true"></div>
<div class="intro-text">
<h1>{one("name")}</h1>
<p class="lede">{one("tagline")}</p>
<p class="note">{BIO}</p>
<nav class="intro-links" aria-label="Jump to">{" ".join(sitetext.inline(x) for x in TEXT["first screen links"])}</nav>
</div>
<div class="caption">
<span class="yr">{first[3]}</span>
<span class="what">{first[4]}</span>
<a class="subj" href="{first[6]}">{first[5]}</a>
<span class="credit">{SHORT[first[0]]}</span>
</div>
<p class="cue">{one("scroll cue")}</p>
</div>
</div>
</section>

<section id="writing" aria-labelledby="writing-h">
<div class="split">
<h2 id="writing-h">Writing</h2>
<div class="stack">
<p class="lede">{one("writing intro")}</p>
<p class="small">{one("writing note")}</p>
</div>
</div>
</section>
{ROOMS}

<section id="projects" aria-labelledby="projects-h">
<div class="split">
<div class="stack">
<h2 id="projects-h">Projects</h2>
<h3 style="margin-top:18px">{one("atoms heading")}</h3>
<p class="small">{one("atoms plate note")}</p>
</div>
<div class="stack">
<p class="lede">{one("atoms lede")}</p>
<p>{one("atoms text")}</p>
<ul class="links narrow">
{chr(10).join(link_item(t, d, "soon") for t, d in ATOMS_LINKS)}
</ul>
</div>
</div>
{FEATURED_BLOCK}<div class="split" style="margin-top:clamp(32px,4vw,56px)">
<div class="stack">
<p class="count"><span class="n" data-to="{COUNT.group(1)}">{COUNT.group(1)}</span><span class="plus">{COUNT.group(2)}</span> <span class="lab">{sitetext.inline(COUNT.group(3))}</span></p>
<h3>{one("other software heading")}</h3>
<p class="small">{one("other software text")}</p>
<p class="small">{one("other software link")}</p>
</div>
<ul class="links areas">
{chr(10).join(link_item(t, d, "d") for t, d in AREAS)}
</ul>
</div>
</section>

<section id="contact" aria-labelledby="contact-h" style="border-bottom:1px solid var(--ink)">
<div class="split">
<h2 id="contact-h">Contact</h2>
<div class="stack">
<p>{one("contact text")}</p>
<p class="small">{one("contact line")}</p>
</div>
</div>
</section>
""", home=True, url=SITE_URL, head=PERSON_LD)

# ---------------------------------------------------------------- atoms page
data = json.load(open(COUNTS))
by_id = {e["id"]: e for e in data["entries"] if e["tip_kind"] == "mechanosynthesis_tool"}
GROUPS = [
    ("Adding carbon to a prepared site", [("cbn-fig5i-ir-c2", "First carbon pair"), ("cbn-fig5j-2ir-c2", "Second pair beside it"),
                                          ("cbn-fig5k-ir-c2-c4", "Extending one pair to four atoms"), ("cbn-fig5l-2ir-c4", "Extending the second pair")]),
    ("Adding carbon to bare silicon", [("blue-c2-donation-eaoge", "Earlier tool, no prepared site")]),
    ("Removing hydrogen", [("barrera-h-abstraction-first-db", "First hydrogen, from anywhere"),
                           ("barrera-h-abstraction-first-db-on-target", "First hydrogen, from the targeted atom"),
                           ("barrera-h-abstraction-second-db", "Second hydrogen, from anywhere"),
                           ("barrera-ir-db-pair-configuration", "Second hydrogen, in the right place")]),
    ("Removing silicon", [("blue-si-abstraction-maoc-4k", "Redesigned tool at 4 K"), ("blue-si-abstraction-maoc-77k", "Redesigned tool at 77 K")]),
]
used = {i for _, rows in GROUPS for i, _ in rows}
assert used == set(by_id), set(by_id) ^ used  # every mechanosynthesis entry is shown once
pos = lambda v: max(0.0, (v * 100 - 40) / 60 * 100)
fmt = lambda v: f"{v * 100:.1f}".rstrip("0").rstrip(".") + "%"
rows = []
for title, items in GROUPS:
    rows.append(f"<h4>{title}</h4>")
    for i, label in items:
        e = by_id[i]; p = e["k"] / e["n"]; lo, hi = e["wilson_low"], e["wilson_high"]
        rows.append(
            f'<div class="row"><span>{label}</span><span class="n"><b>{e["k"]} of {e["n"]}</b> &middot; {fmt(p)}</span>'
            f'<span class="track" role="img" aria-label="{fmt(p)}, 95% range {fmt(lo)} to {fmt(hi)}">'
            f'<span class="band" style="left:{pos(lo):.1f}%;width:{pos(hi) - pos(lo):.1f}%"></span>'
            f'<span class="dot" style="left:{pos(p):.1f}%"></span></span></div>')
chart = ('<div class="chart"><div class="axis"><span></span><span></span><span class="scale">'
         '<span style="left:0">40%</span><span style="left:33.3%">60%</span><span style="left:66.7%">80%</span>'
         '<span style="left:100%">100%</span></span></div>' + "".join(rows) + "</div>")

atoms_page = page("Atom by atom | Jak Potvin", "../", "projects", f"""
<section aria-labelledby="atoms-h">
<div class="split">
<div class="stack">
<h1 id="atoms-h">Atom by atom</h1>
<p class="lede">AI is making design nearly free. Making things is becoming the bottleneck. Atomically precise manufacturing is how the physical world catches up, and it starts with knowing how reliable each atomic step is.</p>
<p>I build the open data and tools that measure that. This page sets out what has been measured so far, using only published counts.</p>
</div>
<figure class="plate"><div class="frame">{lattice}</div><figcaption><span>{LATTICE_CAPTION}</span></figcaption></figure>
</div>
<div class="figures">
<div><span class="v">84 to 97%</span><span class="k">Success of each step in a published four-step carbon build at 4 K.</span><span class="tag">Measured</span></div>
<div><span class="v">About 10</span><span class="k">Longest counted run of steps in a row: silicon atoms removed one by one at 77 K.</span><span class="tag">Measured</span></div>
<div><span class="v">5%</span><span class="k">Share of 100-site arrays that come out perfect at 97% per site, the best measured dopant placement.</span><span class="tag">Calculated</span></div>
<div><span class="v">1 in 100,000</span><span class="k">Most failed steps a check could miss, for a million-step part to come out perfect half the time.</span><span class="tag">Model</span></div>
</div>
</section>

<section aria-labelledby="counts-h">
<h2 id="counts-h">Every published step with a count</h2>
<p style="margin-top:12px">Dot: the measured rate. Bar: its 95% range, which is wide when the count is small. Each count comes with the sentence it was read from, checked by script against the paper.</p>
{chart}
<p class="small" style="margin-top:16px">Sources: three preprints from CBN Nano Technologies, <a href="https://arxiv.org/abs/2605.27250">arXiv:2605.27250</a>, <a href="https://arxiv.org/abs/2606.13876">arXiv:2606.13876</a> and <a href="https://arxiv.org/abs/2512.24431">arXiv:2512.24431</a>. None is peer reviewed yet, and none has been repeated by a second lab.</p>
</section>

<section aria-labelledby="edit-h">
<div class="split">
<h2 id="edit-h">Editing comes before building</h2>
<div class="stack">
<p>Building a whole object atom by atom is decades away. Editing a few atoms in a valuable device is not. Quantum processors are already made by placing single phosphorus atoms in silicon, and a useful device needs only about ten of them in the right places.</p>
<p>The hard part is scale. At 97% per site, a ten-atom device comes out right about three times in four, but a hundred-site array comes out perfect only one time in twenty. That makes checking every site, and reworking the failures, the real job. It is the part I work on.</p>
</div>
</div>
</section>

<section aria-labelledby="build-h">
<h2 id="build-h">What I build</h2>
<ul class="links" style="margin-top:22px">
<li><span class="t">mechdb</span><span class="d">An open dataset of atom-by-atom fabrication outcomes, each tied to its source. On GitHub from 15 December.</span></li>
<li><span class="t">A verification budget</span><span class="d">A paper on how reliable each step, check and repair must be for a long build. In preparation.</span></li>
<li><a class="t" href="calculator/index.html">Atom Factory Calculator</a><span class="d">Good parts per day from measured rates, with every input labelled measured, estimated or made up.</span></li>
<li><span class="t">The bottleneck map</span><span class="d">Each obstacle to this kind of manufacturing, with today&rsquo;s best number and the number needed. Published 15 December.</span></li>
<li><span class="t">sidb-check</span><span class="d">A checker for published logic gates built from single silicon atoms. In preparation.</span></li>
</ul>
</section>

<section aria-labelledby="moves-h">
<h2 id="moves-h">What would move the question</h2>
<p style="margin-top:12px">Whether this becomes manufacturing is unproven. In the papers I have read, none of these has been reported yet. Each would change the picture.</p>
<ol class="moves">
<li>A build of a hundred steps or more, with the outcome of every step counted.</li>
<li>A failed step detected and repaired, with how often the check misses and how often the repair works.</li>
<li>A spent tool reloaded and used again, with counts.</li>
<li>Carbon placed well above 4 K. Silicon removal has been shown at 77 K.</li>
<li>The same step repeated by a second, independent lab.</li>
<li>Raw outcome data released, so others can check the counts.</li>
</ol>
</section>
""", url=SITE_URL + "atoms/")


# ---------------------------------------------------------------- list of plates (full credits)
FULL = {p[0]: p[7] for p in PLATES}
FULL[NO["kennedy-von-braun.jpg"]] = "Wernher von Braun explains the Saturn rocket to President John F. Kennedy, Cape Canaveral, 16 November 1963. NASA photograph."
FULL[LATTICE_NO] = "The top layer of a silicon crystal, drawn for this site."
US_GOV = "Work of the U.S. government; public domain."
NASA = "NASA images are generally not subject to copyright in the United States."
NOTE_BY_FILE = {"eniac.jpg": US_GOV, "berlin-wall-1989.jpg": US_GOV, "kennedy-von-braun.jpg": NASA, "webb-cosmic-cliffs.jpg": NASA,
    "iwo-jima.jpg": "Public domain in the United States: its copyright was not renewed.",
    **{f: "Wikimedia Commons." for f in ("adam-smith-statue.jpg", "magna-carta.jpg", "death-of-caesar.jpg", "alexander-mosaic.jpg", "antikythera.jpg",
                                         "atlas-detector.jpg", "shibuya-crossing.jpg", "summit-supercomputer.jpg", "sars-cov-2.jpg")}}
NOTES = {NO[f]: t for f, t in NOTE_BY_FILE.items() if f in NO}
YEAR = {p[0]: p[3] for p in PLATES}
YEAR[LATTICE_NO] = "Atoms page"
CC_LICENCE = re.compile(r"CC (BY(?:-SA)?) (\d\.\d)")
def link_licence(credit):
    """'CC BY-SA 2.0' in a credit becomes a link to that licence's page at creativecommons.org."""
    return CC_LICENCE.sub(lambda m: f'<a href="https://creativecommons.org/licenses/{m.group(1).lower()}/{m.group(2)}/">{m.group(0)}</a>', credit)
items = "\n".join(f'<li><span class="pl">{YEAR[n]}</span><span>{link_licence(FULL[n])}{(" " + NOTES[n]) if n in NOTES else ""}</span></li>' for n in [p[0] for p in PLATES] + [LATTICE_NO])
plates_page = page("Picture credits | Jak Potvin", "", "", f"""
<section aria-labelledby="pl-h">
<h1 id="pl-h" style="font-size:clamp(36px,5vw,56px)">Picture credits</h1>
<p class="small" style="margin-top:12px">Paintings, drawings and sculpture reproduced here are in the public domain; photographs are credited to their makers. Where a picture is used under a Creative Commons licence, the licence is linked. The copies here are resized, and some are cropped.</p>
<ol class="plates-list">
{items}
</ol>
</section>
""", url=SITE_URL + "plates.html")
OUT.mkdir(exist_ok=True)
(OUT / "index.html").write_text(home, encoding="utf-8", newline="\n")
(OUT / "plates.html").write_text(plates_page, encoding="utf-8", newline="\n")
(OUT / "atoms").mkdir(exist_ok=True)
(OUT / "atoms" / "index.html").write_text(atoms_page, encoding="utf-8", newline="\n")
calc = open(CALC, encoding="utf-8").read()
back = ('<p style="max-width:1180px;margin:0 auto;padding:14px 20px 0;font:14px/1.5 \'IBM Plex Sans\',system-ui,sans-serif">'
        '<a href="../index.html">Atom by atom</a> &middot; <a href="../../index.html#projects">Jak Potvin, projects</a></p>')
assert calc.count("<body>") == 1
(OUT / "atoms" / "calculator").mkdir(exist_ok=True)
assert calc.count("</head>") == 1 and "<title>" in calc
calc_title = html.unescape(re.search(r"<title>(.*?)</title>", calc).group(1))
calc_head = (f'<meta name="description" content="{html.escape(" ".join(TEXT["page description"]))}">\n'
             + social(calc_title, SITE_URL + "atoms/calculator/").replace("{CARD_ALT}", CARD_ALT))
assert calc.count('href="../../assets/fonts/fonts.css"') == 1
calc = calc.replace('href="../../assets/fonts/fonts.css"', 'href="../../assets/fonts/fonts.css' + asset_v("assets/fonts/fonts.css") + '"', 1)
calc = calc.replace("</head>", calc_head + "</head>", 1).replace("<body>", "<body>\n" + back, 1)
(OUT / "atoms" / "calculator" / "index.html").write_text(calc, encoding="utf-8", newline="\n")
# a broken link anywhere on the site lands here; GitHub Pages serves 404.html at any depth, so every address starts with /
not_found = page("Page not found | Jak Potvin", "/", "", f"""
<section aria-labelledby="nf-h">
<h1 id="nf-h" style="font-size:clamp(36px,5vw,56px)">Page not found</h1>
<p style="margin-top:12px">{one("page not found", "/")}</p>
<p><a href="/index.html">Go to the home page</a></p>
</section>
""", noindex=True)
(OUT / "404.html").write_text(not_found, encoding="utf-8", newline="\n")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8", newline="\n")
ADDRESSES = [SITE_URL, SITE_URL + "atoms/", SITE_URL + "atoms/calculator/", SITE_URL + "plates.html"]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                 + "".join(f"<url><loc>{a}</loc></url>\n" for a in ADDRESSES) + "</urlset>\n", encoding="utf-8", newline="\n")
(OUT / "CNAME").write_text("jakpotvin.com\n", newline="\n")
(OUT / ".nojekyll").write_text("")
print("built", sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file()))
