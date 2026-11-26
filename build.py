"""Build jakpotvin.com. Run from this folder: python build.py data/counts.json data/calculator.html (needs Pillow)."""
import html, json, re, sys, pathlib

import sitetext

COUNTS, CALC = sys.argv[1], sys.argv[2]
OUT = pathlib.Path(__file__).parent / "site"
SUBJECTS = [("s-philosophy", "Philosophy and religion"), ("s-psychology", "Psychology"), ("s-sociology", "Sociology"),
            ("s-politics", "Political science"), ("s-economics", "Economics"), ("s-warfare", "War and defense"),
            ("s-physics", "Physics and chemistry"), ("s-biology", "Biology and medicine"), ("s-tech", "Technology and AI"), ("s-future", "The future")]

# ---------------------------------------------------------------- the words, from site-text.txt (Jak edits that file)
SECTIONS = (["name", "page description", "tagline", "bio", "first screen links", "scroll cue", "writing intro", "writing note"]
            + [f"room note: {t}" for _, t in SUBJECTS]
            + ["atoms heading", "atoms plate note", "atoms lede", "atoms text", "atoms links", "projects count", "other software heading",
               "other software text", "other software link", "areas", "contact text", "contact line", "footer"])
TEXT_FILE = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else pathlib.Path(__file__).parent / "site-text.txt"
try:
    TEXT = sitetext.load(TEXT_FILE, SECTIONS)
    ATOMS_LINKS = [sitetext.split_item(p) for p in TEXT[sitetext.key("atoms links")]]
    AREAS = [sitetext.split_item(p) for p in TEXT[sitetext.key("areas")]]
    COUNT = re.match(r"^(\d+)(\+?)\s+(.+)$", " ".join(TEXT["projects count"]))
    if not COUNT:
        raise sitetext.SiteTextError("site-text.txt: [projects count] must start with a number, for example: 80+ projects")
except sitetext.SiteTextError as e:
    print(e, file=sys.stderr)
    sys.exit(2)


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


