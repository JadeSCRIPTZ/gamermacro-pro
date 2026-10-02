"""Teste pentru motor, cu pixeli simulati si mouse fals (rulare: python -m unittest -v)."""
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gm.engine import (Backend, FishConfig, FishingWorker, PixelSpec,  # noqa: E402
                       SeaConfig, SeaWorker, check_bounds)

HIT, MISS = (200, 50, 50), (10, 10, 10)


class FakeBackend(Backend):
    def __init__(self, fn):
        self.fn, self.t0, self.clicks = fn, time.monotonic(), []

    def now(self): return time.monotonic() - self.t0
    def pixel(self, x, y): return self.fn(self.now())
    def position(self): return (10, 10)
    def screen_size(self): return (1920, 1080)
    def click(self, button): self.clicks.append((self.now(), button))
    def press_key(self, key): pass


class SeaFakeBackend(Backend):
    """Trei pixeli independenti (Grinch / Nutcracker / Yeti) dupa pozitie, plus tastatura."""

    def __init__(self, grinch_xy, nutcracker_xy, grinch_fn, nutcracker_fn,
                 yeti_xy=(99, 99), yeti_fn=lambda t: (0, 0, 0)):
        self.t0 = time.monotonic()
        self.gxy, self.nxy, self.yxy = grinch_xy, nutcracker_xy, yeti_xy
        self.gfn, self.nfn, self.yfn = grinch_fn, nutcracker_fn, yeti_fn
        self.clicks, self.keys = [], []

    def now(self): return time.monotonic() - self.t0

    def pixel(self, x, y):
        t = self.now()
        if (x, y) == self.gxy:
            return self.gfn(t)
        if (x, y) == self.nxy:
            return self.nfn(t)
        if (x, y) == self.yxy:
            return self.yfn(t)
        return (0, 0, 0)

    def position(self): return (10, 10)
    def screen_size(self): return (1920, 1080)
    def click(self, button): self.clicks.append((self.now(), button))
    def press_key(self, key): self.keys.append((self.now(), key))


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

    def test_pause_freezes_clicks_resume_continues(self):
        # folosit de SeaWorker cat lupta cu Grinch/Nutcracker
        b = FakeBackend(lambda t: HIT if (t % 0.3) > 0.2 else MISS)  # ciclic: mai lipseste, apoi apare
        w = FishingWorker(fish(), b, lambda *a: None, poll=0.01)
        w.pause()
        w.start()
        time.sleep(0.25)
        self.assertEqual(len(b.clicks), 0)  # in pauza, n-a atins nimic
        w.resume()
        time.sleep(0.6)
        w.request_stop()
        w.join(2)
        self.assertFalse(w.is_alive())
        self.assertGreaterEqual(w.catches, 1)  # dupa resume, prinde normal


G_ON, G_OFF = (255, 30, 30), (0, 0, 0)   # Grinch: inima rosie / absenta
N_ON, N_OFF = (30, 220, 30), (0, 0, 0)   # Nutcracker: nume verde / absent
Y_ON, Y_OFF = (120, 200, 255), (0, 0, 0)  # Yeti: nume albastru / absent


