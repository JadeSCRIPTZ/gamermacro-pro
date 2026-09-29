"""Teste pentru motor, cu pixeli simulati si mouse fals (rulare: python -m unittest -v)."""
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gm.engine import (Backend, FishConfig, FishingWorker, PixelSpec,  # noqa: E402
                       WinterConfig, WinterWorker, check_bounds)

HIT, MISS = (200, 50, 50), (10, 10, 10)


class FakeBackend(Backend):
    def __init__(self, fn):
        self.fn, self.t0, self.clicks = fn, time.monotonic(), []

    def now(self): return time.monotonic() - self.t0
    def pixel(self, x, y): return self.fn(self.now())
    def position(self): return (10, 10)
    def screen_size(self): return (1920, 1080)
    def click(self, button): self.clicks.append((self.now(), button))


def run(worker, seconds):
    worker.start()
    time.sleep(seconds)
    worker.request_stop()
    worker.join(2)
    assert not worker.is_alive(), "worker-ul nu s-a oprit"
    return worker


def spec(tol=15):
    return PixelSpec(5, 5, 200, 50, 50, tol)


def fish(**kw):
    return FishConfig(pixel=spec(), delay=0.02, cooldown=0.05, recast_gap=0.03, **kw)


class Pixel(unittest.TestCase):
    def test_tolerance_is_inclusive_per_channel(self):
        p = PixelSpec(0, 0, 100, 100, 100, 10)
        self.assertTrue(p.hit((110, 90, 100)))
        self.assertFalse(p.hit((111, 100, 100)))
        self.assertFalse(p.hit((100, 100, 89)))

    def test_bounds(self):
        b = FakeBackend(lambda t: MISS)
        check_bounds(b, PixelSpec(1919, 1079))
        with self.assertRaises(ValueError):
            check_bounds(b, PixelSpec(1920, 0))


class Fishing(unittest.TestCase):
    def test_catch_does_two_right_clicks(self):
        # culoarea tinta e deja pe ecran -> asteapta RESET; dispare, apoi apare = bite
        b = FakeBackend(lambda t: HIT if t < 0.1 or t > 0.3 else MISS)
        w = run(FishingWorker(fish(), b, lambda *a: None, poll=0.01), 0.7)
        self.assertGreaterEqual(w.catches, 1)
        self.assertEqual([c[1] for c in b.clicks[:2]], ["right", "right"])

    def test_no_catch_while_color_stays_from_start(self):
        b = FakeBackend(lambda t: HIT)
        w = run(FishingWorker(fish(), b, lambda *a: None, poll=0.01), 0.4)
        self.assertEqual((w.catches, len(b.clicks)), (0, 0))

    def test_auto_recast_is_single_click(self):
        b = FakeBackend(lambda t: HIT if t > 0.15 else MISS)
        w = run(FishingWorker(fish(auto_recast=True), b, lambda *a: None, poll=0.01), 0.3)
        self.assertGreaterEqual(w.catches, 1)
        self.assertEqual(len(b.clicks), w.catches)

    def test_timeout_recalibrates(self):
        b = FakeBackend(lambda t: MISS)
        w = run(FishingWorker(fish(timeout=0.15), b, lambda *a: None, poll=0.01), 0.5)
        self.assertGreaterEqual(w.recals, 1)
        self.assertEqual(w.catches, 0)
        self.assertGreaterEqual(len(b.clicks), 2)

    def test_pixel_wait_delays_then_catches(self):
        # bug vechi: cu pixel_wait > 0 nu prindea niciodata
        b = FakeBackend(lambda t: HIT if t > 0.1 else MISS)
        w = run(FishingWorker(fish(pixel_wait=0.15), b, lambda *a: None, poll=0.01), 0.7)
        self.assertGreaterEqual(w.catches, 1)
        self.assertGreaterEqual(b.clicks[0][0], 0.1 + 0.15)

    def test_pixel_wait_false_alarm(self):
        b = FakeBackend(lambda t: HIT if 0.1 < t < 0.15 else MISS)  # dispare inainte de 0.3s
        w = run(FishingWorker(fish(pixel_wait=0.3), b, lambda *a: None, poll=0.01), 0.7)
        self.assertEqual(w.catches, 0)

    def test_natural_mode_can_skip(self):
        seq = iter([0.0, 0.5, 0.5, 0.5])  # prima detectie sarita, a doua prinsa
        b = FakeBackend(lambda t: HIT if (t % 0.2) > 0.1 else MISS)
        w = run(FishingWorker(fish(natural=True), b, lambda *a: None, poll=0.01,
                              rng=lambda: next(seq, 0.5)), 0.6)
        self.assertEqual(w.skips, 1)
        self.assertGreaterEqual(w.catches, 1)

    def test_stop_is_immediate_even_in_long_cooldown(self):
        cfg = FishConfig(pixel=spec(), delay=0.0, cooldown=10.0, recast_gap=0.01)
        b = FakeBackend(lambda t: HIT if t > 0.05 else MISS)
        w = FishingWorker(cfg, b, lambda *a: None, poll=0.01)
        w.start()
        time.sleep(0.3)
        t0 = time.monotonic()
        w.request_stop()
        w.join(2)
        self.assertFalse(w.is_alive())
        self.assertLess(time.monotonic() - t0, 0.3)

    def test_backend_error_is_reported_and_stops(self):
        def boom(t): raise RuntimeError("ecran indisponibil")
        events = []
        w = FishingWorker(fish(), FakeBackend(boom), lambda *a: events.append(a), poll=0.01)
        w.start(); w.join(2)
        self.assertFalse(w.is_alive())
        self.assertIn("ecran indisponibil", w.error)
        self.assertIn(("stopped",), events)


