"""
GamerMacro Pro
==============
Tab 1 – Macro Recorder : inregistreaza taste + click-uri mouse, redeaza cu
                          viteza variabila si loop
Tab 2 – Pixel Watcher  : detecteaza schimbarea culorii unui pixel si executa
                          o secventa de actiuni (ex: fishing bot Minecraft)

Instalare: pip install pyautogui pillow pynput
Rulare:    python gamermacro.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading, time, json, sys, os

# ── dep check ─────────────────────────────────────────────────────────────────
MISSING = []
try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0
except ImportError:
    MISSING.append("pyautogui")

try:
    from pynput import keyboard as _kb, mouse as _ms
except ImportError:
    MISSING.append("pynput")

if MISSING:
    print(f"Lipsesc: {', '.join(MISSING)}")
    print("Ruleaza: pip install pyautogui pillow pynput")
    sys.exit(1)

# ── palette ───────────────────────────────────────────────────────────────────
BG      = "#0d1117"
PANEL   = "#161b22"
PANEL2  = "#1c2128"
ACCENT  = "#58a6ff"
GREEN   = "#3fb950"
GREEN_D = "#2d8f3c"
RED     = "#f85149"
RED_D   = "#b92d28"
YELLOW  = "#d29922"
PURPLE  = "#bc8cff"
TEXT    = "#e6edf3"
DIM     = "#8b949e"
BORDER  = "#30363d"
INP     = "#0d1117"

# ── pynput → pyautogui key map ────────────────────────────────────────────────
_KEY_MAP = {
    "Key.space":"space","Key.enter":"enter","Key.return":"enter",
    "Key.backspace":"backspace","Key.tab":"tab","Key.esc":"escape",
    "Key.delete":"delete","Key.insert":"insert","Key.home":"home",
    "Key.end":"end","Key.page_up":"pageup","Key.page_down":"pagedown",
    "Key.up":"up","Key.down":"down","Key.left":"left","Key.right":"right",
    "Key.shift":"shift","Key.shift_r":"shiftright",
    "Key.ctrl_l":"ctrl","Key.ctrl_r":"ctrlright",
    "Key.alt_l":"alt","Key.alt_r":"altright",
    "Key.cmd":"winleft","Key.caps_lock":"capslock",
    "Key.f1":"f1","Key.f2":"f2","Key.f3":"f3","Key.f4":"f4",
    "Key.f5":"f5","Key.f6":"f6","Key.f7":"f7","Key.f8":"f8",
    "Key.f9":"f9","Key.f10":"f10","Key.f11":"f11","Key.f12":"f12",
    "Key.num_lock":"numlock","Key.scroll_lock":"scrolllock",
    "Key.print_screen":"printscreen","Key.pause":"pause",
}

def _key_to_str(key):
    if hasattr(key, "char") and key.char:
        return key.char
    return _KEY_MAP.get(str(key), str(key).replace("Key.",""))


# ─────────────────────────────────────────────────────────────────────────────
#  SHARED HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def btn(parent, text, cmd, bg=ACCENT, fg=BG, abg=None,
        w=14, px=10, py=5, state="normal"):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg=fg,
                  activebackground=abg or bg, activeforeground=fg,
                  disabledforeground="#444d56",
                  relief="flat", bd=0, cursor="hand2",
                  font=("Consolas", 10, "bold"),
                  width=w, padx=px, pady=py, state=state)
    return b

def entry_row(parent, label, default="0", w=8):
    f = tk.Frame(parent, bg=PANEL2)
    tk.Label(f, text=label, fg=DIM, bg=PANEL2,
             font=("Consolas", 9)).pack(side="left", padx=(0,4))
    var = tk.StringVar(value=str(default))
    tk.Entry(f, textvariable=var, width=w,
             bg=INP, fg=TEXT, insertbackground=ACCENT,
             relief="flat", bd=3, font=("Consolas", 10),
             justify="center").pack(side="left")
    return f, var

def hsep(parent, pady=6):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=pady)

def section_label(parent, text):
    tk.Label(parent, text=text, fg=ACCENT, bg=PANEL2,
             font=("Consolas", 9, "bold")).pack(anchor="w")

def log_widget(parent, height=8):
    f = tk.Frame(parent, bg=INP)
    f.pack(fill="both", expand=True)
    t = tk.Text(f, bg=INP, fg=TEXT, font=("Consolas", 8),
                relief="flat", state="disabled", wrap="word",
                bd=4, height=height)
    sb = tk.Scrollbar(f, command=t.yview, bg=PANEL2, troughcolor=INP)
    t.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    t.pack(side="left", fill="both", expand=True)
    t.tag_config("ok",     foreground=GREEN)
    t.tag_config("warn",   foreground=YELLOW)
    t.tag_config("error",  foreground=RED)
    t.tag_config("dim",    foreground=DIM)
    t.tag_config("accent", foreground=ACCENT)
    t.tag_config("purple", foreground=PURPLE)
    return t

def write_log(widget, msg, tag="dim"):
    ts = time.strftime("%H:%M:%S")
    widget.configure(state="normal")
    widget.insert("end", f"[{ts}] {msg}\n", tag)
    widget.see("end")
    widget.configure(state="disabled")


# ─────────────────────────────────────────────────────────────────────────────
#  TAB 1 — MACRO RECORDER
# ─────────────────────────────────────────────────────────────────────────────
class RecorderTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=PANEL2)
        self._events     = []      # list of dicts
        self._recording  = False
        self._playing    = False
        self._kb_listener = None
        self._ms_listener = None
        self._play_thread = None
        self._last_t      = 0.0
        self._build()

    def _build(self):
        inner = tk.Frame(self, bg=PANEL2, padx=14, pady=12)
        inner.pack(fill="both", expand=True)

        # ── Controls row ──────────────────────────────────────
        section_label(inner, "CONTROALE INREGISTRARE")
        hsep(inner)

        ctrl = tk.Frame(inner, bg=PANEL2)
        ctrl.pack(fill="x", pady=(0, 8))

        self.rec_btn  = btn(ctrl, "⏺  RECORD", self._start_rec,
                            bg=RED, fg="#fff", abg=RED_D, w=14)
        self.rec_btn.pack(side="left", padx=(0,6))

        self.stop_rec_btn = btn(ctrl, "⏹  STOP REC", self._stop_rec,
                                bg=PANEL, fg=DIM, abg=BORDER, w=14,
                                state="disabled")
        self.stop_rec_btn.pack(side="left", padx=(0,6))

        self.clear_btn = btn(ctrl, "🗑  CLEAR", self._clear,
                             bg=PANEL, fg=DIM, abg=BORDER, w=10)
        self.clear_btn.pack(side="left")

        # ── Playback options ──────────────────────────────────
        section_label(inner, "OPTIUNI REDARE")
        hsep(inner)

        opt = tk.Frame(inner, bg=PANEL2)
        opt.pack(fill="x", pady=(0, 8))

        # Speed
        sf, self.speed_var = entry_row(opt, "Viteza (x):", "1.0", 5)
        sf.pack(side="left", padx=(0,16))

        # Loop count  (0 = infinite)
        lf, self.loop_var = entry_row(opt, "Bucle (0=∞):", "1", 5)
        lf.pack(side="left", padx=(0,16))

        # Hotkey stop toggle
        self.stop_key_var = tk.StringVar(value="F8")
        hkf = tk.Frame(opt, bg=PANEL2)
        hkf.pack(side="left")
        tk.Label(hkf, text="Stop key:", fg=DIM, bg=PANEL2,
                 font=("Consolas", 9)).pack(side="left", padx=(0,4))
        tk.Entry(hkf, textvariable=self.stop_key_var, width=5,
                 bg=INP, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", bd=3, font=("Consolas", 10),
                 justify="center").pack(side="left")

        # ── Playback buttons ──────────────────────────────────
        pb = tk.Frame(inner, bg=PANEL2)
        pb.pack(fill="x", pady=(0, 10))

        self.play_btn = btn(pb, "▶  PLAY", self._start_play,
                            bg=GREEN, fg=BG, abg=GREEN_D, w=14)
        self.play_btn.pack(side="left", padx=(0,6))

        self.stop_play_btn = btn(pb, "■  STOP PLAY", self._stop_play,
                                 bg=PANEL, fg=DIM, abg=BORDER, w=14,
                                 state="disabled")
        self.stop_play_btn.pack(side="left", padx=(0,6))

        # Save / Load
        sf2 = tk.Frame(inner, bg=PANEL2)
        sf2.pack(fill="x", pady=(0,10))
        btn(sf2, "💾  Salveaza", self._save,
            bg=PURPLE, fg=BG, abg="#9c6fd6", w=14).pack(side="left", padx=(0,6))
        btn(sf2, "📂  Incarca",  self._load,
            bg=PURPLE, fg=BG, abg="#9c6fd6", w=14).pack(side="left")

        # ── Status ────────────────────────────────────────────
        self.status_lbl = tk.Label(inner, text="Gata.",
                                   fg=DIM, bg=PANEL2,
                                   font=("Consolas", 8))
        self.status_lbl.pack(anchor="w", pady=(0,4))

        # ── Event log ─────────────────────────────────────────
        section_label(inner, "EVENIMENTE INREGISTRATE")
        hsep(inner)
        self.log = log_widget(inner, height=12)

    # ── Record ─────────────────────────────────────────────────
    def _start_rec(self):
        if self._recording or self._playing:
            return
        self._events.clear()
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self._last_t = time.time()
        self._recording = True
        self.status_lbl.config(text="⏺  Inregistrez… (apasa Stop cand termini)", fg=RED)
        self.rec_btn.config(state="disabled")
        self.stop_rec_btn.config(state="normal")
        self.play_btn.config(state="disabled")

        self._kb_listener = _kb.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release)
        self._ms_listener = _ms.Listener(
            on_click=self._on_click)
        self._kb_listener.start()
        self._ms_listener.start()

    def _on_key_press(self, key):
        if not self._recording:
            return
        now  = time.time()
        delay = now - self._last_t
        self._last_t = now
        k = _key_to_str(key)
        ev = {"type": "key_press", "delay": round(delay, 4), "key": k}
        self._events.append(ev)
        self.after(0, write_log, self.log,
                   f"+{delay:.3f}s  KEY  ↓  [{k}]", "ok")

    def _on_key_release(self, key):
        if not self._recording:
            return
        now   = time.time()
        delay = now - self._last_t
        self._last_t = now
        k = _key_to_str(key)
        ev = {"type": "key_release", "delay": round(delay, 4), "key": k}
        self._events.append(ev)
        self.after(0, write_log, self.log,
                   f"+{delay:.3f}s  KEY  ↑  [{k}]", "dim")

    def _on_click(self, x, y, button, pressed):
        if not self._recording:
            return
        now   = time.time()
        delay = now - self._last_t
        self._last_t = now
        bname = "left" if "left" in str(button) else "right"
        etype = "mouse_press" if pressed else "mouse_release"
        ev = {"type": etype, "delay": round(delay, 4),
              "x": x, "y": y, "button": bname}
        self._events.append(ev)
        sym  = "↓" if pressed else "↑"
        tag  = "warn" if pressed else "dim"
        self.after(0, write_log, self.log,
                   f"+{delay:.3f}s  CLICK {bname.upper()} {sym}  ({x},{y})", tag)

    def _stop_rec(self):
        self._recording = False
        if self._kb_listener:
            self._kb_listener.stop()
        if self._ms_listener:
            self._ms_listener.stop()
        n = len(self._events)
        self.status_lbl.config(
            text=f"Inregistrare oprita. {n} evenimente capturate.", fg=GREEN)
        self.rec_btn.config(state="normal")
        self.stop_rec_btn.config(state="disabled")
        self.play_btn.config(state="normal")
        write_log(self.log, f"Inregistrare completa — {n} evenimente.", "accent")

    def _clear(self):
        if self._recording or self._playing:
            return
        self._events.clear()
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.status_lbl.config(text="Gata.", fg=DIM)
        self.play_btn.config(state="normal")

    # ── Playback ───────────────────────────────────────────────
    def _start_play(self):
        if self._playing or self._recording:
            return
        if not self._events:
            messagebox.showwarning("GamerMacro", "Nu exista evenimente inregistrate!")
            return
        try:
            speed = float(self.speed_var.get())
            loops = int(self.loop_var.get())
            assert speed > 0
        except Exception:
            messagebox.showerror("GamerMacro", "Viteza si bucle trebuie sa fie numere valide.")
            return

        self._playing = True
        self.play_btn.config(state="disabled")
        self.stop_play_btn.config(state="normal")
        self.rec_btn.config(state="disabled")
        self.status_lbl.config(text="▶  Redau macro…", fg=GREEN)
        write_log(self.log, f"Redare pornita (viteza={speed}x, bucle={loops or '∞'})", "accent")

        stop_key = self.stop_key_var.get().lower().strip()
        self._play_thread = threading.Thread(
            target=self._play_loop,
            args=(speed, loops, stop_key),
            daemon=True)
        self._play_thread.start()

    def _play_loop(self, speed, loops, stop_key):
        iteration = 0
        while self._playing:
            iteration += 1
            if loops > 0 and iteration > loops:
                break
            self.after(0, write_log, self.log,
                       f"Iteratie #{iteration}", "purple")
            for ev in self._events:
                if not self._playing:
                    break
                delay = ev["delay"] / speed
                if delay > 0:
                    time.sleep(delay)
                try:
                    t = ev["type"]
                    if t == "key_press":
                        pyautogui.keyDown(ev["key"])
                    elif t == "key_release":
                        pyautogui.keyUp(ev["key"])
                    elif t == "mouse_press":
                        btn_name = ev["button"]
                        pyautogui.mouseDown(ev["x"], ev["y"], button=btn_name)
                    elif t == "mouse_release":
                        btn_name = ev["button"]
                        pyautogui.mouseUp(ev["x"], ev["y"], button=btn_name)
                except pyautogui.FailSafeException:
                    self.after(0, write_log, self.log,
                               "FailSafe! Mouse in colt.", "error")
                    self._playing = False
                    break
                except Exception as e:
                    self.after(0, write_log, self.log,
                               f"Eroare: {e}", "error")

        self._playing = False
        self.after(0, self._play_done)

    def _stop_play(self):
        self._playing = False
        write_log(self.log, "Redare oprita de utilizator.", "warn")

    def _play_done(self):
        self._playing = False
        self.play_btn.config(state="normal")
        self.stop_play_btn.config(state="disabled")
        self.rec_btn.config(state="normal")
        self.status_lbl.config(text="Redare terminata.", fg=DIM)
        write_log(self.log, "Redare completa.", "accent")

    # ── Save / Load ────────────────────────────────────────────
    def _save(self):
        if not self._events:
            messagebox.showwarning("GamerMacro", "Nimic de salvat!")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("GamerMacro Profile", "*.json"), ("All files", "*.*")],
            title="Salveaza profilul")
        if not path:
            return
        try:
            with open(path, "w") as f:
                json.dump({"version": 1, "events": self._events}, f, indent=2)
            write_log(self.log, f"Salvat: {os.path.basename(path)}", "accent")
        except Exception as e:
            messagebox.showerror("GamerMacro", f"Eroare salvare: {e}")

    def _load(self):
        path = filedialog.askopenfilename(
            filetypes=[("GamerMacro Profile", "*.json"), ("All files", "*.*")],
            title="Incarca profilul")
        if not path:
            return
        try:
            with open(path) as f:
                data = json.load(f)
            self._events = data.get("events", [])
            self.log.configure(state="normal")
            self.log.delete("1.0", "end")
            self.log.configure(state="disabled")
            for ev in self._events:
                t = ev["type"]
                d = ev["delay"]
                if "key" in ev:
                    tag = "ok" if t == "key_press" else "dim"
                    sym = "↓" if t == "key_press" else "↑"
                    write_log(self.log, f"+{d:.3f}s  KEY  {sym}  [{ev['key']}]", tag)
                else:
                    tag = "warn" if t == "mouse_press" else "dim"
                    sym = "↓" if t == "mouse_press" else "↑"
                    write_log(self.log, f"+{d:.3f}s  CLICK {ev['button'].upper()} {sym}  ({ev['x']},{ev['y']})", tag)
            n = len(self._events)
            self.status_lbl.config(text=f"Profil incarcat: {n} evenimente.", fg=GREEN)
            self.play_btn.config(state="normal")
            write_log(self.log, f"Profil incarcat: {os.path.basename(path)} ({n} ev)", "accent")
        except Exception as e:
            messagebox.showerror("GamerMacro", f"Eroare incarcare: {e}")


# ─────────────────────────────────────────────────────────────────────────────
#  TAB 2 — PIXEL WATCHER
# ─────────────────────────────────────────────────────────────────────────────
class PixelTab(tk.Frame):
    POLL = 0.05
    TOL  = 15

    def __init__(self, master):
        super().__init__(master, bg=PANEL2)
        self._running = False
        self._thread  = None
        self._build()

    def _build(self):
        inner = tk.Frame(self, bg=PANEL2, padx=14, pady=12)
        inner.pack(fill="both", expand=True)

        # ── Coordinates ───────────────────────────────────────
        section_label(inner, "COORDONATE PIXEL")
        hsep(inner)
        cr = tk.Frame(inner, bg=PANEL2)
        cr.pack(fill="x", pady=(0,5))
        xf, self.x_var = entry_row(cr, "X:", "0", 7)
        xf.pack(side="left", padx=(0,14))
        yf, self.y_var = entry_row(cr, "Y:", "0", 7)
        yf.pack(side="left")
        self.coord_lbl = tk.Label(inner, text="Nicio coordonata capturata.",
                                  fg=DIM, bg=PANEL2, font=("Consolas", 8))
        self.coord_lbl.pack(anchor="w", pady=(0,4))
        self.pos_btn = btn(inner, "🖱  Get Mouse Position (3s)",
                           self._start_capture, bg=ACCENT, fg=BG,
                           abg="#3d8bcd", w=28)
        self.pos_btn.pack(anchor="w", pady=3)

        # ── Colour ────────────────────────────────────────────
        section_label(inner, "CULOARE TINTA")
        hsep(inner)
        rr = tk.Frame(inner, bg=PANEL2)
        rr.pack(fill="x", pady=(0,5))
        rf, self.r_var = entry_row(rr, "R:", "255", 5)
        rf.pack(side="left", padx=(0,6))
        gf, self.g_var = entry_row(rr, "G:", "0",   5)
        gf.pack(side="left", padx=(0,6))
        bf, self.b_var = entry_row(rr, "B:", "0",   5)
        bf.pack(side="left", padx=(0,8))
        self._sw_frame = tk.Frame(rr, width=26, height=26,
                                  bg="#ff0000", relief="flat", bd=1)
        self._sw_frame.pack(side="left", padx=4)
        self._sw_frame.pack_propagate(False)

        self.color_lbl = tk.Label(inner, text="Nicio culoare esan.",
                                  fg=DIM, bg=PANEL2, font=("Consolas", 8))
        self.color_lbl.pack(anchor="w", pady=(0,4))
        self.col_btn = btn(inner, "🎨  Get Colour Under Mouse",
                           self._sample, bg=ACCENT, fg=BG,
                           abg="#3d8bcd", w=28)
        self.col_btn.pack(anchor="w", pady=3)

        # ── Tolerance & action ────────────────────────────────
        section_label(inner, "TOLERANTA & ACTIUNE")
        hsep(inner)
        tr = tk.Frame(inner, bg=PANEL2)
        tr.pack(fill="x", pady=(0,6))
        tf, self.tol_var = entry_row(tr, "±", str(self.TOL), 5)
        tf.pack(side="left")
        tk.Label(tr, text="per canal RGB  (recomandat: 10–25)",
                 fg=DIM, bg=PANEL2, font=("Consolas", 8)).pack(side="left", padx=8)

        ar = tk.Frame(inner, bg=PANEL2)
        ar.pack(fill="x", pady=(0,10))
        action_choices = [
            "Right-click x2 (Minecraft fishing)",
            "Left-click x1",
            "Left-click x2",
            "Press E (interact)",
            "Press F (pickup)",
        ]
        self.action_var = tk.StringVar(value=action_choices[0])
        tk.Label(ar, text="Actiune:", fg=DIM, bg=PANEL2,
                 font=("Consolas", 9)).pack(side="left", padx=(0,6))
        om = tk.OptionMenu(ar, self.action_var, *action_choices)
        om.config(bg=INP, fg=TEXT, activebackground=PANEL,
                  activeforeground=TEXT, relief="flat",
                  font=("Consolas", 9), bd=0, highlightthickness=0)
        om["menu"].config(bg=INP, fg=TEXT, activebackground=ACCENT,
                          activeforeground=BG, relief="flat")
        om.pack(side="left")

        # Cooldown
        cd_r = tk.Frame(inner, bg=PANEL2)
        cd_r.pack(fill="x", pady=(0,10))
        cdf, self.cd_var = entry_row(cd_r, "Cooldown (s):", "3.0", 5)
        cdf.pack(side="left")
        tk.Label(cd_r, text="pauza dupa actiune",
                 fg=DIM, bg=PANEL2, font=("Consolas", 8)).pack(side="left", padx=8)

        # ── Start / Stop ──────────────────────────────────────
        mb = tk.Frame(inner, bg=PANEL2)
        mb.pack(fill="x", pady=(0,10))
        self.start_btn = btn(mb, "▶  START WATCHER",
                             self._start, bg=GREEN, fg=BG, abg=GREEN_D, w=18)
        self.start_btn.pack(side="left", padx=(0,6))
        self.stop_btn  = btn(mb, "■  STOP",
                             self._stop, bg=RED, fg="#fff", abg=RED_D, w=10,
                             state="disabled")
        self.stop_btn.pack(side="left")

        # ── Log ───────────────────────────────────────────────
        section_label(inner, "LOG")
        hsep(inner)
        self.log = log_widget(inner, height=8)
        write_log(self.log, "Pixel Watcher gata.", "dim")
        write_log(self.log, "Captureaza coordonatele si culoarea, apoi apasa START.", "accent")

    # ── Capture position ───────────────────────────────────────
    def _start_capture(self):
        self.pos_btn.config(state="disabled")
        self._cdown(3)

    def _cdown(self, n):
        if n > 0:
            self.coord_lbl.config(
                text=f"Muta mouse-ul pe pixel… captare in {n}s", fg=YELLOW)
            self.after(1000, self._cdown, n-1)
        else:
            try:
                x, y = pyautogui.position()
                self.x_var.set(str(x))
                self.y_var.set(str(y))
                self.coord_lbl.config(text=f"Capturat: X={x}, Y={y}", fg=GREEN)
                write_log(self.log, f"Coordonate: X={x}, Y={y}", "ok")
            except Exception as e:
                self.coord_lbl.config(text=f"Eroare: {e}", fg=RED)
            finally:
                self.pos_btn.config(state="normal")

    # ── Sample colour ──────────────────────────────────────────
    def _sample(self):
        try:
            x, y = int(self.x_var.get()), int(self.y_var.get())
            px = pyautogui.pixel(x, y)
            r, g, b = px[0], px[1], px[2]
            self.r_var.set(str(r)); self.g_var.set(str(g)); self.b_var.set(str(b))
            hx = f"#{r:02x}{g:02x}{b:02x}"
            self._sw_frame.config(bg=hx)
            self.color_lbl.config(text=f"RGB({r},{g},{b})  {hx}", fg=GREEN)
            write_log(self.log, f"Culoare la ({x},{y}) → RGB({r},{g},{b})  {hx}", "ok")
        except Exception as e:
            write_log(self.log, f"Eroare: {e}", "error")

    # ── Validate ───────────────────────────────────────────────
    def _parse(self):
        x   = int(self.x_var.get()); y   = int(self.y_var.get())
        r   = int(self.r_var.get());  g   = int(self.g_var.get())
        b   = int(self.b_var.get());  tol = int(self.tol_var.get())
        cd  = float(self.cd_var.get())
        sc  = pyautogui.size()
        if not (0 <= x < sc.width and 0 <= y < sc.height):
            raise ValueError(f"Coordonate ({x},{y}) in afara ecranului.")
        return x, y, r, g, b, tol, cd

    # ── Watcher loop ───────────────────────────────────────────
    def _watch(self, x, y, tr, tg, tb, tol, cd, action):
        write_log(self.log, "Watcher pornit. Monitorizez pixelul…", "ok")
        catches = 0
        while self._running:
            try:
                px = pyautogui.pixel(x, y)
                cr, cg, cb = px[0], px[1], px[2]
                if (abs(cr-tr)<=tol and abs(cg-tg)<=tol and abs(cb-tb)<=tol):
                    catches += 1
                    self.after(0, write_log, self.log,
                               f"[#{catches}] Trigger! RGB({cr},{cg},{cb})", "warn")
                    # Execute action
                    if "Right-click x2" in action:
                        pyautogui.rightClick(); time.sleep(0.5); pyautogui.rightClick()
                    elif "Left-click x2" in action:
                        pyautogui.click(); time.sleep(0.3); pyautogui.click()
                    elif "Left-click x1" in action:
                        pyautogui.click()
                    elif "Press E" in action:
                        pyautogui.press("e")
                    elif "Press F" in action:
                        pyautogui.press("f")
                    self.after(0, write_log, self.log,
                               f"[#{catches}] Actiune executata. Cooldown {cd}s…", "ok")
                    time.sleep(cd)
            except pyautogui.FailSafeException:
                self.after(0, write_log, self.log, "FailSafe! Mouse in colt.", "error")
                break
            except Exception as e:
                self.after(0, write_log, self.log, f"Eroare: {e}", "error")
                break
            time.sleep(self.POLL)
        self._running = False
        self.after(0, self._done)

    def _start(self):
        try:
            args = self._parse()
        except Exception as e:
            messagebox.showerror("GamerMacro", str(e)); return
        self._running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        action = self.action_var.get()
        self._thread = threading.Thread(
            target=self._watch, args=(*args, action), daemon=True)
        self._thread.start()
        x, y, r, g, b, tol, cd = args
        write_log(self.log, f"START ({x},{y}) RGB({r},{g},{b}) ±{tol} cd={cd}s", "accent")

    def _stop(self):
        self._running = False
        write_log(self.log, "Oprire…", "warn")

    def _done(self):
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        write_log(self.log, "Watcher oprit.", "dim")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("GamerMacro Pro")
        root.configure(bg=BG)
        root.resizable(False, False)
        root.attributes("-topmost", True)
        w, h = 520, 720
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        # Top bar
        tk.Frame(root, bg=ACCENT, height=3).pack(fill="x")
        hdr = tk.Frame(root, bg=BG)
        hdr.pack(fill="x", padx=16, pady=(10,4))
        tk.Label(hdr, text="🎮  GAMERMACRO PRO",
                 fg=ACCENT, bg=BG,
                 font=("Consolas", 15, "bold")).pack(side="left")
        tk.Label(hdr, text="v2.0",
                 fg=DIM, bg=BG,
                 font=("Consolas", 9)).pack(side="right", pady=4)
        tk.Label(root, text="Recorder • Pixel Watcher • Profile Save/Load",
                 fg=DIM, bg=BG, font=("Consolas", 8)).pack(anchor="w", padx=16)

        # Notebook
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",
                         background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                         background=PANEL, foreground=DIM,
                         font=("Consolas", 10, "bold"),
                         padding=[16, 6], borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", PANEL2)],
                  foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, padx=10, pady=8)

        self.rec_tab = RecorderTab(nb)
        self.px_tab  = PixelTab(nb)
        nb.add(self.rec_tab, text="⏺  Macro Recorder")
        nb.add(self.px_tab,  text="👁  Pixel Watcher")

        # Footer
        tk.Label(root,
                 text="⚠  Failsafe: muta mouse-ul in coltul stanga-sus pentru oprire urgenta",
                 fg=YELLOW, bg=BG, font=("Consolas", 7)).pack(pady=(0,6))

    def on_close(self):
        self.rec_tab._recording = False
        self.rec_tab._playing   = False
        self.px_tab._running    = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app  = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
