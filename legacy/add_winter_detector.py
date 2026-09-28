"""
Add Winter category to sidebar with interactive Pixel Detector 2
Visual pixel selector using mouse cursor
"""

code_to_add = '''

        # ── Winter Tab (Pixel Detector 2) ──────────────────────
        winter_btn = tk.Button(sidebar, text="❄️ Winter",
                              font=ModernTheme.FONTS["normal"],
                              bg=ModernTheme.COLORS["bg_main"],
                              fg=ModernTheme.COLORS["text_secondary"],
                              activebackground=ModernTheme.COLORS["bg_card"],
                              activeforeground=ModernTheme.COLORS["green_bright"],
                              relief="flat", bd=0, padx=15, pady=10,
                              anchor="w", cursor="hand2", highlightthickness=0,
                              command=self._show_winter_detector)
        winter_btn.pack(fill="x", pady=(0, 2))
'''

print("✅ Code to add to sidebar creation section:")
print(code_to_add)
print("\n" + "="*60)
print("\nNow need to add the Winter detector UI section")
