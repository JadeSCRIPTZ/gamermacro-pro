"""
GamerMacro Pro — Nebula UI
===========================
Desktop app modern (pywebview: HTML/CSS/JS randate ca fereastra nativa)
peste motorul de automatizare existent din gm/engine.py.

Rulare:  python app.py
Build:   vezi build.bat / build.sh (PyInstaller, include folderul ui/)
"""
from __future__ import annotations

import json
import queue
import threading
import time
from pathlib import Path
from typing import Optional

import webview

from gm.engine import (
    Backend,
    FishConfig,
    FishingWorker,
    PixelSpec,
    RealBackend,
    SeaConfig,
    SeaWorker,
    check_bounds,
)

PROFILE_DIR = Path.home() / ".gamermacro" / "profiles"


def _pixel_from(cfg: dict) -> PixelSpec:
    return PixelSpec(
        x=int(cfg.get("x", 0)),
        y=int(cfg.get("y", 0)),
        r=int(cfg.get("r", 0)),
        g=int(cfg.get("g", 0)),
        b=int(cfg.get("b", 0)),
        tol=int(cfg.get("tol", 15)),
    )


def _fish_config(cfg: dict) -> FishConfig:
    return FishConfig(
        pixel=_pixel_from(cfg),
        delay=float(cfg.get("delay", 0.1)),
        cooldown=float(cfg.get("cooldown", 3.0)),
        timeout=float(cfg.get("timeout", 0) or 0),
        pixel_wait=float(cfg.get("pixel_wait", 0) or 0),
        natural=bool(cfg.get("natural", False)),
        auto_recast=bool(cfg.get("auto_recast", False)),
        recast_gap=float(cfg.get("recast_gap", 0.5) or 0.5),
    )


def _sea_config(cfg: dict) -> SeaConfig:
    return SeaConfig(
        grinch=_pixel_from(cfg.get("grinch", {})),
        nutcracker=_pixel_from(cfg.get("nutcracker", {})),
        yeti=_pixel_from(cfg.get("yeti", {})),
        rod_key=str(cfg.get("rod_key", "1"))[:1] or "1",
        sword_key=str(cfg.get("sword_key", "2"))[:1] or "2",
        fire_key=str(cfg.get("fire_key", "3"))[:1] or "3",
        fire_duration=float(cfg.get("fire_duration", 5.0) or 5.0),
        grinch_interval=float(cfg.get("grinch_interval", 0.35) or 0.35),
        sword_interval=float(cfg.get("sword_interval", 0.35) or 0.35),
        jitter=float(cfg.get("jitter", 0.08) or 0.0),
        max_cycles=max(1, int(cfg.get("max_cycles", 8) or 8)),
        grinch_timeout=float(cfg.get("grinch_timeout", 6.0) or 6.0),
        grinch_delay=float(cfg.get("grinch_delay", 0.0) or 0.0),
        action_delay=float(cfg.get("action_delay", 0.05) or 0.0),
    )


