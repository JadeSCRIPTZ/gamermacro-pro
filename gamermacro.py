"""
GamerMacro Pro — Fishing Edition
Design: Cyberpunk HUD aesthetic — neon on deep black, scanline feel
"""
import tkinter as tk
from tkinter import font as tkfont
import threading, time, random, sys, math

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE    = 0
except ImportError:
    print("Run: pip install pyautogui pillow"); sys.exit(1)

# ── Palette ────────────────────────────────────────────────────────────────────
C = {
    "bg":        "#070B14",
    "bg2":       "#0D1220",
    "bg3":       "#111827",
    "panel":     "#0A0F1E",
    "border":    "#1E2D4A",
    "border2":   "#2A3F66",
    "accent":    "#00D4FF",
    "accent2":   "#0099CC",
    "accent_dim":"#003D52",
    "green":     "#00FF88",
    "green2":    "#00CC6A",
    "green_dim": "#003D22",
    "red":       "#FF2D55",
    "red2":      "#CC1F40",
    "red_dim":   "#3D0011",
    "yellow":    "#FFD60A",
    "purple":    "#BF5AF2",
    "text":      "#E8F4FD",
    "text2":     "#8BAFD4",
    "text3":     "#4A6080",
}

FONT_TITLE  = ("Consolas", 18, "bold")
FONT_HEAD   = ("Consolas", 9,  "bold")
FONT_BODY   = ("Consolas", 10)
FONT_SMALL  = ("Consolas", 8)
FONT_BIG    = ("Consolas", 22, "bold")
FONT_BTN    = ("Consolas", 10, "bold")


# ── Custom Widgets ─────────────────────────────────────────────────────────────
class NeonButton(tk.Canvas):
    """Button with neon glow border and hover effect."""
    def __init__(self, master, text, cmd, color=C["accent"],
                 w=180, h=40, enabled=True, **kw):
        super().__init__(master, width=w, height=h,
                         bg=C["panel"], bd=0, highlightthickness=0, **kw)
        self._text    = text
        self._cmd     = cmd
        self._color   = color
        self._w, self._h = w, h
        self._enabled = enabled
        self._hover   = False

        # Pre-create items — never delete/recreate (avoids TclError crash)
        self._border = self.create_rectangle(1, 1, w-2, h-2,
            outline=color, width=1, fill=C["bg3"])
        self._glow   = self.create_rectangle(3, 3, w-4, h-4,
            outline="", fill="")
        self._label  = self.create_text(w//2, h//2, text=text,
            fill=color, font=FONT_BTN)

        if enabled:
            self.bind("<Enter>",    self._on_enter)
            self.bind("<Leave>",    self._on_leave)
            self.bind("<Button-1>", self._on_click)

        if not enabled:
            self._dim()

    def _on_enter(self, _=None):
        if not self._enabled: return
        self._hover = True
        self.itemconfig(self._border, fill=self._color + "22",
                        outline=self._color, width=2)
        self.itemconfig(self._label, fill="#FFFFFF")

    def _on_leave(self, _=None):
        if not self._enabled: return
        self._hover = False
        self.itemconfig(self._border, fill=C["bg3"],
                        outline=self._color, width=1)
        self.itemconfig(self._label, fill=self._color)

    def _on_click(self, _=None):
        if self._enabled and self._cmd:
            self._cmd()

    def _dim(self):
        self.itemconfig(self._border, fill=C["bg3"],
                        outline=C["border"], width=1)
        self.itemconfig(self._label, fill=C["text3"])

    def set_enabled(self, state: bool):
        self._enabled = state
        if state:
            self._on_leave()
            self.bind("<Enter>",    self._on_enter)
            self.bind("<Leave>",    self._on_leave)
            self.bind("<Button-1>", self._on_click)
        else:
            self.unbind("<Enter>")
            self.unbind("<Leave>")
            self.unbind("<Button-1>")
            self._dim()

    def set_color(self, color):
        self._color = color
        self._on_leave()


