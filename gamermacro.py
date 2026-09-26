"""
GamerMacro Pro — Fishing Edition v6.1
Modern GUI Upgrade: Dark theme + green accents + profile saving
Layout: Sidebar stanga + Continut dreapta (ca Claude)
Tema: Dark grey + verde neon (Modern Premium)
Redimensionabil + Transparente + Smooth animations
"""
import tkinter as tk
from tkinter import font as tkfont
import threading, time, random, sys
import json
from pathlib import Path
from datetime import datetime

# Import modern GUI components
from gamermacro_modern_upgrade import (
    ModernTheme, ProfileManager, ModernComponents, init_profile_manager
)

import pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

from pynput.mouse import Button, Controller as MC
_mouse = MC()

def right_click():
    _mouse.click(Button.right, 1)

# ── Modern Color Palette ───────────────────────────────────────
BG      = ModernTheme.COLORS["bg_primary"]
SIDEBAR = ModernTheme.COLORS["bg_secondary"]
PANEL   = ModernTheme.COLORS["bg_tertiary"]
S1      = PANEL
PANEL2  = ModernTheme.COLORS["bg_secondary"]
INPUT   = ModernTheme.COLORS["bg_tertiary"]
BORD    = ModernTheme.COLORS["border"]
BORD2   = ModernTheme.COLORS["border_accent"]
BLUE    = ModernTheme.COLORS["accent_green"]       # Acum verde
BLUE2   = ModernTheme.COLORS["accent_green_light"]
BLUED   = ModernTheme.COLORS["accent_green_dark"]
PURP    = ModernTheme.COLORS["accent_green"]       # Verde pt consistenta
PURP2   = ModernTheme.COLORS["accent_green_light"]
PURPD   = ModernTheme.COLORS["accent_green_dark"]
GRN     = ModernTheme.COLORS["accent_green"]
GRNDK   = ModernTheme.COLORS["accent_green_dark"]
RED     = ModernTheme.COLORS["error"]
REDDK   = "#7F1D1D"
YEL     = ModernTheme.COLORS["warning"]
TXT     = ModernTheme.COLORS["text_primary"]
TXT2    = ModernTheme.COLORS["text_secondary"]
TXT3    = ModernTheme.COLORS["text_tertiary"]
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
        ("❄️", "Winter"),
        ("📊", "Statistici"),
        ("📋", "Log"),
    ]
    POLL = 0.05

    def __init__(self, root):
        self.root      = root
        self._running  = False
        self._natural  = False
        self._autocast = False
        self._detector2_enabled = False
        self._timeout  = False
        self._catches  = 0
        self._recals   = 0
        self._thread   = None
        self._start_ts = None
        self._ts_list  = []
        self._cur_tab  = None
        
        # Initialize profile manager
        self.profile_mgr = init_profile_manager()
        current_settings = self.profile_mgr.get_current_settings()
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
        self._build_winter()
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

        # ── Profile Management ────────────────────────────────
        c_prof = card()
        section(c_prof, "PROFILURI", PANEL)
        
        # Profile selector
        prof_names = self.profile_mgr.profiles.keys()
        self.profile_var = tk.StringVar(value=self.profile_mgr.current_profile)
        prof_combo = tk.OptionMenu(c_prof, self.profile_var, *prof_names,
                                   command=self._on_profile_change)
        prof_combo.config(bg=INPUT, fg=TXT, activebackground=BLUED,
                         activeforeground=TXT, highlightthickness=0, bd=0)
        prof_combo.pack(fill="x", padx=0, pady=(0,10))
        
        # Profile action buttons
        prof_btn_frame = tk.Frame(c_prof, bg=PANEL)
        prof_btn_frame.pack(fill="x", pady=(0,10))
        
        btn_load = tk.Button(prof_btn_frame, text="Incarca Profil",
                            command=self._load_profile, bg=BLUE, fg=TXT,
                            relief="flat", bd=0, padx=10, pady=5)
        btn_load.pack(side="left", padx=(0,5))
        
        btn_save = tk.Button(prof_btn_frame, text="Salveaza Profil",
                            command=self._save_profile, bg=GRN, fg=TXT,
                            relief="flat", bd=0, padx=10, pady=5)
        btn_save.pack(side="left", padx=(0,5))
        
        btn_new = tk.Button(prof_btn_frame, text="+ Profil Nou",
                           command=self._new_profile, bg=BLUE2, fg=TXT,
                           relief="flat", bd=0, padx=10, pady=5)
        btn_new.pack(side="left")
        
        # Auto-save label
        self._autosave_lbl = tk.Label(c_prof, text="Auto-save: Dezactivat",
                                      fg=TXT3, bg=PANEL, font=(FN,8))
        self._autosave_lbl.pack(anchor="w")

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
        self.pwf  = Inp(c, "Asteapta dupa detectie (s)  — 0 = dezactivat", "0", 7)
        self.pwf.pack(anchor="w", pady=(6,0))
        tk.Label(c, text="Dupa prima detectie, ignora X secunde, apoi actioneaza la urmatoarea.",
                 fg=TXT3, bg=S1, font=(FN,7)).pack(anchor="w")

        # ── Timeout recalibrare ───────────────────────────────
        c2 = card()
        section(c2, "RECALIBRARE AUTOMATA", PANEL)
        tk.Label(c2,
            text="Daca nu detecteaza pixelul in X secunde dupa ce a aruncat → retrage si re-arunca automat.",
            fg=TXT3, bg=PANEL, font=(FN,7), wraplength=380, justify="left"
        ).pack(anchor="w", pady=(0,6))
        tr2 = tk.Frame(c2, bg=PANEL); tr2.pack(fill="x")
        self.tof = Inp(tr2, "Recalibrare dupa (s)  — 0 = dezactivat", "0", 6)
        self.tof.pack(side="left")
        tk.Label(tr2, text="   ex: 15 = daca in 15s nu vede culoarea, re-arunca",
                 fg=TXT3, bg=PANEL, font=(FN,7)).pack(side="left", padx=8)

        # ── Auto-recast ────────────────────────────────────────
        c3a = card()
        section(c3a, "AUTO-RECAST", PANEL)
        self._autocast_var = tk.BooleanVar(value=False)
        tk.Checkbutton(c3a,
            text="Recast automat (o singura aruncare dupa catch)",
            variable=self._autocast_var, bg=PANEL, fg=TXT,
            selectcolor=INPUT, activebackground=PANEL,
            activeforeground=TXT, font=(FN,9),
            command=self._on_autocast).pack(anchor="w")
        self._autocastlbl = tk.Label(c3a, text="Status: Dezactivat (2x click-uri)",
                                     fg=TXT3, bg=PANEL, font=(FN,8))
        self._autocastlbl.pack(anchor="w", pady=(4,0))
        tk.Label(c3a,
            text="Daca activat → o singura aruncare. Daca dezactivat → 2x click-uri (normal).",
            fg=TXT3, bg=PANEL, font=(FN,7), wraplength=380, justify="left"
        ).pack(anchor="w", pady=(4,0))

        gap(12)

        # ── Detector 2 - Pixel Checker 2 (Left Click) ─────────
        c_det2 = card()
        section(c_det2, "PIXEL DETECTOR 2 - CUSTOM ACTION", PANEL)
        
        # Position X, Y
        pos2_frame = tk.Frame(c_det2, bg=PANEL)
        pos2_frame.pack(fill="x", pady=(0, 10))
        self.x2f = Inp(pos2_frame, "Pos X", "640", 5)
        self.x2f.pack(side="left", padx=(0, 10))
        self.y2f = Inp(pos2_frame, "Pos Y", "360", 5)
        self.y2f.pack(side="left")
        
        # RGB Colors
        rgb2_frame = tk.Frame(c_det2, bg=PANEL)
        rgb2_frame.pack(fill="x", pady=(0, 10))
        self.r2f = Inp(rgb2_frame, "R", "150", 4)
        self.r2f.pack(side="left", padx=(0, 10))
        self.g2f = Inp(rgb2_frame, "G", "150", 4)
        self.g2f.pack(side="left", padx=(0, 10))
        self.b2f = Inp(rgb2_frame, "B", "150", 4)
        self.b2f.pack(side="left")
        
        # Tolerance
        tol2_frame = tk.Frame(c_det2, bg=PANEL)
        tol2_frame.pack(fill="x", pady=(0, 10))
        self.tol2f = Inp(tol2_frame, "Tol ±", "25", 5)
        self.tol2f.pack(side="left")
        
        # Number of clicks
        clicks_frame = tk.Frame(c_det2, bg=PANEL)
        clicks_frame.pack(fill="x", pady=(0, 10))
        tk.Label(clicks_frame, text="Clicks:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
        self.clicks_var = tk.IntVar(value=1)
        tk.Spinbox(clicks_frame, from_=1, to=50, textvariable=self.clicks_var,
                  bg=INPUT, fg=TXT, relief="flat", bd=0, width=4, font=(FN,9)).pack(side="left", padx=(0, 20))
        
        # Interval Seconds + Milliseconds
        interval_frame = tk.Frame(c_det2, bg=PANEL)
        interval_frame.pack(fill="x", pady=(0, 10))
        tk.Label(interval_frame, text="Interval:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
        
        self.interval_sec_var = tk.IntVar(value=0)
        tk.Label(interval_frame, text="Sec:", bg=PANEL, fg=TXT2, font=(FN,8)).pack(side="left", padx=(0, 3))
        tk.Spinbox(interval_frame, from_=0, to=60, textvariable=self.interval_sec_var,
                  bg=INPUT, fg=TXT, relief="flat", bd=0, width=3, font=(FN,9)).pack(side="left", padx=(0, 15))
        
        self.interval_ms_var = tk.IntVar(value=500)
        tk.Label(interval_frame, text="Ms:", bg=PANEL, fg=TXT2, font=(FN,8)).pack(side="left", padx=(0, 3))
        tk.Spinbox(interval_frame, from_=0, to=999, textvariable=self.interval_ms_var,
                  bg=INPUT, fg=TXT, relief="flat", bd=0, width=4, font=(FN,9)).pack(side="left")
        
        # Total interval display
        self.interval_lbl = tk.Label(c_det2, text="Total: 0.500s (500ms)",
                                    fg=BLUE, bg=PANEL, font=(FN,9))
        self.interval_lbl.pack(anchor="w", pady=(0, 10))
        
        def update_interval(*args):
            total_ms = self.interval_sec_var.get() * 1000 + self.interval_ms_var.get()
            self.interval_lbl.config(text=f"Total: {total_ms/1000:.3f}s ({total_ms}ms)")
        
        self.interval_sec_var.trace("w", update_interval)
        self.interval_ms_var.trace("w", update_interval)
        
        # Enable checkbox
        self.det2_var = tk.BooleanVar(value=False)
        tk.Checkbutton(c_det2,
            text="Enable Detector 2 (Left Click)",
            variable=self.det2_var, bg=PANEL, fg=TXT,
            selectcolor=INPUT, activebackground=PANEL,
            activeforeground=TXT, font=(FN,9),
            command=self._on_det2_toggle).pack(anchor="w", pady=(0, 5))
        
        self.det2_lbl = tk.Label(c_det2, text="Status: Dezactivat",
                                fg=TXT3, bg=PANEL, font=(FN,8))
        self.det2_lbl.pack(anchor="w")

        gap(12)

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
    #  TAB: WINTER - PIXEL DETECTOR
    # ─────────────────────────────────────────────────────────
    def _build_winter(self):
        f = tk.Frame(self._content, bg=BG)
        self._tab_frames["Winter"] = f
        
        P = tk.Frame(f, bg=BG)
        P.pack(fill="both", expand=True, padx=16, pady=14)
        
        # Title
        title = tk.Label(P, text="❄️ Winter - Visual Pixel Detector",
                        font=(FN, 16, "bold"), bg=BG, fg=BLUE)
        title.pack(pady=(0, 20))
        
        # Info card
        info_frame = tk.Frame(P, bg=PANEL, highlightthickness=1, highlightbackground=BORD)
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_text = tk.Label(info_frame,
                            text="🎯 Select pixels directly with your cursor!\n\n"
                                 "1. Click 'Start Selection' button\n"
                                 "2. Move cursor to the pixel you want\n"
                                 "3. Press SPACE to capture the color\n"
                                 "4. Press ESC to stop selection\n\n"
                                 "Perfect for Detector 2 configuration!",
                            bg=PANEL, fg=TXT2, justify="left",
                            font=(FN, 10), padx=20, pady=20)
        info_text.pack()
        
        # Start selection button
        btn_frame = tk.Frame(P, bg=BG)
        btn_frame.pack(fill="x", pady=(0, 15))
        
        start_btn = tk.Button(btn_frame, text="🎯 Start Pixel Selection",
                             command=self._start_winter_selection,
                             font=(FN, 11, "bold"), bg=BLUE, fg=TXT,
                             activebackground=BLUED, activeforeground=TXT,
                             relief="flat", bd=0, padx=20, pady=12,
                             cursor="hand2", highlightthickness=0)
        start_btn.pack(fill="x")
        
        # Selected values display
        values_frame = tk.Frame(P, bg=PANEL, highlightthickness=1, highlightbackground=BORD)
        values_frame.pack(fill="x", pady=(0, 15))
        
        section(values_frame, "Valores Detectate", PANEL)
        
        # Position display
        pos_row = tk.Frame(values_frame, bg=PANEL)
        pos_row.pack(fill="x", padx=15, pady=(10, 5))
        
        tk.Label(pos_row, text="Position: X=", bg=PANEL, fg=TXT2, font=(FN, 9)).pack(side="left")
        self.winter_x_lbl = tk.Label(pos_row, text="0", bg=PANEL, fg=BLUE, font=(FN, 9, "bold"))
        self.winter_x_lbl.pack(side="left", padx=(0, 15))
        
        tk.Label(pos_row, text="Y=", bg=PANEL, fg=TXT2, font=(FN, 9)).pack(side="left")
        self.winter_y_lbl = tk.Label(pos_row, text="0", bg=PANEL, fg=BLUE, font=(FN, 9, "bold"))
        self.winter_y_lbl.pack(side="left")
        
        # Color display
        color_row = tk.Frame(values_frame, bg=PANEL)
        color_row.pack(fill="x", padx=15, pady=(5, 15))
        
        tk.Label(color_row, text="Color: R=", bg=PANEL, fg=TXT2, font=(FN, 9)).pack(side="left")
        self.winter_r_lbl = tk.Label(color_row, text="0", bg=PANEL, fg=BLUE, font=(FN, 9, "bold"))
        self.winter_r_lbl.pack(side="left", padx=(0, 10))
        
        tk.Label(color_row, text="G=", bg=PANEL, fg=TXT2, font=(FN, 9)).pack(side="left")
        self.winter_g_lbl = tk.Label(color_row, text="0", bg=PANEL, fg=BLUE, font=(FN, 9, "bold"))
        self.winter_g_lbl.pack(side="left", padx=(0, 10))
        
        tk.Label(color_row, text="B=", bg=PANEL, fg=TXT2, font=(FN, 9)).pack(side="left")
        self.winter_b_lbl = tk.Label(color_row, text="0", bg=PANEL, fg=BLUE, font=(FN, 9, "bold"))
        self.winter_b_lbl.pack(side="left")
        
        # Copy instructions
        copy_frame = tk.Frame(P, bg=PANEL, highlightthickness=1, highlightbackground=BORD)
        copy_frame.pack(fill="x")
        
        copy_text = tk.Label(copy_frame,
                            text="📋 Copy these values to Detector 2 in SETARI tab\n"
                                 "Go to Settings → Detector 2 and paste the values",
                            bg=PANEL, fg=TXT3, justify="left",
                            font=(FN, 9), padx=15, pady=15)
        copy_text.pack()
    
    def _start_winter_selection(self):
        """Start winter pixel selection"""
        self._log("Winter mode: Move cursor and press SPACE to capture, ESC to stop", "pur")
        self._detect_pixel_at_cursor()
    
    def _detect_pixel_at_cursor(self):
        """Detect pixel at cursor position"""
        try:
            import pyautogui
            from PIL import ImageGrab
            from pynput import keyboard
            
            def on_press(key):
                try:
                    if key == keyboard.Key.space:
                        x, y = pyautogui.position()
                        screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
                        pixel = screenshot.getpixel((0, 0))
                        
                        self.winter_x_lbl.config(text=str(x))
                        self.winter_y_lbl.config(text=str(y))
                        self.winter_r_lbl.config(text=str(pixel[0]))
                        self.winter_g_lbl.config(text=str(pixel[1]))
                        self.winter_b_lbl.config(text=str(pixel[2]))
                        
                        self._log(f"✓ Captured: X={x}, Y={y}, R={pixel[0]}, G={pixel[1]}, B={pixel[2]}", "ok")
                    
                    elif key == keyboard.Key.esc:
                        return False
                except:
                    pass
            
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
        except Exception as e:
            self._log(f"Error: {str(e)}", "err")

    # ─────────────────────────────────────────────────────────
    #  TAB: WINTER - DETECTOR 2
    # ─────────────────────────────────────────────────────────
    def _build_winter(self):
        f = tk.Frame(self._content, bg=BG)
        self._tab_frames["Winter"] = f
        
        # Scroll
        cv = tk.Canvas(f, bg=BG, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(f, orient="vertical", command=cv.yview,
                         bg=PANEL, troughcolor=BG, activebackground=PURP)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True)
        cv.configure(yscrollcommand=sb.set)
        frm = tk.Frame(cv, bg=BG)
        wid = cv.create_window((0, 0), window=frm, anchor="nw")
        frm.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfig(wid, width=e.width))
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        P = frm
        
        # ── PIXEL SELECTION ────────────────────────────────
        c_select = card()
        section(c_select, "PIXEL SELECTOR", PANEL)
        
        select_frame = tk.Frame(c_select, bg=PANEL)
        select_frame.pack(fill="x", padx=15, pady=15)
        
        self.winter_pick_btn = tk.Button(select_frame, text="🎯 CLICK HERE TO PICK PIXEL",
                                        command=self._winter_pick_pixel,
                                        font=(FN, 11, "bold"),
                                        bg=BLUE, fg=BG, relief="flat", bd=0,
                                        padx=20, pady=12, cursor="hand2",
                                        activebackground=BLUED, activeforeground=TXT,
                                        highlightthickness=0)
        self.winter_pick_btn.pack(fill="x", pady=(0, 15))
        
        tk.Label(select_frame, text="Move cursor on pixel and click to capture color + position",
                fg=TXT3, bg=PANEL, font=(FN, 9), justify="center").pack()
        
        gap(12)
        
        # ── POSITION ───────────────────────────────────────
        c_pos = card()
        section(c_pos, "POSITION", PANEL)
        
        pos_frame = tk.Frame(c_pos, bg=PANEL)
        pos_frame.pack(fill="x", pady=(0, 10))
        self.winter_xf = Inp(pos_frame, "X", "640", 8)
        self.winter_xf.pack(side="left", padx=(0, 15))
        self.winter_yf = Inp(pos_frame, "Y", "360", 8)
        self.winter_yf.pack(side="left")
        
        gap(12)
        
        # ── COLOR DETECTION ────────────────────────────────
        c_color = card()
        section(c_color, "COLOR DETECTION", PANEL)
        
        rgb_frame = tk.Frame(c_color, bg=PANEL)
        rgb_frame.pack(fill="x", pady=(0, 10))
        self.winter_rf = Inp(rgb_frame, "Red (R)", "150", 5)
        self.winter_rf.pack(side="left", padx=(0, 10))
        self.winter_gf = Inp(rgb_frame, "Green (G)", "150", 5)
        self.winter_gf.pack(side="left", padx=(0, 10))
        self.winter_bf = Inp(rgb_frame, "Blue (B)", "150", 5)
        self.winter_bf.pack(side="left")
        
        # Color preview
        preview_frame = tk.Frame(c_color, bg=PANEL)
        preview_frame.pack(fill="x", pady=(0, 15))
        tk.Label(preview_frame, text="Preview:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 10))
        self.winter_color_preview = tk.Frame(preview_frame, bg="#969696", width=100, height=30)
        self.winter_color_preview.pack(side="left", padx=5)
        self.winter_color_preview.pack_propagate(False)
        
        # Tolerance
        tol_frame = tk.Frame(c_color, bg=PANEL)
        tol_frame.pack(fill="x")
        self.winter_tolf = Inp(tol_frame, "Tolerance ±", "25", 5)
        self.winter_tolf.pack(side="left")
        
        gap(12)
        
        # ── CLICK CONFIGURATION ────────────────────────────
        c_clicks = card()
        section(c_clicks, "CLICKS", PANEL)
        
        clicks_frame = tk.Frame(c_clicks, bg=PANEL)
        clicks_frame.pack(fill="x")
        self.winter_clicksf = Inp(clicks_frame, "Number of Clicks (1-50)", "1", 5)
        self.winter_clicksf.pack(side="left")
        
        gap(12)
        
        # ── INTERVAL CONFIGURATION ────────────────────────
        c_interval = card()
        section(c_interval, "INTERVAL BETWEEN CLICKS", PANEL)
        
        interval_frame = tk.Frame(c_interval, bg=PANEL)
        interval_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(interval_frame, text="Sec:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
        self.winter_secf = Inp(interval_frame, "", "0", 4)
        self.winter_secf.pack(side="left", padx=(0, 15))
        
        tk.Label(interval_frame, text="Ms:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
        self.winter_msf = Inp(interval_frame, "", "500", 5)
        self.winter_msf.pack(side="left")
        
        # Total display
        total_frame = tk.Frame(c_interval, bg=PANEL)
        total_frame.pack(fill="x")
        tk.Label(total_frame, text="Total:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 10))
        self.winter_total_lbl = tk.Label(total_frame, text="0.500s (500ms)",
                                        fg=BLUE, bg=PANEL, font=(FN,9, "bold"))
        self.winter_total_lbl.pack(side="left")
        
        # Update total on change
        def update_total(*args):
            try:
                sec = int(self.winter_secf.var.get() or 0)
                ms = int(self.winter_msf.var.get() or 0)
                total_ms = sec * 1000 + ms
                self.winter_total_lbl.config(text=f"{total_ms/1000:.3f}s ({total_ms}ms)")
            except:
                pass
        
        self.winter_secf.var.trace("w", update_total)
        self.winter_msf.var.trace("w", update_total)
        
        gap(12)
        
        # ── ENABLE/DISABLE ────────────────────────────────
        c_enable = card()
        
        self.winter_var = tk.BooleanVar(value=False)
        tk.Checkbutton(c_enable, text="Enable Detector 2",
                      variable=self.winter_var, bg=PANEL, fg=TXT,
                      selectcolor=INPUT, activebackground=PANEL,
                      activeforeground=TXT, font=(FN,10, "bold"),
                      command=self._on_winter_toggle).pack(anchor="w", padx=15, pady=15)
        
        self.winter_status_lbl = tk.Label(c_enable, text="Status: Dezactivat",
                                         fg=TXT3, bg=PANEL, font=(FN,8))
        self.winter_status_lbl.pack(anchor="w", padx=15, pady=(0, 15))

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
    def _winter_pick_pixel(self):
        """Pick pixel for Winter"""
        try:
            import pyautogui
            import time
            from PIL import ImageGrab
            
            messagebox.showinfo("Winter Pixel Picker",
                "Move cursor to desired pixel\n\n"
                "Will capture in 1 second...")
            
            time.sleep(1)
            
            x, y = pyautogui.position()
            img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
            pixel = img.getpixel((0, 0))
            
            if len(pixel) >= 3:
                r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
                
                # Auto-fill all fields
                self.winter_x.var.set(x)
                self.winter_y.var.set(y)
                self.winter_r.var.set(r)
                self.winter_g.var.set(g)
                self.winter_b.var.set(b)
                
                # Update preview
                hex_color = f'#{r:02x}{g:02x}{b:02x}'
                self.winter_preview.config(bg=hex_color)
                
                self.winter_status_lbl.config(
                    text=f"✓ Picked: X={x}, Y={y}, RGB({r},{g},{b})",
                    fg=BLUE)
                
                self._log(f"Winter: Picked pixel at ({x}, {y}) - RGB({r}, {g}, {b})", "ok")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")
    
    def _on_winter_toggle(self):
        """Toggle Winter"""
        if self.winter_var.get():
            self.winter_enabled_lbl.config(text="Status: Activat ✓", fg=BLUE2)
            clicks = self.winter_clicks.get()
            interval_ms = self.winter_sec.get() * 1000 + self.winter_ms.get()
            self._log(f"Winter ACTIVAT — {clicks} click-uri, interval {interval_ms}ms", "pur")
        else:
            self.winter_enabled_lbl.config(text="Status: Dezactivat", fg=TXT3)
            self._log("Winter dezactivat", "dim")

    def _open_pixel_picker(self):
        """Open pixel color picker"""
        try:
            import subprocess
            import sys
            # Run pixel picker in separate process
            subprocess.Popen([sys.executable, "pixel_picker.py"])
        except Exception as e:
            self._log(f"Pixel Picker Error: {e}", "err")
            messagebox.showerror("Error", f"Failed to open Pixel Picker: {e}")
    
    def _winter_pick_pixel(self):
        """Pick pixel for Winter tab"""
        self._log("Opening Pixel Picker... Move cursor and click on pixel", "info")
        self.winter_pick_btn.config(state="disabled", text="🎯 Picking... Click pixel!")
        
        def pick_in_thread():
            from PIL import ImageGrab
            import time
            
            # Show dialog
            messagebox.showinfo("Pixel Picker", 
                "Click on the pixel you want to capture.\n\n"
                "The color and position will be auto-filled!")
            
            # Listen for mouse click
            def on_click(x, y):
                try:
                    img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
                    pixel = img.getpixel((0, 0))
                    if len(pixel) >= 3:
                        r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
                        self.winter_xf.var.set(str(x))
                        self.winter_yf.var.set(str(y))
                        self.winter_rf.var.set(str(r))
                        self.winter_gf.var.set(str(g))
                        self.winter_bf.var.set(str(b))
                        
                        hex_color = f'#{r:02x}{g:02x}{b:02x}'
                        self.winter_color_preview.config(bg=hex_color)
                        
                        self._log(f"Pixel picked: X={x}, Y={y}, RGB({r},{g},{b})", "ok")
                except Exception as e:
                    self._log(f"Error picking pixel: {e}", "err")
                finally:
                    self.winter_pick_btn.config(state="normal", text="🎯 CLICK HERE TO PICK PIXEL")
            
            # Use pynput to detect click
            try:
                from pynput.mouse import Listener
                def on_move(x, y):
                    pass
                def on_click_detect(x, y, button, pressed):
                    if pressed:
                        on_click(x, y)
                        return False
                
                with Listener(on_move=on_move, on_click=on_click_detect) as listener:
                    listener.join()
            except:
                self.winter_pick_btn.config(state="normal", text="🎯 CLICK HERE TO PICK PIXEL")
                self._log("Pixel picker not available", "warn")
        
        import threading
        threading.Thread(target=pick_in_thread, daemon=True).start()
    
    def _on_winter_toggle(self):
        """Toggle Winter/Detector 2"""
        if self.winter_var.get():
            self.winter_status_lbl.config(text="Status: Activat ✓", fg=BLUE2)
            clicks = self.winter_clicksf.var.get() if self.winter_clicksf.var.get() else "1"
            interval_ms = int(self.winter_secf.var.get() or 0) * 1000 + int(self.winter_msf.var.get() or 0)
            self._log(f"Winter (Detector 2) ACTIVAT — {clicks} clicks, interval {interval_ms}ms", "pur")
        else:
            self.winter_status_lbl.config(text="Status: Dezactivat", fg=TXT3)
            self._log("Winter (Detector 2) dezactivat.", "dim")
    
    def _update_winter_display(self, x, y, r, g, b):
        """Update Winter section display with picked color"""
        self.winter_pos_lbl.config(text=f"X={x}, Y={y}")
        self.winter_color_lbl.config(text=f"R={r}, G={g}, B={b}")
        hex_color = f'#{r:02x}{g:02x}{b:02x}'
        self.winter_color_preview.config(bg=hex_color)
        
        # Auto-fill Detector 2 fields
        try:
            self.x2f.var.set(str(x))
            self.y2f.var.set(str(y))
            self.r2f.var.set(str(r))
            self.g2f.var.set(str(g))
            self.b2f.var.set(str(b))
            self._log(f"Winter: Picked color at ({x}, {y}) - RGB({r}, {g}, {b})", "ok")
        except:
            pass

    def _on_det2_toggle(self):
        self._detector2_enabled = self.det2_var.get()
        if self._detector2_enabled:
            self.det2_lbl.config(text="Status: Activat ✓", fg=BLUE2)
            clicks = self.clicks_var.get()
            interval_ms = self.interval_sec_var.get() * 1000 + self.interval_ms_var.get()
            self._log(f"Detector 2 ACTIVAT — {clicks} click-uri, interval {interval_ms}ms", "pur")
        else:
            self.det2_lbl.config(text="Status: Dezactivat", fg=TXT3)
            self._log("Detector 2 dezactivat.", "dim")

    def _on_autocast(self):
        self._autocast = self._autocast_var.get()
        if self._autocast:
            self._autocastlbl.config(text="Status: Activat (1x click)", fg=BLUE2)
            self._log("Auto-Recast ACTIVAT — o singura aruncare.", "pur")
        else:
            self._autocastlbl.config(text="Status: Dezactivat (2x click-uri)", fg=TXT3)
            self._log("Auto-Recast dezactivat — 2x click-uri normale.", "dim")

    def _on_nat(self):
        self._natural = self._nat_var.get()
        if self._natural:
            self._natlbl.config(text="Status: Activat — 8% skip", fg=BLUE2)
            self._log("Mod Natural ACTIVAT.", "pur")
        else:
            self._natlbl.config(text="Status: Dezactivat", fg=TXT3)
            self._log("Mod Natural dezactivat.", "dim")

    def _on_profile_change(self, profile_name):
        """Change active profile"""
        if self.profile_mgr.set_current_profile(profile_name):
            self._log(f"Profil schimbat la: {profile_name}", "pur")
            self._load_current_settings()
    
    def _load_profile(self):
        """Load selected profile settings"""
        profile_name = self.profile_var.get()
        settings = self.profile_mgr.profiles[profile_name]["settings"]
        self._apply_settings(settings)
        self._log(f"Profil incarcat: {profile_name}", "ok")
    
    def _save_profile(self):
        """Save current settings to profile"""
        settings = self._get_current_settings()
        profile_name = self.profile_var.get()
        
        if self.profile_mgr.profiles[profile_name]:
            self.profile_mgr.profiles[profile_name]["settings"] = settings
            self.profile_mgr.save_all_profiles()
            self._log(f"Profil salvat: {profile_name}", "ok")
            self._autosave_lbl.config(text=f"Auto-save: {profile_name} ✓", fg=GRN)
    
    def _new_profile(self):
        """Create new profile"""
        import simpledialog
        name = simpledialog.askstring("Profil Nou", "Introduceti numele profilului:")
        if name and name != "default":
            settings = self._get_current_settings()
            self.profile_mgr.create_profile(name, settings)
            self.profile_var.set(name)
            self._log(f"Profil nou creat: {name}", "ok")
    
    def _load_current_settings(self):
        """Load settings from current profile"""
        settings = self.profile_mgr.get_current_settings()
        self._apply_settings(settings)
    
    def _get_current_settings(self):
        """Get current settings from UI"""
        return {
            "tolerance": float(self.tolf.var.get()),
            "delay": float(self.dlf.var.get()),
            "cooldown": float(self.cdf.var.get()),
            "pixelwait": float(self.pwf.var.get()),
            "timeout": float(self.tof.var.get()),
            "natural_mode": self._natural,
            "auto_recast": self._autocast,
        }
    
    def _apply_settings(self, settings):
        """Apply settings to UI"""
        try:
            self.tolf.var.set(str(int(settings.get("tolerance", 15))))
            self.dlf.var.set(str(settings.get("delay", 0.1)))
            self.cdf.var.set(str(settings.get("cooldown", 3.0)))
            self.pwf.var.set(str(settings.get("pixelwait", 0)))
            self.tof.var.set(str(settings.get("timeout", 0)))
            self._natural = settings.get("natural_mode", False)
            self._autocast = settings.get("auto_recast", False)
        except:
            pass

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
        to  = float(self.tof.var.get())
        sc  = pyautogui.size()
        pw  = float(self.pwf.var.get())
        if not (0 <= x < sc.width and 0 <= y < sc.height):
            raise ValueError(f"({x},{y}) in afara ecranului.")
        return x, y, r, g, b, tol, dl, cd, to, pw

    def _loop(self, x, y, tr, tg, tb, tol, delay, cd, to, pw, nat):
        self._upst("RESET")
        state = "RESET"
        watch_since  = None
        pre_wait_end = None   # timestamp pana cand ignora detectiile
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
                        # ── Auto-recast: 1 click (daca activat) vs 2 clicks (normal) ──
                        if self._autocast:
                            right_click()
                        else:
                            right_click()
                            time.sleep(0.5)
                            right_click()
                        time.sleep(cd)
                        state = "RESET"
                        watch_since = None
                        self._upst("RESET")
                        continue

                    if hit:
                        # ── Pre-wait activ: ignora pana expira ───────────────
                        if pre_wait_end is not None:
                            if time.time() < pre_wait_end:
                                # Inca in perioada de asteptare — ignora
                                time.sleep(self.POLL)
                                continue
                            else:
                                # Pre-wait expirat → acum actioneaza
                                pre_wait_end = None
                                self.root.after(0, self._log,
                                    "Pre-wait expirat — actionez!", "ok")

                        if nat and random.random() < 0.08:
                            skip += 1
                            self.root.after(0, self._log,
                                f"[skip #{skip}] Natural — ignorat.", "pur")
                            state = "RESET"
                            watch_since = None
                            self._upst("RESET")
                            time.sleep(self.POLL)
                            continue

                        # ── Prima detectie cu pre-wait activ ─────────────────
                        if pw > 0 and pre_wait_end is None:
                            pre_wait_end = time.time() + pw
                            self.root.after(0, self._log,
                                f"Detectat! Astept {pw}s inainte sa actionez…",
                                "warn")
                            self._upst("PREWAIT")
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

                        # ── Auto-recast: 1 click (daca activat) vs 2 clicks (normal) ──
                        if self._autocast:
                            right_click()
                            self.root.after(0, self._log,
                                f"[#{n}] Recast (1x click)! Cooldown {cd}s…", "ok")
                        else:
                            right_click()
                            time.sleep(0.5)
                            right_click()
                            self.root.after(0, self._log,
                                f"[#{n}] Re-aruncat! Cooldown {cd}s…", "ok")
                        time.sleep(cd)
                        state = "RESET"
                        watch_since = None
                        pre_wait_end = None
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
        cols = {"IDLE": TXT3, "RESET": TXT3, "WATCH": BLUE2, "PREWAIT": YEL}
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

        x, y, r, g, b, tol, dl, cd, to, pw = args
        nat = self._natural
        self._log(
            f"START  ({x},{y})  RGB({r},{g},{b})  ±{tol}  "
            f"delay={dl}s  cd={cd}s  "
            f"to={'ON '+str(to)+'s' if to else 'OFF'}  "
            f"pw={'ON '+str(pw)+'s' if pw else 'OFF'}  "
            f"nat={'ON' if nat else 'OFF'}", "hi")

        self._thread = threading.Thread(
            target=self._loop,
            args=(x, y, r, g, b, tol, dl, cd, to, pw, nat),
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