class Api:
    """Punte intre JS (pywebview.api.*) si motorul de automatizare."""

    def __init__(self) -> None:
        self._backend: Optional[Backend] = None
        self._backend_error: Optional[str] = None
        self.fish_worker: Optional[FishingWorker] = None
        self.sea_worker: Optional[SeaWorker] = None
        self.events: "queue.Queue[dict]" = queue.Queue()
        self._seq = 0
        self._lock = threading.Lock()
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    # ── backend lazy init (evita crash la pornirea ferestrei) ─────────
    def _get_backend(self) -> Backend:
        if self._backend is None:
            try:
                self._backend = RealBackend()
            except Exception as e:  # ex: fara display / permisiuni
                self._backend_error = f"{type(e).__name__}: {e}"
                raise
        return self._backend

    def _emit(self, source: str):
        def _fn(etype: str, *args):
            with self._lock:
                self._seq += 1
                self.events.put({
                    "id": self._seq,
                    "source": source,
                    "type": etype,
                    "args": list(args),
                    "ts": time.time(),
                })
        return _fn

    # ── evenimente live (poll din JS la ~130ms) ────────────────────────
    def drain_events(self) -> list:
        out = []
        while True:
            try:
                out.append(self.events.get_nowait())
            except queue.Empty:
                break
        return out

    # ── pixel picker (JS face countdown-ul de 3s, apoi cheama asta) ────
    def capture_pixel(self) -> dict:
        try:
            backend = self._get_backend()
            x, y = backend.position()
            r, g, b = backend.pixel(x, y)
            return {"ok": True, "x": x, "y": y, "r": r, "g": g, "b": b}
        except Exception as e:
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    # ── fishing (detector 1) ────────────────────────────────────────
    def start_fishing(self, cfg: dict) -> dict:
        try:
            if self.fish_worker and self.fish_worker.is_alive():
                return {"ok": False, "error": "Macro ruleaza deja."}
            backend = self._get_backend()
            fc = _fish_config(cfg)
            check_bounds(backend, fc.pixel)
            self.fish_worker = FishingWorker(fc, backend, self._emit("fish"))
            self.fish_worker.start()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def stop_fishing(self) -> dict:
        if self.fish_worker:
            self.fish_worker.request_stop()
        return {"ok": True}

    # ── sea creatures / "Winter" (Grinch / Nutcracker) ──────────────
    def _sea_emit(self):
        """La fel ca self._emit('sea'), dar pune Macro pe pauza cat dureaza o
        lupta (Grinch/Nutcracker), ca sa nu incerce sa recasteze in acelasi timp."""
        base = self._emit("sea")

        def _fn(etype: str, *args):
            base(etype, *args)
            if etype == "state" and self.fish_worker and self.fish_worker.is_alive():
                name = args[0] if args else None
                if name in ("GRINCH", "NUTCRACKER"):
                    self.fish_worker.pause()
                elif name == "WATCH":
                    self.fish_worker.resume()
        return _fn

    def start_sea(self, cfg: dict) -> dict:
        try:
            if self.sea_worker and self.sea_worker.is_alive():
                return {"ok": False, "error": "Sistemul de creaturi ruleaza deja."}
            backend = self._get_backend()
            sc = _sea_config(cfg)
            check_bounds(backend, sc.grinch)
            check_bounds(backend, sc.nutcracker)
            check_bounds(backend, sc.yeti)
            self.sea_worker = SeaWorker(sc, backend, self._sea_emit())
            self.sea_worker.start()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def stop_sea(self) -> dict:
        if self.sea_worker:
            self.sea_worker.request_stop()
        if self.fish_worker:
            self.fish_worker.resume()  # nu ramana blocat pe pauza daca opresti Sea in lupta
        return {"ok": True}

    def stop_all(self) -> None:
        try:
            self.stop_fishing()
            self.stop_sea()
        except Exception:
            pass

    # ── profile ──────────────────────────────────────────────────────
    def list_profiles(self) -> list:
        items = []
        for f in sorted(PROFILE_DIR.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                items.append({
                    "name": data.get("name", f.stem),
                    "saved_at": data.get("saved_at", ""),
                })
            except Exception:
                continue
        return items

    def save_profile(self, name: str, state: dict) -> dict:
        try:
            name = (name or "").strip()
            if not name:
                return {"ok": False, "error": "Nume gol."}
            safe = "".join(c for c in name if c.isalnum() or c in " -_()").strip() or "profil"
            data = {
                "name": name,
                "saved_at": time.strftime("%Y-%m-%d %H:%M"),
                "state": state,
            }
            (PROFILE_DIR / f"{safe}.json").write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def load_profile(self, name: str) -> dict:
        try:
            for f in PROFILE_DIR.glob("*.json"):
                data = json.loads(f.read_text(encoding="utf-8"))
                if data.get("name") == name:
                    return {"ok": True, "state": data.get("state", {})}
            return {"ok": False, "error": "Profil negasit."}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def delete_profile(self, name: str) -> dict:
        try:
            for f in PROFILE_DIR.glob("*.json"):
                data = json.loads(f.read_text(encoding="utf-8"))
                if data.get("name") == name:
                    f.unlink()
                    break
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_screen_size(self) -> dict:
        try:
            w, h = self._get_backend().screen_size()
            return {"ok": True, "w": w, "h": h}
        except Exception as e:
            return {"ok": False, "error": str(e)}


def main() -> None:
    ui_dir = Path(__file__).resolve().parent / "ui"
    api = Api()
    window = webview.create_window(
        "GamerMacro Pro — Nebula",
        str(ui_dir / "index.html"),
        js_api=api,
        width=1220,
        height=800,
        min_size=(980, 660),
        background_color="#14101f",
    )

    def _on_closing():
        api.stop_all()

    try:
        window.events.closing += _on_closing
    except Exception:
        pass

    webview.start()


if __name__ == "__main__":
    main()
