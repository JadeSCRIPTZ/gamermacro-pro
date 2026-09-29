"""Motorul de automatizare. Nu depinde de UI si poate fi testat cu un backend fals.

Doua detectoare independente, fiecare pe thread-ul lui, cu start/stop propriu:
  * FishingWorker - pixel principal: detecteaza culoarea, click dreapta (pescuit)
  * WinterWorker  - pixel 2: detecteaza culoarea, click stanga de N ori cu interval
"""
from __future__ import annotations

import random
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

POLL = 0.05
NATURAL_SKIP_CHANCE = 0.08

RGB = Tuple[int, int, int]
Emit = Callable[..., None]


# ── Configurare ──────────────────────────────────────────────────────────────
@dataclass
class PixelSpec:
    x: int = 0
    y: int = 0
    r: int = 255
    g: int = 0
    b: int = 0
    tol: int = 15

    def hit(self, rgb: RGB) -> bool:
        return (abs(rgb[0] - self.r) <= self.tol
                and abs(rgb[1] - self.g) <= self.tol
                and abs(rgb[2] - self.b) <= self.tol)


@dataclass
class FishConfig:
    pixel: PixelSpec = field(default_factory=PixelSpec)
    delay: float = 0.1          # intarziere reactie dupa detectie (s)
    cooldown: float = 3.0       # pauza dupa aruncare (s)
    timeout: float = 0.0        # recalibrare dupa X s fara detectie (0 = oprit)
    pixel_wait: float = 0.0     # asteapta X s dupa prima detectie (0 = oprit)
    natural: bool = False       # 8% sansa sa sara o detectie
    auto_recast: bool = False   # True = 1 click, False = 2 click-uri
    recast_gap: float = 0.5     # pauza intre cele 2 click-uri


@dataclass
class WinterConfig:
    pixel: PixelSpec = field(
        default_factory=lambda: PixelSpec(640, 360, 150, 150, 150, 25))
    clicks: int = 1
    interval_s: int = 0
    interval_ms: int = 500
    cooldown_s: int = 1
    cooldown_ms: int = 0
    rearm_on_clear: bool = True  # nu declansa din nou cat timp culoarea ramane

    @property
    def interval(self) -> float:
        return self.interval_s + self.interval_ms / 1000.0

    @property
    def cooldown(self) -> float:
        return self.cooldown_s + self.cooldown_ms / 1000.0


# ── Backend (ecran + mouse) ──────────────────────────────────────────────────
class Backend:
    def pixel(self, x: int, y: int) -> RGB:
        raise NotImplementedError

    def position(self) -> Tuple[int, int]:
        raise NotImplementedError

    def screen_size(self) -> Tuple[int, int]:
        raise NotImplementedError

    def click(self, button: str) -> None:  # "left" | "right"
        raise NotImplementedError


class NullBackend(Backend):
    """Nu face nimic - pentru selftest si previzualizari."""

    def pixel(self, x, y): return (0, 0, 0)
    def position(self): return (0, 0)
    def screen_size(self): return (1920, 1080)
    def click(self, button): pass


class RealBackend(Backend):
    """Acelasi mecanism ca in versiunea veche: pyautogui pentru ecran, pynput pentru click."""

    def __init__(self) -> None:
        import pyautogui
        from pynput.mouse import Button, Controller
        pyautogui.PAUSE = 0
        self._pg = pyautogui
        self._left, self._right = Button.left, Button.right
        self._mouse = Controller()
        self._lock = threading.Lock()  # doua detectoare nu se calca pe click

    def pixel(self, x, y):
        p = self._pg.pixel(x, y)
        return int(p[0]), int(p[1]), int(p[2])

    def position(self):
        p = self._pg.position()
        return int(p[0]), int(p[1])

    def screen_size(self):
        s = self._pg.size()
        return int(s[0]), int(s[1])

    def click(self, button):
        with self._lock:
            self._mouse.click(self._left if button == "left" else self._right, 1)


def check_bounds(backend: Backend, px: PixelSpec) -> None:
    w, h = backend.screen_size()
    if not (0 <= px.x < w and 0 <= px.y < h):
        raise ValueError(f"({px.x},{px.y}) e in afara ecranului ({w}×{h}).")


# ── Workeri ──────────────────────────────────────────────────────────────────
class _Worker(threading.Thread):
    kind = "worker"

    def __init__(self, backend: Backend, emit: Emit, poll: float = POLL,
                 rng: Callable[[], float] = random.random) -> None:
        super().__init__(daemon=True, name=f"gm-{self.kind}")
        self.backend, self._emit, self.poll, self._rng = backend, emit, poll, rng
        self._halt = threading.Event()
        self.error: Optional[str] = None

    def request_stop(self) -> None:
        self._halt.set()

    @property
    def stopping(self) -> bool:
        return self._halt.is_set()

    def _wait(self, seconds: float) -> bool:
        """Asteapta intreruptibil. False daca s-a cerut oprirea."""
        if seconds > 0:
            return not self._halt.wait(seconds)
        return not self._halt.is_set()

    def log(self, level: str, msg: str) -> None:
        self._emit("log", level, msg)

    def state(self, name: str) -> None:
        self._emit("state", name)

    def run(self) -> None:
        try:
            self._run()
        except Exception as e:  # eroare de backend: raporteaza si opreste
            self.error = f"{type(e).__name__}: {e}"
            self.log("err", f"Eroare: {self.error}")
        finally:
            self.state("IDLE")
            self._emit("stopped")

    def _run(self) -> None:
        raise NotImplementedError


