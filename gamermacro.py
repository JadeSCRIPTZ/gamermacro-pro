"""
GamerMacro Pro — Fishing Edition  v2.1
Cyberpunk HUD design — stable tkinter only, no Canvas widgets
"""
import tkinter as tk
import threading, time, random, sys, math

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE    = 0
except ImportError:
    print("Run: pip install pyautogui pillow"); sys.exit(1)

# ── Palette ────────────────────────────────────────────────────────────────────
C = {
    "bg":       "#070B14", "bg2": "#0D1220", "bg3": "#111827",
    "panel":    "#0A0F1E", "border": "#1E2D4A", "border2": "#2A3F66",
    "accent":   "#00D4FF", "accent2": "#0099CC", "accent_dim": "#003D52",
    "green":    "#00FF88", "green2": "#00CC6A",
    "red":      "#FF2D55", "red2": "#CC1F40",
    "yellow":   "#FFD60A", "purple": "#BF5AF2",
    "text":     "#E8F4FD", "text2": "#8BAFD4", "text3": "#4A6080",
}

FB = ("Consolas", 10, "bold")   # font button
FH = ("Consolas", 9,  "bold")   # font header
FS = ("Consolas", 8)            # font small
FM = ("Consolas", 10)           # font medium
FL = ("Consolas", 11, "bold")   # font large


# ─────────────────────────────────────────────────────────────────────────────
#  STABLE WIDGETS  (no Canvas item creation in __init__)
# ─────────────────────────────────────────────────────────────────────────────

class NeonButton(tk.Frame):
    """Neon border button: tk.Frame(border color) wraps tk.Button."""
    def __init__(self, master, text, cmd,
                 color=None, w=200, h=40, enabled=True, **kw):
        color = color or C["accent"]
        super().__init__(master, bg=color, padx=1, pady=1, **kw)

        self._color   = color
        self._cmd     = cmd
        self._enabled = enabled

        self._btn = tk.Button(
            self, text=text, command=self._click,
            bg=C["bg3"], fg=color,
            activebackground=C["bg2"], activeforeground="#FFFFFF",
            disabledforeground=C["text3"],
            relief="flat", bd=0, cursor="hand2",
            font=FB, width=w // 10,
            pady=(h - 24) // 2,
            state="normal" if enabled else "disabled")
        self._btn.pack(fill="both", expand=True)

        self._btn.bind("<Enter>", self._on_enter)
        self._btn.bind("<Leave>", self._on_leave)

        if not enabled:
            self.config(bg=C["border"])

    def _click(self):
        if self._enabled and self._cmd:
            self._cmd()

    def _on_enter(self, _=None):
        if not self._enabled: return
        self._btn.config(bg=C["accent_dim"] if self._color == C["accent"]
                         else C["bg2"],
                         fg="#FFFFFF")

    def _on_leave(self, _=None):
        if not self._enabled: return
        self._btn.config(bg=C["bg3"], fg=self._color)

    def set_enabled(self, state: bool):
        self._enabled = state
        self._btn.config(state="normal" if state else "disabled")
        self.config(bg=self._color if state else C["border"])
        if state:
            self._btn.config(bg=C["bg3"], fg=self._color)


class ToggleSwitch(tk.Frame):
    """ON/OFF toggle as a styled button row — no Canvas."""
    def __init__(self, master, on_toggle=None, **kw):
        super().__init__(master, bg=C["panel"], **kw)
        self._on       = False
        self._callback = on_toggle

        self._off_btn = tk.Button(self, text="  OFF  ",
            bg=C["border"], fg=C["text3"],
            activebackground=C["border2"], activeforeground=C["text"],
            relief="flat", bd=0, font=FS, cursor="hand2",
            command=self._set_off)
        self._off_btn.pack(side="left")

        tk.Frame(self, bg=C["border2"], width=1).pack(side="left", fill="y")

        self._on_btn = tk.Button(self, text="  ON  ",
            bg=C["bg3"], fg=C["text3"],
            activebackground=C["bg3"], activeforeground=C["purple"],
            relief="flat", bd=0, font=FS, cursor="hand2",
            command=self._set_on)
        self._on_btn.pack(side="left")

        self._update()

    def _set_on(self):
        if self._on: return
        self._on = True
        self._update()
        if self._callback: self._callback(True)

    def _set_off(self):
        if not self._on: return
        self._on = False
        self._update()
        if self._callback: self._callback(False)

    def _update(self):
        if self._on:
            self._on_btn.config(bg=C["purple"], fg="#FFFFFF")
            self._off_btn.config(bg=C["bg3"], fg=C["text3"])
        else:
            self._off_btn.config(bg=C["border"], fg=C["text"])
            self._on_btn.config(bg=C["bg3"], fg=C["text3"])

    def get(self): return self._on


