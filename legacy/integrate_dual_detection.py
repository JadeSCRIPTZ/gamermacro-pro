"""
Integrates dual pixel detection into main gamermacro.py UI
Adds beautiful detector 2 section to the settings
"""

# This script shows what needs to be added to gamermacro.py

addition = """

# ── Detector 2 - Pixel Checker 2 (Left Click) ────────────────
c_det2 = card()
section(c_det2, "PIXEL DETECTOR 2 - CUSTOM ACTION", PANEL)

# Position
pos2_frame = tk.Frame(c_det2, bg=PANEL)
pos2_frame.pack(fill="x", pady=(0, 10))

tk.Label(pos2_frame, text="Position X:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
self.x2f = Inp(pos2_frame, "", "640", 5)
self.x2f.pack(side="left", padx=(0, 15))

tk.Label(pos2_frame, text="Position Y:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
self.y2f = Inp(pos2_frame, "", "360", 5)
self.y2f.pack(side="left")

# Color RGB
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

self.tol2f = Inp(tol2_frame, "Tolerance ±", "25", 5)
self.tol2f.pack(side="left")

# Click count
clicks_frame = tk.Frame(c_det2, bg=PANEL)
clicks_frame.pack(fill="x", pady=(0, 10))

tk.Label(clicks_frame, text="Nr. Clicks:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
self.clicks_var = tk.IntVar(value=1)
clicks_spin = tk.Spinbox(clicks_frame, from_=1, to=50, textvariable=self.clicks_var,
                         bg=INPUT, fg=TXT, relief="flat", bd=0, width=5)
clicks_spin.pack(side="left", padx=(0, 20))

# Interval Seconds
tk.Label(clicks_frame, text="Interval Sec:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
self.interval_sec_var = tk.IntVar(value=0)
sec_spin = tk.Spinbox(clicks_frame, from_=0, to=60, textvariable=self.interval_sec_var,
                      bg=INPUT, fg=TXT, relief="flat", bd=0, width=4)
sec_spin.pack(side="left", padx=(0, 10))

# Interval Milliseconds
tk.Label(clicks_frame, text="Ms:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
self.interval_ms_var = tk.IntVar(value=500)
ms_spin = tk.Spinbox(clicks_frame, from_=0, to=999, textvariable=self.interval_ms_var,
                     bg=INPUT, fg=TXT, relief="flat", bd=0, width=5)
ms_spin.pack(side="left")

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
    command=self._on_det2_toggle).pack(anchor="w", pady=(0, 10))

self.det2_lbl = tk.Label(c_det2, text="Status: Dezactivat",
                        fg=TXT3, bg=PANEL, font=(FN,8))
self.det2_lbl.pack(anchor="w")

gap(12)
"""

print("🔧 Integration code ready!")
print("\nAdd this to gamermacro.py after the Auto-Recast section")
print("\nThis adds:")
print("  ✅ Pixel position (X, Y)")
print("  ✅ Color detection (R, G, B)")
print("  ✅ Tolerance")
print("  ✅ Number of clicks (1-50)")
print("  ✅ Interval (Seconds + Milliseconds)")
print("  ✅ Total interval display")
print("  ✅ Enable/Disable checkbox")

