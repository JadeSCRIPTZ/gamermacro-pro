"""
GamerMacro Pro — Fishing Edition v6.0
Layout: Sidebar stanga + Continut dreapta (ca Claude)
Tema: Dark grey + albastru-mov
Redimensionabil
"""
import tkinter as tk
from tkinter import font as tkfont
import threading, time, random, sys

import pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

from pynput.mouse import Button, Controller as MC
_mouse = MC()

def right_click():
    _mouse.click(Button.right, 1)

# ── Palette: dark grey + blue-violet ──────────────────────────
BG      = "#0F1117"   # fundal principal
SIDEBAR = "#141820"   # sidebar stanga
PANEL   = "#1A1F2E"   # card/panel
PANEL2  = "#1E2438"   # panel mai deschis
INPUT   = "#252D42"   # input background
BORD    = "#2D3554"   # border
BORD2   = "#3D4870"   # border accent
BLUE    = "#4F8EF7"   # albastru principal
BLUE2   = "#7AB3FF"   # albastru deschis
BLUED   = "#1A3A7A"   # albastru inchis
PURP    = "#7C5CFC"   # violet
PURP2   = "#A78BFA"   # violet deschis
PURPD   = "#2D1B69"   # violet inchis
GRN     = "#34D399"   # verde
GRNDK   = "#064E3B"   # verde inchis
RED     = "#F87171"   # rosu
REDDK   = "#7F1D1D"   # rosu inchis
YEL     = "#FBBF24"   # galben
TXT     = "#E8EEFF"   # text principal
TXT2    = "#8B9BB4"   # text secundar
TXT3    = "#454E6A"   # text muted
FN      = "Segoe UI"
POLL    = 0.05


# ─────────────────────────────────────────────────────────────
#  WIDGETS
# ─────────────────────────────────────────────────────────────
class SidebarBtn(tk.Frame):
    """Buton sidebar cu indicator activ."""
    def __init__(self, master, icon, label, cmd, **kw):
        super().__init__(master, bg=SIDEBAR, cursor="hand2", **kw)
        self._cmd     = cmd
        self._active  = False
        self._icon    = icon
        self._label   = label

        self._indicator = tk.Frame(self, bg=SIDEBAR, width=3)
        self._indicator.pack(side="left", fill="y")

        self._inner = tk.Frame(self, bg=SIDEBAR)
        self._inner.pack(side="left", fill="both",
                         expand=True, padx=(8, 12), pady=8)

        self._ic_lbl = tk.Label(self._inner, text=icon,
                                fg=TXT3, bg=SIDEBAR,
                                font=(FN, 14))
        self._ic_lbl.pack(anchor="w")

        self._tx_lbl = tk.Label(self._inner, text=label,
                                fg=TXT3, bg=SIDEBAR,
                                font=(FN, 8))
        self._tx_lbl.pack(anchor="w")

        self.bind("<Button-1>", self._click)
        self._inner.bind("<Button-1>", self._click)
        self._ic_lbl.bind("<Button-1>", self._click)
        self._tx_lbl.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._hover)
        self._inner.bind("<Enter>", self._hover)
        self.bind("<Leave>", self._leave)
        self._inner.bind("<Leave>", self._leave)

    def _click(self, _=None):
        self._cmd()

    def _hover(self, _=None):
        if not self._active:
            self._inner.config(bg=PANEL)
            self._ic_lbl.config(bg=PANEL)
            self._tx_lbl.config(bg=PANEL)

    def _leave(self, _=None):
        if not self._active:
            self._inner.config(bg=SIDEBAR)
            self._ic_lbl.config(bg=SIDEBAR)
            self._tx_lbl.config(bg=SIDEBAR)

    def set_active(self, active):
        self._active = active
        if active:
            self._indicator.config(bg=PURP)
            self._inner.config(bg=PANEL2)
            self._ic_lbl.config(fg=PURP2, bg=PANEL2)
            self._tx_lbl.config(fg=TXT, bg=PANEL2)
        else:
            self._indicator.config(bg=SIDEBAR)
            self._inner.config(bg=SIDEBAR)
            self._ic_lbl.config(fg=TXT3, bg=SIDEBAR)
            self._tx_lbl.config(fg=TXT3, bg=SIDEBAR)


