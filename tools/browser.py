"""Headless Microsoft Edge for the site's browser tests, over the DevTools protocol (standard library only).

Site() serves site/ on 127.0.0.1. Browser() starts Edge with a throwaway profile in which every host except
127.0.0.1 is unresolvable, so any request the pages make to another host shows up as a failure.
"""
import base64
import functools
import http.server
import json
import os
import select
import shutil
import socket
import struct
import subprocess
import tempfile
import threading
import time
import urllib.parse
from pathlib import Path

EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
SITE_DIR = Path(__file__).resolve().parent.parent / "site"
DESKTOP = dict(width=1440, height=900, mobile=False)
PHONE = dict(width=412, height=915, mobile=True)
CRLF = "\r\n"


def open_home(browser, site, cfg, hash=""):
    """Open the home page with a viewport config such as DESKTOP or {**PHONE, "reduced_motion": True}."""
    return browser.open(site.url("index.html" + hash), **cfg)


class _WS:
    """Minimal WebSocket client (text frames, client masking, ping replies)."""

    def __init__(self, url):
        u = urllib.parse.urlparse(url)
        self.s = socket.create_connection((u.hostname, u.port), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET {u.path} HTTP/1.1{CRLF}Host: {u.hostname}:{u.port}{CRLF}Upgrade: websocket{CRLF}"
               f"Connection: Upgrade{CRLF}Sec-WebSocket-Key: {key}{CRLF}Sec-WebSocket-Version: 13{CRLF}{CRLF}")
        self.s.sendall(req.encode())
        buf = b""
        while (CRLF + CRLF).encode() not in buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise RuntimeError("DevTools handshake closed")
            buf += chunk
        head, self.rest = buf.split((CRLF + CRLF).encode(), 1)
        if b" 101 " not in head.split(CRLF.encode())[0]:
            raise RuntimeError("DevTools handshake failed")

    def _exact(self, n):
        out = bytearray()
        if self.rest:
            take = self.rest[:n]
            out += take
            self.rest = self.rest[len(take):]
        while len(out) < n:
            chunk = self.s.recv(min(1 << 20, n - len(out)))
            if not chunk:
                raise RuntimeError("DevTools socket closed")
            out += chunk
        return bytes(out)

    def _frame(self, op, data):
        hdr = bytearray([0x80 | op])
        n = len(data)
        if n < 126:
            hdr.append(0x80 | n)
        elif n < 65536:
            hdr.append(0x80 | 126)
            hdr += struct.pack(">H", n)
        else:
            hdr.append(0x80 | 127)
            hdr += struct.pack(">Q", n)
        mask = os.urandom(4)
        hdr += mask
        self.s.sendall(bytes(hdr) + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def send(self, text):
        self._frame(1, text.encode())

    def recv(self, timeout):
        if not self.rest:
            r, _, _ = select.select([self.s], [], [], timeout)
            if not r:
                return None
        msg = bytearray()
        while True:
            b0, b1 = self._exact(2)
            op, fin, n = b0 & 0x0F, b0 & 0x80, b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._exact(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._exact(8))[0]
            mask = self._exact(4) if b1 & 0x80 else None
            payload = self._exact(n)
            if mask:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            if op == 9:
                self._frame(0xA, payload)
                continue
            if op == 8:
                raise RuntimeError("DevTools connection closed by the browser")
            if op == 0xA:
                continue
            msg += payload
            if fin:
                return msg.decode("utf-8")

    def close(self):
        try:
            self.s.close()
        except OSError:
            pass


class _CDP:
    def __init__(self, ws):
        self.ws, self.n, self.events = ws, 0, []

    def _take(self, raw):
        m = json.loads(raw)
        if "method" in m:
            self.events.append(m)
        return m

    def call(self, method, params=None, session=None, timeout=60):
        self.n += 1
        mid = self.n
        msg = {"id": mid, "method": method, "params": params or {}}
        if session:
            msg["sessionId"] = session
        self.ws.send(json.dumps(msg))
        end = time.time() + timeout
        while time.time() < end:
            raw = self.ws.recv(max(0.05, end - time.time()))
            if raw is None:
                continue
            m = self._take(raw)
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})
        raise TimeoutError(method)

    def pump(self, seconds):
        end = time.time() + seconds
        while time.time() < end:
            raw = self.ws.recv(max(0.01, end - time.time()))
            if raw:
                self._take(raw)

    def wait_event(self, name, session, start, timeout=30):
        end = time.time() + timeout
        while True:
            for m in self.events[start:]:
                if m["method"] == name and m.get("sessionId") == session:
                    return m
            if time.time() > end:
                raise TimeoutError(name)
            self.pump(0.1)


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class _Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 128  # the default (5) refuses connections when a page asks for many files at once


