"""
GamerMacro Pro — Fishing Edition v4.0
Theme : Modern grey-violet (Discord/Linear inspired)
Scroll: canvas + recursive mousewheel bind
Layout: compact 2-col to fit screen without needing scroll
"""
import tkinter as tk
import threading, time, random, sys, math

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0
except ImportError:
    print("Run: pip install pyautogui pillow"); sys.exit(1)

# ─── Palette ──────────────────────────────────────────────────
BG    = "#23253A"   # fundal – gri-albastru inchis
S1    = "#2E3150"   # card suprafata
S2    = "#363A5C"   # input / suprafata 2
S3    = "#404468"   # hover / suprafata 3
BORD  = "#4B508A"   # border
ACC   = "#9B8FFF"   # violet accent principal
ACC2  = "#C4BBFF"   # violet deschis / text accent
ACCDK = "#5A4FCC"   # violet inchis (hover butoane)
GRN   = "#57E89C"   # verde
GRNDK = "#1A5C3A"   # verde bg
RED   = "#FF7575"   # rosu
REDDK = "#5C1F1F"   # rosu bg
YEL   = "#FFCC44"   # galben
TXT   = "#E8E9F3"   # text principal
TXT2  = "#9DA3C8"   # text secundar
TXT3  = "#5A5F8A"   # text disabled/muted

FN = "Segoe UI"     # font principal

def mk_btn(parent, text, cmd, bg=ACC, fg=TXT, abg=ACCDK,
           dfg=TXT3, state="normal", **kw):
    return tk.Button(parent, text=text, command=cmd,
                     bg=bg, fg=fg,
                     activebackground=abg, activeforeground=TXT,
                     disabledforeground=dfg,
                     relief="flat", bd=0, cursor="hand2",
                     font=(FN, 10, "bold"), state=state, **kw)

def lbl(parent, text, fg=TXT2, size=9, bold=False, **kw):
    return tk.Label(parent, text=text, fg=fg, bg=parent["bg"],
                    font=(FN, size, "bold" if bold else "normal"), **kw)

def sep(parent, color=BORD):
    tk.Frame(parent, bg=color, height=1).pack(fill="x")

def gap(parent, n=8):
    tk.Frame(parent, bg=parent["bg"], height=n).pack(fill="x")


class Field(tk.Frame):
    """Label + Entry compact."""
    def __init__(self, master, label, val="0", w=7, **kw):
        super().__init__(master, bg=master["bg"], **kw)
        lbl(self, label, fg=TXT2, size=8).pack(anchor="w", pady=(0,2))
        self.var = tk.StringVar(value=str(val))
        e = tk.Entry(self, textvariable=self.var, width=w,
                     bg=S2, fg=TXT, insertbackground=ACC2,
                     relief="flat", bd=0,
                     font=("Consolas", 10), justify="center",
                     highlightthickness=1,
                     highlightbackground=BORD,
                     highlightcolor=ACC)
        e.pack(ipady=6, ipadx=4)
        e.bind("<FocusIn>",  lambda _: e.config(highlightbackground=ACC))
        e.bind("<FocusOut>", lambda _: e.config(highlightbackground=BORD))


class Swatch(tk.Frame):
    def __init__(self, master, sz=38, **kw):
        super().__init__(master, width=sz, height=sz, bg=S2,
                         highlightthickness=1,
                         highlightbackground=BORD, **kw)
        self.pack_propagate(False)
    def update(self, r, g, b):
        c = f"#{r:02x}{g:02x}{b:02x}"
        self.config(bg=c, highlightbackground=c)


class Toggle(tk.Frame):
    """OFF | ON toggle — plain buttons, never crashes."""
    def __init__(self, master, cb=None, **kw):
        super().__init__(master, bg=S2,
                         highlightthickness=1,
                         highlightbackground=BORD, **kw)
        self._on = False; self._cb = cb
        self._boff = tk.Button(self, text=" OFF ",
            bg=S3, fg=TXT2, activebackground=BORD,
            activeforeground=TXT, relief="flat", bd=0,
            font=(FN, 8, "bold"), cursor="hand2",
            command=self._do_off)
        self._boff.pack(side="left", padx=2, pady=2)
        tk.Frame(self, bg=BORD, width=1).pack(side="left", fill="y")
        self._bon = tk.Button(self, text="  ON  ",
            bg=S2, fg=TXT3, activebackground=ACCDK,
            activeforeground=ACC2, relief="flat", bd=0,
            font=(FN, 8, "bold"), cursor="hand2",
            command=self._do_on)
        self._bon.pack(side="left", padx=2, pady=2)
        self._refresh()

    def _do_on(self):
        if self._on: return
        self._on = True; self._refresh()
        if self._cb: self._cb(True)

    def _do_off(self):
        if not self._on: return
        self._on = False; self._refresh()
        if self._cb: self._cb(False)

    def _refresh(self):
        if self._on:
            self._bon.config(bg=ACC, fg=TXT)
            self._boff.config(bg=S2, fg=TXT3)
            self.config(highlightbackground=ACC)
        else:
            self._boff.config(bg=S3, fg=TXT2)
            self._bon.config(bg=S2, fg=TXT3)
            self.config(highlightbackground=BORD)

    def get(self): return self._on