class FishingWorker(_Worker):
    """Automat de stari RESET -> WATCH -> (PREWAIT) -> catch -> RESET (ca in versiunea veche)."""
    kind = "fishing"

    def __init__(self, cfg: FishConfig, backend: Backend, emit: Emit, **kw) -> None:
        super().__init__(backend, emit, **kw)
        self.cfg = cfg
        self.catches = 0
        self.recals = 0
        self.skips = 0
        self.catch_times: List[float] = []
        self.started_at = 0.0

    def _recast(self) -> bool:
        c = self.cfg
        self.backend.click("right")
        if not c.auto_recast:
            if not self._wait(c.recast_gap):
                return False
            self.backend.click("right")
        return True

    def _catch(self, rgb: RGB) -> bool:
        c = self.cfg
        self.catches += 1
        n = self.catches
        self.catch_times.append(time.time())
        self._emit("catch", n)
        self.log("warn", f"[#{n}] Bobber!  RGB({rgb[0]},{rgb[1]},{rgb[2]})  delay {c.delay:g}s…")
        if not self._wait(c.delay) or not self._recast():
            return False
        what = "Recast (1× click)" if c.auto_recast else "Re-aruncat"
        self.log("ok", f"[#{n}] {what}! Cooldown {c.cooldown:g}s…")
        return self._wait(c.cooldown)

    def _run(self) -> None:
        c, p = self.cfg, self.cfg.pixel
        self.started_at = time.time()
        self.log("hi",
                 f"START  ({p.x},{p.y})  RGB({p.r},{p.g},{p.b})  ±{p.tol}  "
                 f"delay={c.delay:g}s  cd={c.cooldown:g}s  "
                 f"to={'ON ' + format(c.timeout, 'g') + 's' if c.timeout else 'OFF'}  "
                 f"pw={'ON ' + format(c.pixel_wait, 'g') + 's' if c.pixel_wait else 'OFF'}  "
                 f"nat={'ON' if c.natural else 'OFF'}")
        state = "RESET"
        self.state(state)
        watch_since = wait_until = 0.0

        while not self.stopping:
            rgb = self.backend.pixel(p.x, p.y)
            hit = p.hit(rgb)
            now = time.monotonic()

            if state == "RESET":
                if not hit:
                    state, watch_since = "WATCH", now
                    self.state(state)

            else:  # WATCH sau PREWAIT
                if c.timeout > 0 and now - watch_since > c.timeout:
                    self.recals += 1
                    self.log("pur", f"[RECAL #{self.recals}] Timeout {c.timeout:g}s — retrag!")
                    self._emit("recal", self.recals)
                    if not self._recast() or not self._wait(c.cooldown):
                        break
                    state = "RESET"
                    self.state(state)
                    continue

                if state == "WATCH" and hit:
                    if c.natural and self._rng() < NATURAL_SKIP_CHANCE:
                        self.skips += 1
                        self.log("pur", f"[skip #{self.skips}] Natural — ignorat.")
                        state = "RESET"
                        self.state(state)
                    elif c.pixel_wait > 0:
                        wait_until = now + c.pixel_wait
                        state = "PREWAIT"
                        self.state(state)
                        self.log("warn", f"Detectat! Astept {c.pixel_wait:g}s inainte sa actionez…")
                    else:
                        if not self._catch(rgb):
                            break
                        state = "RESET"
                        self.state(state)
                        continue

                elif state == "PREWAIT" and now >= wait_until:
                    if hit:
                        self.log("ok", "Pre-wait expirat — actionez!")
                        if not self._catch(rgb):
                            break
                        state = "RESET"
                        self.state(state)
                        continue
                    self.log("dim", "Pre-wait expirat, culoarea a disparut — reiau urmarirea.")
                    state = "WATCH"
                    self.state(state)

            if not self._wait(self.poll):
                break


class WinterWorker(_Worker):
    """Pixel 2: cand vede culoarea, click stanga de N ori cu interval fix, apoi pauza."""
    kind = "winter"

    def __init__(self, cfg: WinterConfig, backend: Backend, emit: Emit, **kw) -> None:
        super().__init__(backend, emit, **kw)
        self.cfg = cfg
        self.triggers = 0
        self.clicks_done = 0
        self.last_trigger = 0.0

    def _fire(self) -> bool:
        c = self.cfg
        self.triggers += 1
        n = self.triggers
        self.state("CLICKING")
        self.log("warn", f"[Winter #{n}] Culoare detectata — {c.clicks} click-uri…")
        done = 0
        for i in range(c.clicks):
            if self.stopping:
                break
            self.backend.click("left")
            done += 1
            self.clicks_done += 1
            if i < c.clicks - 1 and not self._wait(c.interval):
                break
        self.last_trigger = time.time()
        self._emit("trigger", n, done)
        if self.stopping:
            return False
        self.log("ok", f"[Winter #{n}] Gata ({done}/{c.clicks}). Pauza {c.cooldown:.3f}s…")
        self.state("COOLDOWN")
        return self._wait(c.cooldown)

    def _run(self) -> None:
        c, p = self.cfg, self.cfg.pixel
        self.log("hi",
                 f"WINTER START  ({p.x},{p.y})  RGB({p.r},{p.g},{p.b})  ±{p.tol}  "
                 f"{c.clicks} click-uri la {c.interval:.3f}s  pauza {c.cooldown:.3f}s  "
                 f"reamorsare={'dupa ce dispare' if c.rearm_on_clear else 'imediat'}")
        armed = True
        self.state("WATCH")
        while not self.stopping:
            hit = p.hit(self.backend.pixel(p.x, p.y))
            if armed:
                if hit:
                    if not self._fire():
                        break
                    armed = not c.rearm_on_clear
                    self.state("WATCH" if armed else "WAIT_CLEAR")
            elif not hit:
                armed = True
                self.state("WATCH")
            if not self._wait(self.poll):
                break
