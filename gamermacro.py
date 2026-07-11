"""
GamerMacro Pro — Fishing Edition v5.1
Stabil, fara taburi, fara crash-uri garantat.
"""
import tkinter as tk
import threading, time, random, sys

import pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

from pynput.mouse import Button, Controller as MC
_mouse = MC()

def right_click():
    _mouse.click(Button.right, 1)

# ── Culori ─────────────────────────────────────────────────────
BG   = "#1C1917"
S1   = "#292524"
S2   = "#3C3835"
S3   = "#44403C"
BRD  = "#57534E"
ORG  = "#D97706"
ORG2 = "#F59E0B"
ORG3 = "#78350F"
GRN  = "#34D399"
RED  = "#F87171"
REDK = "#7F1D1D"
YEL  = "#FBBF24"
PRP  = "#A78BFA"
BLU  = "#60A5FA"
TXT  = "#FAFAF9"
TX2  = "#A8A29E"
TX3  = "#57534E"
FN   = "Segoe UI"


def btn(p, text, cmd, bg=ORG, fg="#1C1917", abg=None,
        dis=False, fsize=10, **kw):
    b = tk.Button(p, text=text, command=cmd,
                  bg=bg, fg=fg,
                  activebackground=abg or bg,
                  activeforeground=fg,
                  disabledforeground=TX3,
                  relief="flat", bd=0, cursor="hand2",
                  font=(FN, fsize, "bold"),
                  state="disabled" if dis else "normal", **kw)
    return b


def lbl(p, text, fg=TX2, size=8, bold=False, **kw):
    return tk.Label(p, text=text, fg=fg, bg=p["bg"],
                    font=(FN, size, "bold" if bold else "normal"), **kw)


def sep(p, pady=6):
    tk.Frame(p, bg=BRD, height=1).pack(fill="x", pady=pady)


def sec(p, icon, title):
    f = tk.Frame(p, bg=p["bg"])
    f.pack(fill="x", pady=(10, 4))
    tk.Label(f, text=icon, fg=ORG2, bg=p["bg"],
             font=(FN, 10)).pack(side="left", padx=(0, 6))
    tk.Label(f, text=title, fg=TXT, bg=p["bg"],
             font=(FN, 10, "bold")).pack(side="left")
    tk.Frame(f, bg=S3, height=1).pack(
        side="left", fill="x", expand=True, padx=(8, 0))


class Inp(tk.Frame):
    """Label + Entry compact."""
    def __init__(self, master, label, val="0", w=7, **kw):
        super().__init__(master, bg=master["bg"], **kw)
        tk.Label(self, text=label, fg=TX2, bg=self["bg"],
                 font=(FN, 8)).pack(anchor="w", pady=(0, 2))
        self.var = tk.StringVar(value=str(val))
        e = tk.Entry(self, textvariable=self.var, width=w,
                     bg=S2, fg=TXT, insertbackground=ORG2,
                     relief="flat", bd=0,
                     font=("Consolas", 10), justify="center",
                     highlightthickness=1,
                     highlightbackground=BRD,
                     highlightcolor=ORG)
        e.pack(ipady=6, ipadx=4)
        e.bind("<FocusIn>",
               lambda _: e.config(highlightbackground=ORG))
        e.bind("<FocusOut>",
               lambda _: e.config(highlightbackground=BRD))


class Swatch(tk.Frame):
    def __init__(self, master, sz=34, **kw):
        super().__init__(master, width=sz, height=sz,
                         bg=S2, highlightthickness=1,
                         highlightbackground=BRD, **kw)
        self.pack_propagate(False)

    def set(self, r, g, b):
        c = f"#{r:02x}{g:02x}{b:02x}"
        self.config(bg=c, highlightbackground=c)


