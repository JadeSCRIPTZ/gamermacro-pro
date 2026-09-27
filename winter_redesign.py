# Complete Winter tab redesign
# This will replace _build_winter completely

WINTER_CODE = '''
    def _build_winter(self):
        """Winter tab - Detector 2 with pixel picker"""
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

        # Helper functions
        def gap(n=10): tk.Frame(P, bg=bg, height=n).pack(fill="x")
        def card():
            c = tk.Frame(P, bg=PANEL, highlightthickness=1, highlightbackground=BORD)
            c.pack(fill="x", padx=15, pady=(10, 0))
            return c
        def section(c, title):
            tk.Label(c, text=title, font=(FN, 9, "bold"), bg=PANEL, fg=BLUE).pack(anchor="w", padx=15, pady=(15, 10))

        # ── PIXEL PICKER ───────────────────────────────────────
        c_pick = card()
        section(c_pick, "🎯 PIXEL PICKER")
        
        pick_frame = tk.Frame(c_pick, bg=PANEL)
        pick_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        pick_btn = tk.Button(pick_frame, text="🎯 SELECT PIXEL FROM SCREEN",
                            command=self._winter_pick_pixel,
                            font=(FN, 10, "bold"), bg=BLUE, fg=BG,
                            relief="flat", bd=0, padx=20, pady=10,
                            cursor="hand2", activebackground=BLUED,
                            activeforeground=TXT, highlightthickness=0)
        pick_btn.pack(fill="x")
        
        self.winter_status = tk.Label(pick_frame, text="Status: Ready",
                                     fg=TXT3, bg=PANEL, font=(FN, 8))
        self.winter_status.pack(anchor="w", pady=(8, 0))

        gap(12)

        # ── POSITION ───────────────────────────────────────────
        c_pos = card()
        section(c_pos, "📍 POSITION")
        
        pos_frame = tk.Frame(c_pos, bg=PANEL)
        pos_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.winter_xf = Inp(pos_frame, "X", "640", 8)
        self.winter_xf.pack(side="left", padx=(0, 15))
        self.winter_yf = Inp(pos_frame, "Y", "360", 8)
        self.winter_yf.pack(side="left")

        gap(12)

        # ── COLOR ──────────────────────────────────────────────
        c_color = card()
        section(c_color, "🎨 COLOR")
        
        rgb_frame = tk.Frame(c_color, bg=PANEL)
        rgb_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.winter_rf = Inp(rgb_frame, "R", "150", 5)
        self.winter_rf.pack(side="left", padx=(0, 10))
        self.winter_gf = Inp(rgb_frame, "G", "150", 5)
        self.winter_gf.pack(side="left", padx=(0, 10))
        self.winter_bf = Inp(rgb_frame, "B", "150", 5)
        self.winter_bf.pack(side="left")
        
        # Color preview
        preview_frame = tk.Frame(c_color, bg=PANEL)
        preview_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        tk.Label(preview_frame, text="Preview:", bg=PANEL, fg=TXT2, font=(FN, 9)).pack(side="left", padx=(0, 10))
        self.winter_preview = tk.Frame(preview_frame, bg="#969696", width=100, height=30)
        self.winter_preview.pack(side="left")
        self.winter_preview.pack_propagate(False)
        
        # Tolerance
        tol_frame = tk.Frame(c_color, bg=PANEL)
        tol_frame.pack(fill="x", padx=15)
        self.winter_tolf = Inp(tol_frame, "Tol ±", "25", 5)
        self.winter_tolf.pack(side="left")

        gap(12)

        # ── CLICKS ────────────────────────────────────────────
        c_clicks = card()
        section(c_clicks, "🖱️ CLICKS")
        
        clicks_frame = tk.Frame(c_clicks, bg=PANEL)
        clicks_frame.pack(fill="x", padx=15, pady=(0, 15))
        self.winter_clicksf = Inp(clicks_frame, "Clicks", "1", 5)
        self.winter_clicksf.pack(side="left")

        gap(12)

        # ── INTERVAL ───────────────────────────────────────────
        c_interval = card()
        section(c_interval, "⏱️ INTERVAL")
        
        interval_frame = tk.Frame(c_interval, bg=PANEL)
        interval_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        tk.Label(interval_frame, text="Sec:", bg=PANEL, fg=TXT2, font=(FN, 9)).pack(side="left", padx=(0, 5))
        self.winter_secf = Inp(interval_frame, "", "0", 4)
        self.winter_secf.pack(side="left", padx=(0, 15))
        
        tk.Label(interval_frame, text="Ms:", bg=PANEL, fg=TXT2, font=(FN, 9)).pack(side="left", padx=(0, 5))
        self.winter_msf = Inp(interval_frame, "", "500", 5)
        self.winter_msf.pack(side="left")
        
        # Total
        total_frame = tk.Frame(c_interval, bg=PANEL)
        total_frame.pack(fill="x", padx=15)
        tk.Label(total_frame, text="Total:", bg=PANEL, fg=TXT2, font=(FN, 9)).pack(side="left", padx=(0, 10))
        self.winter_total_lbl = tk.Label(total_frame, text="0.500s (500ms)",
                                        fg=BLUE, bg=PANEL, font=(FN, 9, "bold"))
        self.winter_total_lbl.pack(side="left")
        
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

        # ── ENABLE ────────────────────────────────────────────
        c_enable = card()
        section(c_enable, "✅ CONTROL")
        
        enable_frame = tk.Frame(c_enable, bg=PANEL)
        enable_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.winter_var = tk.BooleanVar(value=False)
        tk.Checkbutton(enable_frame,
            text="Enable Winter (Detector 2)",
            variable=self.winter_var, bg=PANEL, fg=TXT,
            selectcolor=INPUT, activebackground=PANEL,
            activeforeground=TXT, font=(FN, 9),
            command=self._on_winter_toggle).pack(anchor="w")
        
        self.winter_lbl = tk.Label(enable_frame, text="Status: Dezactivat",
                                  fg=TXT3, bg=PANEL, font=(FN, 8))
        self.winter_lbl.pack(anchor="w", pady=(5, 0))

        gap(20)
'''

print(WINTER_CODE)
