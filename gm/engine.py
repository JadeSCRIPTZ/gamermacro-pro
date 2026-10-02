"""Motorul de automatizare. Nu depinde de UI si poate fi testat cu un backend fals.

Doua detectoare independente, fiecare pe thread-ul lui, cu start/stop propriu:
  * FishingWorker - pixel principal: detecteaza culoarea, click dreapta (pescuit)
  * SeaWorker     - "Winter": recunoaste Grinch/Nutcracker dupa culoare si lupta automat
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
class SeaConfig:
    """Recunoaste Grinch (inima rosie) / Nutcracker si Yeti (foc+sabie) si lupta automat."""
    grinch: PixelSpec = field(
        default_factory=lambda: PixelSpec(0, 0, 255, 60, 60, 20))
    nutcracker: PixelSpec = field(
        default_factory=lambda: PixelSpec(0, 0, 60, 200, 60, 20))
    yeti: PixelSpec = field(
        default_factory=lambda: PixelSpec(0, 0, 120, 200, 255, 20))
    rod_key: str = "1"
    sword_key: str = "2"
    fire_key: str = "3"
    fire_duration: float = 5.0     # cat tine efectul de foc = fereastra de atac cu sabia
    grinch_interval: float = 0.35  # interval de baza intre click-uri la Grinch
    sword_interval: float = 0.35   # interval de baza intre click-uri cu sabia
    jitter: float = 0.08           # variatie aleatoare +/- pe fiecare interval (anti-pattern robotic)
    max_cycles: int = 8            # plafon siguranta: cicluri foc+sabie la Nutcracker/Yeti
    grinch_timeout: float = 6.0    # plafon siguranta: cat batem Grinch-ul inainte sa renuntam
    grinch_delay: float = 0.0      # asteapta atat inainte de primul click la Grinch
    action_delay: float = 0.05     # mica pauza intre taste/click-uri la foc+sabie (jocul are nevoie
                                    # de un moment sa inregistreze fiecare actiune separat)


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

    def press_key(self, key: str) -> None:  # ex: "1", "2", "3" - schimba slotul hotbar
        raise NotImplementedError


class NullBackend(Backend):
    """Nu face nimic - pentru selftest si previzualizari."""

    def pixel(self, x, y): return (0, 0, 0)
    def position(self): return (0, 0)
    def screen_size(self): return (1920, 1080)
    def click(self, button): pass
    def press_key(self, key): pass


class RealBackend(Backend):
    """Acelasi mecanism ca in versiunea veche: pyautogui pentru ecran, pynput pentru click/tastatura."""

    def __init__(self) -> None:
        import pyautogui
        from pynput.mouse import Button, Controller as MouseController
        from pynput.keyboard import Controller as KeyboardController
        pyautogui.PAUSE = 0
        self._pg = pyautogui
        self._left, self._right = Button.left, Button.right
        self._mouse = MouseController()
        self._keyboard = KeyboardController()
        self._lock = threading.Lock()  # detectoarele nu se calca pe click/taste

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

    def press_key(self, key):
        with self._lock:
            self._keyboard.press(key)
            self._keyboard.release(key)


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
        self._paused = threading.Event()
        self.error: Optional[str] = None

    def request_stop(self) -> None:
        self._halt.set()
        self._paused.clear()  # nu ramane blocat in pauza daca cineva cere stop

    @property
    def stopping(self) -> bool:
        return self._halt.is_set()

    def pause(self) -> None:
        self._paused.set()

    def resume(self) -> None:
        self._paused.clear()

    @property
    def paused(self) -> bool:
        return self._paused.is_set()

    def _wait(self, seconds: float) -> bool:
        """Asteapta intreruptibil. False daca s-a cerut oprirea."""
        if seconds > 0:
            return not self._halt.wait(seconds)
        return not self._halt.is_set()

    def _jittered(self, base: float, jitter: float) -> float:
        """Interval +/- o variatie aleatoare, ca sa nu para un click-uri robotic."""
        if jitter <= 0:
            return max(0.0, base)
        delta = (self._rng() * 2 - 1) * jitter
        return max(0.02, base + delta)

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
        was_paused = False

        while not self.stopping:
            if self.paused:
                if not was_paused:
                    self.state("PAUSED")
                    was_paused = True
                if not self._wait(self.poll):
                    break
                continue
            if was_paused:
                was_paused = False
                state = "RESET"  # reincepe curat dupa o pauza (ex: lupta cu Nutcracker)
                self.state(state)

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


class SeaWorker(_Worker):
    """Al treilea detector: recunoaste Grinch/Nutcracker/Yeti dupa culoare si lupta automat.

    Grinch (HP mic) -> asteapta grinch_delay (optional), apoi atac cu ce ai in
    mana (undita), click stanga pana dispare.

    Nutcracker si Yeti (HP mare) -> acelasi sistem de foc+sabie: cicluri de
    foc (tasta+click dreapta) urmat de sabie (tasta+click stanga in bucla),
    cronometrate de la activarea focului, pana dispare sau se atinge plafonul
    de cicluri. Intre fiecare tasta/click din secventa de foc+sabie exista o
    mica pauza (action_delay) ca jocul sa apuce sa inregistreze fiecare
    actiune separat (fara ea, schimbarea pe sabie poate sa nu se produca).
    """
    kind = "sea"

    def __init__(self, cfg: SeaConfig, backend: Backend, emit: Emit, **kw) -> None:
        super().__init__(backend, emit, **kw)
        self.cfg = cfg
        self.grinch_kills = 0
        self.nutcracker_kills = 0
        self.nutcracker_fails = 0
        self.yeti_kills = 0
        self.yeti_fails = 0

    def _hit(self, px: PixelSpec) -> bool:
        return px.hit(self.backend.pixel(px.x, px.y))

    def _fight_grinch(self) -> Optional[bool]:
        """True = a disparut (mort), False = plafon atins fara sa moara, None = s-a cerut stop."""
        c = self.cfg
        self.state("GRINCH")
        self.log("warn", "Grinch detectat — atac cu ce am in mana…")
        if c.grinch_delay > 0 and not self._wait(c.grinch_delay):
            return None
        t0 = time.monotonic()
        clicks = 0
        gave_up = False
        while not self.stopping and self._hit(c.grinch):
            self.backend.click("left")
            clicks += 1
            if time.monotonic() - t0 > c.grinch_timeout:
                gave_up = True
                self.log("err", f"Grinch: plafon {c.grinch_timeout:g}s atins, renunt.")
                break
            if not self._wait(self._jittered(c.grinch_interval, c.jitter)):
                return None
        if self.stopping:
            return None
        if gave_up:
            return False
        self.grinch_kills += 1
        n = self.grinch_kills
        self._emit("grinch", n, clicks)
        self.log("ok", f"[Grinch #{n}] Gata — {clicks} click-uri.")
        return True

    def _fight_big(self, name: str, pixel: PixelSpec) -> Tuple[Optional[bool], int]:
        """Sistemul comun foc+sabie, folosit de Nutcracker si Yeti.

        Returneaza (rezultat, cicluri): rezultat True = a murit, False = plafon
        atins fara sa moara, None = s-a cerut stop (cicluri e oricum util pt log).
        """
        c = self.cfg
        self.state(name.upper())
        self.log("warn", f"{name} detectat — secventa foc + sabie…")
        killed = False
        cycles = 0
        while not self.stopping and cycles < c.max_cycles:
            if not pixel.hit(self.backend.pixel(pixel.x, pixel.y)):
                killed = True
                break
            cycles += 1
            self.backend.press_key(c.fire_key)
            if not self._wait(c.action_delay):
                return None, cycles
            self.backend.click("right")
            t0 = time.monotonic()  # cronometrul celor fire_duration secunde incepe de aici
            if not self._wait(c.action_delay):
                return None, cycles
            self.backend.press_key(c.sword_key)
            if not self._wait(c.action_delay):
                return None, cycles
            self.log("dim", f"[{name}] ciclul {cycles}/{c.max_cycles}: foc pornit, "
                             f"atac {c.fire_duration:g}s…")
            while not self.stopping and time.monotonic() - t0 < c.fire_duration:
                self.backend.click("left")
                if not pixel.hit(self.backend.pixel(pixel.x, pixel.y)):
                    killed = True
                    break
                if not self._wait(self._jittered(c.sword_interval, c.jitter)):
                    return None, cycles
            if killed:
                break
        if self.stopping:
            return None, cycles
        self.backend.press_key(c.rod_key)
        return killed, cycles

    def _fight_nutcracker(self) -> Optional[bool]:
        killed, cycles = self._fight_big("Nutcracker", self.cfg.nutcracker)
        if killed is None:
            return None
        if killed:
            self.nutcracker_kills += 1
            n = self.nutcracker_kills
            self._emit("nutcracker", n, cycles, True)
            self.log("ok", f"[Nutcracker #{n}] Mort dupa {cycles} cicluri. Revin la undita.")
        else:
            self.nutcracker_fails += 1
            self._emit("nutcracker", self.nutcracker_kills, cycles, False)
            self.log("err", f"[Nutcracker] Plafon de {self.cfg.max_cycles} cicluri atins fara "
                             f"sa moara — revin la undita si astept sa dispara.")
        return killed

    def _fight_yeti(self) -> Optional[bool]:
        killed, cycles = self._fight_big("Yeti", self.cfg.yeti)
        if killed is None:
            return None
        if killed:
            self.yeti_kills += 1
            n = self.yeti_kills
            self._emit("yeti", n, cycles, True)
            self.log("ok", f"[Yeti #{n}] Mort dupa {cycles} cicluri. Revin la undita.")
        else:
            self.yeti_fails += 1
            self._emit("yeti", self.yeti_kills, cycles, False)
            self.log("err", f"[Yeti] Plafon de {self.cfg.max_cycles} cicluri atins fara sa "
                             f"moara — revin la undita si astept sa dispara.")
        return killed

    def _run(self) -> None:
        c = self.cfg
        self.log("hi",
                 f"SEA START  grinch=({c.grinch.x},{c.grinch.y})  "
                 f"nutcracker=({c.nutcracker.x},{c.nutcracker.y})  "
                 f"yeti=({c.yeti.x},{c.yeti.y})  "
                 f"foc={c.fire_duration:g}s  plafon={c.max_cycles} cicluri  "
                 f"taste={c.rod_key}/{c.sword_key}/{c.fire_key}")
        self.state("WATCH")
        # "armed" = putem ataca daca apare; dupa un esec (plafon atins fara sa moara)
        # se dezarmeaza pana dispare culoarea, ca sa nu reatace la nesfarsit acelasi mob blocat.
        g_armed = n_armed = y_armed = True
        while not self.stopping:
            g_hit = self._hit(c.grinch)
            n_hit = self._hit(c.nutcracker)
            y_hit = self._hit(c.yeti)

            if g_hit and g_armed:
                result = self._fight_grinch()
                if result is None:
                    break
                g_armed = result
                self.state("WATCH" if g_armed else "STUCK")
            elif n_hit and n_armed:
                result = self._fight_nutcracker()
                if result is None:
                    break
                n_armed = result
                self.state("WATCH" if n_armed else "STUCK")
            elif y_hit and y_armed:
                result = self._fight_yeti()
                if result is None:
                    break
                y_armed = result
                self.state("WATCH" if y_armed else "STUCK")
            else:
                rearmed = False
                if not g_hit and not g_armed:
                    g_armed, rearmed = True, True
                if not n_hit and not n_armed:
                    n_armed, rearmed = True, True
                if not y_hit and not y_armed:
                    y_armed, rearmed = True, True
                if rearmed:
                    self.state("WATCH")
            if not self._wait(self.poll):
                break
