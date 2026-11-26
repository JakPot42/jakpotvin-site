"""Copies of each plate for the site: a tiny blurred one for the backdrop of plates shown whole on the first screen
(and, when asked for, a small one). The source files in site/assets/img/ are used as they are for the slideshow."""
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
    """Write src's blurred copy into blur_dir and, when small_dir is given, its small copy there, under the same file name."""
    src, blur_dir = Path(src), Path(blur_dir)
    blur_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        if small_dir is not None:
            Path(small_dir).mkdir(parents=True, exist_ok=True)
            _fit(im, SMALL_LONG_SIDE).save(Path(small_dir) / src.name, "JPEG", quality=82, progressive=True, optimize=True)
        _fit(im, BLUR_LONG_SIDE).filter(ImageFilter.GaussianBlur(BLUR_RADIUS)).save(blur_dir / src.name, "JPEG", quality=70)
