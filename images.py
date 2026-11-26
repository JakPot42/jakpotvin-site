"""Copies of each plate for the site: a small one for the album, a tiny blurred one for the backdrop of plates
shown whole on the first screen. The source files in site/assets/img/ are used as they are for the slideshow."""
from pathlib import Path

from PIL import Image, ImageFilter

SMALL_LONG_SIDE = 900
BLUR_LONG_SIDE = 96
BLUR_RADIUS = 6
WHOLE_MAX_UPSCALE = 1.5


def show_whole(width, height):
    """True when a plate should be shown whole on the first screen: tall, square, or too small to fill it sharply."""
    return width / height < 1.2 or width < 1400


def _fit(im, long_side):
    w, h = im.size
    scale = min(1.0, long_side / max(w, h))
    size = (max(1, round(w * scale)), max(1, round(h * scale)))
    return im if size == (w, h) else im.resize(size, Image.LANCZOS)


def write_copies(src, small_dir, blur_dir):
    """Write src's small copy into small_dir and its blurred copy into blur_dir, under the same file name."""
    src, small_dir, blur_dir = Path(src), Path(small_dir), Path(blur_dir)
    small_dir.mkdir(parents=True, exist_ok=True)
    blur_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        _fit(im, SMALL_LONG_SIDE).save(small_dir / src.name, "JPEG", quality=82, progressive=True, optimize=True)
        _fit(im, BLUR_LONG_SIDE).filter(ImageFilter.GaussianBlur(BLUR_RADIUS)).save(blur_dir / src.name, "JPEG", quality=70)