class Winter(unittest.TestCase):
    def cfg(self, **kw):
        base = dict(pixel=spec(), clicks=3, interval_s=0, interval_ms=100,
                    cooldown_s=0, cooldown_ms=200)
        base.update(kw)
        return WinterConfig(**base)

    def test_left_clicks_n_times_with_interval(self):
        b = FakeBackend(lambda t: HIT if t > 0.1 else MISS)
        w = run(WinterWorker(self.cfg(), b, lambda *a: None, poll=0.01), 0.6)
        first = b.clicks[:3]
        self.assertEqual([c[1] for c in first], ["left"] * 3)
        gaps = [first[1][0] - first[0][0], first[2][0] - first[1][0]]
        for g in gaps:
            self.assertTrue(0.08 <= g <= 0.30, gaps)

    def test_interval_is_seconds_plus_milliseconds(self):
        self.assertAlmostEqual(self.cfg(interval_s=2, interval_ms=250).interval, 2.25)
        self.assertAlmostEqual(self.cfg(cooldown_s=1, cooldown_ms=5).cooldown, 1.005)

    def test_rearm_on_clear_fires_once_while_color_stays(self):
        b = FakeBackend(lambda t: HIT if t > 0.05 else MISS)
        w = run(WinterWorker(self.cfg(clicks=1), b, lambda *a: None, poll=0.01), 0.8)
        self.assertEqual(w.triggers, 1)

    def test_rearm_on_clear_fires_again_after_color_leaves(self):
        b = FakeBackend(lambda t: HIT if (t % 0.4) > 0.2 else MISS)
        w = run(WinterWorker(self.cfg(clicks=1), b, lambda *a: None, poll=0.01), 1.0)
        self.assertGreaterEqual(w.triggers, 2)

    def test_without_rearm_repeats_every_cooldown(self):
        b = FakeBackend(lambda t: HIT)
        w = run(WinterWorker(self.cfg(clicks=1, rearm_on_clear=False), b,
                             lambda *a: None, poll=0.01), 0.75)
        self.assertGreaterEqual(w.triggers, 3)

    def test_stop_mid_sequence(self):
        b = FakeBackend(lambda t: HIT)
        w = WinterWorker(self.cfg(clicks=50, interval_s=1, interval_ms=0), b,
                         lambda *a: None, poll=0.01)
        w.start()
        time.sleep(0.25)
        t0 = time.monotonic()
        w.request_stop()
        w.join(2)
        self.assertFalse(w.is_alive())
        self.assertLess(time.monotonic() - t0, 0.3)
        self.assertLessEqual(len(b.clicks), 2)

    def test_does_nothing_when_color_absent(self):
        b = FakeBackend(lambda t: MISS)
        w = run(WinterWorker(self.cfg(), b, lambda *a: None, poll=0.01), 0.3)
        self.assertEqual((w.triggers, len(b.clicks)), (0, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
