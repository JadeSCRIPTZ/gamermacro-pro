"""
GamerMacro Pro — Fishing Edition v5.0
- Timeout recalibrare (daca nu vede culoarea in X sec, retrage si re-arunca)
- Statistici per minut / 30min / 1h
- Statistici Hypixel Skyblock Fishing (nivel, rod, bait, sea creature chance)
"""
import tkinter as tk
from tkinter import ttk
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

# ── Palette (Claude orange + warm grey) ───────────────────────
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
BLUE  = "#60A5FA"
TEAL  = "#2DD4BF"
TEXT  = "#FAFAF9"
TEXT2 = "#A8A29E"
TEXT3 = "#57534E"
FN    = "Segoe UI"
POLL  = 0.05

# ── Hypixel Skyblock Fishing Data ─────────────────────────────
FISHING_RODS = [
    "Rookie Rod", "Decent Rod", "Good Rod", "Great Rod",
    "Incredible Rod", "Angler Rod", "Auger Rod", "Shredder Rod",
    "Challenging Rod", "Rod of Legends", "Spent Rod", "Rod of the Sea",
    "Lava Rod", "Lava Fishing Rod", "Magma Rod", "Inferno Rod",
    "Thunder Rod", "Phantom Rod", "Dusk Rod", "Rod of Aquarius"
]

BAITS = [
    "Niciun Momeala", "Carrot Bait", "Pufferfish Bait", "Fish Bait",
    "Blessed Bait", "Whale Bait", "Shark Bait", "Grand Bait"
]

BAIT_BONUS = {
    "Niciun Momeala": 0,
    "Carrot Bait": 0,
    "Pufferfish Bait": 0,
    "Fish Bait": 15,
    "Blessed Bait": 25,
    "Whale Bait": 15,
    "Shark Bait": 20,
    "Grand Bait": 25,
}

LOCATIONS = [
    "Hub (Lake)", "Spider's Den", "The Barn", "Mushroom Desert",
    "Blazing Fortress", "The End", "Crimson Isle",
    "Crystal Hollows", "Glacial Cave", "Jerry's Workshop",
    "Kuudra", "Deep Caverns"
]

# Sea creature chance bazat pe nivel fishing
def get_sea_creature_chance(fishing_level, pet_perk=0, rod_bonus=0, bait_bonus=0):
    base = 20 + fishing_level * 0.2
    total = base + pet_perk + rod_bonus + bait_bonus
    return min(total, 100)

# Creatures disponibile bazat pe nivel
def get_available_creatures(fishing_level, location):
    creatures = []
    if fishing_level >= 1:
        creatures += ["Squid", "Sea Walker", "Night Squid"]
    if fishing_level >= 5:
        creatures += ["Sea Guardian", "Sea Witch"]
    if fishing_level >= 10:
        creatures += ["Sea Archer", "Sea Leech"]
    if fishing_level >= 15:
        creatures += ["Guardian Defender", "Deep Sea Protector"]
    if fishing_level >= 20:
        creatures += ["Sea Emperor"]
    if fishing_level >= 25:
        creatures += ["Catfish", "Ocelot"]
    if "Crimson" in location and fishing_level >= 1:
        creatures = ["Lava Leech", "Fire Eel", "Magma Slug",
                     "Taurus", "Thunderlord", "Lord Jawbus"]
    if "Crystal" in location and fishing_level >= 1:
        creatures = ["Vanquisher", "Rider of the Deep",
                     "Abyssal Miner", "Crystal Hollows Leech"]
    return creatures if creatures else ["Sea Walker"]

# XP necesar per nivel fishing
FISHING_XP = [0, 50, 125, 235, 395, 625, 955, 1425, 2095,
               3045, 4385, 6275, 8940, 12700, 17960, 25340,
               35640, 50040, 70040, 97640, 135640]

def xp_to_next(level):
    if level >= len(FISHING_XP)-1:
        return "MAX"
    return FISHING_XP[level+1] - FISHING_XP[level]


# ── UI Helpers ────────────────────────────────────────────────
def mk_btn(parent, text, cmd, bg=ORG, fg="#1C1917", abg=ORG2,
           state="normal", fsize=9, **kw):
    return tk.Button(parent, text=text, command=cmd,
                     bg=bg, fg=fg,
                     activebackground=abg, activeforeground="#1C1917",
                     disabledforeground=TEXT3,
                     relief="flat", bd=0, cursor="hand2",
                     font=(FN, fsize, "bold"),
                     state=state, **kw)

class Field(tk.Frame):
    def __init__(self, master, label, val="0", w=7, **kw):
        bg = master["bg"]
        super().__init__(master, bg=bg, **kw)
        tk.Label(self, text=label, fg=TEXT2, bg=bg,
                 font=(FN,8)).pack(anchor="w", pady=(0,2))
        self.var = tk.StringVar(value=str(val))
        e = tk.Entry(self, textvariable=self.var, width=w,
                     bg=S2, fg=TEXT, insertbackground=ORG2,
                     relief="flat", bd=0,
                     font=("Consolas",10), justify="center",
                     highlightthickness=1,
                     highlightbackground=BORD,
                     highlightcolor=ORG)
        e.pack(ipady=6, ipadx=4)
        e.bind("<FocusIn>",  lambda _: e.config(highlightbackground=ORG))
        e.bind("<FocusOut>", lambda _: e.config(highlightbackground=BORD))

