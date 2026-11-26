import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.browser import EDGE, Browser, Site  # noqa: E402


@pytest.fixture(scope="session")
def site():
    with Site() as s:
        yield s


def _browser(**kw):
    if not EDGE.exists():
        pytest.skip(f"Microsoft Edge is not installed at {EDGE}; browser tests skipped")
    return Browser(**kw)


@pytest.fixture(scope="session")
def browser():
    with _browser() as b:
        yield b


@pytest.fixture(scope="session")
def browser_nosda():
    with _browser(no_scroll_timeline=True) as b:
        yield b