class FlatBtn(tk.Button):
    """Buton flat stilizat."""
    def __init__(self, master, text, cmd,
                 bg=PURP, fg=TXT, abg=None,
                 state="normal", size=9, **kw):
        super().__init__(master, text=text, command=cmd,
                         bg=bg, fg=fg,
                         activebackground=abg or PURPD,
                         activeforeground=TXT,
                         disabledforeground=TXT3,
                         relief="flat", bd=0,
                         cursor="hand2",
                         font=(FN, size, "bold"),
                         state=state, **kw)

    def enable(self):  self.config(state="normal")
    def disable(self): self.config(state="disabled")


class Inp(tk.Frame):
    """Label + Entry stilizat."""
    def __init__(self, master, label, val="0", w=8, **kw):
        super().__init__(master, bg=master["bg"], **kw)
        tk.Label(self, text=label, fg=TXT2,
                 bg=self["bg"],
                 font=(FN, 8)).pack(anchor="w", pady=(0, 3))
        self.var = tk.StringVar(value=str(val))
        e = tk.Entry(self, textvariable=self.var,
                     width=w, bg=INPUT, fg=TXT,
                     insertbackground=BLUE2,
                     relief="flat", bd=0,
                     font=("Consolas", 10),
                     justify="center",
                     highlightthickness=1,
                     highlightbackground=BORD,
                     highlightcolor=PURP)
        e.pack(ipady=7, ipadx=4)
        e.bind("<FocusIn>",
               lambda _: e.config(highlightbackground=PURP))
        e.bind("<FocusOut>",
               lambda _: e.config(highlightbackground=BORD))


class Swatch(tk.Frame):
    def __init__(self, master, sz=32, **kw):
        super().__init__(master, width=sz, height=sz,
                         bg=INPUT, highlightthickness=1,
                         highlightbackground=BORD, **kw)
        self.pack_propagate(False)
    def set(self, r, g, b):
        c = f"#{r:02x}{g:02x}{b:02x}"
        self.config(bg=c, highlightbackground=c)


class StatBox(tk.Frame):
    """Card cu valoare + label."""
    def __init__(self, master, title, color=BLUE2, **kw):
        super().__init__(master, bg=INPUT,
                         highlightthickness=1,
                         highlightbackground=BORD, **kw)
        tk.Label(self, text=title, fg=TXT3,
                 bg=INPUT, font=(FN, 7, "bold")).pack(pady=(8, 2))
        self._val = tk.Label(self, text="—", fg=color,
                             bg=INPUT,
                             font=(FN, 18, "bold"))
        self._val.pack()
        tk.Label(self, text="catches", fg=TXT3,
                 bg=INPUT, font=(FN, 7)).pack(pady=(0, 8))

    def set(self, v): self._val.config(text=str(v))


def divider(p, bg=None, pady=8):
    tk.Frame(p, bg=bg or BORD, height=1).pack(
        fill="x", pady=pady)

def section(p, text, bg=None):
    bg = bg or p["bg"]
    tk.Label(p, text=text, fg=TXT2, bg=bg,
             font=(FN, 8, "bold")).pack(
        anchor="w", pady=(12, 4))