# ─── Main App ──────────────────────────────────────────────────
class App:
    POLL = 0.05

    def __init__(self, root):
        self.root = root
        self._running = self._natural = False
        self._catches = 0
        self._thread  = None
        self._setup_window()
        self._build()

    def _setup_window(self):
        self.root.title("GamerMacro Pro")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        W, H = 520, 650
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    def _build(self):
        # ── Top bar violet ──────────────────────────────────────
        tk.Frame(self.root, bg=ACC, height=3).pack(fill="x")

        # ── Header ─────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=18, pady=(12, 8))

        hl = tk.Frame(hdr, bg=BG)
        hl.pack(side="left")
        tk.Label(hl, text="GamerMacro Pro",
                 fg=TXT, bg=BG,
                 font=(FN, 17, "bold")).pack(anchor="w")
        tk.Label(hl, text="Fishing Edition  ·  Pixel Watcher",
                 fg=TXT3, bg=BG,
                 font=(FN, 9)).pack(anchor="w")

        hr = tk.Frame(hdr, bg=BG)
        hr.pack(side="right", anchor="ne")
        self._status = tk.Label(hr, text="⬤  IDLE",
                                fg=TXT3, bg=BG,
                                font=(FN, 9, "bold"))
        self._status.pack(anchor="e")
        self._clbl = tk.Label(hr, text="Catches: 0",
                              fg=YEL, bg=BG,
                              font=(FN, 9))
        self._clbl.pack(anchor="e", pady=(3, 0))

        sep(self.root, BORD)

        # ── Scroll canvas ───────────────────────────────────────
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)

        self._cvs = tk.Canvas(outer, bg=BG, bd=0,
                              highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical",
                          command=self._cvs.yview,
                          bg=S2, troughcolor=BG,
                          activebackground=ACC)
        sb.pack(side="right", fill="y")
        self._cvs.pack(side="left", fill="both", expand=True)
        self._cvs.configure(yscrollcommand=sb.set)

        self._frm = tk.Frame(self._cvs, bg=BG)
        self._wid = self._cvs.create_window(
            (0, 0), window=self._frm, anchor="nw")

        self._frm.bind("<Configure>",
            lambda e: self._cvs.configure(
                scrollregion=self._cvs.bbox("all")))
        self._cvs.bind("<Configure>",
            lambda e: self._cvs.itemconfig(self._wid, width=e.width))

        # ── Footer ──────────────────────────────────────────────
        sep(self.root, BORD)
        tk.Label(self.root,
                 text="⚠  Failsafe: muta mouse-ul in coltul stanga-sus",
                 fg=TXT3, bg=BG, font=(FN, 8)).pack(pady=5)

        # ── Build content + bind scroll ─────────────────────────
        self._content(self._frm)
        self._bind_scroll(self._frm)

    # ── Bind mousewheel recursiv pe toate widget-urile ─────────
    def _bind_scroll(self, w):
        w.bind("<MouseWheel>",
               lambda e: self._cvs.yview_scroll(
                   int(-1*(e.delta/120)), "units"))
        w.bind("<Button-4>",
               lambda e: self._cvs.yview_scroll(-1, "units"))
        w.bind("<Button-5>",
               lambda e: self._cvs.yview_scroll(1, "units"))
        for ch in w.winfo_children():
            self._bind_scroll(ch)

    # ── Card helper ────────────────────────────────────────────
    def _card(self, parent, **kw):
        w = tk.Frame(parent, bg=S1,
                     highlightthickness=1,
                     highlightbackground=BORD, **kw)
        w.pack(fill="x", padx=14, pady=(0, 12))
        return tk.Frame(w, bg=S1)

    # ── Section label ──────────────────────────────────────────
    def _sec(self, parent, icon, title):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", padx=14, pady=(12, 5))
        tk.Label(f, text=icon, fg=ACC2, bg=BG,
                 font=(FN, 10)).pack(side="left", padx=(0, 6))
        tk.Label(f, text=title, fg=TXT, bg=BG,
                 font=(FN, 10, "bold")).pack(side="left")
        tk.Frame(f, bg=BORD, height=1).pack(
            side="left", fill="x", expand=True, padx=(8, 0))

    # ── All content ────────────────────────────────────────────
    def _content(self, P):
        # ══ ROW 1: Coordonate + Culoare (side by side) ══════════
        self._sec(P, "🎯", "Coordonate  &  Culoare")
        row1 = tk.Frame(P, bg=BG)
        row1.pack(fill="x", padx=14, pady=(0, 12))

        # Card Coordonate
        cc = tk.Frame(row1, bg=S1,
                      highlightthickness=1,
                      highlightbackground=BORD)
        cc.pack(side="left", fill="both", expand=True, padx=(0, 6))
        ccc = tk.Frame(cc, bg=S1)
        ccc.pack(fill="both", padx=12, pady=12)

        xy = tk.Frame(ccc, bg=S1)
        xy.pack(fill="x", pady=(0, 8))
        self.xf = Field(xy, "X  (pixeli)", "0", 7)
        self.xf.pack(side="left", padx=(0, 10))
        self.yf = Field(xy, "Y  (pixeli)", "0", 7)
        self.yf.pack(side="left")

        self._clbl_coord = tk.Label(ccc, text="Nicio coordonata.",
                                    fg=TXT3, bg=S1, font=(FN, 8))
        self._clbl_coord.pack(anchor="w", pady=(0, 8))

        self._capbtn = mk_btn(ccc,
            "🖱  Get Position  (3s)",
            self._start_cap, bg=ACC, abg=ACCDK)
        self._capbtn.pack(fill="x", ipady=7)

        # Card Culoare
        col = tk.Frame(row1, bg=S1,
                       highlightthickness=1,
                       highlightbackground=BORD)
        col.pack(side="left", fill="both", expand=True)
        colc = tk.Frame(col, bg=S1)
        colc.pack(fill="both", padx=12, pady=12)

        rgb = tk.Frame(colc, bg=S1)
        rgb.pack(fill="x", pady=(0, 6))
        self.rf = Field(rgb, "R", "255", 4); self.rf.pack(side="left", padx=(0,5))
        self.gf = Field(rgb, "G", "0",   4); self.gf.pack(side="left", padx=(0,5))
        self.bf = Field(rgb, "B", "0",   4); self.bf.pack(side="left", padx=(0,8))
        self._sw = Swatch(rgb, 36); self._sw.pack(side="left")

        self._clbl_col = tk.Label(colc, text="Nicio culoare.",
                                  fg=TXT3, bg=S1, font=(FN, 8))
        self._clbl_col.pack(anchor="w", pady=(0, 8))

        self._colbtn = mk_btn(colc,
            "🎨  Sample Colour",
            self._sample, bg=ACC, abg=ACCDK)
        self._colbtn.pack(fill="x", ipady=7)

        # ══ ROW 2: Setari detectie ════════════════════════════════
        self._sec(P, "⚙️", "Setari Detectie")
        sc = self._card(P)
        sc.pack(fill="both", padx=12, pady=12)

        srow = tk.Frame(sc, bg=S1)
        srow.pack(fill="x")
        self.tolf  = Field(srow, "Toleranta  ±",        "15",  6)
        self.tolf.pack(side="left", padx=(0, 16))
        self.dlf   = Field(srow, "Delay reactie  (s)",  "0.1", 6)
        self.dlf.pack(side="left", padx=(0, 16))
        self.cdf   = Field(srow, "Cooldown  (s)",       "3.0", 6)
        self.cdf.pack(side="left")

        # ══ ROW 3: Mod Natural ════════════════════════════════════
        self._sec(P, "🎲", "Mod Natural")
        nc = self._card(P)
        nc.pack(fill="both", padx=12, pady=12)

        natrow = tk.Frame(nc, bg=S1)
        natrow.pack(fill="x")

        natleft = tk.Frame(natrow, bg=S1)
        natleft.pack(side="left", fill="x", expand=True)
        tk.Label(natleft, text="8% sansa sa sara o detectie",
                 fg=TXT, bg=S1,
                 font=(FN, 10, "bold")).pack(anchor="w")
        tk.Label(natleft,
                 text="Ignorare intentionata ~1/12 detectii — apare mai uman.",
                 fg=TXT2, bg=S1,
                 font=(FN, 8)).pack(anchor="w", pady=(2, 0))

        self._tog = Toggle(natrow, cb=self._on_nat)
        self._tog.pack(side="right", padx=(12, 0))

        self._natlbl = tk.Label(nc, text="Status: Dezactivat",
                                fg=TXT3, bg=S1, font=(FN, 8))
        self._natlbl.pack(anchor="w", pady=(8, 0))

        # ══ ROW 4: Control ════════════════════════════════════════
        self._sec(P, "▶", "Control Macro")
        bc = self._card(P)
        bc.pack(fill="both", padx=12, pady=12)

        brow = tk.Frame(bc, bg=S1)
        brow.pack(fill="x")

        self._startbtn = mk_btn(brow, "▶   START MACRO",
            self._start, bg=ACC, abg=ACCDK)
        self._startbtn.pack(side="left", fill="x",
                            expand=True, ipady=10, padx=(0, 8))

        self._stopbtn = mk_btn(brow, "■   STOP",
            self._stop, bg=REDDK, fg=RED,
            abg="#6B2222", dfg=TXT3, state="disabled")
        self._stopbtn.pack(side="left", fill="x",
                           expand=True, ipady=10)

        # ══ ROW 5: Log ════════════════════════════════════════════
        self._sec(P, "📋", "Log Activitate")
        lc = self._card(P)
        lc.pack(fill="both", padx=12, pady=(0, 12))

        strow = tk.Frame(lc, bg=S1)
        strow.pack(fill="x", pady=(0, 8))
        self._stlbl = tk.Label(strow, text="State: IDLE",
                               fg=TXT3, bg=S1, font=(FN, 9, "bold"))
        self._stlbl.pack(side="left")

        lf = tk.Frame(lc, bg=S2,
                      highlightthickness=1,
                      highlightbackground=BORD)
        lf.pack(fill="both")
        self._log_w = tk.Text(lf,
            bg=S2, fg=TXT2, font=("Consolas", 8),
            relief="flat", state="disabled", wrap="word",
            bd=6, height=10, selectbackground=S3)
        self._log_w.pack(fill="both")

        for tag, col in [("ok", GRN), ("warn", YEL), ("err", RED),
                         ("dim", TXT3), ("hi", ACC2), ("pur", ACC2)]:
            self._log_w.tag_config(tag, foreground=col)

        gap(P, 10)

        # Re-bind scroll after all widgets are created
        self.root.after(100, lambda: self._bind_scroll(self._frm))

        self._log("GamerMacro Pro v4.0 ready.", "hi")
        self._log("Seteaza coordonatele si culoarea, apoi START.", "dim")
        self._log("Sfat: arunca undita INAINTE de a apasa START.", "dim")

    # ── Log ────────────────────────────────────────────────────
    def _log(self, msg, tag="dim"):
        ts = time.strftime("%H:%M:%S")
        self._log_w.configure(state="normal")
        self._log_w.insert("end", f"[{ts}]  {msg}\n", tag)
        self._log_w.see("end")
        self._log_w.configure(state="disabled")

    def _set_state(self, s):
        cols = {"IDLE": TXT3, "RESET": TXT3, "WATCH": ACC2, "RUNNING": GRN}
        self.root.after(0, self._stlbl.config,
            {"text": f"State: {s}", "fg": cols.get(s, TXT3)})

    # ── Capture ────────────────────────────────────────────────
    def _start_cap(self):
        self._capbtn.config(state="disabled")
        self._cdown(3)

    def _cdown(self, n):
        if n > 0:
            self._clbl_coord.config(
                text=f"Muta mouse-ul…  {n}s", fg=YEL)
            self.root.after(1000, self._cdown, n - 1)
        else:
            try:
                x, y = pyautogui.position()
                self.xf.var.set(str(x))
                self.yf.var.set(str(y))
                self._clbl_coord.config(
                    text=f"✓  X={x}  Y={y}", fg=GRN)
                self._log(f"Coordonate → X={x}  Y={y}", "ok")
            except Exception as e:
                self._clbl_coord.config(text=f"Eroare: {e}", fg=RED)
            finally:
                self._capbtn.config(state="normal")

    # ── Sample ─────────────────────────────────────────────────
    def _sample(self):
        try:
            x = int(self.xf.var.get())
            y = int(self.yf.var.get())
        except ValueError:
            self._log("Coordonate invalide.", "err"); return
        try:
            p = pyautogui.pixel(x, y)
            r, g, b = p[0], p[1], p[2]
            self.rf.var.set(str(r))
            self.gf.var.set(str(g))
            self.bf.var.set(str(b))
            self._sw.update(r, g, b)
            hx = f"#{r:02x}{g:02x}{b:02x}"
            self._clbl_col.config(
                text=f"✓  RGB({r},{g},{b})  {hx}", fg=GRN)
            self._log(f"Culoare → RGB({r},{g},{b})  {hx}", "ok")
        except Exception as e:
            self._clbl_col.config(text=f"Eroare: {e}", fg=RED)
            self._log(f"Eroare: {e}", "err")

    # ── Natural ────────────────────────────────────────────────
    def _on_nat(self, state):
        self._natural = state
        if state:
            self._natlbl.config(text="Status: Activat  —  8% skip", fg=ACC2)
            self._log("Mod Natural ACTIVAT.", "pur")
        else:
            self._natlbl.config(text="Status: Dezactivat", fg=TXT3)
            self._log("Mod Natural dezactivat.", "dim")

    # ── Parse ──────────────────────────────────────────────────
    def _parse(self):
        x     = int(self.xf.var.get())
        y     = int(self.yf.var.get())
        r     = int(self.rf.var.get())
        g     = int(self.gf.var.get())
        b     = int(self.bf.var.get())
        tol   = int(self.tolf.var.get())
        delay = float(self.dlf.var.get())
        cd    = float(self.cdf.var.get())
        sc    = pyautogui.size()
        if not (0 <= x < sc.width and 0 <= y < sc.height):
            raise ValueError(f"({x},{y}) in afara ecranului.")
        return x, y, r, g, b, tol, delay, cd

    # ── Loop ───────────────────────────────────────────────────
    def _watch(self, x, y, tr, tg, tb, tol, delay, cd, nat):
        self._set_state("RESET")
        state = "RESET"; skip = 0

        while self._running:
            try:
                p = pyautogui.pixel(x, y)
                cr, cg, cb = p[0], p[1], p[2]
                hit = (abs(cr-tr)<=tol and
                       abs(cg-tg)<=tol and
                       abs(cb-tb)<=tol)

                if state == "RESET":
                    if not hit:
                        state = "WATCH"; self._set_state("WATCH")

                elif state == "WATCH" and hit:
                    if nat and random.random() < 0.08:
                        skip += 1
                        self.root.after(0, self._log,
                            f"[skip #{skip}] Mod natural — ignorat.", "pur")
                        state = "RESET"; self._set_state("RESET")
                        time.sleep(self.POLL); continue

                    self._catches += 1
                    n = self._catches
                    self.root.after(0, self._log,
                        f"[#{n}] Bobber!  RGB({cr},{cg},{cb})  delay {delay}s…",
                        "warn")
                    self.root.after(0, self._clbl.config,
                        {"text": f"Catches: {n}"})

                    if delay > 0: time.sleep(delay)
                    if not self._running: break

                    pyautogui.rightClick()
                    time.sleep(0.5)
                    pyautogui.rightClick()

                    self.root.after(0, self._log,
                        f"[#{n}] Re-aruncat. Cooldown {cd}s…", "ok")
                    time.sleep(cd)
                    state = "RESET"; self._set_state("RESET")

            except pyautogui.FailSafeException:
                self.root.after(0, self._log,
                    "FAILSAFE! Mouse in colt.", "err"); break
            except Exception as e:
                self.root.after(0, self._log, f"Eroare: {e}", "err"); break

            time.sleep(self.POLL)

        self._running = False
        self.root.after(0, self._done)

    # ── Start / Stop ───────────────────────────────────────────
    def _start(self):
        if self._running: return
        try: args = self._parse()
        except ValueError as e:
            self._log(f"Input: {e}", "err"); return

        self._running = True
        self._catches = 0
        self._clbl.config(text="Catches: 0")
        self._ui(True)
        x,y,r,g,b,tol,delay,cd = args
        self._log(
            f"START ({x},{y}) RGB({r},{g},{b}) ±{tol} "
            f"delay={delay}s cd={cd}s nat={'ON' if self._natural else 'OFF'}",
            "hi")
        self._thread = threading.Thread(
            target=self._watch,
            args=(x,y,r,g,b,tol,delay,cd,self._natural),
            daemon=True)
        self._thread.start()

    def _stop(self):
        self._running = False
        self._log("Oprire…", "warn")

    def _done(self):
        self._ui(False)
        self._set_state("IDLE")
        self._log("Macro oprit.", "dim")

    def _ui(self, run):
        self._status.config(
            text="⬤  RUNNING" if run else "⬤  IDLE",
            fg=GRN if run else TXT3)
        self._startbtn.config(
            state="disabled" if run else "normal",
            bg=S3 if run else ACC)
        self._stopbtn.config(
            state="normal" if run else "disabled",
            bg=RED if run else REDDK,
            fg=TXT if run else RED)
        self._capbtn.config(state="disabled" if run else "normal")
        self._colbtn.config(state="disabled" if run else "normal")

    def on_close(self):
        self._running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