# ── Aplicatia ──────────────────────────────────────────────────
class App:
    POLL = 0.05

    def __init__(self, root):
        self.root      = root
        self._running  = False
        self._natural  = False
        self._timeout  = False
        self._catches  = 0
        self._recals   = 0
        self._thread   = None
        self._start_ts = None
        self._ts_list  = []   # timestamps catches
        self._stats_job = None

        self._setup()
        self._build()

        # Stats update dupa ce UI e gata
        self.root.after(1000, self._tick_stats)

    def _setup(self):
        self.root.title("GamerMacro Pro — Fishing")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        W, H = 500, 800
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    def _build(self):
        # Bara portocalie sus
        tk.Frame(self.root, bg=ORG, height=3).pack(fill="x")

        # Header
        h = tk.Frame(self.root, bg=BG)
        h.pack(fill="x", padx=18, pady=(12, 8))
        hl = tk.Frame(h, bg=BG); hl.pack(side="left")
        row = tk.Frame(hl, bg=BG); row.pack(anchor="w")
        tk.Label(row, text="●", fg=ORG, bg=BG,
                 font=(FN, 14)).pack(side="left", padx=(0, 8))
        tk.Label(row, text="GamerMacro Pro",
                 fg=TXT, bg=BG,
                 font=(FN, 16, "bold")).pack(side="left")
        tk.Label(hl, text="Fishing Edition  ·  v5.1",
                 fg=TX3, bg=BG, font=(FN, 8)).pack(anchor="w", pady=(2, 0))

        hr = tk.Frame(h, bg=BG); hr.pack(side="right", anchor="ne")
        self._status = tk.Label(hr, text="  IDLE  ",
                                fg=TX3, bg=S2,
                                font=(FN, 9, "bold"), padx=10, pady=4)
        self._status.pack(anchor="e")
        self._clbl = tk.Label(hr, text="Catches: 0",
                              fg=YEL, bg=BG, font=(FN, 8))
        self._clbl.pack(anchor="e", pady=(3, 0))

        tk.Frame(self.root, bg=BRD, height=1).pack(fill="x")

        # Canvas scroll
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)
        cv = tk.Canvas(outer, bg=BG, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical",
                          command=cv.yview,
                          bg=S2, troughcolor=BG,
                          activebackground=ORG)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        cv.configure(yscrollcommand=sb.set)
        self._frm = tk.Frame(cv, bg=BG)
        wid = cv.create_window((0, 0), window=self._frm, anchor="nw")
        self._frm.bind("<Configure>",
                       lambda e: cv.configure(
                           scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",
                lambda e: cv.itemconfig(wid, width=e.width))
        self.root.bind_all("<MouseWheel>",
                           lambda e: cv.yview_scroll(
                               int(-1 * (e.delta / 120)), "units"))

        tk.Frame(self.root, bg=BRD, height=1).pack(fill="x")
        tk.Label(self.root,
                 text="⚠  Failsafe: muta mouse-ul in coltul stanga-sus",
                 fg=TX3, bg=BG, font=(FN, 7)).pack(pady=4)

        self._content()

    def _card(self):
        o = tk.Frame(self._frm, bg=S1,
                     highlightthickness=1,
                     highlightbackground=BRD)
        o.pack(fill="x", padx=14, pady=(0, 10))
        i = tk.Frame(o, bg=S1)
        i.pack(fill="both", padx=12, pady=10)
        return i

    def _content(self):
        P = self._frm

        def gap(n=8):
            tk.Frame(P, bg=BG, height=n).pack(fill="x")

        gap(10)

        # ── COORDONATE ────────────────────────────────────────
        sec(P, "🎯", "Coordonate Pixel")
        c = self._card()
        r = tk.Frame(c, bg=S1); r.pack(fill="x", pady=(0, 8))
        self.xf = Inp(r, "X  (pixeli)", "0", 8)
        self.xf.pack(side="left", padx=(0, 14))
        self.yf = Inp(r, "Y  (pixeli)", "0", 8)
        self.yf.pack(side="left")
        self._clbl_c = tk.Label(c, text="Nicio coordonata capturata.",
                                fg=TX3, bg=S1, font=(FN, 8))
        self._clbl_c.pack(anchor="w", pady=(0, 8))
        self._capbtn = btn(c,
                           "🖱   Captureaza Pozitie  ( 3s countdown )",
                           self._cap)
        self._capbtn.pack(fill="x", ipady=8)

        # ── CULOARE ───────────────────────────────────────────
        sec(P, "🎨", "Culoare Tinta")
        c = self._card()
        r = tk.Frame(c, bg=S1); r.pack(fill="x", pady=(0, 8))
        self.rf = Inp(r, "R", "255", 5); self.rf.pack(side="left", padx=(0, 8))
        self.gf = Inp(r, "G", "0",   5); self.gf.pack(side="left", padx=(0, 8))
        self.bf = Inp(r, "B", "0",   5); self.bf.pack(side="left", padx=(0, 10))
        self._sw = Swatch(c.__class__.__mro__[0] and r or r, 36)
        self._sw = Swatch(r, 36); self._sw.pack(side="left")
        self._clbl_col = tk.Label(c, text="Nicio culoare capturata.",
                                  fg=TX3, bg=S1, font=(FN, 8))
        self._clbl_col.pack(anchor="w", pady=(0, 8))
        self._samplebtn = btn(c, "🎨   Sample Culoare la Pixel",
                              self._sample)
        self._samplebtn.pack(fill="x", ipady=8)

        # ── SETARI ────────────────────────────────────────────
        sec(P, "⚙️", "Setari Detectie")
        c = self._card()
        r = tk.Frame(c, bg=S1); r.pack(fill="x", pady=(0, 8))
        self.tolf = Inp(r, "Toleranta ±",        "15",  7)
        self.tolf.pack(side="left", padx=(0, 16))
        self.dlf  = Inp(r, "Delay reactie (s)",  "0.1", 7)
        self.dlf.pack(side="left")
        self.cdf  = Inp(c, "Cooldown dupa aruncare (s)", "3.0", 7)
        self.cdf.pack(anchor="w")

        # ── TIMEOUT RECALIBRARE ───────────────────────────────
        sec(P, "🔄", "Timeout Recalibrare")
        c = self._card()
        r = tk.Frame(c, bg=S1); r.pack(fill="x", pady=(0, 8))

        self._to_var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(r,
                            text="Activ — recalibreaza daca nu vede culoarea in X secunde",
                            variable=self._to_var,
                            bg=S1, fg=TXT,
                            selectcolor=S2,
                            activebackground=S1,
                            activeforeground=TXT,
                            font=(FN, 9),
                            command=self._on_to_toggle)
        cb.pack(anchor="w")

        r2 = tk.Frame(c, bg=S1); r2.pack(fill="x")
        self.tof = Inp(r2, "Timeout (secunde)", "15", 6)
        self.tof.pack(side="left")
        self._tolbl = tk.Label(r2, text="  —  Dezactivat",
                               fg=TX3, bg=S1, font=(FN, 8))
        self._tolbl.pack(side="left", padx=(10, 0))

        # ── MOD NATURAL ───────────────────────────────────────
        sec(P, "🎲", "Mod Natural")
        c = self._card()
        r = tk.Frame(c, bg=S1); r.pack(fill="x", pady=(0, 6))
        self._nat_var = tk.BooleanVar(value=False)
        tk.Checkbutton(r,
                       text="8% sansa sa sara o detectie (apare mai uman)",
                       variable=self._nat_var,
                       bg=S1, fg=TXT,
                       selectcolor=S2,
                       activebackground=S1,
                       font=(FN, 9),
                       command=self._on_nat).pack(anchor="w")
        self._natlbl = tk.Label(c, text="Status: Dezactivat",
                                fg=TX3, bg=S1, font=(FN, 8))
        self._natlbl.pack(anchor="w")

        # ── CONTROL ───────────────────────────────────────────
        sec(P, "▶", "Control Macro")
        c = self._card()
        r = tk.Frame(c, bg=S1); r.pack(fill="x")
        self._startbtn = btn(r, "▶   START MACRO",
                             self._start, bg=ORG, abg=ORG2, fsize=10)
        self._startbtn.pack(side="left", fill="x",
                            expand=True, ipady=12, padx=(0, 8))
        self._stopbtn = btn(r, "■   STOP",
                            self._stop, bg=REDK, fg=RED,
                            abg="#5C1111", dis=True, fsize=10)
        self._stopbtn.pack(side="left", fill="x",
                           expand=True, ipady=12)

        # ── STATE + LOG ───────────────────────────────────────
        sec(P, "📋", "Log Activitate")
        c = self._card()
        sr = tk.Frame(c, bg=S1); sr.pack(fill="x", pady=(0, 6))
        self._stlbl = tk.Label(sr, text="State: IDLE",
                               fg=TX3, bg=S1,
                               font=(FN, 9, "bold"))
        self._stlbl.pack(side="left")
        self._rlbl = tk.Label(sr, text="Recal: 0",
                              fg=PRP, bg=S1,
                              font=(FN, 9, "bold"))
        self._rlbl.pack(side="right")
        self._log_w = tk.Text(c, bg=S2, fg=TX2,
                              font=("Consolas", 8),
                              relief="flat", state="disabled",
                              wrap="word", bd=6, height=8,
                              selectbackground=S3)
        self._log_w.pack(fill="both")
        for tag, col in [("ok", GRN), ("warn", YEL), ("err", RED),
                         ("dim", TX3), ("hi", ORG2), ("pur", PRP),
                         ("bl", BLU)]:
            self._log_w.tag_config(tag, foreground=col)

        # ── STATISTICI ────────────────────────────────────────
        sec(P, "📊", "Statistici Sesiune")
        c = self._card()

        # Rate cards
        rc = tk.Frame(c, bg=S1); rc.pack(fill="x", pady=(0, 8))

        def rate_box(parent, title, attr, color=ORG2):
            f = tk.Frame(parent, bg=S2,
                         highlightthickness=1,
                         highlightbackground=BRD)
            f.pack(side="left", fill="both",
                   expand=True, padx=(0, 6))
            tk.Label(f, text=title, fg=TX3, bg=S2,
                     font=(FN, 7, "bold")).pack(pady=(6, 2))
            v = tk.Label(f, text="—", fg=color, bg=S2,
                         font=(FN, 15, "bold"))
            v.pack()
            tk.Label(f, text="catches", fg=TX3, bg=S2,
                     font=(FN, 7)).pack(pady=(0, 6))
            setattr(self, attr, v)

        rate_box(rc, "PE MINUT",  "_stat_min")
        rate_box(rc, "30 MINUTE", "_stat_30m", BLU)
        rate_box(rc, "1 ORA",     "_stat_1h",  GRN)

        # Detalii
        dc = tk.Frame(c, bg=S1); dc.pack(fill="x")

        def detail_row(parent, label, attr, color=TX2):
            f = tk.Frame(parent, bg=S1)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, fg=TX2, bg=S1,
                     font=(FN, 9)).pack(side="left")
            v = tk.Label(f, text="—", fg=color, bg=S1,
                         font=(FN, 9, "bold"))
            v.pack(side="right")
            setattr(self, attr, v)

        detail_row(dc, "Timp sesiune:",        "_stat_time", ORG2)
        detail_row(dc, "Total catches:",       "_stat_tot",  GRN)
        detail_row(dc, "Timp mediu intre:",    "_stat_avg",  TX2)
        detail_row(dc, "Proiectie 1h:",        "_stat_p1h",  YEL)
        detail_row(dc, "Proiectie 8h:",        "_stat_p8h",  YEL)
        detail_row(dc, "Recalibrari:",         "_stat_rec",  PRP)

        gap(12)

        self._log("GamerMacro Pro v5.1 ready.", "hi")
        self._log("Nou: Timeout recalibrare + statistici live!", "bl")
        self._log("Configureaza si apasa START MACRO.", "dim")

    # ── Toggle handlers ────────────────────────────────────────
    def _on_to_toggle(self):
        self._timeout = self._to_var.get()
        if self._timeout:
            self._tolbl.config(text="  —  Activat", fg=PRP)
            self._log("Timeout recalibrare ACTIVAT.", "pur")
        else:
            self._tolbl.config(text="  —  Dezactivat", fg=TX3)
            self._log("Timeout dezactivat.", "dim")

    def _on_nat(self):
        self._natural = self._nat_var.get()
        if self._natural:
            self._natlbl.config(text="Status: Activat — 8% skip", fg=ORG2)
            self._log("Mod Natural ACTIVAT.", "pur")
        else:
            self._natlbl.config(text="Status: Dezactivat", fg=TX3)
            self._log("Mod Natural dezactivat.", "dim")

    # ── Captureaza pozitie ─────────────────────────────────────
    def _cap(self):
        self._capbtn.config(state="disabled")
        self._cd(3)

    def _cd(self, n):
        if n > 0:
            self._clbl_c.config(text=f"Muta mouse-ul pe pixel…  {n}s",
                                fg=YEL)
            self.root.after(1000, self._cd, n - 1)
        else:
            try:
                x, y = pyautogui.position()
                self.xf.var.set(str(x))
                self.yf.var.set(str(y))
                self._clbl_c.config(text=f"✓  X={x}   Y={y}", fg=GRN)
                self._log(f"Coordonate → X={x}  Y={y}", "ok")
            except Exception as e:
                self._clbl_c.config(text=f"Eroare: {e}", fg=RED)
            finally:
                self._capbtn.config(state="normal")

    # ── Sample culoare ─────────────────────────────────────────
    def _sample(self):
        try:
            x = int(self.xf.var.get())
            y = int(self.yf.var.get())
            p = pyautogui.pixel(x, y)
            r, g, b = p[0], p[1], p[2]
            self.rf.var.set(str(r))
            self.gf.var.set(str(g))
            self.bf.var.set(str(b))
            self._sw.set(r, g, b)
            hx = f"#{r:02x}{g:02x}{b:02x}"
            self._clbl_col.config(
                text=f"✓  RGB({r},{g},{b})   {hx}", fg=GRN)
            self._log(f"Culoare → RGB({r},{g},{b})  {hx}", "ok")
        except Exception as e:
            self._clbl_col.config(text=f"Eroare: {e}", fg=RED)
            self._log(f"Eroare: {e}", "err")

    # ── Parse ──────────────────────────────────────────────────
    def _parse(self):
        x   = int(self.xf.var.get())
        y   = int(self.yf.var.get())
        r   = int(self.rf.var.get())
        g   = int(self.gf.var.get())
        b   = int(self.bf.var.get())
        tol = int(self.tolf.var.get())
        dl  = float(self.dlf.var.get())
        cd  = float(self.cdf.var.get())
        to  = float(self.tof.var.get()) if self._timeout else 0
        sc  = pyautogui.size()
        if not (0 <= x < sc.width and 0 <= y < sc.height):
            raise ValueError(f"Coordonate ({x},{y}) in afara ecranului.")
        return x, y, r, g, b, tol, dl, cd, to

    # ── Macro loop ─────────────────────────────────────────────
    def _loop(self, x, y, tr, tg, tb, tol, delay, cd, to, nat):
        self._upst("RESET")
        state = "RESET"
        watch_since = None
        skip = 0

        while self._running:
            try:
                p = pyautogui.pixel(x, y)
                cr, cg, cb = p[0], p[1], p[2]
                hit = (abs(cr-tr)<=tol and
                       abs(cg-tg)<=tol and
                       abs(cb-tb)<=tol)

                if state == "RESET":
                    if not hit:
                        state = "WATCH"
                        watch_since = time.time()
                        self._upst("WATCH")

                elif state == "WATCH":
                    # Timeout recalibrare
                    if (to > 0 and watch_since and
                            time.time() - watch_since > to):
                        self._recals += 1
                        nr = self._recals
                        self.root.after(0, self._log,
                            f"[RECAL #{nr}] Timeout {to}s → retrag si re-arunc!",
                            "pur")
                        self.root.after(0, self._rlbl.config,
                            {"text": f"Recal: {nr}"})
                        right_click()
                        time.sleep(0.5)
                        right_click()
                        time.sleep(cd)
                        state = "RESET"
                        watch_since = None
                        self._upst("RESET")
                        continue

                    if hit:
                        if nat and random.random() < 0.08:
                            skip += 1
                            self.root.after(0, self._log,
                                f"[skip #{skip}] Mod natural — ignorat.", "pur")
                            state = "RESET"
                            watch_since = None
                            self._upst("RESET")
                            time.sleep(self.POLL)
                            continue

                        self._catches += 1
                        self._ts_list.append(time.time())
                        n = self._catches
                        self.root.after(0, self._log,
                            f"[#{n}] Bobber!  RGB({cr},{cg},{cb})"
                            f"  delay {delay}s…", "warn")
                        self.root.after(0, self._clbl.config,
                            {"text": f"Catches: {n}"})

                        if delay > 0:
                            time.sleep(delay)
                        if not self._running:
                            break

                        right_click()
                        time.sleep(0.5)
                        right_click()

                        self.root.after(0, self._log,
                            f"[#{n}] Re-aruncat! Cooldown {cd}s…", "ok")
                        time.sleep(cd)
                        state = "RESET"
                        watch_since = None
                        self._upst("RESET")

            except pyautogui.FailSafeException:
                self.root.after(0, self._log,
                    "FAILSAFE! Mouse in colt.", "err")
                break
            except Exception as e:
                self.root.after(0, self._log,
                    f"Eroare: {e}", "err")
                break

            time.sleep(self.POLL)

        self._running = False
        self.root.after(0, self._done)

    def _upst(self, s):
        cols = {"IDLE": TX3, "RESET": TX3, "WATCH": ORG2}
        self.root.after(0, self._stlbl.config,
                        {"text": f"State: {s}",
                         "fg": cols.get(s, TX3)})

    # ── Start / Stop ───────────────────────────────────────────
    def _start(self):
        if self._running:
            return
        try:
            args = self._parse()
        except ValueError as e:
            self._log(f"Input invalid: {e}", "err")
            return

        self._running  = True
        self._catches  = 0
        self._recals   = 0
        self._start_ts = time.time()
        self._ts_list.clear()
        self._clbl.config(text="Catches: 0")
        self._rlbl.config(text="Recal: 0")
        self._ui(True)

        x, y, r, g, b, tol, dl, cd, to = args
        self._log(
            f"START  ({x},{y})  RGB({r},{g},{b})  ±{tol}  "
            f"delay={dl}s  cd={cd}s  "
            f"timeout={'ON ' + str(to) + 's' if to > 0 else 'OFF'}  "
            f"nat={'ON' if self._natural else 'OFF'}", "hi")

        self._thread = threading.Thread(
            target=self._loop,
            args=(x, y, r, g, b, tol, dl, cd, to, self._natural),
            daemon=True)
        self._thread.start()

    def _stop(self):
        self._running = False
        self._log("Oprire…", "warn")

    def _done(self):
        self._ui(False)
        self._upst("IDLE")
        self._log("Macro oprit.", "dim")

    def _ui(self, run):
        self._status.config(
            text="  RUNNING  " if run else "  IDLE  ",
            fg="#1C1917" if run else TX3,
            bg=ORG if run else S2)
        self._startbtn.config(
            state="disabled" if run else "normal",
            bg=S3 if run else ORG)
        self._stopbtn.config(
            state="normal" if run else "disabled",
            bg=RED if run else REDK,
            fg="#1C1917" if run else RED)
        self._capbtn.config(
            state="disabled" if run else "normal")
        self._samplebtn.config(
            state="disabled" if run else "normal")

    # ── Statistici (la fiecare 3s) ─────────────────────────────
    def _tick_stats(self):
        try:
            self._compute_stats()
        except Exception:
            pass
        self.root.after(3000, self._tick_stats)

    def _compute_stats(self):
        now     = time.time()
        total   = self._catches
        elapsed = (now - self._start_ts) if self._start_ts else 0
        ts      = self._ts_list

        # Timp sesiune
        if self._start_ts and self._running:
            h = int(elapsed // 3600)
            m = int((elapsed % 3600) // 60)
            s = int(elapsed % 60)
            self._stat_time.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        else:
            self._stat_time.config(text="—")

        self._stat_tot.config(text=str(total))
        self._stat_rec.config(text=str(self._recals))

        # Rate
        if elapsed >= 60:
            rpm = total / (elapsed / 60)
        elif elapsed > 0:
            rpm = total / (elapsed / 60)
        else:
            rpm = 0

        # Ultimul minut
        last_min = len([t for t in ts if now - t <= 60])
        self._stat_min.config(text=str(last_min))
        self._stat_30m.config(text=f"{rpm * 30:.1f}")
        self._stat_1h.config(text=f"{rpm * 60:.1f}")

        # Proiectii
        self._stat_p1h.config(text=f"{rpm * 60:.0f} catches")
        self._stat_p8h.config(text=f"{rpm * 480:.0f} catches")

        # Timp mediu
        if len(ts) >= 2:
            diffs = [ts[i] - ts[i-1] for i in range(1, len(ts))]
            avg = sum(diffs) / len(diffs)
            self._stat_avg.config(text=f"{avg:.1f}s")
        else:
            self._stat_avg.config(text="—")

    # ── Log ────────────────────────────────────────────────────
    def _log(self, msg, tag="dim"):
        ts = time.strftime("%H:%M:%S")
        self._log_w.configure(state="normal")
        self._log_w.insert("end", f"[{ts}]  {msg}\n", tag)
        self._log_w.see("end")
        self._log_w.configure(state="disabled")

    def on_close(self):
        self._running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app  = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