# ─────────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────────
class App:
    TABS = [
        ("🎣", "Macro"),
        ("⚙️", "Setari"),
        ("📊", "Statistici"),
        ("📋", "Log"),
    ]
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
        self._ts_list  = []
        self._cur_tab  = None
        self._tab_btns = {}
        self._tab_frames = {}

        self._setup()
        self._build()
        self.root.after(500, self._show_tab, "Macro")
        self.root.after(1000, self._tick_stats)

    def _setup(self):
        self.root.title("GamerMacro Pro")
        self.root.configure(bg=BG)
        self.root.minsize(680, 480)
        self.root.attributes("-topmost", True)
        W, H = 760, 560
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    def _build(self):
        # ── Layout principal: sidebar + content ───────────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True)

        # ── SIDEBAR ───────────────────────────────────────────
        self._sidebar = tk.Frame(main, bg=SIDEBAR, width=90)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(self._sidebar, bg=SIDEBAR)
        logo.pack(fill="x", pady=(16, 8))
        tk.Label(logo, text="●", fg=PURP, bg=SIDEBAR,
                 font=(FN, 20)).pack()
        tk.Label(logo, text="GM", fg=TXT, bg=SIDEBAR,
                 font=(FN, 9, "bold")).pack()

        tk.Frame(self._sidebar, bg=BORD, height=1).pack(
            fill="x", padx=10, pady=(4, 12))

        # Tab butoane in sidebar
        for icon, label in self.TABS:
            b = SidebarBtn(self._sidebar, icon, label,
                           cmd=lambda l=label: self._show_tab(l))
            b.pack(fill="x")
            self._tab_btns[label] = b

        # Status jos in sidebar
        tk.Frame(self._sidebar, bg=BORD, height=1).pack(
            fill="x", padx=10, pady=(12, 8), side="bottom")
        self._sidebar_status = tk.Label(
            self._sidebar, text="IDLE",
            fg=TXT3, bg=SIDEBAR,
            font=(FN, 7, "bold"))
        self._sidebar_status.pack(side="bottom", pady=(0, 6))
        self._sidebar_dot = tk.Label(
            self._sidebar, text="●",
            fg=TXT3, bg=SIDEBAR,
            font=(FN, 16))
        self._sidebar_dot.pack(side="bottom")

        # ── CONTENT AREA ──────────────────────────────────────
        content_wrap = tk.Frame(main, bg=BG)
        content_wrap.pack(side="left", fill="both", expand=True)

        # Header
        hdr = tk.Frame(content_wrap, bg=PANEL, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        self._hdr_title = tk.Label(hdr, text="Macro",
                                   fg=TXT, bg=PANEL,
                                   font=(FN, 13, "bold"))
        self._hdr_title.pack(side="left", padx=20, pady=14)

        self._hdr_catch = tk.Label(hdr, text="Catches: 0",
                                   fg=YEL, bg=PANEL,
                                   font=(FN, 9))
        self._hdr_catch.pack(side="right", padx=20)

        self._hdr_recal = tk.Label(hdr, text="",
                                   fg=PURP2, bg=PANEL,
                                   font=(FN, 9))
        self._hdr_recal.pack(side="right", padx=(0, 10))

        tk.Frame(content_wrap, bg=BORD, height=1).pack(fill="x")

        # Container pentru toate tab-urile
        self._content = tk.Frame(content_wrap, bg=BG)
        self._content.pack(fill="both", expand=True)

        # Construieste toate tab-urile
        self._build_macro()
        self._build_settings()
        self._build_stats()
        self._build_log()

    # ── Navigare tab-uri ──────────────────────────────────────
    def _show_tab(self, name):
        # Ascunde toate
        for f in self._tab_frames.values():
            f.pack_forget()
        # Dezactiveaza toate butoanele
        for b in self._tab_btns.values():
            b.set_active(False)
        # Afiseaza tab-ul selectat
        if name in self._tab_frames:
            self._tab_frames[name].pack(
                fill="both", expand=True)
        if name in self._tab_btns:
            self._tab_btns[name].set_active(True)
        self._hdr_title.config(text=name)
        self._cur_tab = name

    # ─────────────────────────────────────────────────────────
    #  TAB: MACRO
    # ─────────────────────────────────────────────────────────
    def _build_macro(self):
        f = tk.Frame(self._content, bg=BG)
        self._tab_frames["Macro"] = f

        # Scroll
        cv = tk.Canvas(f, bg=BG, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(f, orient="vertical",
                          command=cv.yview,
                          bg=PANEL, troughcolor=BG,
                          activebackground=PURP)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True)
        cv.configure(yscrollcommand=sb.set)
        frm = tk.Frame(cv, bg=BG)
        wid = cv.create_window((0, 0), window=frm, anchor="nw")
        frm.bind("<Configure>",
                 lambda e: cv.configure(
                     scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",
                lambda e: cv.itemconfig(wid, width=e.width))
        cv.bind("<MouseWheel>",
                lambda e: cv.yview_scroll(
                    int(-1*(e.delta/120)), "units"))

        P = frm
        bg = BG

        def gap(n=10): tk.Frame(P, bg=bg, height=n).pack(fill="x")
        def card():
            o = tk.Frame(P, bg=PANEL,
                         highlightthickness=1,
                         highlightbackground=BORD)
            o.pack(fill="x", padx=16, pady=(0, 10))
            return tk.Frame(o, bg=PANEL)

        gap(14)

        # ── Coordonate + Culoare (2 coloane) ──────────────────
        row_top = tk.Frame(P, bg=bg)
        row_top.pack(fill="x", padx=16, pady=(0, 10))

        # Card coordonate
        cc = tk.Frame(row_top, bg=PANEL,
                      highlightthickness=1,
                      highlightbackground=BORD)
        cc.pack(side="left", fill="both",
                expand=True, padx=(0, 8))
        ci = tk.Frame(cc, bg=PANEL)
        ci.pack(fill="both", padx=12, pady=12)
        section(ci, "COORDONATE PIXEL", PANEL)
        xy = tk.Frame(ci, bg=PANEL); xy.pack(fill="x", pady=(0,8))
        self.xf = Inp(xy, "X", "0", 7); self.xf.pack(side="left", padx=(0,8))
        self.yf = Inp(xy, "Y", "0", 7); self.yf.pack(side="left")
        self._clbl_c = tk.Label(ci, text="Nicio coordonata.",
                                fg=TXT3, bg=PANEL, font=(FN,7))
        self._clbl_c.pack(anchor="w", pady=(0,6))
        self._capbtn = FlatBtn(ci, "🖱  Get Position (3s)",
                               self._cap, bg=PURP, abg=PURPD)
        self._capbtn.pack(fill="x", ipady=7)

        # Card culoare
        col = tk.Frame(row_top, bg=PANEL,
                       highlightthickness=1,
                       highlightbackground=BORD)
        col.pack(side="left", fill="both", expand=True)
        coli = tk.Frame(col, bg=PANEL)
        coli.pack(fill="both", padx=12, pady=12)
        section(coli, "CULOARE TINTA", PANEL)
        rgb = tk.Frame(coli, bg=PANEL); rgb.pack(fill="x", pady=(0,6))
        self.rf = Inp(rgb, "R", "255", 4); self.rf.pack(side="left", padx=(0,4))
        self.gf = Inp(rgb, "G", "0",   4); self.gf.pack(side="left", padx=(0,4))
        self.bf = Inp(rgb, "B", "0",   4); self.bf.pack(side="left", padx=(0,8))
        self._sw = Swatch(rgb, 30); self._sw.pack(side="left")
        self._clbl_col = tk.Label(coli, text="Nicio culoare.",
                                  fg=TXT3, bg=PANEL, font=(FN,7))
        self._clbl_col.pack(anchor="w", pady=(0,6))
        self._samplebtn = FlatBtn(coli, "🎨  Sample Colour",
                                  self._sample, bg=PURP, abg=PURPD)
        self._samplebtn.pack(fill="x", ipady=7)

        # ── Control butoane mari ───────────────────────────────
        ctrl = tk.Frame(P, bg=bg)
        ctrl.pack(fill="x", padx=16, pady=(0, 10))

        self._startbtn = FlatBtn(ctrl, "▶   START MACRO",
                                 self._start, bg=PURP, abg=PURPD,
                                 size=11)
        self._startbtn.pack(side="left", fill="x",
                            expand=True, ipady=14, padx=(0, 8))

        self._stopbtn = FlatBtn(ctrl, "■   STOP",
                                self._stop, bg=REDDK, fg=RED,
                                abg="#5C1111", state="disabled",
                                size=11)
        self._stopbtn.pack(side="left", fill="x",
                           expand=True, ipady=14)

        # ── State display ─────────────────────────────────────
        st_card = card()
        st_card.pack(fill="x", padx=12, pady=8)
        sr = tk.Frame(st_card, bg=PANEL); sr.pack(fill="x")
        tk.Label(sr, text="State:", fg=TXT2, bg=PANEL,
                 font=(FN,9)).pack(side="left")
        self._stlbl = tk.Label(sr, text="IDLE",
                               fg=TXT3, bg=PANEL,
                               font=(FN,9,"bold"))
        self._stlbl.pack(side="left", padx=6)
        self._rlbl = tk.Label(sr, text="",
                              fg=PURP2, bg=PANEL,
                              font=(FN,9,"bold"))
        self._rlbl.pack(side="right")

        gap(12)

    # ─────────────────────────────────────────────────────────
    #  TAB: SETARI
    # ─────────────────────────────────────────────────────────
    def _build_settings(self):
        f = tk.Frame(self._content, bg=BG)
        self._tab_frames["Setari"] = f

        cv = tk.Canvas(f, bg=BG, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(f, orient="vertical", command=cv.yview,
                          bg=PANEL, troughcolor=BG, activebackground=PURP)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True)
        cv.configure(yscrollcommand=sb.set)
        frm = tk.Frame(cv, bg=BG)
        wid = cv.create_window((0,0), window=frm, anchor="nw")
        frm.bind("<Configure>",
                 lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",
                lambda e: cv.itemconfig(wid, width=e.width))
        cv.bind("<MouseWheel>",
                lambda e: cv.yview_scroll(int(-1*(e.delta/120)),"units"))

        P = frm
        def gap(n=10): tk.Frame(P, bg=BG, height=n).pack(fill="x")
        def card():
            o = tk.Frame(P, bg=PANEL, highlightthickness=1,
                         highlightbackground=BORD)
            o.pack(fill="x", padx=16, pady=(0,10))
            i = tk.Frame(o, bg=PANEL)
            i.pack(fill="both", padx=14, pady=12)
            return i

        gap(14)

        # ── Detectie ──────────────────────────────────────────
        c = card()
        section(c, "SETARI DETECTIE", PANEL)
        r1 = tk.Frame(c, bg=PANEL); r1.pack(fill="x", pady=(0,8))
        self.tolf = Inp(r1, "Toleranta ±",       "15",  7)
        self.tolf.pack(side="left", padx=(0,16))
        self.dlf  = Inp(r1, "Delay reactie (s)", "0.1", 7)
        self.dlf.pack(side="left")
        self.cdf  = Inp(c, "Cooldown dupa aruncare (s)", "3.0", 7)
        self.cdf.pack(anchor="w")

        # ── Timeout recalibrare ───────────────────────────────
        c2 = card()
        section(c2, "TIMEOUT RECALIBRARE", PANEL)

        tr = tk.Frame(c2, bg=PANEL); tr.pack(fill="x", pady=(0,8))
        self._to_var = tk.BooleanVar(value=False)
        tk.Checkbutton(tr,
            text="Activ — retrage si re-aruncă dacă nu vede culoarea",
            variable=self._to_var, bg=PANEL, fg=TXT,
            selectcolor=INPUT, activebackground=PANEL,
            activeforeground=TXT, font=(FN,9),
            command=self._on_to).pack(anchor="w")

        tr2 = tk.Frame(c2, bg=PANEL); tr2.pack(fill="x")
        self.tof = Inp(tr2, "Timeout (secunde)", "15", 6)
        self.tof.pack(side="left")
        self._tolbl = tk.Label(tr2, text="   Dezactivat",
                               fg=TXT3, bg=PANEL, font=(FN,8))
        self._tolbl.pack(side="left", padx=8)

        # ── Mod natural ───────────────────────────────────────
        c3 = card()
        section(c3, "MOD NATURAL", PANEL)
        self._nat_var = tk.BooleanVar(value=False)
        tk.Checkbutton(c3,
            text="8% șansă să sară o detectie (pare mai uman)",
            variable=self._nat_var, bg=PANEL, fg=TXT,
            selectcolor=INPUT, activebackground=PANEL,
            activeforeground=TXT, font=(FN,9),
            command=self._on_nat).pack(anchor="w")
        self._natlbl = tk.Label(c3, text="Status: Dezactivat",
                                fg=TXT3, bg=PANEL, font=(FN,8))
        self._natlbl.pack(anchor="w", pady=(4,0))

        gap(12)

    # ─────────────────────────────────────────────────────────
    #  TAB: STATISTICI
    # ─────────────────────────────────────────────────────────
    def _build_stats(self):
        f = tk.Frame(self._content, bg=BG)
        self._tab_frames["Statistici"] = f

        P = tk.Frame(f, bg=BG)
        P.pack(fill="both", expand=True, padx=16, pady=14)

        # Rate boxes
        section(P, "RATE PESCUIT")
        rb = tk.Frame(P, bg=BG); rb.pack(fill="x", pady=(0,12))
        self._sb_min = StatBox(rb, "PE MINUT",  BLUE2)
        self._sb_min.pack(side="left", fill="both", expand=True, padx=(0,6))
        self._sb_30m = StatBox(rb, "30 MINUTE", PURP2)
        self._sb_30m.pack(side="left", fill="both", expand=True, padx=(0,6))
        self._sb_1h  = StatBox(rb, "1 ORA",     GRN)
        self._sb_1h.pack(side="left", fill="both", expand=True)

        # Detalii
        section(P, "DETALII SESIUNE")
        dc = tk.Frame(P, bg=PANEL, highlightthickness=1,
                      highlightbackground=BORD)
        dc.pack(fill="x", pady=(0,12))
        di = tk.Frame(dc, bg=PANEL); di.pack(fill="both", padx=14, pady=10)

        def drow(label, attr, color=TXT2):
            r = tk.Frame(di, bg=PANEL); r.pack(fill="x", pady=3)
            tk.Label(r, text=label, fg=TXT2, bg=PANEL,
                     font=(FN,9)).pack(side="left")
            v = tk.Label(r, text="—", fg=color, bg=PANEL,
                         font=(FN,9,"bold"))
            v.pack(side="right")
            setattr(self, attr, v)

        drow("Timp sesiune:",       "_st_time",  BLUE2)
        drow("Total catches:",      "_st_tot",   GRN)
        drow("Timp mediu:",         "_st_avg",   TXT2)
        drow("Proiectie 1h:",       "_st_p1h",   YEL)
        drow("Proiectie 8h:",       "_st_p8h",   YEL)
        drow("Recalibrari:",        "_st_rec",   PURP2)
        drow("Recalibrari/ora:",    "_st_rrate", PURP2)

        # Grafic
        section(P, "CATCHES / MINUT  (ultimele 10 min)")
        gf = tk.Frame(P, bg=PANEL, highlightthickness=1,
                      highlightbackground=BORD)
        gf.pack(fill="x")
        self._graph = tk.Label(gf,
            text="Nu exista date inca.",
            fg=TXT3, bg=PANEL,
            font=("Consolas", 8), justify="left")
        self._graph.pack(anchor="w", padx=12, pady=10)

    # ─────────────────────────────────────────────────────────
    #  TAB: LOG
    # ─────────────────────────────────────────────────────────
    def _build_log(self):
        f = tk.Frame(self._content, bg=BG)
        self._tab_frames["Log"] = f

        P = tk.Frame(f, bg=BG)
        P.pack(fill="both", expand=True, padx=16, pady=14)

        section(P, "LOG ACTIVITATE")
        lf = tk.Frame(P, bg=PANEL, highlightthickness=1,
                      highlightbackground=BORD)
        lf.pack(fill="both", expand=True)
        self._log_w = tk.Text(lf, bg=PANEL, fg=TXT2,
                              font=("Consolas", 8),
                              relief="flat", state="disabled",
                              wrap="word", bd=10,
                              selectbackground=INPUT)
        sb2 = tk.Scrollbar(lf, orient="vertical",
                           command=self._log_w.yview,
                           bg=PANEL, troughcolor=PANEL)
        self._log_w.configure(yscrollcommand=sb2.set)
        sb2.pack(side="right", fill="y")
        self._log_w.pack(fill="both", expand=True)

        for tag, col in [("ok",GRN),("warn",YEL),("err",RED),
                         ("dim",TXT3),("hi",BLUE2),("pur",PURP2)]:
            self._log_w.tag_config(tag, foreground=col)

        # Clear btn
        br = tk.Frame(P, bg=BG); br.pack(fill="x", pady=(8,0))
        FlatBtn(br, "🗑  Sterge Log", self._clear_log,
                bg=INPUT, fg=TXT2, abg=BORD, size=9
                ).pack(side="right", ipady=5, ipadx=10)

        self._log("GamerMacro Pro v6.0 ready.", "hi")
        self._log("Layout: Sidebar + Content (ca Claude UI)", "dim")
        self._log("Seteaza coordonatele in tab Macro, setarile in tab Setari.", "dim")

    # ─────────────────────────────────────────────────────────
    #  LOGICA
    # ─────────────────────────────────────────────────────────
    def _on_to(self):
        self._timeout = self._to_var.get()
        if self._timeout:
            self._tolbl.config(text="   Activat", fg=PURP2)
            self._log("Timeout recalibrare ACTIVAT.", "pur")
        else:
            self._tolbl.config(text="   Dezactivat", fg=TXT3)
            self._log("Timeout dezactivat.", "dim")

    def _on_nat(self):
        self._natural = self._nat_var.get()
        if self._natural:
            self._natlbl.config(text="Status: Activat — 8% skip", fg=BLUE2)
            self._log("Mod Natural ACTIVAT.", "pur")
        else:
            self._natlbl.config(text="Status: Dezactivat", fg=TXT3)
            self._log("Mod Natural dezactivat.", "dim")

    def _cap(self):
        self._capbtn.disable()
        self._cd(3)

    def _cd(self, n):
        if n > 0:
            self._clbl_c.config(
                text=f"Muta mouse-ul…  {n}s", fg=YEL)
            self.root.after(1000, self._cd, n - 1)
        else:
            try:
                x, y = pyautogui.position()
                self.xf.var.set(str(x))
                self.yf.var.set(str(y))
                self._clbl_c.config(
                    text=f"✓  X={x}  Y={y}", fg=GRN)
                self._log(f"Coordonate → X={x}  Y={y}", "ok")
            except Exception as e:
                self._clbl_c.config(text=f"Eroare: {e}", fg=RED)
            finally:
                self._capbtn.enable()

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
                text=f"✓  RGB({r},{g},{b})  {hx}", fg=GRN)
            self._log(f"Culoare → RGB({r},{g},{b})  {hx}", "ok")
        except Exception as e:
            self._clbl_col.config(text=f"Eroare: {e}", fg=RED)
            self._log(f"Eroare: {e}", "err")

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
            raise ValueError(f"({x},{y}) in afara ecranului.")
        return x, y, r, g, b, tol, dl, cd, to

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
                    if (to > 0 and watch_since and
                            time.time() - watch_since > to):
                        self._recals += 1
                        nr = self._recals
                        self.root.after(0, self._log,
                            f"[RECAL #{nr}] Timeout {to}s — retrag!", "pur")
                        self.root.after(0, self._rlbl.config,
                            {"text": f"Recal: {nr}"})
                        self.root.after(0, self._hdr_recal.config,
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
                                f"[skip #{skip}] Natural — ignorat.", "pur")
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
                        self.root.after(0, self._hdr_catch.config,
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
        cols = {"IDLE": TXT3, "RESET": TXT3, "WATCH": BLUE2}
        c = cols.get(s, TXT3)
        self.root.after(0, self._stlbl.config, {"text": s, "fg": c})
        self.root.after(0, self._sidebar_status.config,
                        {"text": s, "fg": c})

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
        self._hdr_catch.config(text="Catches: 0")
        self._hdr_recal.config(text="")
        self._rlbl.config(text="")
        self._ui(True)

        x, y, r, g, b, tol, dl, cd, to = args
        nat = self._natural
        self._log(
            f"START  ({x},{y})  RGB({r},{g},{b})  ±{tol}  "
            f"delay={dl}s  cd={cd}s  "
            f"to={'ON '+str(to)+'s' if to else 'OFF'}  "
            f"nat={'ON' if nat else 'OFF'}", "hi")

        self._thread = threading.Thread(
            target=self._loop,
            args=(x, y, r, g, b, tol, dl, cd, to, nat),
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
        dot_col = GRN if run else TXT3
        self._sidebar_dot.config(fg=dot_col)
        self._startbtn.config(
            state="disabled" if run else "normal",
            bg=INPUT if run else PURP)
        self._stopbtn.config(
            state="normal" if run else "disabled",
            bg=RED if run else REDDK,
            fg="#0F1117" if run else RED)
        self._capbtn.config(
            state="disabled" if run else "normal")
        self._samplebtn.config(
            state="disabled" if run else "normal")

    def _clear_log(self):
        self._log_w.configure(state="normal")
        self._log_w.delete("1.0", "end")
        self._log_w.configure(state="disabled")

    def _log(self, msg, tag="dim"):
        if not hasattr(self, '_log_w'): return
        ts = time.strftime("%H:%M:%S")
        self._log_w.configure(state="normal")
        self._log_w.insert("end", f"[{ts}]  {msg}\n", tag)
        self._log_w.see("end")
        self._log_w.configure(state="disabled")

    def _tick_stats(self):
        try: self._compute_stats()
        except: pass
        self.root.after(3000, self._tick_stats)

    def _compute_stats(self):
        now     = time.time()
        total   = self._catches
        elapsed = (now - self._start_ts) if self._start_ts else 0
        ts      = self._ts_list

        if self._start_ts and self._running:
            h = int(elapsed // 3600)
            m = int((elapsed % 3600) // 60)
            s = int(elapsed % 60)
            self._st_time.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        else:
            self._st_time.config(text="—")

        self._st_tot.config(text=str(total))
        self._st_rec.config(text=str(self._recals))

        rpm = (total / (elapsed / 60)) if elapsed > 0 else 0
        last_min = len([t for t in ts if now - t <= 60])

        self._sb_min.set(last_min)
        self._sb_30m.set(f"{rpm*30:.1f}")
        self._sb_1h.set(f"{rpm*60:.1f}")
        self._st_p1h.config(text=f"{rpm*60:.0f} catches")
        self._st_p8h.config(text=f"{rpm*480:.0f} catches")

        if len(ts) >= 2:
            diffs = [ts[i]-ts[i-1] for i in range(1,len(ts))]
            self._st_avg.config(text=f"{sum(diffs)/len(diffs):.1f}s")
        else:
            self._st_avg.config(text="—")

        if elapsed > 60:
            self._st_rrate.config(
                text=f"{self._recals/(elapsed/3600):.1f}/ora")
        else:
            self._st_rrate.config(text="—")

        # Grafic
        bars = []
        mx = 1
        for i in range(10, 0, -1):
            cnt = len([t for t in ts
                       if now-i*60 <= t < now-(i-1)*60])
            bars.append((f"-{i}m", cnt))
            mx = max(mx, cnt)
        lines = []
        for label, val in bars:
            filled = int((val/mx)*18) if mx > 0 else 0
            bar = "█"*filled + "░"*(18-filled)
            lines.append(f"{label:>4}  {bar}  {val}")
        self._graph.config(
            text="\n".join(lines) if any(v for _,v in bars)
                 else "Nu exista date inca.")

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
