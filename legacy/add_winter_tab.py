"""
Add complete Winter tab with full Detector 2 configuration
"""

code_to_add = '''
    # ── WINTER TAB - DETECTOR 2 (PIXEL CHECKER 2) ──────────
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
        
        # Title
        title = tk.Label(P, text="Pixel Detector 2 - Custom Action",
                        font=(FN, 14, "bold"), bg=BG, fg=BLUE)
        title.pack(pady=(20, 10), padx=20)
        
        # ── PIXEL SELECTION ────────────────────────────────
        c_select = card()
        section(c_select, "PIXEL SELECTOR", PANEL)
        
        select_frame = tk.Frame(c_select, bg=PANEL)
        select_frame.pack(fill="x", padx=15, pady=15)
        
        self.pick_btn = tk.Button(select_frame, text="🎯 CLICK HERE TO PICK PIXEL",
                                 command=self._winter_pick_pixel,
                                 font=(FN, 11, "bold"),
                                 bg=BLUE, fg=BG, relief="flat", bd=0,
                                 padx=20, pady=12, cursor="hand2",
                                 activebackground=BLUED, activeforeground=TXT,
                                 highlightthickness=0)
        self.pick_btn.pack(fill="x", pady=(0, 15))
        
        tk.Label(select_frame, text="Move your cursor on the pixel you want and click",
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
        section(c_clicks, "CLICK CONFIGURATION", PANEL)
        
        # Number of clicks
        clicks_frame = tk.Frame(c_clicks, bg=PANEL)
        clicks_frame.pack(fill="x", pady=(0, 15))
        self.winter_clicksf = Inp(clicks_frame, "Clicks (1-50)", "1", 5)
        self.winter_clicksf.pack(side="left")
        
        gap(12)
        
        # ── INTERVAL CONFIGURATION ────────────────────────
        c_interval = card()
        section(c_interval, "INTERVAL BETWEEN CLICKS", PANEL)
        
        # Seconds
        sec_frame = tk.Frame(c_interval, bg=PANEL)
        sec_frame.pack(fill="x", pady=(0, 10))
        self.winter_secf = Inp(sec_frame, "Seconds (0-60)", "0", 5)
        self.winter_secf.pack(side="left", padx=(0, 15))
        
        # Milliseconds
        self.winter_msf = Inp(sec_frame, "Ms (0-999)", "500", 6)
        self.winter_msf.pack(side="left")
        
        # Total display
        total_frame = tk.Frame(c_interval, bg=PANEL)
        total_frame.pack(fill="x", pady=(0, 15))
        tk.Label(total_frame, text="Total Interval:", bg=PANEL, fg=TXT2, font=(FN,9)).pack(side="left", padx=(0, 10))
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
'''

print("Winter tab code ready to add to gamermacro.py")
print("\nAdd this code after _build_macro method")
print("\nAlso add to TABS list:")
print('    TABS = [')
print('        ("🎣", "Macro"),')
print('        ("⚙️", "Setari"),')
print('        ("❄️", "Winter"),')
print('        ("📊", "Statistici"),')
print('        ("📋", "Log"),')
print('    ]')

