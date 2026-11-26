import pytest
from PIL import Image

from images import BLUR_LONG_SIDE, SMALL_LONG_SIDE, show_whole, write_copies


@pytest.mark.parametrize("w, h, whole", [(2000, 1319, False), (1158, 1800, True), (1100, 1100, True), (630, 455, True),
                                         (1400, 900, False), (1399, 900, True), (1800, 1002, False)])
def test_show_whole_rule(w, h, whole):
    assert show_whole(w, h) is whole


def make_source(path, size):
    im = Image.new("RGB", size)
    px = im.load()
    for x in range(0, size[0], 7):
        for y in range(0, size[1], 5):
            px[x, y] = ((x * 3) % 256, (y * 5) % 256, (x + y) % 256)
    im.save(path, quality=95, exif=Image.Exif())
    return path


def test_copies_sizes(tmp_path):
    big = make_source(tmp_path / "big.jpg", (2000, 1000))
    small_dir, blur_dir = tmp_path / "small", tmp_path / "blur"
    write_copies(big, small_dir, blur_dir)
    assert SMALL_LONG_SIDE == 900 and BLUR_LONG_SIDE == 96
    assert Image.open(small_dir / "big.jpg").size == (900, 450)
    assert Image.open(blur_dir / "big.jpg").size == (96, 48)
    tiny = make_source(tmp_path / "tiny.jpg", (630, 455))
    write_copies(tiny, small_dir, blur_dir)
    assert Image.open(small_dir / "tiny.jpg").size == (630, 455)


def test_copies_deterministic(tmp_path):
    src = make_source(tmp_path / "a.jpg", (1200, 800))
    write_copies(src, tmp_path / "s1", tmp_path / "b1")
    write_copies(src, tmp_path / "s2", tmp_path / "b2")
    assert (tmp_path / "s1" / "a.jpg").read_bytes() == (tmp_path / "s2" / "a.jpg").read_bytes()
    assert (tmp_path / "b1" / "a.jpg").read_bytes() == (tmp_path / "b2" / "a.jpg").read_bytes()


def test_copies_have_no_metadata(tmp_path):
    src = make_source(tmp_path / "a.jpg", (1200, 800))
    write_copies(src, tmp_path / "s", tmp_path / "b")
    for p in (tmp_path / "s" / "a.jpg", tmp_path / "b" / "a.jpg"):
        info = Image.open(p).info
        assert "exif" not in info and "icc_profile" not in info, p


def test_copies_are_progressive_small_and_blurred(tmp_path):
    src = make_source(tmp_path / "a.jpg", (1200, 800))
    write_copies(src, tmp_path / "s", tmp_path / "b")
    assert Image.open(tmp_path / "s" / "a.jpg").info.get("progressive") == 1
    assert (tmp_path / "b" / "a.jpg").stat().st_size < 4000