class ToggleSwitch(tk.Canvas):
    """Animated ON/OFF toggle switch."""
    def __init__(self, master, on_toggle=None, **kw):
        super().__init__(master, width=56, height=26,
                         bg=C["panel"], bd=0, highlightthickness=0, **kw)
        self._on       = False
        self._callback = on_toggle
        self._track = self.create_rounded_rect(2, 4, 54, 22, 9,
                                               fill=C["bg3"], outline=C["border2"])
        self._knob  = self.create_oval(5, 6, 21, 20, fill=C["text3"], outline="")
        self.bind("<Button-1>", self._toggle)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
               x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
               x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        return self.create_polygon(pts, smooth=True, **kw)

    def _toggle(self, _=None):
        self._on = not self._on
        if self._on:
            self.itemconfig(self._track, fill=C["purple"]+"44",
                            outline=C["purple"])
            self.coords(self._knob, 35, 6, 51, 20)
            self.itemconfig(self._knob, fill=C["purple"])
        else:
            self.itemconfig(self._track, fill=C["bg3"],
                            outline=C["border2"])
            self.coords(self._knob, 5, 6, 21, 20)
            self.itemconfig(self._knob, fill=C["text3"])
        if self._callback:
            self._callback(self._on)

    def get(self): return self._on


class GlowLabel(tk.Label):
    """Label with colored text."""
    def __init__(self, parent, text="", color=C["text"], size=10,
                 bold=False, **kw):
        st = "bold" if bold else "normal"
        super().__init__(parent, text=text, fg=color, bg=C["panel"],
                         font=("Consolas", size, st), **kw)


class SectionHeader(tk.Frame):
    """Section header with accent line."""
    def __init__(self, parent, title, icon=""):
        super().__init__(parent, bg=C["panel"])
        tk.Label(self, text=f"{icon}  {title}" if icon else title,
                 fg=C["accent"], bg=C["panel"],
                 font=("Consolas", 9, "bold")).pack(side="left")
        tk.Frame(self, bg=C["border2"], height=1).pack(
            side="left", fill="x", expand=True, padx=(10, 0))


class InputField(tk.Frame):
    """Styled input with label."""
    def __init__(self, parent, label, default="0", width=7,
                 num_only=True):
        super().__init__(parent, bg=C["panel"])
        tk.Label(self, text=label, fg=C["text2"], bg=C["panel"],
                 font=FONT_SMALL).pack(anchor="w", pady=(0, 2))
        self.var = tk.StringVar(value=str(default))
        vcmd = (self.register(lambda v: v.replace(".", "", 1).isdigit()
                              or v == ""), "%P") if num_only else None
        e = tk.Entry(self, textvariable=self.var, width=width,
                     bg=C["bg2"], fg=C["text"],
                     insertbackground=C["accent"],
                     relief="flat", bd=0,
                     font=("Consolas", 11),
                     justify="center",
                     highlightthickness=1,
                     highlightcolor=C["accent"],
                     highlightbackground=C["border"])
        if vcmd:
            e.config(validate="key", validatecommand=vcmd)
        e.pack(ipady=5, ipadx=4)


class ColorSwatch(tk.Canvas):
    """Live color preview square."""
    def __init__(self, parent, size=34):
        super().__init__(parent, width=size, height=size,
                         bg=C["panel"], bd=0,
                         highlightthickness=1,
                         highlightbackground=C["border2"])
        self._s = size
        self._rect = self.create_rectangle(0, 0, size, size,
                                           fill="#111111", outline="")

    def set(self, r, g, b):
        self.itemconfig(self._rect,
                        fill=f"#{r:02x}{g:02x}{b:02x}")


