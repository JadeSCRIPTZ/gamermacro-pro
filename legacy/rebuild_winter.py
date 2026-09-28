# Read the file
with open('gamermacro.py', 'r') as f:
    content = f.read()

# Find where _build_winter starts
import re
match = re.search(r'(    # ─+\n    #  TAB: WINTER.*?\n    # ─+\n    def _build_winter\(self\):.*?)(?=\n    # ─|    def _build_stats)', content, re.DOTALL)

if match:
    old_winter = match.group(1)
    print(f"Found old _build_winter ({len(old_winter)} chars)")
    
    # New clean Winter implementation
    new_winter = '''    # ─────────────────────────────────────────────────────────
    #  TAB: WINTER - DETECTOR 2 ONLY
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
        bg = BG
        
        def gap(n=10): tk.Frame(P, bg=bg, height=n).pack(fill="x")
        def card():
            c = tk.Frame(P, bg=PANEL, highlightthickness=1, highlightbackground=BORD)
            c.pack(fill="x", padx=15, pady=(10, 0))
            return c
        def section(c, title):
            tk.Label(c, text=title, font=(FN, 10, "bold"), bg=PANEL, fg=BLUE).pack(anchor="w", padx=15, pady=(15, 10))
        
        gap(8)
        
        # PIXEL PICKER
        c_pick = card()
        section(c_pick, "🎯 PIXEL PICKER")
        
        pick_btn = tk.Button(c_pick, text="SELECT PIXEL FROM SCREEN",
                            command=self._winter_pick_pixel,
                            font=(FN, 11, "bold"),
                            bg=BLUE, fg=BG, relief="flat", bd=0, padx=20, pady=12,
                            cursor="hand2", activebackground=BLUED, activeforeground=TXT,
                            highlightthickness=0)
        pick_btn.pack(fill="x", padx=15, pady=(0, 15))
        
        self.winter_pick_status = tk.Label(c_pick, text="Status: Ready",
                                          fg=TXT3, bg=PANEL, font=(FN, 8))
        self.winter_pick_status.pack(anchor="w", padx=15, pady=(0, 15))
        
        gap(8)
        
        # POSITION
        c_pos = card()
        section(c_pos, "📍 POSITION")
        
        pos_frame = tk.Frame(c_pos, bg=PANEL)
        pos_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.winter_x = Inp(pos_frame, "X", "640", 8)
        self.winter_x.pack(side="left", padx=(0, 20))
        self.winter_y = Inp(pos_frame, "Y", "360", 8)
        self.winter_y.pack(side="left")
        
        gap(8)
        
        # COLOR
        c_color = card()
        section(c_color, "🎨 COLOR")
        
        rgb_frame = tk.Frame(c_color, bg=PANEL)
        rgb_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.winter_r = Inp(rgb_frame, "R", "150", 5)
        self.winter_r.pack(side="left", padx=(0, 10))
        self.winter_g = Inp(rgb_frame, "G", "150", 5)
        self.winter_g.pack(side="left", padx=(0, 10))
        self.winter_b = Inp(rgb_frame, "B", "150", 5)
        self.winter_b.pack(side="left")
        
        # Preview
        prev_frame = tk.Frame(c_color, bg=PANEL)
        prev_frame.pack(fill="x", padx=15, pady=(0, 15))
        tk.Label(prev_frame, text="Preview:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 10))
        self.winter_preview = tk.Frame(prev_frame, bg="#666666", width=100, height=30)
        self.winter_preview.pack(side="left")
        self.winter_preview.pack_propagate(False)
        
        gap(8)
        
        # TOLERANCE
        c_tol = card()
        section(c_tol, "⚙️ TOLERANCE")
        
        self.winter_tol = Inp(c_tol, "Tol ±", "25", 5)
        self.winter_tol.pack(padx=15, pady=(0, 15))
        
        gap(8)
        
        # CLICKS
        c_clicks = card()
        section(c_clicks, "🖱️ CLICKS")
        
        self.winter_clicks = Inp(c_clicks, "Number", "1", 5)
        self.winter_clicks.pack(padx=15, pady=(0, 15))
        
        gap(8)
        
        # INTERVAL
        c_int = card()
        section(c_int, "⏱️ INTERVAL")
        
        int_frame = tk.Frame(c_int, bg=PANEL)
        int_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        tk.Label(int_frame, text="Sec:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
        self.winter_sec = Inp(int_frame, "", "0", 4)
        self.winter_sec.pack(side="left", padx=(0, 20))
        
        tk.Label(int_frame, text="Ms:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 5))
        self.winter_ms = Inp(int_frame, "", "500", 5)
        self.winter_ms.pack(side="left")
        
        self.winter_total = tk.Label(c_int, text="Total: 0.500s (500ms)",
                                    fg=BLUE, bg=PANEL, font=(FN, 9, "bold"))
        self.winter_total.pack(anchor="w", padx=15, pady=(0, 15))
        
        def update_total(*args):
            try:
                sec = int(self.winter_sec.var.get() or 0)
                ms = int(self.winter_ms.var.get() or 0)
                total_ms = sec * 1000 + ms
                self.winter_total.config(text=f"Total: {total_ms/1000:.3f}s ({total_ms}ms)")
            except: pass
        
        self.winter_sec.var.trace("w", update_total)
        self.winter_ms.var.trace("w", update_total)
        
        gap(8)
        
        # CONTROL
        c_ctrl = card()
        section(c_ctrl, "✅ CONTROL")
        
        self.winter_var = tk.BooleanVar(value=False)
        tk.Checkbutton(c_ctrl,
            text="Enable Winter (Detector 2)",
            variable=self.winter_var, bg=PANEL, fg=TXT,
            selectcolor=INPUT, activebackground=PANEL,
            activeforeground=TXT, font=(FN,10),
            command=self._on_winter_toggle).pack(anchor="w", padx=15, pady=(0, 5))
        
        self.winter_status = tk.Label(c_ctrl, text="Status: Dezactivat",
                                     fg=TXT3, bg=PANEL, font=(FN,8))
        self.winter_status.pack(anchor="w", padx=15, pady=(0, 15))
        
        gap(20)
'''
    
    # Replace
    new_content = content.replace(old_winter, new_winter)
    
    with open('gamermacro.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Rebuilt _build_winter completely clean!")
else:
    print("Could not find _build_winter")