class StatusOrb(tk.Label):
    """Pulsing dot via label text color cycling."""
    def __init__(self, master, **kw):
        super().__init__(master, text="●", fg=C["text3"],
                         bg=C["bg"], font=("Consolas", 14), **kw)
        self._on   = False
        self._tick = 0
        self._job  = None

    def set_active(self, active: bool):
        self._on = active
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        if active:
            self._pulse()
        else:
            self.config(fg=C["text3"])

    def _pulse(self):
        if not self._on: return
        self._tick += 1
        bright = 0.55 + 0.45 * math.sin(self._tick * 0.18)
        g = int(200 + 55 * bright)
        self.config(fg=f"#00{g:02x}55")
        self._job = self.after(45, self._pulse)


class ColorSwatch(tk.Frame):
    """Color preview square using Frame bg — no Canvas."""
    def __init__(self, master, size=36, **kw):
        super().__init__(master, width=size, height=size,
                         bg="#111111",
                         highlightthickness=1,
                         highlightbackground=C["border2"], **kw)
        self.pack_propagate(False)

    def set(self, r, g, b):
        self.config(bg=f"#{r:02x}{g:02x}{b:02x}")


class InputField(tk.Frame):
    """Label + styled Entry combo."""
    def __init__(self, master, label, default="0", w=7, **kw):
        super().__init__(master, bg=C["panel"], **kw)
        tk.Label(self, text=label, fg=C["text2"],
                 bg=C["panel"], font=FS).pack(anchor="w", pady=(0, 3))
        self.var = tk.StringVar(value=str(default))
        self._e = tk.Entry(self, textvariable=self.var, width=w,
                           bg=C["bg2"], fg=C["text"],
                           insertbackground=C["accent"],
                           relief="flat", bd=0, font=FM,
                           justify="center",
                           highlightthickness=1,
                           highlightcolor=C["accent"],
                           highlightbackground=C["border"])
        self._e.pack(ipady=6, ipadx=4)
        self._e.bind("<FocusIn>",
            lambda _: self._e.config(highlightbackground=C["accent"]))
        self._e.bind("<FocusOut>",
            lambda _: self._e.config(highlightbackground=C["border"]))


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
class FishBotApp:
    POLL = 0.05

    def __init__(self, root: tk.Tk):
        self.root      = root
        self._running  = False
        self._thread   = None
        self._natural  = False
        self._catches  = 0
        self._build_window()
        self._build_ui()

    def _build_window(self):
        r = self.root
        r.title("GamerMacro Pro — Fishing Edition")
        r.configure(bg=C["bg"])
        r.resizable(False, False)
        r.attributes("-topmost", True)
        w, h = 480, 760
        sw, sh = r.winfo_screenwidth(), r.winfo_screenheight()
        r.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Build all UI ───────────────────────────────────────────────────────────
    def _build_ui(self):
        root = self.root

        # Top accent bar
        tk.Frame(root, bg=C["accent"], height=2).pack(fill="x")

        # ── Header ─────────────────────────────────────────────
        hdr = tk.Frame(root, bg=C["bg"])
        hdr.pack(fill="x", padx=20, pady=(14, 10))

        left = tk.Frame(hdr, bg=C["bg"])
        left.pack(side="left")
        tk.Label(left, text="GAMERMACRO PRO",
                 fg=C["accent"], bg=C["bg"],
                 font=("Consolas", 19, "bold")).pack(anchor="w")
        tk.Label(left, text="FISHING EDITION  //  PIXEL WATCHER  //  v2.1",
                 fg=C["text3"], bg=C["bg"], font=FS).pack(anchor="w")

        right = tk.Frame(hdr, bg=C["bg"])
        right.pack(side="right", anchor="ne")
        self.orb = StatusOrb(right)
        self.orb.pack(side="left", padx=(0, 6))
        self.status_lbl = tk.Label(right, text="IDLE",
                                   fg=C["text3"], bg=C["bg"],
                                   font=("Consolas", 10, "bold"))
        self.status_lbl.pack(side="left")

        # Divider
        tk.Frame(root, bg=C["border2"], height=1).pack(fill="x")

        # ── Scrollable content ─────────────────────────────────
        wrap = tk.Frame(root, bg=C["bg"])
        wrap.pack(fill="both", expand=True)
        P = wrap  # alias

        def sp(n=10):
            tk.Frame(P, bg=C["bg"], height=n).pack(fill="x")

        sp(14)

        # ══ SECTION 1: COORDONATE ══════════════════════════════
        self._sec(P, "01", "COORDONATE PIXEL", "🎯")
        sp(8)

        card1 = self._card(P)
        xy = tk.Frame(card1, bg=C["panel"])
        xy.pack(fill="x", padx=16, pady=(14, 8))
        self.x_f = InputField(xy, "X  —  pixeli", "0", 8)
        self.x_f.pack(side="left", padx=(0, 14))
        self.y_f = InputField(xy, "Y  —  pixeli", "0", 8)
        self.y_f.pack(side="left")

        self.coord_lbl = tk.Label(card1, text="Nicio coordonata capturata.",
                                  fg=C["text3"], bg=C["panel"], font=FS)
        self.coord_lbl.pack(anchor="w", padx=16, pady=(0, 10))

        self.cap_btn = NeonButton(card1,
            "🖱   GET MOUSE POSITION  ( 3 secunde countdown )",
            self._start_capture, color=C["accent"], w=440, h=40)
        self.cap_btn.pack(padx=16, pady=(0, 14), fill="x")

        sp(10)

        # ══ SECTION 2: CULOARE ═════════════════════════════════
        self._sec(P, "02", "CULOARE TINTA", "🎨")
        sp(8)

        card2 = self._card(P)
        rgb_row = tk.Frame(card2, bg=C["panel"])
        rgb_row.pack(fill="x", padx=16, pady=(14, 8))

        self.r_f = InputField(rgb_row, "R", "255", 5)
        self.r_f.pack(side="left", padx=(0, 8))
        self.g_f = InputField(rgb_row, "G", "0", 5)
        self.g_f.pack(side="left", padx=(0, 8))
        self.b_f = InputField(rgb_row, "B", "0", 5)
        self.b_f.pack(side="left", padx=(0, 16))
        self.swatch = ColorSwatch(rgb_row, size=38)
        self.swatch.pack(side="left")

        self.color_lbl = tk.Label(card2, text="Nicio culoare capturata.",
                                  fg=C["text3"], bg=C["panel"], font=FS)
        self.color_lbl.pack(anchor="w", padx=16, pady=(0, 10))

        self.sample_btn = NeonButton(card2,
            "🎨   SAMPLE COLOUR AT CAPTURED PIXEL",
            self._sample_color, color=C["accent"], w=440, h=40)
        self.sample_btn.pack(padx=16, pady=(0, 14), fill="x")

        sp(10)

        # ══ SECTION 3: SETARI ══════════════════════════════════
        self._sec(P, "03", "SETARI DETECTIE", "⚙")
        sp(8)

        card3 = self._card(P)
        s = tk.Frame(card3, bg=C["panel"])
        s.pack(fill="x", padx=16, pady=14)

        row1 = tk.Frame(s, bg=C["panel"])
        row1.pack(fill="x", pady=(0, 10))
        self.tol_f   = InputField(row1, "Toleranta  ±",        "15",  7)
        self.tol_f.pack(side="left", padx=(0, 20))
        self.delay_f = InputField(row1, "Delay reactie  ( s )", "0.1", 7)
        self.delay_f.pack(side="left")

        row2 = tk.Frame(s, bg=C["panel"])
        row2.pack(fill="x")
        self.cd_f = InputField(row2, "Cooldown dupa actiune  ( s )", "3.0", 7)
        self.cd_f.pack(side="left")

        sp(10)

        # ══ SECTION 4: MOD NATURAL ═════════════════════════════
        self._sec(P, "04", "MOD NATURAL", "🎲")
        sp(8)

        card4 = self._card(P)
        nat = tk.Frame(card4, bg=C["panel"])
        nat.pack(fill="x", padx=16, pady=14)

        nat_top = tk.Frame(nat, bg=C["panel"])
        nat_top.pack(fill="x")

        nat_txt = tk.Frame(nat_top, bg=C["panel"])
        nat_txt.pack(side="left", expand=True, fill="x")
        tk.Label(nat_txt, text="8% sansa sa sara o detectie",
                 fg=C["text"], bg=C["panel"],
                 font=("Consolas", 11, "bold")).pack(anchor="w")
        tk.Label(nat_txt,
                 text="Programul ignora intentionat ~1 din 12 detectii\n"
                      "pentru a parea mai natural si mai putin bot.",
                 fg=C["text2"], bg=C["panel"],
                 font=FS, justify="left").pack(anchor="w", pady=(3, 0))

        self.toggle = ToggleSwitch(nat_top, on_toggle=self._on_natural)
        self.toggle.pack(side="right", padx=(14, 0))

        self.nat_lbl = tk.Label(nat, text="STATUS: DEZACTIVAT",
                                fg=C["text3"], bg=C["panel"],
                                font=("Consolas", 8, "bold"))
        self.nat_lbl.pack(anchor="w", pady=(10, 0))

        sp(10)

        # ══ SECTION 5: CONTROL ═════════════════════════════════
        self._sec(P, "05", "CONTROL MACRO", "▶")
        sp(8)

        card5 = self._card(P)
        btns = tk.Frame(card5, bg=C["panel"])
        btns.pack(padx=16, pady=14)

        self.start_btn = NeonButton(btns, "▶   START MACRO",
            self._start_macro, color=C["green"], w=210, h=48)
        self.start_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = NeonButton(btns, "■   STOP",
            self._stop_macro, color=C["red"], w=180, h=48, enabled=False)
        self.stop_btn.pack(side="left")

        sp(10)

        # ══ SECTION LOG ════════════════════════════════════════
        self._sec(P, "LOG", "ACTIVITATE", "📋")
        sp(8)

        card6 = self._card(P)

        stat_row = tk.Frame(card6, bg=C["panel"])
        stat_row.pack(fill="x", padx=16, pady=(10, 6))
        self.catch_lbl = tk.Label(stat_row, text="CATCHES: 0",
                                  fg=C["yellow"], bg=C["panel"],
                                  font=("Consolas", 9, "bold"))
        self.catch_lbl.pack(side="left")
        self.state_lbl = tk.Label(stat_row, text="STATE: IDLE",
                                  fg=C["text3"], bg=C["panel"],
                                  font=("Consolas", 9, "bold"))
        self.state_lbl.pack(side="right")

        self.log = tk.Text(card6,
            bg=C["bg2"], fg=C["text2"], font=FS,
            relief="flat", state="disabled", wrap="word",
            bd=0, height=10, selectbackground=C["accent_dim"],
            insertbackground=C["accent"])
        self.log.pack(fill="both", padx=16, pady=(0, 14))

        self.log.tag_config("ok",     foreground=C["green"])
        self.log.tag_config("warn",   foreground=C["yellow"])
        self.log.tag_config("error",  foreground=C["red"])
        self.log.tag_config("dim",    foreground=C["text3"])
        self.log.tag_config("accent", foreground=C["accent"])
        self.log.tag_config("purple", foreground=C["purple"])

        sp(4)

        # Footer
        tk.Label(root,
            text="⚠  FAILSAFE: muta mouse-ul in coltul stanga-sus pentru oprire urgenta",
            fg=C["text3"], bg=C["bg"], font=FS).pack(pady=(4, 8))

        self._log("GamerMacro Pro v2.1 pornit.", "accent")
        self._log("Seteaza coordonatele, culoarea, apoi START.", "dim")
        self._log("Sfat: arunca undita INAINTE de a apasa START.", "dim")

    # ── UI helpers ─────────────────────────────────────────────────────────────
    def _sec(self, parent, num, title, icon=""):
        f = tk.Frame(parent, bg=C["bg"])
        f.pack(fill="x", padx=18)
        tk.Label(f, text=f"[ {num} ]", fg=C["text3"],
                 bg=C["bg"], font=("Consolas", 8, "bold")).pack(side="left",
                                                                 padx=(0, 8))
        tk.Label(f, text=f"{icon}  {title}",
                 fg=C["accent"], bg=C["bg"],
                 font=("Consolas", 9, "bold")).pack(side="left")
        tk.Frame(f, bg=C["border2"], height=1).pack(
            side="left", fill="x", expand=True, padx=(10, 0))

    def _card(self, parent):
        outer = tk.Frame(parent, bg=C["border2"], padx=1, pady=1)
        outer.pack(fill="x", padx=18)
        inner = tk.Frame(outer, bg=C["panel"])
        inner.pack(fill="both")
        return inner

    # ── Log ────────────────────────────────────────────────────────────────────
    def _log(self, msg, tag="dim"):
        ts = time.strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"[{ts}]  {msg}\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    # ── Capture position ───────────────────────────────────────────────────────
    def _start_capture(self):
        self.cap_btn.set_enabled(False)
        self._cdown(3)

    def _cdown(self, n):
        if n > 0:
            self.coord_lbl.config(
                text=f"  Muta mouse-ul pe pixel…  {n}s", fg=C["yellow"])
            self.root.after(1000, self._cdown, n - 1)
        else:
            try:
                x, y = pyautogui.position()
                self.x_f.var.set(str(x))
                self.y_f.var.set(str(y))
                self.coord_lbl.config(
                    text=f"  ✓  X = {x}   Y = {y}", fg=C["green"])
                self._log(f"Coordonate capturate  →  X={x}  Y={y}", "ok")
            except Exception as e:
                self.coord_lbl.config(text=f"  ✗  {e}", fg=C["red"])
            finally:
                self.cap_btn.set_enabled(True)

    # ── Sample colour ──────────────────────────────────────────────────────────
    def _sample_color(self):
        try:
            x = int(self.x_f.var.get())
            y = int(self.y_f.var.get())
        except ValueError:
            self._log("Coordonate invalide.", "error"); return
        try:
            px = pyautogui.pixel(x, y)
            r, g, b = px[0], px[1], px[2]
            self.r_f.var.set(str(r))
            self.g_f.var.set(str(g))
            self.b_f.var.set(str(b))
            self.swatch.set(r, g, b)
            hx = f"#{r:02x}{g:02x}{b:02x}"
            self.color_lbl.config(
                text=f"  ✓  RGB({r}, {g}, {b})   {hx}", fg=C["green"])
            self._log(f"Culoare  →  RGB({r},{g},{b})  {hx}", "ok")
        except Exception as e:
            self.color_lbl.config(text=f"  ✗  {e}", fg=C["red"])
            self._log(f"Eroare: {e}", "error")

    # ── Natural toggle ─────────────────────────────────────────────────────────
    def _on_natural(self, state: bool):
        self._natural = state
        if state:
            self.nat_lbl.config(
                text="STATUS: ACTIVAT  —  8% skip per detectie",
                fg=C["purple"])
            self._log("Mod Natural ACTIVAT (8% skip).", "purple")
        else:
            self.nat_lbl.config(text="STATUS: DEZACTIVAT", fg=C["text3"])
            self._log("Mod Natural dezactivat.", "dim")

    # ── Parse inputs ───────────────────────────────────────────────────────────
    def _parse(self):
        x     = int(self.x_f.var.get())
        y     = int(self.y_f.var.get())
        r     = int(self.r_f.var.get())
        g     = int(self.g_f.var.get())
        b     = int(self.b_f.var.get())
        tol   = int(self.tol_f.var.get())
        delay = float(self.delay_f.var.get())
        cd    = float(self.cd_f.var.get())
        sc    = pyautogui.size()
        if not (0 <= x < sc.width and 0 <= y < sc.height):
            raise ValueError(f"Coordonate ({x},{y}) in afara ecranului.")
        return x, y, r, g, b, tol, delay, cd

    # ── Macro loop ─────────────────────────────────────────────────────────────
    def _watch(self, x, y, tr, tg, tb, tol, delay, cd, natural):
        self._upstate("RESET")
        state   = "RESET"
        skipped = 0

        while self._running:
            try:
                px = pyautogui.pixel(x, y)
                cr, cg, cb = px[0], px[1], px[2]
                match = (abs(cr-tr) <= tol and
                         abs(cg-tg) <= tol and
                         abs(cb-tb) <= tol)

                if state == "RESET":
                    if not match:
                        state = "WATCH"
                        self._upstate("WATCH")

                elif state == "WATCH":
                    if match:
                        if natural and random.random() < 0.08:
                            skipped += 1
                            self.root.after(0, self._log,
                                f"[skip #{skipped}] Mod natural — ignorat.", "purple")
                            state = "RESET"
                            self._upstate("RESET")
                            time.sleep(self.POLL); continue

                        self._catches += 1
                        n = self._catches
                        self.root.after(0, self._log,
                            f"[#{n}] Bobber!  RGB({cr},{cg},{cb})  "
                            f"— delay {delay}s…", "warn")
                        self.root.after(0, self.catch_lbl.config,
                            {"text": f"CATCHES: {n}"})

                        if delay > 0: time.sleep(delay)
                        if not self._running: break

                        pyautogui.rightClick()
                        time.sleep(0.5)
                        pyautogui.rightClick()

                        self.root.after(0, self._log,
                            f"[#{n}] Re-aruncat. Cooldown {cd}s…", "ok")
                        time.sleep(cd)
                        state = "RESET"
                        self._upstate("RESET")

            except pyautogui.FailSafeException:
                self.root.after(0, self._log,
                    "FAILSAFE! Mouse in colt stanga-sus.", "error")
                break
            except Exception as e:
                self.root.after(0, self._log, f"Eroare: {e}", "error"); break

            time.sleep(self.POLL)

        self._running = False
        self.root.after(0, self._stopped)

    def _upstate(self, s):
        col = {
            "RESET": C["text3"],
            "WATCH": C["accent"],
            "IDLE":  C["text3"],
        }.get(s, C["text3"])
        self.root.after(0, self.state_lbl.config,
                        {"text": f"STATE: {s}", "fg": col})

    # ── Start / Stop ───────────────────────────────────────────────────────────
    def _start_macro(self):
        if self._running: return
        try:
            args = self._parse()
        except ValueError as e:
            self._log(f"Eroare input: {e}", "error"); return

        self._running = True
        self._catches = 0
        self.catch_lbl.config(text="CATCHES: 0")
        self._set_ui(True)

        x, y, r, g, b, tol, delay, cd = args
        nat = self._natural
        self._log(
            f"START  ({x},{y})  RGB({r},{g},{b})  ±{tol}  "
            f"delay={delay}s  cd={cd}s  nat={'ON' if nat else 'OFF'}",
            "accent")

        self._thread = threading.Thread(
            target=self._watch,
            args=(x, y, r, g, b, tol, delay, cd, nat),
            daemon=True)
        self._thread.start()

    def _stop_macro(self):
        self._running = False
        self._log("Oprire solicitata…", "warn")

    def _stopped(self):
        self._set_ui(False)
        self._upstate("IDLE")
        self._log("Macro oprit.", "dim")

    def _set_ui(self, running: bool):
        self.orb.set_active(running)
        self.status_lbl.config(
            text="RUNNING" if running else "IDLE",
            fg=C["green"] if running else C["text3"])
        self.start_btn.set_enabled(not running)
        self.stop_btn.set_enabled(running)
        self.cap_btn.set_enabled(not running)
        self.sample_btn.set_enabled(not running)

    def on_close(self):
        self._running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app  = FishBotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