class StatusOrb(tk.Canvas):
    """Animated pulsing status orb."""
    def __init__(self, parent, size=14):
        super().__init__(parent, width=size+4, height=size+4,
                         bg=C["panel"], bd=0, highlightthickness=0)
        self._s   = size
        self._on  = False
        self._anim = None
        self._outer = self.create_oval(0, 0, size+4, size+4,
                                       fill="", outline="")
        self._inner = self.create_oval(2, 2, size+2, size+2,
                                       fill=C["text3"], outline="")

    def set_active(self, active: bool):
        self._on = active
        if self._anim:
            self.after_cancel(self._anim)
        if active:
            self._pulse(0)
        else:
            self.itemconfig(self._outer, fill="", outline="")
            self.itemconfig(self._inner, fill=C["text3"])

    def _pulse(self, t):
        if not self._on: return
        brightness = 0.5 + 0.5 * math.sin(t * 0.15)
        g = int(200 + 55 * brightness)
        color = f"#00{g:02x}55"
        glow  = f"#00{int(g*0.3):02x}22"
        self.itemconfig(self._inner, fill=color)
        self.itemconfig(self._outer, fill=glow, outline="")
        self._anim = self.after(40, self._pulse, t + 1)


# ── Main Application ───────────────────────────────────────────────────────────
class FishBotApp:
    POLL = 0.05

    def __init__(self, root: tk.Tk):
        self.root      = root
        self._running  = False
        self._thread   = None
        self._natural  = False
        self._build_window()
        self._build_ui()

    # ── Window ─────────────────────────────────────────────────────────────────
    def _build_window(self):
        r = self.root
        r.title("GamerMacro Pro")
        r.configure(bg=C["bg"])
        r.resizable(False, False)
        r.attributes("-topmost", True)
        w, h = 460, 720
        sw, sh = r.winfo_screenwidth(), r.winfo_screenheight()
        r.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Full UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Top accent bar ─────────────────────────────────────
        bar = tk.Frame(self.root, bg=C["accent"], height=2)
        bar.pack(fill="x")

        # ── Header ─────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=C["bg"], padx=20, pady=14)
        hdr.pack(fill="x")

        left = tk.Frame(hdr, bg=C["bg"])
        left.pack(side="left")
        tk.Label(left, text="GAMERMACRO", fg=C["accent"],
                 bg=C["bg"], font=("Consolas", 20, "bold")).pack(anchor="w")
        tk.Label(left, text="FISHING EDITION  //  PIXEL WATCHER",
                 fg=C["text3"], bg=C["bg"],
                 font=("Consolas", 8)).pack(anchor="w")

        right = tk.Frame(hdr, bg=C["bg"])
        right.pack(side="right", anchor="n")
        status_row = tk.Frame(right, bg=C["bg"])
        status_row.pack()
        self.orb = StatusOrb(status_row, size=12)
        self.orb.pack(side="left", padx=(0, 6))
        self.status_lbl = tk.Label(status_row, text="IDLE",
                                   fg=C["text3"], bg=C["bg"],
                                   font=("Consolas", 9, "bold"))
        self.status_lbl.pack(side="left")

        # ── Separator ──────────────────────────────────────────
        tk.Frame(self.root, bg=C["border"], height=1).pack(fill="x")

        # ── Scrollable content ─────────────────────────────────
        self.canvas_wrap = tk.Canvas(self.root, bg=C["bg"],
                                     bd=0, highlightthickness=0)
        self.canvas_wrap.pack(fill="both", expand=True)
        self.content = tk.Frame(self.canvas_wrap, bg=C["bg"])
        self.canvas_wrap.create_window((0, 0), window=self.content,
                                       anchor="nw")
        self.content.bind("<Configure>",
            lambda e: self.canvas_wrap.configure(
                scrollregion=self.canvas_wrap.bbox("all")))

        P = self.content  # alias
        PAD = {"padx": 18, "pady": 0}

        def vpad(n=8):
            tk.Frame(P, bg=C["bg"], height=n).pack(fill="x")

        vpad(12)

        # ╔══════════════════════════════════════╗
        # ║  SECTION 1: PIXEL COORDINATES       ║
        # ╚══════════════════════════════════════╝
        self._section(P, "01", "COORDONATE PIXEL", "🎯")
        vpad(8)

        coord_card = self._card(P)

        # X / Y row
        xy_row = tk.Frame(coord_card, bg=C["panel"])
        xy_row.pack(fill="x", padx=14, pady=(12, 8))

        self.x_field = InputField(xy_row, "X  (pixeli)", "0", 8)
        self.x_field.pack(side="left", padx=(0, 12))
        self.y_field = InputField(xy_row, "Y  (pixeli)", "0", 8)
        self.y_field.pack(side="left")

        self.coord_status = tk.Label(coord_card,
            text="Nicio coordonata capturata.", fg=C["text3"],
            bg=C["panel"], font=FONT_SMALL)
        self.coord_status.pack(anchor="w", padx=14, pady=(0, 8))

        self.capture_btn = NeonButton(coord_card,
            "🖱   GET MOUSE POSITION  ( 3s )",
            self._start_capture,
            color=C["accent"], w=418, h=38)
        self.capture_btn.pack(padx=14, pady=(0, 12))

        vpad(10)

        # ╔══════════════════════════════════════╗
        # ║  SECTION 2: TARGET COLOUR           ║
        # ╚══════════════════════════════════════╝
        self._section(P, "02", "CULOARE TINTA", "🎨")
        vpad(8)

        color_card = self._card(P)

        rgb_row = tk.Frame(color_card, bg=C["panel"])
        rgb_row.pack(fill="x", padx=14, pady=(12, 8))

        self.r_field = InputField(rgb_row, "R", "255", 5)
        self.r_field.pack(side="left", padx=(0, 8))
        self.g_field = InputField(rgb_row, "G", "0", 5)
        self.g_field.pack(side="left", padx=(0, 8))
        self.b_field = InputField(rgb_row, "B", "0", 5)
        self.b_field.pack(side="left", padx=(0, 14))

        self.swatch = ColorSwatch(rgb_row, size=36)
        self.swatch.pack(side="left", padx=(0, 8))

        self.color_status = tk.Label(color_card,
            text="Nicio culoare capturata.", fg=C["text3"],
            bg=C["panel"], font=FONT_SMALL)
        self.color_status.pack(anchor="w", padx=14, pady=(0, 8))

        self.sample_btn = NeonButton(color_card,
            "🎨   SAMPLE COLOUR AT PIXEL",
            self._sample_color,
            color=C["accent"], w=418, h=38)
        self.sample_btn.pack(padx=14, pady=(0, 12))

        vpad(10)

        # ╔══════════════════════════════════════╗
        # ║  SECTION 3: DETECTION SETTINGS      ║
        # ╚══════════════════════════════════════╝
        self._section(P, "03", "SETARI DETECTIE", "⚙")
        vpad(8)

        settings_card = self._card(P)
        s_inner = tk.Frame(settings_card, bg=C["panel"])
        s_inner.pack(fill="x", padx=14, pady=12)

        row1 = tk.Frame(s_inner, bg=C["panel"])
        row1.pack(fill="x", pady=(0, 10))
        self.tol_field   = InputField(row1, "Toleranta  ±", "15", 7)
        self.tol_field.pack(side="left", padx=(0, 20))
        self.delay_field = InputField(row1, "Delay reactie  (s)", "0.1", 7)
        self.delay_field.pack(side="left")

        row2 = tk.Frame(s_inner, bg=C["panel"])
        row2.pack(fill="x")
        self.cd_field = InputField(row2, "Cooldown dupa actiune  (s)", "3.0", 7)
        self.cd_field.pack(side="left")

        vpad(10)

        # ╔══════════════════════════════════════╗
        # ║  SECTION 4: NATURAL MODE            ║
        # ╚══════════════════════════════════════╝
        self._section(P, "04", "MOD NATURAL", "🎲")
        vpad(8)

        nat_card = self._card(P)
        nat_inner = tk.Frame(nat_card, bg=C["panel"])
        nat_inner.pack(fill="x", padx=14, pady=14)

        nat_top = tk.Frame(nat_inner, bg=C["panel"])
        nat_top.pack(fill="x")

        nat_left = tk.Frame(nat_top, bg=C["panel"])
        nat_left.pack(side="left", expand=True, fill="x")
        tk.Label(nat_left, text="8% sansa sa sara o detectie",
                 fg=C["text"], bg=C["panel"],
                 font=("Consolas", 11, "bold")).pack(anchor="w")
        tk.Label(nat_left,
                 text="Activeaza pentru a parea mai uman — programul\n"
                      "ignora intentionat 1 din 12 detectii.",
                 fg=C["text2"], bg=C["panel"],
                 font=FONT_SMALL, justify="left").pack(anchor="w", pady=(3, 0))

        self.nat_toggle = ToggleSwitch(nat_top, on_toggle=self._toggle_natural)
        self.nat_toggle.pack(side="right", padx=(10, 0))

        self.nat_status = tk.Label(nat_inner,
            text="DEZACTIVAT", fg=C["text3"],
            bg=C["panel"], font=("Consolas", 8, "bold"))
        self.nat_status.pack(anchor="w", pady=(8, 0))

        vpad(10)

        # ╔══════════════════════════════════════╗
        # ║  SECTION 5: CONTROL BUTTONS         ║
        # ╚══════════════════════════════════════╝
        self._section(P, "05", "CONTROL", "▶")
        vpad(8)

        ctrl_card = self._card(P)
        btn_row = tk.Frame(ctrl_card, bg=C["panel"])
        btn_row.pack(padx=14, pady=14)

        self.start_btn = NeonButton(btn_row,
            "▶   START MACRO",
            self._start_macro,
            color=C["green"], w=200, h=46)
        self.start_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = NeonButton(btn_row,
            "■   STOP",
            self._stop_macro,
            color=C["red"], w=200, h=46,
            enabled=False)
        self.stop_btn.pack(side="left")

        vpad(10)

        # ╔══════════════════════════════════════╗
        # ║  SECTION 6: ACTIVITY LOG            ║
        # ╚══════════════════════════════════════╝
        self._section(P, "LOG", "ACTIVITATE", "📋")
        vpad(8)

        log_card = self._card(P)

        log_header = tk.Frame(log_card, bg=C["panel"])
        log_header.pack(fill="x", padx=14, pady=(10, 4))
        self.catch_lbl = tk.Label(log_header,
            text="CATCHES: 0", fg=C["yellow"],
            bg=C["panel"], font=("Consolas", 9, "bold"))
        self.catch_lbl.pack(side="left")
        self.state_lbl = tk.Label(log_header,
            text="STATE: IDLE", fg=C["text3"],
            bg=C["panel"], font=("Consolas", 9, "bold"))
        self.state_lbl.pack(side="right")

        self.log_box = tk.Text(log_card,
            bg=C["bg2"], fg=C["text2"],
            font=("Consolas", 8),
            relief="flat", state="disabled",
            wrap="word", bd=0, height=9,
            selectbackground=C["accent_dim"],
            insertbackground=C["accent"])
        self.log_box.pack(fill="both", padx=14, pady=(0, 14))

        # Log tags
        self.log_box.tag_config("ok",     foreground=C["green"])
        self.log_box.tag_config("warn",   foreground=C["yellow"])
        self.log_box.tag_config("error",  foreground=C["red"])
        self.log_box.tag_config("dim",    foreground=C["text3"])
        self.log_box.tag_config("accent", foreground=C["accent"])
        self.log_box.tag_config("purple", foreground=C["purple"])

        vpad(6)

        # ── Footer ─────────────────────────────────────────────
        tk.Label(self.root,
            text="⚠  FAILSAFE: muta mouse-ul in coltul stanga-sus pentru oprire urgenta",
            fg=C["text3"], bg=C["bg"],
            font=("Consolas", 7)).pack(pady=(4, 8))

        # Initial log
        self._log("GamerMacro Pro — Fishing Edition pornit.", "accent")
        self._log("Seteaza coordonatele, culoarea, apoi apasa START.", "dim")
        self._log("Sfat: Arunca undita INAINTE de a porni macro-ul.", "dim")

        # Catches counter
        self._catches = 0

    # ── UI Helpers ─────────────────────────────────────────────────────────────
    def _section(self, parent, num, title, icon=""):
        f = tk.Frame(parent, bg=C["bg"])
        f.pack(fill="x", padx=18, pady=(0, 0))
        tk.Label(f, text=f"[ {num} ]", fg=C["text3"], bg=C["bg"],
                 font=("Consolas", 8, "bold")).pack(side="left", padx=(0, 8))
        tk.Label(f, text=f"{icon}  {title}" if icon else title,
                 fg=C["accent"], bg=C["bg"],
                 font=("Consolas", 9, "bold")).pack(side="left")
        tk.Frame(f, bg=C["border2"], height=1).pack(
            side="left", fill="x", expand=True, padx=(10, 0))

    def _card(self, parent):
        outer = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        outer.pack(fill="x", padx=18, pady=0)
        inner = tk.Frame(outer, bg=C["panel"])
        inner.pack(fill="both")
        return inner

    # ── Logging ────────────────────────────────────────────────────────────────
    def _log(self, msg, tag="dim"):
        ts = time.strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}]  {msg}\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ── Capture position ───────────────────────────────────────────────────────
    def _start_capture(self):
        self.capture_btn.set_enabled(False)
        self._cdown(3)

    def _cdown(self, n):
        if n > 0:
            self.coord_status.config(
                text=f"  Muta mouse-ul pe pixel target…  {n}s",
                fg=C["yellow"])
            self.root.after(1000, self._cdown, n - 1)
        else:
            try:
                x, y = pyautogui.position()
                self.x_field.var.set(str(x))
                self.y_field.var.set(str(y))
                self.coord_status.config(
                    text=f"  ✓  Capturat:  X = {x}   Y = {y}",
                    fg=C["green"])
                self._log(f"Coordonate capturate → X={x}  Y={y}", "ok")
            except Exception as e:
                self.coord_status.config(
                    text=f"  ✗  Eroare: {e}", fg=C["red"])
            finally:
                self.capture_btn.set_enabled(True)

    # ── Sample colour ──────────────────────────────────────────────────────────
    def _sample_color(self):
        try:
            x = int(self.x_field.var.get())
            y = int(self.y_field.var.get())
        except ValueError:
            self._log("Coordonate invalide.", "error"); return
        try:
            px = pyautogui.pixel(x, y)
            r, g, b = px[0], px[1], px[2]
            self.r_field.var.set(str(r))
            self.g_field.var.set(str(g))
            self.b_field.var.set(str(b))
            self.swatch.set(r, g, b)
            hx = f"#{r:02x}{g:02x}{b:02x}"
            self.color_status.config(
                text=f"  ✓  RGB({r}, {g}, {b})   {hx}",
                fg=C["green"])
            self._log(f"Culoare samplata → RGB({r},{g},{b})  {hx}", "ok")
        except Exception as e:
            self.color_status.config(
                text=f"  ✗  Eroare: {e}", fg=C["red"])
            self._log(f"Eroare sampla: {e}", "error")

    # ── Natural mode toggle ────────────────────────────────────────────────────
    def _toggle_natural(self, state: bool):
        self._natural = state
        if state:
            self.nat_status.config(
                text="ACTIVAT  —  8% sansa de skip per detectie",
                fg=C["purple"])
            self._log("Mod Natural ACTIVAT.", "purple")
        else:
            self.nat_status.config(text="DEZACTIVAT", fg=C["text3"])
            self._log("Mod Natural dezactivat.", "dim")

    # ── Parse & validate ───────────────────────────────────────────────────────
    def _parse(self):
        x     = int(self.x_field.var.get())
        y     = int(self.y_field.var.get())
        r     = int(self.r_field.var.get())
        g     = int(self.g_field.var.get())
        b     = int(self.b_field.var.get())
        tol   = int(self.tol_field.var.get())
        delay = float(self.delay_field.var.get())
        cd    = float(self.cd_field.var.get())
        sc    = pyautogui.size()
        if not (0 <= x < sc.width and 0 <= y < sc.height):
            raise ValueError(f"Coordonate ({x},{y}) in afara ecranului.")
        return x, y, r, g, b, tol, delay, cd

    # ── Macro loop ─────────────────────────────────────────────────────────────
    def _watch(self, x, y, tr, tg, tb, tol, delay, cd, natural):
        self._set_state("RESET")
        state = "RESET"
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
                        self._set_state("WATCH")

                elif state == "WATCH":
                    if match:
                        # Natural mode: 8% skip
                        if natural and random.random() < 0.08:
                            skipped += 1
                            self.root.after(0, self._log,
                                f"[skip #{skipped}] Mod natural — sarit intentionat.",
                                "purple")
                            state = "RESET"
                            self._set_state("RESET")
                            time.sleep(self.POLL); continue

                        self._catches += 1
                        n = self._catches
                        self.root.after(0, self._log,
                            f"[#{n}] Bobber! RGB({cr},{cg},{cb}) — delay {delay}s…",
                            "warn")
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
                        self._set_state("RESET")

            except pyautogui.FailSafeException:
                self.root.after(0, self._log,
                    "FAILSAFE activat! Mouse in colt.", "error"); break
            except Exception as e:
                self.root.after(0, self._log, f"Eroare: {e}", "error"); break

            time.sleep(self.POLL)

        self._running = False
        self.root.after(0, self._on_stopped)

    def _set_state(self, state):
        colors = {
            "RESET": C["text3"],
            "WATCH": C["accent"],
            "IDLE":  C["text3"],
        }
        self.root.after(0, self.state_lbl.config,
            {"text": f"STATE: {state}",
             "fg": colors.get(state, C["text3"])})

    # ── Start / Stop ───────────────────────────────────────────────────────────
    def _start_macro(self):
        if self._running: return
        try:
            args = self._parse()
        except ValueError as e:
            self._log(f"Eroare: {e}", "error"); return

        self._running  = True
        self._catches  = 0
        self.catch_lbl.config(text="CATCHES: 0")
        self._set_ui(True)

        x, y, r, g, b, tol, delay, cd = args
        nat = self._natural
        self._log(
            f"START  ({x},{y})  RGB({r},{g},{b})  "
            f"±{tol}  delay={delay}s  cd={cd}s  "
            f"natural={'ON' if nat else 'OFF'}",
            "accent")

        self._thread = threading.Thread(
            target=self._watch,
            args=(x, y, r, g, b, tol, delay, cd, nat),
            daemon=True)
        self._thread.start()

    def _stop_macro(self):
        self._running = False
        self._log("Oprire solicitata…", "warn")

    def _on_stopped(self):
        self._set_ui(False)
        self._set_state("IDLE")
        self._log("Macro oprit.", "dim")

    # ── UI state ───────────────────────────────────────────────────────────────
    def _set_ui(self, running: bool):
        self.orb.set_active(running)
        self.status_lbl.config(
            text="RUNNING" if running else "IDLE",
            fg=C["green"] if running else C["text3"])
        self.start_btn.set_enabled(not running)
        self.stop_btn.set_enabled(running)
        self.capture_btn.set_enabled(not running)
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