class Site:
    """Serves a folder (default: site/) on 127.0.0.1 at a free port, from a background thread."""

    def __init__(self, root=SITE_DIR):
        self.root = Path(root)

    def __enter__(self):
        handler = functools.partial(_QuietHandler, directory=str(self.root))
        self.server = _Server(("127.0.0.1", 0), handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def url(self, path=""):
        return f"http://127.0.0.1:{self.port}/{path}"

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(5)


NO_SCROLL_TIMELINE = """(() => { const real = CSS.supports.bind(CSS);
  CSS.supports = (...a) => /animation-timeline|view-timeline|scroll-timeline|animation-range/.test(a.join(' ')) ? false : real(...a); })();"""


class Browser:
    """Headless Edge with a fresh profile.

    no_scroll_timeline=True makes pages see no CSS scroll-driven animation support (CSS.supports answers false),
    the way an older browser does; Edge's own switch for the feature no longer turns it off."""

    def __init__(self, no_scroll_timeline=False):
        self.no_scroll_timeline = no_scroll_timeline
        self.page = None

    def __enter__(self):
        self.profile = tempfile.mkdtemp(prefix="jakpotvin-edge-")
        args = [str(EDGE), "--headless=new", "--remote-debugging-port=0", f"--user-data-dir={self.profile}",
                "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--disable-sync",
                "--disable-background-networking", "--disable-component-update", "--disable-default-apps",
                "--hide-scrollbars", "--mute-audio",
                "--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1"]
        args.append("about:blank")
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        portfile = Path(self.profile) / "DevToolsActivePort"
        for _ in range(300):
            if portfile.exists() and len(portfile.read_text().split()) >= 2:
                break
            time.sleep(0.1)
        else:
            self.__exit__(None, None, None)
            raise RuntimeError("Edge did not start (no DevToolsActivePort)")
        port, path = portfile.read_text().split()[:2]
        self.cdp = _CDP(_WS(f"ws://127.0.0.1:{port}{path}"))
        return self

    def open(self, url, width, height, mobile=False, reduced_motion=False, javascript=True, kbps=None, latency=0):
        """Open url in a fresh tab and wait for its load event. kbps (kilobits a second) and latency (ms) slow the
        connection, as on a weak phone signal."""
        if self.page is not None:
            self.page.close()
        cdp = self.cdp
        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        s = cdp.call("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        for domain in ("Page.enable", "Runtime.enable", "Log.enable", "Network.enable"):
            cdp.call(domain, {}, s)
        cdp.call("Network.setCacheDisabled", {"cacheDisabled": True}, s)
        if kbps:
            cdp.call("Network.emulateNetworkConditions", {"offline": False, "latency": latency,
                     "downloadThroughput": kbps * 1000 / 8, "uploadThroughput": kbps * 1000 / 8}, s)
        if self.no_scroll_timeline:
            cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": NO_SCROLL_TIMELINE}, s)
        page = Page(cdp, tid, s, mobile)
        page.resize(width, height, settle=0)
        cdp.call("Emulation.setTouchEmulationEnabled", {"enabled": mobile}, s)
        if not javascript:
            cdp.call("Emulation.setScriptExecutionDisabled", {"value": True}, s)
        cdp.call("Emulation.setEmulatedMedia", {"features": [
            {"name": "prefers-reduced-motion", "value": "reduce" if reduced_motion else "no-preference"},
            {"name": "prefers-color-scheme", "value": "light"}]}, s)
        page.start = len(cdp.events)
        cdp.call("Page.navigate", {"url": url}, s)
        cdp.wait_event("Page.loadEventFired", s, page.start)
        self.page = page
        return page

    def __exit__(self, *exc):
        try:
            if getattr(self, "cdp", None):
                try:
                    self.cdp.call("Browser.close", timeout=10)
                except Exception:
                    pass
                self.cdp.ws.close()
        finally:
            try:
                self.proc.wait(15)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(10)
            for _ in range(20):
                shutil.rmtree(self.profile, ignore_errors=True)
                if not os.path.exists(self.profile):
                    break
                time.sleep(0.25)


class Page:
    def __init__(self, cdp, target, session, mobile):
        self.cdp, self.target, self.s, self.mobile, self.start = cdp, target, session, mobile, 0

    def _events(self, *names):
        return [m for m in self.cdp.events[self.start:] if m.get("sessionId") == self.s and m["method"] in names]

    def eval(self, js):
        """Evaluate an expression (promises are awaited) and return its JSON value."""
        r = self.cdp.call("Runtime.evaluate", {"expression": js, "awaitPromise": True, "returnByValue": True}, self.s)
        if "exceptionDetails" in r:
            d = r["exceptionDetails"]
            raise RuntimeError(d.get("exception", {}).get("description") or d.get("text"))
        return r.get("result", {}).get("value")

    def wait(self, seconds):
        self.cdp.pump(seconds)

    def scroll_to(self, y):
        self.eval(f"(window.scrollTo(0, {int(y)}), new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))))")

    def _center(self, selector):
        box = self.eval("(() => { const el = document.querySelector(%s); if (!el) return null; el.scrollIntoView({block: 'nearest'});"
                        " const r = el.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()"
                        % json.dumps(selector))
        if box is None:
            raise LookupError(f"no element matches {selector}")
        return box

    def hover(self, selector):
        x, y = self._center(selector)
        self.cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y}, self.s)
        self.wait(0.1)

    def click(self, selector):
        x, y = self._center(selector)
        for kind in ("mouseMoved", "mousePressed", "mouseReleased"):
            self.cdp.call("Input.dispatchMouseEvent", {"type": kind, "x": x, "y": y, "button": "left", "clickCount": 1}, self.s)
        self.wait(0.1)

    def resize(self, width, height, settle=0.3):
        self.cdp.call("Emulation.setDeviceMetricsOverride",
                      {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": self.mobile}, self.s)
        if settle:
            self.wait(settle)

    def screenshot(self, path):
        self.eval("document.fonts.ready.then(() => new Promise(r => setTimeout(r, 150)))")
        r = self.cdp.call("Page.captureScreenshot", {"format": "jpeg", "quality": 75}, self.s)
        Path(path).write_bytes(base64.b64decode(r["data"]))

    def screenshot_png(self):
        """The page as it shows now, as PNG bytes (lossless, for measuring colours)."""
        self.eval("document.fonts.ready.then(() => new Promise(r => setTimeout(r, 150)))")
        r = self.cdp.call("Page.captureScreenshot", {"format": "png"}, self.s)
        return base64.b64decode(r["data"])

    def console_problems(self):
        out = []
        for m in self._events("Runtime.exceptionThrown", "Runtime.consoleAPICalled", "Log.entryAdded"):
            p = m["params"]
            if m["method"] == "Runtime.exceptionThrown":
                d = p["exceptionDetails"]
                out.append("exception: " + str(d.get("exception", {}).get("description") or d.get("text")))
            elif m["method"] == "Runtime.consoleAPICalled" and p["type"] in ("error", "warning", "assert"):
                out.append(p["type"] + ": " + " ".join(str(a.get("value", a.get("description", ""))) for a in p["args"]))
            elif m["method"] == "Log.entryAdded" and p["entry"]["level"] in ("error", "warning"):
                e = p["entry"]
                out.append(f"log {e['level']}: {e.get('text')} {e.get('url', '')}".strip())
        return out

    def outside_requests(self):
        hosts = set()
        for m in self._events("Network.requestWillBeSent"):
            u = urllib.parse.urlparse(m["params"]["request"]["url"])
            if u.scheme in ("http", "https", "ws", "wss") and u.hostname != "127.0.0.1":
                hosts.add(u.hostname)
        return sorted(hosts)

    def requests(self):
        """URLs requested since the page was opened, in order."""
        return [m["params"]["request"]["url"] for m in self._events("Network.requestWillBeSent")]

    def failed_requests(self):
        urls = {m["params"]["requestId"]: m["params"]["request"]["url"] for m in self._events("Network.requestWillBeSent")}
        out = []
        for m in self._events("Network.loadingFailed", "Network.responseReceived"):
            p = m["params"]
            if m["method"] == "Network.loadingFailed":
                out.append(f"failed {p.get('errorText')} {urls.get(p['requestId'], '?')}")
            elif p["response"]["status"] >= 400:
                out.append(f"HTTP {p['response']['status']} {p['response']['url']}")
        return out

    def close(self):
        try:
            self.cdp.call("Target.closeTarget", {"targetId": self.target}, timeout=10)
        except Exception:
            pass
