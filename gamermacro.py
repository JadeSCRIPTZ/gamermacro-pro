"""
GamerMacro Pro — Fishing Edition v4.1
Fix: pynput mouse pentru right-click in Minecraft (mouse capturat)
Scurtat: doar functia de fishing
"""
import tkinter as tk
import threading, time, random, sys, math

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0
except ImportError:
    print("Run: pip install pyautogui pillow"); sys.exit(1)

try:
    from pynput.mouse import Button, Controller as MouseController
    _mouse = MouseController()
    def right_click():
        _mouse.click(Button.right, 1)
except ImportError:
    print("Run: pip install pynput"); sys.exit(1)

# ── Palette ────────────────────────────────────────────────────
BG    = "#1C1917"
S1    = "#292524"
S2    = "#3C3835"
S3    = "#44403C"
BORD  = "#57534E"
BORD2 = "#78716C"
ORG   = "#D97706"
ORG2  = "#F59E0B"
ORG3  = "#78350F"
GRN   = "#34D399"
GRNDK = "#064E3B"
RED   = "#F87171"
REDDK = "#7F1D1D"
YEL   = "#FBBF24"
PURP  = "#A78BFA"
TEXT  = "#FAFAF9"
TEXT2 = "#A8A29E"
TEXT3 = "#57534E"
FN    = "Segoe UI"
POLL  = 0.05

def mk_btn(parent, text, cmd, bg=ORG, fg="#1C1917", abg=ORG2,
           state="normal", **kw):
    return tk.Button(parent, text=text, command=cmd,
                     bg=bg, fg=fg,
                     activebackground=abg, activeforeground="#1C1917",
                     disabledforeground=TEXT3,
                     relief="flat", bd=0, cursor="hand2",
                     font=(FN, 10, "bold"),
                     state=state, **kw)

class Field(tk.Frame):
    def __init__(self, master, label, val="0", w=7, **kw):
        bg = master["bg"]
        super().__init__(master, bg=bg, **kw)
        tk.Label(self, text=label, fg=TEXT2, bg=bg,
                 font=(FN, 8)).pack(anchor="w", pady=(0,2))
        self.var = tk.StringVar(value=str(val))
        e = tk.Entry(self, textvariable=self.var, width=w,
                     bg=S2, fg=TEXT, insertbackground=ORG2,
                     relief="flat", bd=0,
                     font=("Consolas", 10), justify="center",
                     highlightthickness=1,
                     highlightbackground=BORD,
                     highlightcolor=ORG)
        e.pack(ipady=6, ipadx=4)
        e.bind("<FocusIn>",  lambda _: e.config(highlightbackground=ORG))
        e.bind("<FocusOut>", lambda _: e.config(highlightbackground=BORD))

class Swatch(tk.Frame):
    def __init__(self, master, sz=36, **kw):
        super().__init__(master, width=sz, height=sz,
                         bg=S2, highlightthickness=1,
                         highlightbackground=BORD, **kw)
        self.pack_propagate(False)
    def set_color(self, r, g, b):
        self.config(bg=f"#{r:02x}{g:02x}{b:02x}",
                    highlightbackground=f"#{r:02x}{g:02x}{b:02x}")