class Swatch(tk.Frame):
    def __init__(self, master, sz=36, **kw):
        super().__init__(master, width=sz, height=sz, bg=S2,
                         highlightthickness=1,
                         highlightbackground=BORD, **kw)
        self.pack_propagate(False)
    def set_color(self, r, g, b):
        c = f"#{r:02x}{g:02x}{b:02x}"
        self.config(bg=c, highlightbackground=c)

class Toggle(tk.Frame):
    def __init__(self, master, cb=None, **kw):
        super().__init__(master, bg=S2,
                         highlightthickness=1,
                         highlightbackground=BORD, **kw)
        self._on = False; self._cb = cb
        self._boff = tk.Button(self, text=" OFF ",
            bg=S3, fg=TEXT2, activebackground=BORD,
            activeforeground=TEXT, relief="flat", bd=0,
            font=(FN,8,"bold"), cursor="hand2", command=self._do_off)
        self._boff.pack(side="left", padx=2, pady=2)
        tk.Frame(self, bg=BORD, width=1).pack(side="left", fill="y")
        self._bon = tk.Button(self, text="  ON  ",
            bg=S2, fg=TEXT3, activebackground=ORG3,
            activeforeground=ORG2, relief="flat", bd=0,
            font=(FN,8,"bold"), cursor="hand2", command=self._do_on)
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

def styled_dropdown(parent, var, values, w=22):
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Dark.TCombobox",
        fieldbackground=S2, background=S2,
        foreground=TEXT, selectbackground=ORG3,
        selectforeground=ORG2, arrowcolor=ORG2,
        bordercolor=BORD)
    style.map("Dark.TCombobox",
        fieldbackground=[("readonly", S2)],
        foreground=[("readonly", TEXT)])
    cb = ttk.Combobox(parent, textvariable=var, values=values,
                      state="readonly", width=w,
                      style="Dark.TCombobox", font=(FN,9))
    return cb