class Sea(unittest.TestCase):
    def cfg(self, **kw):
        base = dict(
            grinch=PixelSpec(1, 1, *G_ON, 15),
            nutcracker=PixelSpec(2, 2, *N_ON, 15),
            yeti=PixelSpec(3, 3, *Y_ON, 15),
            rod_key="1", sword_key="2", fire_key="3",
            fire_duration=0.1, grinch_interval=0.02, sword_interval=0.02,
            jitter=0.0, max_cycles=3, grinch_timeout=0.5,
            grinch_delay=0.0, action_delay=0.0,  # rapid in teste; cazuri dedicate mai jos
        )
        base.update(kw)
        return SeaConfig(**base)

    def test_grinch_spams_left_click_until_gone_no_keys(self):
        b = SeaFakeBackend((1, 1), (2, 2),
                           grinch_fn=lambda t: G_ON if t < 0.08 else G_OFF,
                           nutcracker_fn=lambda t: N_OFF)
        w = run(SeaWorker(self.cfg(), b, lambda *a: None, poll=0.01), 0.3)
        self.assertEqual(w.grinch_kills, 1)
        self.assertEqual(w.nutcracker_kills, 0)
        self.assertTrue(b.clicks)
        self.assertTrue(all(btn == "left" for _, btn in b.clicks))
        self.assertEqual(b.keys, [])  # Grinch nu umbla la hotbar - ramane pe undita

    def test_nutcracker_single_cycle_then_dead(self):
        b = SeaFakeBackend((1, 1), (2, 2),
                           grinch_fn=lambda t: G_OFF,
                           nutcracker_fn=lambda t: N_ON if t < 0.05 else N_OFF)
        w = run(SeaWorker(self.cfg(fire_duration=0.15), b, lambda *a: None, poll=0.01), 0.4)
        self.assertEqual(w.nutcracker_kills, 1)
        self.assertEqual(w.nutcracker_fails, 0)
        self.assertEqual(b.keys[0][1], "3")   # foc
        self.assertEqual(b.keys[1][1], "2")   # sabie, fara asteptare
        self.assertEqual(b.keys[-1][1], "1")  # revine la undita la final
        self.assertEqual(b.clicks[0][1], "right")
        self.assertTrue(b.keys[0][0] <= b.clicks[0][0] <= b.keys[1][0])

    def test_nutcracker_multiple_cycles_then_dead(self):
        # moare abia dupa primul ciclu de foc, in al doilea
        b = SeaFakeBackend((1, 1), (2, 2),
                           grinch_fn=lambda t: G_OFF,
                           nutcracker_fn=lambda t: N_ON if t < 0.18 else N_OFF)
        w = run(SeaWorker(self.cfg(fire_duration=0.12, max_cycles=5), b,
                          lambda *a: None, poll=0.01), 0.6)
        self.assertEqual(w.nutcracker_kills, 1)
        fire_presses = [k for k in b.keys if k[1] == "3"]
        self.assertEqual(len(fire_presses), 2)

    def test_yeti_single_cycle_then_dead(self):
        # acelasi sistem ca Nutcracker, dar pe pixelul si contoarele proprii lui Yeti
        b = SeaFakeBackend((1, 1), (2, 2),
                           grinch_fn=lambda t: G_OFF, nutcracker_fn=lambda t: N_OFF,
                           yeti_xy=(3, 3), yeti_fn=lambda t: Y_ON if t < 0.05 else Y_OFF)
        w = run(SeaWorker(self.cfg(fire_duration=0.15), b, lambda *a: None, poll=0.01), 0.4)
        self.assertEqual(w.yeti_kills, 1)
        self.assertEqual(w.yeti_fails, 0)
        self.assertEqual(w.nutcracker_kills, 0)  # independent de Nutcracker
        self.assertEqual(b.keys[0][1], "3")
        self.assertEqual(b.keys[1][1], "2")
        self.assertEqual(b.keys[-1][1], "1")
        self.assertEqual(b.clicks[0][1], "right")

    def test_action_delay_separates_fire_click_and_sword_key(self):
        # regresie pt bug-ul "nu schimba pe sabie": trebuie sa fie o pauza masurabila
        # intre apasarea pe 3, click dreapta si apasarea pe 2 - nu toate deodata.
        b = SeaFakeBackend((1, 1), (2, 2),
                           grinch_fn=lambda t: G_OFF,
                           nutcracker_fn=lambda t: N_ON if t < 0.05 else N_OFF)
        w = run(SeaWorker(self.cfg(fire_duration=0.3, action_delay=0.05), b,
                          lambda *a: None, poll=0.01), 0.6)
        self.assertEqual(w.nutcracker_kills, 1)
        fire_t = b.keys[0][0]
        sword_t = b.keys[1][0]
        right_click_t = b.clicks[0][0]
        self.assertGreaterEqual(right_click_t - fire_t, 0.03)
        self.assertGreaterEqual(sword_t - right_click_t, 0.03)

    def test_grinch_delay_waits_before_first_click(self):
        b = SeaFakeBackend((1, 1), (2, 2),
                           grinch_fn=lambda t: G_ON if t < 0.3 else G_OFF,
                           nutcracker_fn=lambda t: N_OFF)
        w = run(SeaWorker(self.cfg(grinch_delay=0.15), b, lambda *a: None, poll=0.01), 0.5)
        self.assertEqual(w.grinch_kills, 1)
        self.assertGreaterEqual(b.clicks[0][0], 0.12)

    def test_nutcracker_gives_up_after_max_cycles(self):
        b = SeaFakeBackend((1, 1), (2, 2),
                           grinch_fn=lambda t: G_OFF,
                           nutcracker_fn=lambda t: N_ON)  # nu moare niciodata
        w = run(SeaWorker(self.cfg(fire_duration=0.05, max_cycles=3), b,
                          lambda *a: None, poll=0.01), 0.6)
        self.assertEqual(w.nutcracker_kills, 0)
        self.assertEqual(w.nutcracker_fails, 1)
        fire_presses = [k for k in b.keys if k[1] == "3"]
        self.assertEqual(len(fire_presses), 3)  # exact plafonul
        self.assertEqual(b.keys[-1][1], "1")    # revine la undita oricum

    def test_stop_mid_nutcracker_fight_is_immediate(self):
        b = SeaFakeBackend((1, 1), (2, 2),
                           grinch_fn=lambda t: G_OFF,
                           nutcracker_fn=lambda t: N_ON)
        w = SeaWorker(self.cfg(fire_duration=5.0, sword_interval=0.05, max_cycles=10), b,
                      lambda *a: None, poll=0.01)
        w.start()
        time.sleep(0.15)
        t0 = time.monotonic()
        w.request_stop()
        w.join(2)
        self.assertFalse(w.is_alive())
        self.assertLess(time.monotonic() - t0, 0.3)

    def test_does_nothing_when_both_absent(self):
        b = SeaFakeBackend((1, 1), (2, 2),
                           grinch_fn=lambda t: G_OFF, nutcracker_fn=lambda t: N_OFF)
        w = run(SeaWorker(self.cfg(), b, lambda *a: None, poll=0.01), 0.2)
        self.assertEqual((w.grinch_kills, w.nutcracker_kills, len(b.clicks), len(b.keys)),
                         (0, 0, 0, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