def page(title, root, current, body, script="", home=False):
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
<link rel="stylesheet" href="{root}assets/fonts/fonts.css">
<link rel="stylesheet" href="{root}assets/site.css">
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
{script}{'<script src="assets/home.js" defer></script>' if home else ""}
</body>
</html>
"""


def plate(no, src, alt, caption, cls="", ratio=None, pos="50% 50%"):
    if src is None:
        return (f'<figure class="plate pending"><div class="frame" style="aspect-ratio:{ratio}"><span>Image to come</span></div>'
                f'<figcaption><b>Plate {no}.</b><span>{caption}</span></figcaption></figure>')
    style = f' style="aspect-ratio:{ratio}"' if ratio else ""
    img = (f'<img src="{src}" alt="{html.escape(alt)}"{"" if no == "I" else " loading=lazy"}'
           f'{f" style=\"height:100%;object-fit:cover;object-position:{pos}\"" if ratio else ""}>')
    return (f'<figure class="plate {cls}"><div class="frame"{style}>{img}</div>'
            f'<figcaption><b>Plate {no}.</b><span>{caption}</span></figcaption></figure>')


# Plate IV: an engraved-style drawing of the silicon surface, two carbon pairs placed between the rows.
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

# ---------------------------------------------------------------- home: the album wall
OUT_IMG = pathlib.Path(__file__).parent / "site" / "assets" / "img"
PLATES = [  # chronological by what is shown; (no, file, alt, year, what, subject, anchor, credit, column, grow, pos): column and grow are set below
 ("I", "death-of-socrates.jpg", "Socrates, seated on his prison bed, reaches for the cup of hemlock with one hand and points upward with the other while his followers grieve.", "399 BC", "Socrates is condemned and drinks the hemlock", "Philosophy and religion", "#s-philosophy", "Jacques-Louis David, The Death of Socrates, 1787. The Metropolitan Museum of Art, New York.", 0, 0, "55% 45%"),
 ("II", "school-of-athens.jpg", "Plato pointing upward and Aristotle gesturing toward the ground, among other philosophers in a painted hall.", "c. 360 BC", "Plato and Aristotle at the Academy", "Philosophy and religion", "#s-philosophy", "Raphael, The School of Athens (detail), fresco, 1509 to 1511. Apostolic Palace, Vatican.", 0, 0, "50% 40%"),
 ("III", "caesar-coustou.jpg", "Marble statue of Julius Caesar in a laurel wreath and armour, holding a baton and looking sharply to one side.", "49 BC", "Caesar crosses the Rubicon", "Political science", "#s-politics", "Nicolas Coustou, Julius Caesar, marble, commissioned 1696. Louvre, Paris. Photograph by Marie-Lan Nguyen.", 0, 0, "50% 20%"),
 ("", "botticelli-augustine.jpg", "Saint Augustine at his desk, one hand on his chest, looking up from his books toward a light, with a clock and an armillary sphere on the shelf behind him.", "c. 400", "Augustine writes the Confessions", "Philosophy and religion", "#s-philosophy", "Sandro Botticelli, Saint Augustine in His Study, fresco, 1480. Church of Ognissanti, Florence.", 0, 0, "50% 30%"),
 ("IV", "coronation-charlemagne.jpg", "Charlemagne kneels as the pope lowers a crown onto his head, courtiers and clergy crowded around.", "800", "Charlemagne crowned emperor in Rome", "Political science", "#s-politics", "Friedrich Kaulbach, The Coronation of Charlemagne, 1861. Maximilianeum, Munich.", 0, 0, "62% 50%"),
 ("", "magna-carta.jpg", "The Magna Carta of 1215: a sheet of parchment densely written in medieval Latin.", "1215", "King John seals Magna Carta at Runnymede", "Political science", "#s-politics", "Magna Carta, 1215. Cotton MS Augustus II.106, British Library, London.", 0, 0, "50% 40%"),
 ("V", "vitruvian-man.jpg", "Leonardo da Vinci's drawing of a man in two overlapping poses inside a circle and a square.", "c. 1490", "Leonardo measures the human body", "Biology and medicine", "#s-biology", "Leonardo da Vinci, Vitruvian Man, pen and ink. Gallerie dell&rsquo;Accademia, Venice.", 0, 0, "50% 45%"),
 ("", "bruegel-harvesters.jpg", "Peasants in a golden wheat field at harvest: some cut and bind the grain, others rest and eat together under a pear tree.", "1565", "Bruegel paints a village at harvest time", "Sociology", "#s-sociology", "Pieter Bruegel the Elder, The Harvesters, 1565. The Metropolitan Museum of Art, New York.", 0, 0, "55% 60%"),
 ("VI", "newton-romney.jpg", "Isaac Newton, seated, holds a prism up to a beam of sunlight while two women look on.", "1666", "Newton splits sunlight with a prism", "Physics and chemistry", "#s-physics", "Newton with the Prism. Stipple engraving by R. M. Meadows, 1809, after George Romney. Wellcome Collection.", 0, 0, "72% 50%"),
 ("VII", "alchemist-phosphorus.jpg", "An old man kneels in a dark laboratory, gazing at a glass flask that glows with white light.", "1669", "Hennig Brand discovers phosphorus", "Physics and chemistry", "#s-physics", "Joseph Wright of Derby, The Alchemist Discovering Phosphorus (detail), 1771, reworked 1795. Derby Museum and Art Gallery.", 0, 0, "50% 50%"),
 ("VIII", "adam-smith-statue.jpg", "Bronze statue of Adam Smith on a stone plinth, with St Giles' Cathedral behind him.", "1776", "Adam Smith publishes The Wealth of Nations", "Economics", "#s-economics", "Alexander Stoddart, statue of Adam Smith, bronze, 2008. Royal Mile, Edinburgh. Photograph by Stefan Schäfer, Lich, licensed CC BY-SA 4.0.", 0, 0, "66% 42%"),
 ("IX", "washington-crossing.jpg", "George Washington standing in a crowded rowing boat pushing through river ice, a flag behind him.", "1776", "Washington crosses the Delaware", "War and defense", "#s-warfare", "Emanuel Leutze, Washington Crossing the Delaware, 1851. The Metropolitan Museum of Art, New York.", 0, 0, "33% 50%"),
 ("X", "jenner-hillemacher.jpg", "A doctor leans in to vaccinate a small child held on its mother's lap in a farmhouse, a boy and a girl watching.", "1796", "Jenner gives the first vaccination against smallpox", "Biology and medicine", "#s-biology", "Eugène-Ernest Hillemacher, Edward Jenner Vaccinating a Boy, 1884. Wellcome Collection.", 0, 0, "55% 50%"),
 ("", "goya-sleep-of-reason.jpg", "A man slumped asleep over his desk while owls and bats swarm out of the darkness behind him and a lynx watches.", "1799", "Goya: the sleep of reason produces monsters", "Psychology", "#s-psychology", "Francisco Goya, The Sleep of Reason Produces Monsters, plate 43 of Los Caprichos, etching and aquatint, 1799. The Metropolitan Museum of Art, New York.", 0, 0, "50% 50%"),
 ("XI", "napoleon-alps.jpg", "Napoleon in a billowing red cloak on a rearing white horse, pointing up toward a mountain pass.", "1800", "Napoleon crosses the Alps", "War and defense", "#s-warfare", "Jacques-Louis David, Napoleon Crossing the Alps, one of five versions painted from 1801.", 0, 0, "56% 40%"),
 ("XIII", "iron-rolling-mill.jpg", "Workers with long tongs guide a white-hot iron bar into a rolling machine in a vast factory hall.", "1875", "A rolling mill making railway track", "Economics", "#s-economics", "Adolph Menzel, The Iron Rolling Mill, 1872 to 1875. Nationalgalerie, Berlin.", 0, 0, "47% 50%"),
 ("XIV", "seurat-grande-jatte.jpg", "Parisians of every kind, in top hats, bustles and work clothes, resting and strolling on a sunny riverbank, painted in dots.", "1884", "Parisians of every class share a Sunday afternoon", "Sociology", "#s-sociology", "Georges Seurat, A Sunday on La Grande Jatte, 1884 to 1886. The Art Institute of Chicago.", 0, 0, "50% 50%"),
 ("XV", "charcot-salpetriere.jpg", "Charcot stands before a packed room of physicians and students, presenting a fainting woman held up by an assistant and a nurse.", "1887", "Charcot lectures on hysteria at the Salpêtrière", "Psychology", "#s-psychology", "André Brouillet, A Clinical Lesson at the Salpêtrière, 1887. Paris Descartes University.", 0, 0, "60% 50%"),
 ("XVI", "first-flight.jpg", "A biplane lifts a few feet off the sand at Kitty Hawk while a man watches from the right.", "1903", "The first powered flight, Kitty Hawk", "Technology and AI", "#s-tech", "Photograph by John T. Daniels, 17 December 1903: Orville Wright at the controls, Wilbur alongside. Library of Congress.", 0, 0, "56% 50%"),
 ("", "eniac.jpg", "Rows of tall panels covered in switches, dials and cables fill a room, with operators setting up the machine.", "1946", "ENIAC, the first general-purpose electronic computer, is unveiled", "Technology and AI", "#s-tech", "ENIAC at the Moore School, University of Pennsylvania, 1946. U.S. Army Photo.", 0, 0, "50% 50%"),
 ("XVII", "kennedy-von-braun.jpg", "Wernher von Braun and President Kennedy, both looking and pointing upward, beside a model Saturn rocket.", "1963", "Von Braun shows Kennedy the Saturn rocket", "The future", "#s-future", "NASA photograph, Cape Canaveral, 16 November 1963.", 0, 0, "50% 38%"),
 ("XVIII", "earthrise.jpg", "The Earth, half lit, rising above the grey horizon of the Moon against black space.", "1968", "Apollo 8 sees the Earth rise over the Moon", "The future", "#s-future", "Earthrise. Photograph by William Anders, Apollo 8, 24 December 1968. NASA.", 0, 0, "56% 55%"),
]
# lay the album out automatically: four columns, each plate goes to the shortest column so far (keeps rough date order)
from PIL import Image as _Img
_cols, _h, _ps = 4, [0.0] * 4, []
PLATES = [_p for _p in PLATES if (OUT_IMG / _p[1]).exists()]
for _p in PLATES:
    _w, _hh = _Img.open(OUT_IMG / _p[1]).size; _g = min(max(_hh / _w, 0.55), 1.3)
    _c = min(range(_cols), key=lambda i: _h[i]); _h[_c] += _g
    _ps.append(_p[:8] + (_c, round(_g, 3), _p[10]))
PLATES = _ps
# copies of each plate (images.py): small/ for the album, blur/ for the backdrop of plates shown whole
import images
SIZE = {}
for _p in PLATES:
    images.write_copies(OUT_IMG / _p[1], OUT_IMG / "small", OUT_IMG / "blur")
    with _Img.open(OUT_IMG / _p[1]) as _im:
        SIZE[_p[1]] = _im.size
WHOLE = {f: images.show_whole(*wh) for f, wh in SIZE.items()}
for _d in ("small", "blur"):  # a plate removed from PLATES, or whose file is gone, leaves no copies behind
    for _stale in (OUT_IMG / _d).glob("*.jpg"):
        if _stale.name not in SIZE:
            _stale.unlink()
def roman(n):
    out = ""
    for v, s in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v: out += s; n -= v
    return out
PLATES = [(roman(i + 1),) + p[1:] for i, p in enumerate(PLATES)]
NO = {p[1]: p[0] for p in PLATES}
LATTICE_NO = roman(len(PLATES) + 1)
SHORT_BY_FILE = {"death-of-socrates.jpg": "David, The Death of Socrates", "school-of-athens.jpg": "Raphael, The School of Athens",
    "caesar-coustou.jpg": "Coustou, Julius Caesar", "coronation-charlemagne.jpg": "Kaulbach, The Coronation of Charlemagne",
    "magna-carta.jpg": "Magna Carta, 1215", "botticelli-augustine.jpg": "Botticelli, Saint Augustine in His Study", "vitruvian-man.jpg": "Leonardo, Vitruvian Man",
    "newton-romney.jpg": "Meadows after Romney, Newton with the Prism", "alchemist-phosphorus.jpg": "Wright of Derby, The Alchemist",
    "adam-smith-statue.jpg": "Stoddart, Adam Smith", "washington-crossing.jpg": "Leutze, Washington Crossing the Delaware",
    "jenner-hillemacher.jpg": "Hillemacher, Jenner Vaccinating a Boy", "napoleon-alps.jpg": "David, Napoleon Crossing the Alps",
    "iron-rolling-mill.jpg": "Menzel, The Iron Rolling Mill", "seurat-grande-jatte.jpg": "Seurat, A Sunday on La Grande Jatte",
    "charcot-salpetriere.jpg": "Brouillet, A Clinical Lesson", "bruegel-harvesters.jpg": "Bruegel, The Harvesters",
    "goya-sleep-of-reason.jpg": "Goya, The Sleep of Reason Produces Monsters", "first-flight.jpg": "Daniels, First Flight",
    "kennedy-von-braun.jpg": "NASA, Kennedy and von Braun", "eniac.jpg": "U.S. Army, ENIAC", "earthrise.jpg": "Anders, Earthrise"}
SHORT = {p[0]: SHORT_BY_FILE[p[1]] for p in PLATES}
def plate_data(p):
    """The data-* attributes the slideshow and the album caption read for a plate."""
    no, f, alt, yr, what, subj, href, credit, col, grow, pos = p
    return " ".join(f'data-{k}="{html.escape(v, quote=True)}"' for k, v in
                    (("yr", yr), ("what", what), ("subj", subj), ("href", href), ("credit", SHORT[no]), ("no", no)))
def tile(i, p):
    no, f, alt, yr, what, subj, href, credit, col, grow, pos = p
    img = f'<img src="assets/img/small/{f}" alt="{html.escape(alt)}" style="object-position:{pos}" loading=lazy>'
    inner = f'<a href="{href}">{img}</a>' if href else img
    return (f'<figure class="tile" data-i="{i}" {plate_data(p)} style="flex-grow:{grow};order:{i}">{inner}'
            f'<figcaption class="no">Plate {no}</figcaption></figure>')
def slide(i, p):
    """One plate of the first-screen slideshow; only the first has its image address set, home.js loads the rest."""
    no, f, alt, yr, what, subj, href, credit, col, grow, pos = p
    w, h = SIZE[f]
    whole = WHOLE[f]
    src = f'src="assets/img/{f}" fetchpriority="high"' if i == 0 else f'data-src="assets/img/{f}"'
    bg = f'<img class="bg" src="assets/img/blur/{f}" alt="">' if whole else ""
    cls = "slide" + (" whole" if whole else "") + (" on" if i == 0 else "")
    return (f'<figure class="{cls}" data-i="{i}" {plate_data(p)}>{bg}'
            f'<img class="art" {src} alt="{html.escape(alt)}" style="--w:{w};--h:{h};object-position:{pos}"></figure>')
cols = ["".join(tile(i, p) for i, p in enumerate(PLATES) if p[8] == c) for c in range(4)]
wall = "".join(f'<div class="col">{c}</div>' for c in cols)
first = PLATES[0]

def row(anchor, title):
    nos = [p[0] for p in PLATES if p[6] == "#" + anchor]
    label = ("Plate to come" if not nos else ("Plate " if len(nos) == 1 else "Plates ") + " and ".join(nos))
    cr = "; ".join(SHORT[n] for n in nos)
    return f'<li id="{anchor}"><span class="pl">{label}</span><h3>{title}</h3><span class="cr">{cr}</span><span class="soon">First essay from 15 December</span></li>'
index = "\n".join(row(a, t) for a, t in SUBJECTS)


# ---------------------------------------------------------------- writing: one room per subject
import colorsys
from PIL import Image
ROOM_TEXT = {
 "s-philosophy": "How to think, what to value, and what we can know.",
 "s-psychology": "Why people think and act the way they do.",
 "s-sociology": "How groups, institutions and cultures hold together, and how they come apart.",
 "s-politics": "Who holds power, how they got it, and what keeps it in check.",
 "s-economics": "How wealth is made, traded and lost.",
 "s-warfare": "Strategy, technology, and why wars are won.",
 "s-physics": "Matter and energy, down to single atoms.",
 "s-biology": "Life, the body, and how to keep it working.",
 "s-future": "Where technology is taking us, and what to do about it.",
}
ROOM_FILE = {"alchemist-phosphorus.jpg": ("alchemist-full.jpg", 1100 / 1427)}
ROOM_BG = {  # wall colours picked from each room's painting; auto-sampling made too many of them brown
 "s-philosophy": "#1f2a44",  # Aristotle's blue robe
 "s-psychology": "#3b1e16",  # the Salpêtrière's red walls
 "s-sociology": "#3a3014",   # Bruegel's wheat field
 "s-politics": "#3a1620",    # Charlemagne's crimson
 "s-economics": "#3a2010",   # the mill's furnace light
 "s-warfare": "#232a33",     # the winter sky over the Delaware
 "s-physics": "#1d1a36",     # the alchemist's night window
 "s-biology": "#3a2e18",     # Leonardo's sepia
 "s-tech": "#2e2c28",        # the dunes at Kill Devil Hills, in shadow
 "s-future": "#102f3d",      # the Florida sky
}  # rooms show the whole painting where the album shows a detail
def room_colour(path):
    im = Image.open(path).convert("RGB"); im.thumbnail((96, 96))
    q = im.quantize(colors=8, method=Image.Quantize.MEDIANCUT); pal = q.getpalette(); best = None
    for count, idx in q.getcolors():
        r, g, bl = (c / 255 for c in pal[idx * 3: idx * 3 + 3]); h, l, s = colorsys.rgb_to_hls(r, g, bl)
        score = count * (0.08 + s) * (0.25 + min(l, 1 - l))
        if best is None or score > best[0]: best = (score, h, s)
    _, h, s = best
    r, g, bl = colorsys.hls_to_rgb(h, 0.16, min(max(s, 0.18), 0.42))
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(bl * 255))
def aspect(f):
    w, h = Image.open(OUT / "assets" / "img" / f).size; return w / h
def room(anchor, title):
    ps = [p for p in PLATES if p[6] == "#" + anchor]
    if ps:
        files = [ROOM_FILE.get(p[1], (p[1], None))[0] for p in ps]
        asp = [aspect(f) for f in files]; bg = room_colour(OUT / "assets" / "img" / files[0])
        rows, cur, s = [], [], 0.0
        for item in zip(ps, files, asp):
            if cur and s + item[2] > 2.6: rows.append(cur); cur, s = [], 0.0
            cur.append(item); s += item[2]
        rows.append(cur)
        per_width = sum(1 / sum(x[2] for x in r) for r in rows)
        fig = lambda p, f, a: (f'<figure class="plate rp" style="flex:{a:.3f} 1 0"><img src="assets/img/{f}" alt="{html.escape(p[2])}" loading="lazy" style="aspect-ratio:{a:.4f}">'
                               f'<figcaption><b>Plate {p[0]}.</b> {SHORT[p[0]]}</figcaption></figure>')
        inner = "".join('<div class="room-row">' + "".join(fig(*x) for x in r) + '</div>' for r in rows)
        plates = f'<div class="room-plates rows" style="max-width:min(100%, calc(68svh / {per_width:.3f}))">{inner}</div>'
        nos = [p[0] for p in ps]; label = ("Plate " if len(nos) == 1 else "Plates ") + (nos[0] if len(nos) == 1 else ", ".join(nos[:-1]) + " and " + nos[-1])
    else:
        bg = "#23262b"
        plates = '<div class="room-plates"><div class="room-empty">Plate to come</div></div>'
        label = "Plate to come"
    bg = ROOM_BG.get(anchor, bg)
    return (f'<section class="room" id="{anchor}" data-bg="{bg}" style="--bg:{bg}" aria-labelledby="{anchor}-h"><div class="room-in">'
            f'<div class="room-text"><p class="room-pl">{label}</p><h2 id="{anchor}-h">{title}</h2>'
            f'<p class="room-soon">{one("room note: " + title)}</p></div>{plates}</div></section>')
OUT.mkdir(exist_ok=True)
ROOMS = ('<div class="rooms">' + "".join(room(a, t) for a, t in SUBJECTS)
         + f'<div class="rooms-stage" style="grid-row:1 / span {len(SUBJECTS)}"></div></div>')  # home.js pins the plates here on desktop

BIO = one("bio")
home = page("Jak Potvin", "", "home", f"""
<section class="intro" aria-label="Introduction">
<div class="intro-stage">
<div class="hero">
<div class="slides" data-current="0">
{chr(10).join(slide(i, p) for i, p in enumerate(PLATES))}
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
<span class="credit"><b>Plate {first[0]}.</b> {SHORT[first[0]]}</span>
</div>
<button class="pause" type="button" aria-pressed="false" aria-label="Pause the slideshow"><span aria-hidden="true"></span></button>
<p class="cue">{one("scroll cue")}</p>
</div>
<div class="album">
<div class="wall">{wall}</div>
<p class="album-caption"><span class="yr">{first[3]}</span> <span class="what">{first[4]}</span> <a class="subj" href="{first[6]}">{first[5]}</a> <span class="credit"><b>Plate {first[0]}.</b> {SHORT[first[0]]}</span></p>
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
<p class="small">Plate {NO["alchemist-phosphorus.jpg"]}: {one("atoms plate note")}</p>
</div>
<div class="stack">
<p class="lede">{one("atoms lede")}</p>
<p>{one("atoms text")}</p>
<ul class="links narrow">
{chr(10).join(link_item(t, d, "soon") for t, d in ATOMS_LINKS)}
</ul>
</div>
</div>
<div class="split" style="margin-top:clamp(32px,4vw,56px)">
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
""", home=True)

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
<figure class="plate"><div class="frame">{lattice}</div><figcaption><b>Plate {LATTICE_NO}.</b><span>{LATTICE_CAPTION}</span></figcaption></figure>
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
""")


