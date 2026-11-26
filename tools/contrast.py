"""Contrast of text over whatever is behind it (a painting, a shade), measured the way WCAG defines it.

text_contrast() hides all text, takes one screenshot, and for each element takes the pixel at the 90th percentile of
brightness inside the element's box as its background: the text has to stand out against nearly the brightest part of
what is behind it. The text shadow is ignored, so the measure errs on the strict side."""
import io
import json
import re

from PIL import Image

HIDE = ("*, *::before, *::after { color: transparent !important; text-shadow: none !important; "
        "text-decoration-color: transparent !important; } .caption, .room-soon { border-color: transparent !important; }")


def luminance(rgb):
    """WCAG relative luminance of an sRGB colour given as 0 to 255 values."""
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb[:3]
    return round(0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b), 12)


def contrast(a, b):
    """WCAG contrast ratio of two colours, from 1 to 21, in either order."""
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def over(rgba, rgb):
    """A colour with alpha (0 to 1) painted over an opaque one."""
    r, g, b, a = rgba
    return tuple(a * c + (1 - a) * d for c, d in zip((r, g, b), rgb))


def _rgba(css):
    v = [float(x) for x in re.findall(r"[\d.]+", css)]
    return (v + [1.0])[:4]


def text_contrast(page, selectors):
    """{selector: contrast ratio} for each selector whose first element is on screen with a non-zero box."""
    found = page.eval("(sels => sels.map(s => { const el = document.querySelector(s); if (!el) return null;"
                      " const r = el.getBoundingClientRect(), c = getComputedStyle(el);"
                      " if (!r.width || !r.height || c.visibility === 'hidden' || r.bottom <= 0 || r.top >= innerHeight) return null;"
                      " return [s, r.left, r.top, r.right, r.bottom, c.color, devicePixelRatio]; }))(%s)" % json.dumps(selectors))
    page.eval("(() => { const s = document.createElement('style'); s.id = 'contrast-hide'; s.textContent = %s;"
              " document.head.appendChild(s); return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); })()"
              % json.dumps(HIDE))
    try:
        shot = Image.open(io.BytesIO(page.screenshot_png())).convert("RGB")
    finally:
        page.eval("document.getElementById('contrast-hide').remove(); 1")
    out = {}
    for item in found:
        if item is None:
            continue
        sel, left, top, right, bottom, color, dpr = item
        box = (max(0, round(left * dpr)), max(0, round(top * dpr)), min(shot.width, round(right * dpr)), min(shot.height, round(bottom * dpr)))
        if box[2] <= box[0] or box[3] <= box[1]:
            continue
        data = shot.crop(box).tobytes()
        pixels = sorted((data[i:i + 3] for i in range(0, len(data), 3)), key=luminance)
        bg = tuple(pixels[min(len(pixels) - 1, int(len(pixels) * 0.9))])
        out[sel] = contrast(over(_rgba(color), bg), bg)
    return out