# ─────────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────────
class App:
    POLL = 0.05

    def __init__(self, root):
        self.root      = root
        self._running  = False
        self._natural  = False
        self._catches  = 0
        self._recals   = 0
        self._thread   = None
        self._start_ts = None
        self._log_w    = None

        # Statistici pe timp
        self._session_catches = []  # timestamps ale fiecarui catch

        self._setup_window()
        self._build()

        # Update statistici la fiecare 5 secunde
        self._update_stats_job()

    def _setup_window(self):
        self.root.title("GamerMacro Pro — Fishing")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        W, H = 520, 780
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    def _build(self):
        tk.Frame(self.root, bg=ORG, height=3).pack(fill="x")

        # Header
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(12,8))
        hl = tk.Frame(hdr, bg=BG); hl.pack(side="left")
        logo = tk.Frame(hl, bg=BG); logo.pack(anchor="w")
        tk.Label(logo, text="●", fg=ORG, bg=BG,
                 font=(FN,14)).pack(side="left", padx=(0,8))
        tk.Label(logo, text="GamerMacro Pro",
                 fg=TEXT, bg=BG,
                 font=(FN,16,"bold")).pack(side="left")
        tk.Label(hl, text="Fishing Edition  v5.0",
                 fg=TEXT3, bg=BG, font=(FN,8)).pack(anchor="w", pady=(2,0))

        hr = tk.Frame(hdr, bg=BG); hr.pack(side="right", anchor="ne")
        self._status_lbl = tk.Label(hr, text="  IDLE  ",
            fg=TEXT3, bg=S2, font=(FN,9,"bold"), padx=10, pady=4)
        self._status_lbl.pack(anchor="e")
        self._catch_lbl = tk.Label(hr, text="Catches: 0",
            fg=YEL, bg=BG, font=(FN,8))
        self._catch_lbl.pack(anchor="e", pady=(3,0))

        tk.Frame(self.root, bg=BORD, height=1).pack(fill="x")

        # Notebook tabs
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TNotebook",
            background=BG, borderwidth=0, tabmargins=0)
        style.configure("Dark.TNotebook.Tab",
            background=S2, foreground=TEXT2,
            font=(FN,9,"bold"), padding=[14,6],
            borderwidth=0)
        style.map("Dark.TNotebook.Tab",
            background=[("selected", S1)],
            foreground=[("selected", ORG2)])

        nb = ttk.Notebook(self.root, style="Dark.TNotebook")
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        # Tab 1: Macro
        self._tab_macro = tk.Frame(nb, bg=BG)
        nb.add(self._tab_macro, text="🎣  Macro")

        # Tab 2: Statistici
        self._tab_stats = tk.Frame(nb, bg=BG)
        nb.add(self._tab_stats, text="📊  Statistici")

        # Tab 3: Skyblock Profile
        self._tab_skyblock = tk.Frame(nb, bg=BG)
        nb.add(self._tab_skyblock, text="🎮  Skyblock")

        self._build_macro_tab()
        self._build_stats_tab()
        self._build_skyblock_tab()

        tk.Frame(self.root, bg=BORD, height=1).pack(fill="x")
        tk.Label(self.root,
            text="⚠  Failsafe: muta mouse-ul in coltul stanga-sus",
            fg=TEXT3, bg=BG, font=(FN,7)).pack(pady=4)

    # ─────────────────────────────────────────────────────────
    #  TAB 1 — MACRO
    # ─────────────────────────────────────────────────────────
    def _build_macro_tab(self):
        P = self._tab_macro
        cv = tk.Canvas(P, bg=BG, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(P, orient="vertical", command=cv.yview,
                          bg=S2, troughcolor=BG, activebackground=ORG)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        cv.configure(yscrollcommand=sb.set)
        frm = tk.Frame(cv, bg=BG)
        wid = cv.create_window((0,0), window=frm, anchor="nw")
        frm.bind("<Configure>",
            lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",
            lambda e: cv.itemconfig(wid, width=e.width))
        P.bind_all("<MouseWheel>",
            lambda e: cv.yview_scroll(int(-1*(e.delta/120)),"units"))

        def gap(n=8):
            tk.Frame(frm, bg=BG, height=n).pack(fill="x")

        def sec(icon, title):
            f = tk.Frame(frm, bg=BG)
            f.pack(fill="x", padx=16, pady=(12,5))
            tk.Label(f, text=icon, fg=ORG2, bg=BG,
                     font=(FN,10)).pack(side="left", padx=(0,6))
            tk.Label(f, text=title, fg=TEXT, bg=BG,
                     font=(FN,10,"bold")).pack(side="left")
            tk.Frame(f, bg=BORD2, height=1).pack(
                side="left", fill="x", expand=True, padx=(10,0))

        def card():
            o = tk.Frame(frm, bg=S1,
                         highlightthickness=1,
                         highlightbackground=BORD)
            o.pack(fill="x", padx=16, pady=(0,10))
            return tk.Frame(o, bg=S1)

        gap(12)

        # ── Coordonate ────────────────────────────────────────
        sec("🎯", "Coordonate Pixel")
        c1 = card(); c1.pack(fill="both", padx=14, pady=12)
        xy = tk.Frame(c1, bg=S1); xy.pack(fill="x", pady=(0,8))
        self.xf = Field(xy, "X  (pixeli)", "0", 8)
        self.xf.pack(side="left", padx=(0,14))
        self.yf = Field(xy, "Y  (pixeli)", "0", 8)
        self.yf.pack(side="left")
        self._coord_lbl = tk.Label(c1, text="Nicio coordonata capturata.",
            fg=TEXT3, bg=S1, font=(FN,8))
        self._coord_lbl.pack(anchor="w", pady=(0,8))
        self._cap_btn = mk_btn(c1,
            "🖱   Captureaza Pozitie  ( 3s countdown )",
            self._start_cap, bg=ORG, abg=ORG2)
        self._cap_btn.pack(fill="x", ipady=8)

        # ── Culoare ───────────────────────────────────────────
        sec("🎨", "Culoare Tinta")
        c2 = card(); c2.pack(fill="both", padx=14, pady=12)
        rgb = tk.Frame(c2, bg=S1); rgb.pack(fill="x", pady=(0,8))
        self.rf = Field(rgb, "R", "255", 5); self.rf.pack(side="left", padx=(0,8))
        self.gf = Field(rgb, "G", "0",   5); self.gf.pack(side="left", padx=(0,8))
        self.bf = Field(rgb, "B", "0",   5); self.bf.pack(side="left", padx=(0,12))
        self._sw = Swatch(rgb, 38); self._sw.pack(side="left")
        self._color_lbl = tk.Label(c2, text="Nicio culoare capturata.",
            fg=TEXT3, bg=S1, font=(FN,8))
        self._color_lbl.pack(anchor="w", pady=(0,8))
        self._sample_btn = mk_btn(c2,
            "🎨   Sample Culoare la Pixel",
            self._sample, bg=ORG, abg=ORG2)
        self._sample_btn.pack(fill="x", ipady=8)

        # ── Setari ────────────────────────────────────────────
        sec("⚙️", "Setari Detectie")
        c3 = card(); c3.pack(fill="both", padx=14, pady=12)
        r1 = tk.Frame(c3, bg=S1); r1.pack(fill="x", pady=(0,10))
        self.tolf = Field(r1, "Toleranta  ±",       "15",  7)
        self.tolf.pack(side="left", padx=(0,16))
        self.dlf  = Field(r1, "Delay reactie  (s)", "0.1", 7)
        self.dlf.pack(side="left")
        self.cdf  = Field(c3, "Cooldown dupa aruncare  (s)", "3.0", 7)
        self.cdf.pack(anchor="w")

        # ── Timeout Recalibrare ───────────────────────────────
        sec("🔄", "Timeout Recalibrare")
        c4 = card(); c4.pack(fill="both", padx=14, pady=12)

        tr = tk.Frame(c4, bg=S1); tr.pack(fill="x", pady=(0,8))
        self._timeout_tog = Toggle(tr, cb=self._on_timeout_toggle)
        self._timeout_tog.pack(side="left", padx=(0,14))
        tk.Label(tr, text="Recalibrare automata",
                 fg=TEXT, bg=S1,
                 font=(FN,10,"bold")).pack(side="left")

        self.timeout_f = Field(c4,
            "Daca nu vede culoarea in X secunde → retrage si re-arunca",
            "15", 6)
        self.timeout_f.pack(anchor="w")

        self._timeout_lbl = tk.Label(c4,
            text="Status: Dezactivat",
            fg=TEXT3, bg=S1, font=(FN,8))
        self._timeout_lbl.pack(anchor="w", pady=(6,0))

        # ── Mod Natural ───────────────────────────────────────
        sec("🎲", "Mod Natural")
        c5 = card(); c5.pack(fill="both", padx=14, pady=12)
        nat = tk.Frame(c5, bg=S1); nat.pack(fill="x")
        ntxt = tk.Frame(nat, bg=S1); ntxt.pack(side="left", fill="x", expand=True)
        tk.Label(ntxt, text="8% sansa sa sara o detectie",
                 fg=TEXT, bg=S1,
                 font=(FN,10,"bold")).pack(anchor="w")
        tk.Label(ntxt, text="Ignora ~1 din 12 detectii intentionat — apare mai uman.",
                 fg=TEXT2, bg=S1, font=(FN,8)).pack(anchor="w", pady=(3,0))
        self._tog = Toggle(nat, cb=self._on_nat)
        self._tog.pack(side="right", padx=(14,0))
        self._nat_lbl = tk.Label(c5, text="Status: Dezactivat",
                                  fg=TEXT3, bg=S1, font=(FN,8))
        self._nat_lbl.pack(anchor="w", pady=(8,0))

        # ── Control ───────────────────────────────────────────
        sec("▶", "Control Macro")
        c6 = card(); c6.pack(fill="both", padx=14, pady=12)
        br = tk.Frame(c6, bg=S1); br.pack(fill="x")
        self._startbtn = mk_btn(br, "▶   START MACRO",
            self._start, bg=ORG, abg=ORG2, fsize=10)
        self._startbtn.pack(side="left", fill="x",
                            expand=True, ipady=12, padx=(0,8))
        self._stopbtn = mk_btn(br, "■   STOP",
            self._stop, bg=REDDK, fg=RED,
            abg="#5C1111", state="disabled", fsize=10)
        self._stopbtn.pack(side="left", fill="x", expand=True, ipady=12)

        # ── Log ───────────────────────────────────────────────
        sec("📋", "Log Activitate")
        c7 = card()
        sr = tk.Frame(c7, bg=S1); sr.pack(fill="x", padx=14, pady=(10,6))
        self._st_lbl = tk.Label(sr, text="State: IDLE",
                                fg=TEXT3, bg=S1, font=(FN,9,"bold"))
        self._st_lbl.pack(side="left")
        self._recal_lbl = tk.Label(sr, text="Recalibrari: 0",
                                   fg=PURP, bg=S1, font=(FN,9,"bold"))
        self._recal_lbl.pack(side="right")
        self._log_w = tk.Text(c7, bg=S2, fg=TEXT2,
            font=("Consolas",8), relief="flat",
            state="disabled", wrap="word",
            bd=6, height=9, selectbackground=S3)
        self._log_w.pack(fill="both", padx=14, pady=(0,14))
        for tag, col in [("ok",GRN),("warn",YEL),("err",RED),
                         ("dim",TEXT3),("hi",ORG2),("pur",PURP),("bl",BLUE)]:
            self._log_w.tag_config(tag, foreground=col)

        gap(12)

        self._log("GamerMacro Pro v5.0 ready.", "hi")
        self._log("Nou: Timeout recalibrare + statistici detaliate!", "bl")
        self._log("Seteaza coordonatele si culoarea, apoi apasa START.", "dim")

    # ─────────────────────────────────────────────────────────
    #  TAB 2 — STATISTICI
    # ─────────────────────────────────────────────────────────
    def _build_stats_tab(self):
        P = self._tab_stats
        cv = tk.Canvas(P, bg=BG, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(P, orient="vertical", command=cv.yview,
                          bg=S2, troughcolor=BG, activebackground=ORG)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        cv.configure(yscrollcommand=sb.set)
        frm = tk.Frame(cv, bg=BG)
        wid = cv.create_window((0,0), window=frm, anchor="nw")
        frm.bind("<Configure>",
            lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",
            lambda e: cv.itemconfig(wid, width=e.width))

        def gap(n=8):
            tk.Frame(frm, bg=BG, height=n).pack(fill="x")

        def sec(icon, title):
            f = tk.Frame(frm, bg=BG)
            f.pack(fill="x", padx=16, pady=(12,5))
            tk.Label(f, text=icon, fg=ORG2, bg=BG,
                     font=(FN,10)).pack(side="left", padx=(0,6))
            tk.Label(f, text=title, fg=TEXT, bg=BG,
                     font=(FN,10,"bold")).pack(side="left")
            tk.Frame(f, bg=BORD2, height=1).pack(
                side="left", fill="x", expand=True, padx=(10,0))

        def card():
            o = tk.Frame(frm, bg=S1,
                         highlightthickness=1,
                         highlightbackground=BORD)
            o.pack(fill="x", padx=16, pady=(0,10))
            return tk.Frame(o, bg=S1)

        gap(12)

        # ── Sesiune curenta ───────────────────────────────────
        sec("⏱", "Sesiune Curenta")
        c1 = card(); c1.pack(fill="both", padx=14, pady=14)

        def stat_row(parent, label, var_name, color=TEXT):
            f = tk.Frame(parent, bg=S1)
            f.pack(fill="x", pady=3)
            tk.Label(f, text=label, fg=TEXT2, bg=S1,
                     font=(FN,9)).pack(side="left")
            lbl = tk.Label(f, text="—", fg=color, bg=S1,
                           font=(FN,9,"bold"))
            lbl.pack(side="right")
            setattr(self, var_name, lbl)
            return lbl

        stat_row(c1, "Timp sesiune:", "_s_time", ORG2)
        stat_row(c1, "Total catches:", "_s_total", GRN)
        stat_row(c1, "Recalibrari:", "_s_recal", PURP)

        tk.Frame(c1, bg=BORD, height=1).pack(fill="x", pady=8)

        # ── Rate ─────────────────────────────────────────────
        sec("📈", "Rate Pescuit")
        c2 = card()
        rg = tk.Frame(c2, bg=S1)
        rg.pack(fill="x", padx=14, pady=14)

        def rate_card(parent, label, var_name, color=ORG2):
            f = tk.Frame(parent, bg=S2,
                         highlightthickness=1,
                         highlightbackground=BORD)
            f.pack(side="left", fill="both", expand=True, padx=(0,6))
            tk.Label(f, text=label, fg=TEXT3, bg=S2,
                     font=(FN,7,"bold")).pack(pady=(8,2))
            lbl = tk.Label(f, text="—", fg=color, bg=S2,
                           font=(FN,16,"bold"))
            lbl.pack()
            tk.Label(f, text="catches", fg=TEXT3, bg=S2,
                     font=(FN,7)).pack(pady=(0,8))
            setattr(self, var_name, lbl)

        rate_card(rg, "PE MINUT", "_r_min")
        rate_card(rg, "30 MINUTE", "_r_30m", BLUE)
        rate_card(rg, "1 ORA", "_r_1h", GRN)

        # ── Proiectii ─────────────────────────────────────────
        sec("🔮", "Proiectii (bazat pe rate curenta)")
        c3 = card(); c3.pack(fill="both", padx=14, pady=14)

        stat_row(c3, "In 30 minute:", "_p_30m", YEL)
        stat_row(c3, "In 1 ora:", "_p_1h", YEL)
        stat_row(c3, "In 8 ore (sesiune):", "_p_8h", YEL)
        stat_row(c3, "In 24 ore:", "_p_24h", YEL)

        tk.Frame(c3, bg=BORD, height=1).pack(fill="x", pady=8)

        stat_row(c3, "Timp mediu intre catches:", "_avg_time", TEXT2)
        stat_row(c3, "Recalibrari pe ora:", "_recal_rate", PURP)

        # ── Grafic text ────────────────────────────────────────
        sec("📉", "Catches per Minut (ultimele 10 min)")
        c4 = card()
        self._graph_lbl = tk.Label(c4, text="Nu exista date inca.",
            fg=TEXT3, bg=S1, font=("Consolas",8),
            justify="left")
        self._graph_lbl.pack(anchor="w", padx=14, pady=12)

        gap(12)

    # ─────────────────────────────────────────────────────────
    #  TAB 3 — SKYBLOCK PROFILE
    # ─────────────────────────────────────────────────────────
    def _build_skyblock_tab(self):
        P = self._tab_skyblock
        cv = tk.Canvas(P, bg=BG, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(P, orient="vertical", command=cv.yview,
                          bg=S2, troughcolor=BG, activebackground=ORG)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        cv.configure(yscrollcommand=sb.set)
        frm = tk.Frame(cv, bg=BG)
        wid = cv.create_window((0,0), window=frm, anchor="nw")
        frm.bind("<Configure>",
            lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",
            lambda e: cv.itemconfig(wid, width=e.width))

        def gap(n=8):
            tk.Frame(frm, bg=BG, height=n).pack(fill="x")

        def sec(icon, title):
            f = tk.Frame(frm, bg=BG)
            f.pack(fill="x", padx=16, pady=(12,5))
            tk.Label(f, text=icon, fg=ORG2, bg=BG,
                     font=(FN,10)).pack(side="left", padx=(0,6))
            tk.Label(f, text=title, fg=TEXT, bg=BG,
                     font=(FN,10,"bold")).pack(side="left")
            tk.Frame(f, bg=BORD2, height=1).pack(
                side="left", fill="x", expand=True, padx=(10,0))

        def card():
            o = tk.Frame(frm, bg=S1,
                         highlightthickness=1,
                         highlightbackground=BORD)
            o.pack(fill="x", padx=16, pady=(0,10))
            return tk.Frame(o, bg=S1)

        gap(12)

        # ── Profil Fishing ────────────────────────────────────
        sec("🎣", "Profil Fishing")
        c1 = card(); c1.pack(fill="both", padx=14, pady=12)

        r1 = tk.Frame(c1, bg=S1); r1.pack(fill="x", pady=(0,10))
        tk.Label(r1, text="Nivel Fishing:", fg=TEXT2, bg=S1,
                 font=(FN,9)).pack(side="left", padx=(0,8))
        self._fishing_lvl = tk.IntVar(value=1)
        lvl_spin = tk.Spinbox(r1, from_=1, to=60,
                              textvariable=self._fishing_lvl,
                              width=5, bg=S2, fg=TEXT,
                              buttonbackground=S3,
                              relief="flat", bd=0,
                              font=("Consolas",10),
                              highlightthickness=1,
                              highlightbackground=BORD,
                              command=self._update_skyblock)
        lvl_spin.pack(side="left")
        self._fishing_xp_lbl = tk.Label(r1,
            text="XP pana la urmatorul nivel: —",
            fg=TEXT3, bg=S1, font=(FN,8))
        self._fishing_xp_lbl.pack(side="left", padx=(12,0))

        r2 = tk.Frame(c1, bg=S1); r2.pack(fill="x", pady=(0,10))
        tk.Label(r2, text="Undita:", fg=TEXT2, bg=S1,
                 font=(FN,9)).pack(side="left", padx=(0,8))
        self._rod_var = tk.StringVar(value=FISHING_RODS[0])
        rod_cb = styled_dropdown(r2, self._rod_var, FISHING_RODS, 25)
        rod_cb.pack(side="left")
        rod_cb.bind("<<ComboboxSelected>>",
                    lambda _: self._update_skyblock())

        r3 = tk.Frame(c1, bg=S1); r3.pack(fill="x", pady=(0,10))
        tk.Label(r3, text="Momeala:", fg=TEXT2, bg=S1,
                 font=(FN,9)).pack(side="left", padx=(0,8))
        self._bait_var = tk.StringVar(value=BAITS[0])
        bait_cb = styled_dropdown(r3, self._bait_var, BAITS, 20)
        bait_cb.pack(side="left")
        bait_cb.bind("<<ComboboxSelected>>",
                     lambda _: self._update_skyblock())

        r4 = tk.Frame(c1, bg=S1); r4.pack(fill="x")
        tk.Label(r4, text="Locatie:", fg=TEXT2, bg=S1,
                 font=(FN,9)).pack(side="left", padx=(0,8))
        self._loc_var = tk.StringVar(value=LOCATIONS[0])
        loc_cb = styled_dropdown(r4, self._loc_var, LOCATIONS, 22)
        loc_cb.pack(side="left")
        loc_cb.bind("<<ComboboxSelected>>",
                    lambda _: self._update_skyblock())

        # ── Sea Creature Chance ────────────────────────────────
        sec("🌊", "Sea Creature Chance")
        c2 = card(); c2.pack(fill="both", padx=14, pady=12)

        # Bonus-uri extra
        b1 = tk.Frame(c2, bg=S1); b1.pack(fill="x", pady=(0,8))
        tk.Label(b1, text="Pet Perk bonus %:", fg=TEXT2, bg=S1,
                 font=(FN,9)).pack(side="left", padx=(0,8))
        self.pet_bonus = Field(b1, "", "0", 5)
        self.pet_bonus.pack(side="left")
        tk.Label(b1, text="Rod bonus %:", fg=TEXT2, bg=S1,
                 font=(FN,9)).pack(side="left", padx=(16,8))
        self.rod_bonus = Field(b1, "", "0", 5)
        self.rod_bonus.pack(side="left")

        mk_btn(c2, "🔄  Calculeaza",
            self._update_skyblock, bg=ORG, abg=ORG2,
            fsize=9).pack(anchor="w", pady=(0,8), ipady=6, ipadx=10)

        self._scc_lbl = tk.Label(c2,
            text="Sea Creature Chance: —",
            fg=GRN, bg=S1, font=(FN,14,"bold"))
        self._scc_lbl.pack(anchor="w")
        self._scc_detail = tk.Label(c2, text="",
            fg=TEXT2, bg=S1, font=(FN,8))
        self._scc_detail.pack(anchor="w", pady=(4,0))

        # ── Creaturi disponibile ──────────────────────────────
        sec("👾", "Creaturi Disponibile la Nivelul Tau")
        c3 = card()
        self._creatures_txt = tk.Text(c3, bg=S1, fg=TEXT2,
            font=(FN,9), relief="flat", state="disabled",
            wrap="word", bd=8, height=8)
        self._creatures_txt.pack(fill="both", padx=6, pady=6)
        self._creatures_txt.tag_config("name", foreground=ORG2, font=(FN,9,"bold"))
        self._creatures_txt.tag_config("info", foreground=TEXT3)

        # ── Tips ─────────────────────────────────────────────
        sec("💡", "Tips Hypixel Skyblock Fishing")
        c4 = card()
        tips = [
            ("🎣", "Foloseste Blessed Bait sau Grand Bait pentru +25% SCC"),
            ("⚡", "Dolphin Pet creste SCC cu pana la 30%"),
            ("🌊", "Fishing Minion cu enchant-uri maximizeaza profitul"),
            ("💎", "Siren Hat + Fishing Suit = max Fishing Fortune"),
            ("🐟", "Jerry's Workshop in timpul evenimentelor = rare drops"),
            ("📈", "Nivel Fishing 24+ deblocheaza Sea Emperor"),
            ("🎯", "Toleranta +/- 15 e optima pentru detectie bobber"),
            ("⏱", "Delay 0.1s simuleaza timp uman de reactie"),
        ]
        for icon, tip in tips:
            f = tk.Frame(c4, bg=S1)
            f.pack(fill="x", padx=14, pady=3)
            tk.Label(f, text=icon, fg=ORG2, bg=S1,
                     font=(FN,10)).pack(side="left", padx=(0,6))
            tk.Label(f, text=tip, fg=TEXT2, bg=S1,
                     font=(FN,8), wraplength=400,
                     justify="left").pack(side="left", anchor="w")
        tk.Frame(c4, bg=S1, height=10).pack(fill="x")

        gap(12)
        self._update_skyblock()

    # ─────────────────────────────────────────────────────────
    #  LOGICA
    # ─────────────────────────────────────────────────────────
    def _on_timeout_toggle(self, state):
        if state:
            self._timeout_lbl.config(
                text="Activat — recalibreaza daca nu vede culoarea in X secunde",
                fg=PURP)
            self._log("Timeout recalibrare ACTIVAT.", "pur")
        else:
            self._timeout_lbl.config(text="Status: Dezactivat", fg=TEXT3)
            self._log("Timeout recalibrare dezactivat.", "dim")

    def _on_nat(self, state):
        self._natural = state
        if state:
            self._nat_lbl.config(
                text="Status: Activat  —  8% skip per detectie", fg=ORG2)
            self._log("Mod Natural ACTIVAT.", "pur")
        else:
            self._nat_lbl.config(text="Status: Dezactivat", fg=TEXT3)
            self._log("Mod Natural dezactivat.", "dim")

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
                self._log(f"Coordonate → X={x}  Y={y}", "ok")
            except Exception as e:
                self._coord_lbl.config(text=f"Eroare: {e}", fg=RED)
            finally:
                self._cap_btn.config(state="normal")

    def _sample(self):
        try:
            x = int(self.xf.var.get()); y = int(self.yf.var.get())
            p = pyautogui.pixel(x, y)
            r, g, b = p[0], p[1], p[2]
            self.rf.var.set(str(r)); self.gf.var.set(str(g))
            self.bf.var.set(str(b))
            self._sw.set_color(r, g, b)
            hx = f"#{r:02x}{g:02x}{b:02x}"
            self._color_lbl.config(text=f"✓  RGB({r},{g},{b})  {hx}", fg=GRN)
            self._log(f"Culoare → RGB({r},{g},{b})  {hx}", "ok")
        except Exception as e:
            self._color_lbl.config(text=f"Eroare: {e}", fg=RED)
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
        use_timeout = self._timeout_tog.get()
        timeout_sec = float(self.timeout_f.var.get()) if use_timeout else 0
        sc  = pyautogui.size()
        if not (0 <= x < sc.width and 0 <= y < sc.height):
            raise ValueError(f"Coordonate ({x},{y}) in afara ecranului.")
        return x, y, r, g, b, tol, dl, cd, use_timeout, timeout_sec

    # ── Macro loop ────────────────────────────────────────────
    def _watch(self, x, y, tr, tg, tb, tol, delay, cd,
               use_timeout, timeout_sec, nat):
        self._upst("RESET")
        state    = "RESET"
        skip     = 0
        watch_since = None   # cand am intrat in WATCH

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

                    # ── TIMEOUT RECALIBRARE ───────────────────
                    if (use_timeout and timeout_sec > 0 and
                            watch_since is not None and
                            time.time() - watch_since > timeout_sec):
                        self._recals += 1
                        nr = self._recals
                        self.root.after(0, self._log,
                            f"[RECAL #{nr}] Timeout {timeout_sec}s — retrag si re-arunc!", "pur")
                        self.root.after(0, self._recal_lbl.config,
                            {"text": f"Recalibrari: {nr}"})

                        right_click()        # Trage undita
                        time.sleep(0.5)
                        right_click()        # Re-arunca
                        time.sleep(cd)       # Asteapta sa se aseze

                        state = "RESET"
                        watch_since = None
                        self._upst("RESET")
                        self.root.after(0, self._log,
                            f"[RECAL #{nr}] Re-aruncat. Reiau monitorizarea.", "dim")
                        continue

                    # ── DETECTIE NORMALA ──────────────────────
                    if hit:
                        if nat and random.random() < 0.08:
                            skip += 1
                            self.root.after(0, self._log,
                                f"[skip #{skip}] Mod natural — ignorat.", "pur")
                            state = "RESET"; watch_since = None
                            self._upst("RESET")
                            time.sleep(self.POLL); continue

                        self._catches += 1
                        self._session_catches.append(time.time())
                        n = self._catches
                        self.root.after(0, self._log,
                            f"[#{n}] Bobber!  RGB({cr},{cg},{cb})  delay {delay}s…",
                            "warn")
                        self.root.after(0, self._catch_lbl.config,
                            {"text": f"Catches: {n}"})

                        if delay > 0: time.sleep(delay)
                        if not self._running: break

                        right_click()
                        time.sleep(0.5)
                        right_click()

                        self.root.after(0, self._log,
                            f"[#{n}] Re-aruncat! Cooldown {cd}s…", "ok")
                        time.sleep(cd)
                        state = "RESET"; watch_since = None
                        self._upst("RESET")

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
            {"text": f"State: {s}", "fg": cols.get(s, TEXT3)})

    def _start(self):
        if self._running: return
        try: args = self._parse()
        except ValueError as e:
            self._log(f"Input invalid: {e}", "err"); return

        self._running  = True
        self._catches  = 0
        self._recals   = 0
        self._start_ts = time.time()
        self._session_catches.clear()
        self._catch_lbl.config(text="Catches: 0")
        self._recal_lbl.config(text="Recalibrari: 0")
        self._ui(True)

        x,y,r,g,b,tol,delay,cd,use_to,to_sec = args
        nat = self._natural
        self._log(
            f"START  ({x},{y})  RGB({r},{g},{b})  ±{tol}  "
            f"delay={delay}s  cd={cd}s  "
            f"timeout={'ON '+str(to_sec)+'s' if use_to else 'OFF'}  "
            f"nat={'ON' if nat else 'OFF'}", "hi")

        self._thread = threading.Thread(
            target=self._watch,
            args=(x,y,r,g,b,tol,delay,cd,use_to,to_sec,nat),
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

    # ── Update statistici (la fiecare 5s) ────────────────────
    def _update_stats_job(self):
        self._compute_stats()
        self.root.after(5000, self._update_stats_job)

    def _compute_stats(self):
        now = time.time()
        catches = self._session_catches
        total   = len(catches)
        elapsed = (now - self._start_ts) if self._start_ts else 0

        # Timp sesiune
        if self._start_ts and self._running:
            h = int(elapsed // 3600)
            m = int((elapsed % 3600) // 60)
            s = int(elapsed % 60)
            self._s_time.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        else:
            self._s_time.config(text="—")

        self._s_total.config(text=str(total))
        self._s_recal.config(text=str(self._recals))

        # Rate per minut
        if elapsed > 0:
            rate_min = total / (elapsed / 60)
        else:
            rate_min = 0

        # Rate din ultimul minut
        last_min = [t for t in catches if now - t <= 60]
        last_min_rate = len(last_min)

        self._r_min.config(text=f"{last_min_rate}")
        self._r_30m.config(text=f"{rate_min * 30:.1f}")
        self._r_1h.config(text=f"{rate_min * 60:.1f}")

        # Proiectii
        self._p_30m.config(text=f"{rate_min * 30:.0f} catches")
        self._p_1h.config(text=f"{rate_min * 60:.0f} catches")
        self._p_8h.config(text=f"{rate_min * 480:.0f} catches")
        self._p_24h.config(text=f"{rate_min * 1440:.0f} catches")

        # Timp mediu
        if total >= 2:
            diffs = [catches[i]-catches[i-1] for i in range(1, len(catches))]
            avg = sum(diffs)/len(diffs)
            self._avg_time.config(text=f"{avg:.1f}s")
        else:
            self._avg_time.config(text="—")

        # Recalibrari pe ora
        if elapsed > 60:
            self._recal_rate.config(
                text=f"{self._recals / (elapsed/3600):.1f}/ora")
        else:
            self._recal_rate.config(text="—")

        # Grafic per minut (ultimele 10 minute)
        self._update_graph(catches, now)

    def _update_graph(self, catches, now):
        bars = []
        max_val = 1
        for i in range(10, 0, -1):
            start = now - i * 60
            end   = now - (i-1) * 60
            cnt   = len([t for t in catches if start <= t < end])
            bars.append((f"-{i}m", cnt))
            max_val = max(max_val, cnt)

        lines = []
        bar_h = 6
        for label, val in bars:
            filled = int((val / max_val) * 20) if max_val > 0 else 0
            bar = "█" * filled + "░" * (20 - filled)
            lines.append(f"{label:>4}  {bar}  {val}")

        self._graph_lbl.config(
            text="\n".join(lines) if any(v for _, v in bars)
                 else "Nu exista date inca.")

    # ── Update Skyblock ───────────────────────────────────────
    def _update_skyblock(self):
        lvl = self._fishing_lvl.get()
        bait = self._bait_var.get()
        loc  = self._loc_var.get()

        # XP
        xp_next = xp_to_next(lvl)
        self._fishing_xp_lbl.config(
            text=f"XP pana la nivelul {lvl+1}: {xp_next}")

        # SCC
        try:
            pet_b = float(self.pet_bonus.var.get() or 0)
            rod_b = float(self.rod_bonus.var.get() or 0)
        except:
            pet_b = rod_b = 0
        bait_b = BAIT_BONUS.get(bait, 0)
        scc = get_sea_creature_chance(lvl, pet_b, rod_b, bait_b)
        self._scc_lbl.config(text=f"Sea Creature Chance: {scc:.1f}%")
        self._scc_detail.config(
            text=f"Baza: {20 + lvl*0.2:.1f}%  |  "
                 f"Pet: +{pet_b}%  |  Rod: +{rod_b}%  |  "
                 f"Bait ({bait}): +{bait_b}%")

        # Creaturi
        creatures = get_available_creatures(lvl, loc)
        self._creatures_txt.config(state="normal")
        self._creatures_txt.delete("1.0", "end")
        self._creatures_txt.insert("end",
            f"La nivel Fishing {lvl} in {loc}:\n\n", "info")
        for i, c in enumerate(creatures, 1):
            self._creatures_txt.insert("end", f"  {i:2}. ", "info")
            self._creatures_txt.insert("end", c + "\n", "name")
        if not creatures:
            self._creatures_txt.insert("end",
                "Nicio creatura disponibila.", "info")
        self._creatures_txt.config(state="disabled")

    # ── Log ───────────────────────────────────────────────────
    def _log(self, msg, tag="dim"):
        if self._log_w is None: return
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