class Toggle(tk.Frame):
    def __init__(self, master, cb=None, **kw):
        super().__init__(master, bg=S2,
                         highlightthickness=1,
                         highlightbackground=BORD, **kw)
        self._on = False; self._cb = cb
        self._boff = tk.Button(self, text=" OFF ",
            bg=S3, fg=TEXT2, activebackground=BORD,
            activeforeground=TEXT, relief="flat", bd=0,
            font=(FN, 8, "bold"), cursor="hand2",
            command=self._do_off)
        self._boff.pack(side="left", padx=2, pady=2)
        tk.Frame(self, bg=BORD, width=1).pack(side="left", fill="y")
        self._bon = tk.Button(self, text="  ON  ",
            bg=S2, fg=TEXT3, activebackground=ORG3,
            activeforeground=ORG2, relief="flat", bd=0,
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
            self._bon.config(bg=ORG, fg="#1C1917")
            self._boff.config(bg=S2, fg=TEXT3)
            self.config(highlightbackground=ORG)
        else:
            self._boff.config(bg=S3, fg=TEXT2)
            self._bon.config(bg=S2, fg=TEXT3)
            self.config(highlightbackground=BORD)

    def get(self): return self._on


class App:
    POLL = 0.05

    def __init__(self, root):
        self.root     = root
        self._running = False
        self._natural = False
        self._catches = 0
        self._thread  = None
        self._setup_window()
        self._build()

    def _setup_window(self):
        self.root.title("GamerMacro Pro — Fishing")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        W, H = 480, 720
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    def _build(self):
        # Top bar
        tk.Frame(self.root, bg=ORG, height=3).pack(fill="x")

        # Header
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(14,10))
        hl = tk.Frame(hdr, bg=BG)
        hl.pack(side="left")
        logo = tk.Frame(hl, bg=BG)
        logo.pack(anchor="w")
        tk.Label(logo, text="●", fg=ORG, bg=BG,
                 font=(FN,15)).pack(side="left", padx=(0,8))
        tk.Label(logo, text="GamerMacro Pro",
                 fg=TEXT, bg=BG,
                 font=(FN,17,"bold")).pack(side="left")
        tk.Label(hl, text="Fishing Edition  ·  Pixel Watcher",
                 fg=TEXT3, bg=BG,
                 font=(FN,9)).pack(anchor="w", pady=(2,0))

        hr = tk.Frame(hdr, bg=BG)
        hr.pack(side="right", anchor="ne")
        self._status_lbl = tk.Label(hr,
            text="  IDLE  ", fg=TEXT3, bg=S2,
            font=(FN,9,"bold"), padx=10, pady=4)
        self._status_lbl.pack(anchor="e")
        self._catch_lbl = tk.Label(hr,
            text="Catches: 0", fg=YEL, bg=BG,
            font=(FN,8))
        self._catch_lbl.pack(anchor="e", pady=(4,0))

        tk.Frame(self.root, bg=BORD, height=1).pack(fill="x")

        # Scroll canvas
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)
        self._cv = tk.Canvas(outer, bg=BG, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical",
                          command=self._cv.yview,
                          bg=S2, troughcolor=BG, activebackground=ORG)
        sb.pack(side="right", fill="y")
        self._cv.pack(side="left", fill="both", expand=True)
        self._cv.configure(yscrollcommand=sb.set)
        self._frm = tk.Frame(self._cv, bg=BG)
        self._wid = self._cv.create_window((0,0), window=self._frm, anchor="nw")
        self._frm.bind("<Configure>",
            lambda e: self._cv.configure(scrollregion=self._cv.bbox("all")))
        self._cv.bind("<Configure>",
            lambda e: self._cv.itemconfig(self._wid, width=e.width))
        self.root.bind_all("<MouseWheel>",
            lambda e: self._cv.yview_scroll(int(-1*(e.delta/120)),"units"))

        tk.Frame(self.root, bg=BORD, height=1).pack(fill="x")
        tk.Label(self.root,
            text="⚠  Failsafe: muta mouse-ul in coltul stanga-sus",
            fg=TEXT3, bg=BG, font=(FN,7)).pack(pady=5)

        self._build_content(self._frm)
        self.root.after(100, lambda: self._bind_scroll(self._frm))

    def _bind_scroll(self, w):
        w.bind("<MouseWheel>",
               lambda e: self._cv.yview_scroll(int(-1*(e.delta/120)),"units"))
        for ch in w.winfo_children():
            self._bind_scroll(ch)

    def _card(self, parent):
        f = tk.Frame(parent, bg=S1,
                     highlightthickness=1,
                     highlightbackground=BORD)
        f.pack(fill="x", padx=16, pady=(0,12))
        return tk.Frame(f, bg=S1)

    def _sec(self, parent, icon, title):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", padx=16, pady=(12,5))
        tk.Label(f, text=icon, fg=ORG2, bg=BG,
                 font=(FN,10)).pack(side="left", padx=(0,6))
        tk.Label(f, text=title, fg=TEXT, bg=BG,
                 font=(FN,10,"bold")).pack(side="left")
        tk.Frame(f, bg=BORD2, height=1).pack(
            side="left", fill="x", expand=True, padx=(10,0))

    def _build_content(self, P):
        def gap(n=8):
            tk.Frame(P, bg=BG, height=n).pack(fill="x")

        gap(12)

        # ── 1. Coordonate ─────────────────────────────────────
        self._sec(P, "🎯", "Coordonate Pixel")
        c1 = self._card(P); c1.pack(fill="both", padx=14, pady=12)

        xy = tk.Frame(c1, bg=S1); xy.pack(fill="x", pady=(0,8))
        self.xf = Field(xy, "X  (pixeli)", "0", 8)
        self.xf.pack(side="left", padx=(0,14))
        self.yf = Field(xy, "Y  (pixeli)", "0", 8)
        self.yf.pack(side="left")

        self._coord_lbl = tk.Label(c1,
            text="Nicio coordonata capturata.",
            fg=TEXT3, bg=S1, font=(FN,8))
        self._coord_lbl.pack(anchor="w", pady=(0,8))

        self._cap_btn = mk_btn(c1,
            "🖱   Captureaza Pozitie  ( 3s countdown )",
            self._start_cap, bg=ORG, abg=ORG2)
        self._cap_btn.pack(fill="x", ipady=8)

        # ── 2. Culoare ────────────────────────────────────────
        self._sec(P, "🎨", "Culoare Tinta")
        c2 = self._card(P); c2.pack(fill="both", padx=14, pady=12)

        rgb = tk.Frame(c2, bg=S1); rgb.pack(fill="x", pady=(0,8))
        self.rf = Field(rgb, "R", "255", 5); self.rf.pack(side="left", padx=(0,8))
        self.gf = Field(rgb, "G", "0",   5); self.gf.pack(side="left", padx=(0,8))
        self.bf = Field(rgb, "B", "0",   5); self.bf.pack(side="left", padx=(0,12))
        self._sw = Swatch(rgb, 38); self._sw.pack(side="left")

        self._color_lbl = tk.Label(c2,
            text="Nicio culoare capturata.",
            fg=TEXT3, bg=S1, font=(FN,8))
        self._color_lbl.pack(anchor="w", pady=(0,8))

        self._sample_btn = mk_btn(c2,
            "🎨   Sample Culoare la Pixel",
            self._sample, bg=ORG, abg=ORG2)
        self._sample_btn.pack(fill="x", ipady=8)

        # ── 3. Setari ─────────────────────────────────────────
        self._sec(P, "⚙️", "Setari Detectie")
        c3 = self._card(P); c3.pack(fill="both", padx=14, pady=12)

        r1 = tk.Frame(c3, bg=S1); r1.pack(fill="x", pady=(0,10))
        self.tolf  = Field(r1, "Toleranta  ±",       "15",  7)
        self.tolf.pack(side="left", padx=(0,20))
        self.dlf   = Field(r1, "Delay reactie  (s)", "0.1", 7)
        self.dlf.pack(side="left")

        self.cdf = Field(c3, "Cooldown dupa aruncare  (s)", "3.0", 7)
        self.cdf.pack(anchor="w")

        # ── 4. Mod Natural ────────────────────────────────────
        self._sec(P, "🎲", "Mod Natural")
        c4 = self._card(P); c4.pack(fill="both", padx=14, pady=14)

        nat = tk.Frame(c4, bg=S1); nat.pack(fill="x")
        ntxt = tk.Frame(nat, bg=S1); ntxt.pack(side="left", fill="x", expand=True)
        tk.Label(ntxt, text="8% sansa sa sara o detectie",
                 fg=TEXT, bg=S1,
                 font=(FN,10,"bold")).pack(anchor="w")
        tk.Label(ntxt,
                 text="Ignora intentionat ~1 din 12 detectii — apare mai uman.",
                 fg=TEXT2, bg=S1, font=(FN,8),
                 justify="left").pack(anchor="w", pady=(3,0))
        self._tog = Toggle(nat, cb=self._on_nat)
        self._tog.pack(side="right", padx=(14,0))
        self._nat_lbl = tk.Label(c4, text="Status: Dezactivat",
                                 fg=TEXT3, bg=S1, font=(FN,8))
        self._nat_lbl.pack(anchor="w", pady=(10,0))

        # ── 5. Control ────────────────────────────────────────
        self._sec(P, "▶", "Control Macro")
        c5 = self._card(P); c5.pack(fill="both", padx=14, pady=14)

        br = tk.Frame(c5, bg=S1); br.pack(fill="x")
        self._startbtn = mk_btn(br, "▶   START MACRO",
            self._start, bg=ORG, abg=ORG2)
        self._startbtn.pack(side="left", fill="x",
                            expand=True, ipady=12, padx=(0,8))
        self._stopbtn = mk_btn(br, "■   STOP",
            self._stop, bg=REDDK, fg=RED,
            abg="#5C1111", state="disabled")
        self._stopbtn.pack(side="left", fill="x",
                           expand=True, ipady=12)

        # ── Log ───────────────────────────────────────────────
        self._sec(P, "📋", "Log Activitate")
        c6 = self._card(P); c6.pack(fill="both", padx=14, pady=(0,14))

        sr = tk.Frame(c6, bg=S1); sr.pack(fill="x", pady=(0,8))
        self._st_lbl = tk.Label(sr, text="State: IDLE",
                                fg=TEXT3, bg=S1, font=(FN,9,"bold"))
        self._st_lbl.pack(side="left")

        self._log_w = tk.Text(c6,
            bg=S2, fg=TEXT2, font=("Consolas",8),
            relief="flat", state="disabled",
            wrap="word", bd=6, height=10,
            selectbackground=S3)
        self._log_w.pack(fill="both")

        for tag, col in [("ok",GRN),("warn",YEL),("err",RED),
                         ("dim",TEXT3),("hi",ORG2),("pur",PURP)]:
            self._log_w.tag_config(tag, foreground=col)

        gap(14)

        self._log("GamerMacro Pro v4.1 ready.", "hi")
        self._log("Fix: right-click prin pynput — functioneaza in Minecraft!", "ok")
        self._log("Seteaza coordonatele si culoarea, apoi apasa START.", "dim")
        self._log("Sfat: arunca undita INAINTE de a apasa START.", "dim")

    # ── Capture ───────────────────────────────────────────────
    def _start_cap(self):
        self._cap_btn.config(state="disabled")
        self._cdown(3)

    def _cdown(self, n):
        if n > 0:
            self._coord_lbl.config(
                text=f"Muta mouse-ul pe pixel…  {n}s", fg=YEL)
            self.root.after(1000, self._cdown, n-1)
        else:
            try:
                x, y = pyautogui.position()
                self.xf.var.set(str(x))
                self.yf.var.set(str(y))
                self._coord_lbl.config(
                    text=f"✓  X={x}   Y={y}", fg=GRN)
                self._log(f"Coordonate capturate → X={x}  Y={y}", "ok")
            except Exception as e:
                self._coord_lbl.config(text=f"Eroare: {e}", fg=RED)
            finally:
                self._cap_btn.config(state="normal")

    # ── Sample ────────────────────────────────────────────────
    def _sample(self):
        try:
            x = int(self.xf.var.get()); y = int(self.yf.var.get())
            p = pyautogui.pixel(x, y)
            r, g, b = p[0], p[1], p[2]
            self.rf.var.set(str(r)); self.gf.var.set(str(g))
            self.bf.var.set(str(b))
            self._sw.set_color(r, g, b)
            hx = f"#{r:02x}{g:02x}{b:02x}"
            self._color_lbl.config(
                text=f"✓  RGB({r},{g},{b})   {hx}", fg=GRN)
            self._log(f"Culoare → RGB({r},{g},{b})  {hx}", "ok")
        except Exception as e:
            self._color_lbl.config(text=f"Eroare: {e}", fg=RED)
            self._log(f"Eroare: {e}", "err")

    # ── Natural ───────────────────────────────────────────────
    def _on_nat(self, state):
        self._natural = state
        if state:
            self._nat_lbl.config(
                text="Status: Activat  —  8% skip per detectie", fg=ORG2)
            self._log("Mod Natural ACTIVAT.", "pur")
        else:
            self._nat_lbl.config(text="Status: Dezactivat", fg=TEXT3)
            self._log("Mod Natural dezactivat.", "dim")

    # ── Parse ─────────────────────────────────────────────────
    def _parse(self):
        x   = int(self.xf.var.get())
        y   = int(self.yf.var.get())
        r   = int(self.rf.var.get())
        g   = int(self.gf.var.get())
        b   = int(self.bf.var.get())
        tol = int(self.tolf.var.get())
        dl  = float(self.dlf.var.get())
        cd  = float(self.cdf.var.get())
        sc  = pyautogui.size()
        if not (0 <= x < sc.width and 0 <= y < sc.height):
            raise ValueError(f"Coordonate ({x},{y}) in afara ecranului.")
        return x, y, r, g, b, tol, dl, cd

    # ── Macro loop ────────────────────────────────────────────
    def _watch(self, x, y, tr, tg, tb, tol, delay, cd, nat):
        self._upst("RESET")
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
                        state = "WATCH"; self._upst("WATCH")

                elif state == "WATCH" and hit:
                    if nat and random.random() < 0.08:
                        skip += 1
                        self.root.after(0, self._log,
                            f"[skip #{skip}] Mod natural — ignorat.", "pur")
                        state = "RESET"; self._upst("RESET")
                        time.sleep(self.POLL); continue

                    self._catches += 1
                    n = self._catches
                    self.root.after(0, self._log,
                        f"[#{n}] Bobber!  RGB({cr},{cg},{cb})  delay {delay}s…",
                        "warn")
                    self.root.after(0, self._catch_lbl.config,
                        {"text": f"Catches: {n}"})

                    if delay > 0: time.sleep(delay)
                    if not self._running: break

                    # ── RIGHT CLICK via pynput ────────────────
                    # Functioneaza in Minecraft (mouse capturat)
                    right_click()
                    time.sleep(0.5)
                    right_click()
                    # ─────────────────────────────────────────

                    self.root.after(0, self._log,
                        f"[#{n}] Re-aruncat! Cooldown {cd}s…", "ok")
                    time.sleep(cd)
                    state = "RESET"; self._upst("RESET")

            except pyautogui.FailSafeException:
                self.root.after(0, self._log,
                    "FAILSAFE! Mouse in colt.", "err"); break
            except Exception as e:
                self.root.after(0, self._log, f"Eroare: {e}", "err"); break

            time.sleep(self.POLL)

        self._running = False
        self.root.after(0, self._stopped)

    def _upst(self, s):
        cols = {"IDLE":TEXT3,"RESET":TEXT3,"WATCH":ORG2}
        self.root.after(0, self._st_lbl.config,
            {"text":f"State: {s}","fg":cols.get(s,TEXT3)})

    # ── Start / Stop ──────────────────────────────────────────
    def _start(self):
        if self._running: return
        try: args = self._parse()
        except ValueError as e:
            self._log(f"Input invalid: {e}", "err"); return

        self._running = True
        self._catches = 0
        self._catch_lbl.config(text="Catches: 0")
        self._ui(True)

        x,y,r,g,b,tol,delay,cd = args
        self._log(
            f"START  ({x},{y})  RGB({r},{g},{b})  ±{tol}  "
            f"delay={delay}s  cd={cd}s  "
            f"nat={'ON' if self._natural else 'OFF'}", "hi")

        self._thread = threading.Thread(
            target=self._watch,
            args=(x,y,r,g,b,tol,delay,cd,self._natural),
            daemon=True)
        self._thread.start()

    def _stop(self):
        self._running = False
        self._log("Oprire…", "warn")

    def _stopped(self):
        self._ui(False)
        self._upst("IDLE")
        self._log("Macro oprit.", "dim")

    def _ui(self, run):
        self._status_lbl.config(
            text="  RUNNING  " if run else "  IDLE  ",
            fg="#1C1917" if run else TEXT3,
            bg=ORG if run else S2)
        self._startbtn.config(
            state="disabled" if run else "normal",
            bg=S3 if run else ORG)
        self._stopbtn.config(
            state="normal" if run else "disabled",
            bg=RED if run else REDDK,
            fg="#1C1917" if run else RED)
        self._cap_btn.config(state="disabled" if run else "normal")
        self._sample_btn.config(state="disabled" if run else "normal")

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