# ---------------------------------------------------------------- list of plates (full credits)
FULL = {p[0]: p[7] for p in PLATES}
FULL[NO["alchemist-phosphorus.jpg"]] = FULL[NO["alchemist-phosphorus.jpg"]].replace(" (detail)", "")
FULL[NO["kennedy-von-braun.jpg"]] = "Wernher von Braun explains the Saturn rocket to President John F. Kennedy, Cape Canaveral, 16 November 1963. NASA photograph."
FULL[LATTICE_NO] = "The top layer of a silicon crystal, drawn for this site."
NOTE_BY_FILE = {"caesar-coustou.jpg": "Wikimedia Commons.", "eniac.jpg": "Work of the U.S. government; public domain.", "adam-smith-statue.jpg": "Wikimedia Commons.", "magna-carta.jpg": "Wikimedia Commons.",
    "kennedy-von-braun.jpg": "NASA images are generally not subject to copyright in the United States.",
    "earthrise.jpg": "NASA images are generally not subject to copyright in the United States."}
NOTES = {NO[f]: t for f, t in NOTE_BY_FILE.items() if f in NO}
items = "\n".join(f'<li><span class="pl">Plate {n}</span><span>{FULL[n]}{(" " + NOTES[n]) if n in NOTES else ""}</span></li>' for n in [p[0] for p in PLATES] + [LATTICE_NO])
plates_page = page("List of plates | Jak Potvin", "", "", f"""
<section aria-labelledby="pl-h">
<h1 id="pl-h" style="font-size:clamp(36px,5vw,56px)">List of plates</h1>
<p class="small" style="margin-top:12px">Paintings, drawings and sculpture reproduced here are in the public domain; photographs are credited to their makers.</p>
<ol class="plates-list">
{items}
</ol>
</section>
""")
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
(OUT / "atoms" / "calculator" / "index.html").write_text(calc.replace("<body>", "<body>\n" + back, 1), encoding="utf-8", newline="\n")
(OUT / "CNAME").write_text("jakpotvin.com\n", newline="\n")
(OUT / ".nojekyll").write_text("")
print("built", sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file()))
