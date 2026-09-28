"""
GamerMacro Pro - Dual Pixel Detection System
Two independent detectors with custom click actions and timing
"""
import tkinter as tk
from tkinter import ttk
import json

class EnhancedDetectionSystem:
    """Dual detector system with full customization"""
    
    def __init__(self):
        self.detectors = {
            "detector_1": self.get_default_detector_1(),
            "detector_2": self.get_default_detector_2(),
        }
    
    def get_default_detector_1(self):
        """Bobber detection (right-click)"""
        return {
            "name": "🎣 Bobber Detection",
            "enabled": True,
            "x": 640,
            "y": 360,
            "r": 50,
            "g": 200,
            "b": 100,
            "tolerance": 25,
            "action_type": "right_click",
            "click_count": 2,
            "reaction_delay_sec": 0,
            "reaction_delay_ms": 100,
            "click_interval_sec": 0,
            "click_interval_ms": 500,
            "cooldown": 3.0,
        }
    
    def get_default_detector_2(self):
        """Custom detection (left-click)"""
        return {
            "name": "⚡ Custom Detection",
            "enabled": False,
            "x": 640,
            "y": 360,
            "r": 100,
            "g": 150,
            "b": 50,
            "tolerance": 20,
            "action_type": "left_click",
            "click_count": 1,
            "reaction_delay_sec": 0,
            "reaction_delay_ms": 50,
            "click_interval_sec": 0,
            "click_interval_ms": 300,
            "cooldown": 1.0,
        }


class DetectorPanel:
    """Beautiful dual detector panel"""
    
    def __init__(self, root, system):
        self.root = root
        self.system = system
        self.create_panel()
    
    def create_panel(self):
        """Create detector configuration panel"""
        # Container
        container = tk.Frame(self.root, bg="#141820")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            container,
            text="🔍 DUAL PIXEL DETECTION SYSTEM",
            font=("Segoe UI", 16, "bold"),
            bg="#141820",
            fg="#00ff88"
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Description
        desc = tk.Label(
            container,
            text="Configure two independent pixel detectors with custom click actions",
            font=("Segoe UI", 10),
            bg="#141820",
            fg="#a0a8b8"
        )
        desc.pack(anchor="w", pady=(0, 20))
        
        # Detectors in two columns
        detectors_frame = tk.Frame(container, bg="#141820")
        detectors_frame.pack(fill="both", expand=True)
        
        # Detector 1
        self.create_detector_card(
            detectors_frame,
            "detector_1",
            self.system.detectors["detector_1"],
            side="left"
        )
        
        # Detector 2
        self.create_detector_card(
            detectors_frame,
            "detector_2",
            self.system.detectors["detector_2"],
            side="right"
        )
    
    def create_detector_card(self, parent, detector_id, detector_data, side):
        """Create individual detector card"""
        card_frame = tk.Frame(parent, bg="#1a1f2e", highlightthickness=1, highlightbackground="#2d3748")
        card_frame.pack(side=side, fill="both", expand=True, padx=(0, 10) if side == "left" else (10, 0))
        
        # Header
        header = tk.Frame(card_frame, bg="#1a1f2e")
        header.pack(fill="x", padx=15, pady=15)
        
        title = tk.Label(
            header,
            text=detector_data["name"],
            font=("Segoe UI", 12, "bold"),
            bg="#1a1f2e",
            fg="#00d98e"
        )
        title.pack(anchor="w")
        
        # Enable toggle
        self.enable_vars = {}
        self.enable_vars[detector_id] = tk.BooleanVar(value=detector_data["enabled"])
        
        enable_cb = tk.Checkbutton(
            header,
            text="Enabled",
            variable=self.enable_vars[detector_id],
            font=("Segoe UI", 9),
            bg="#1a1f2e",
            fg="#a0a8b8",
            selectcolor="#1a1f2e",
            activebackground="#1a1f2e",
            activeforeground="#00d98e"
        )
        enable_cb.pack(anchor="e")
        
        # Content
        content = tk.Frame(card_frame, bg="#1a1f2e")
        content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Pixel Detection Section
        self.add_section(content, "📍 PIXEL COLOR", detector_id, detector_data, [
            ("X Position:", "x", 640),
            ("Y Position:", "y", 360),
            ("Red (R):", "r", 50),
            ("Green (G):", "g", 200),
            ("Blue (B):", "b", 100),
            ("Tolerance:", "tolerance", 25),
        ])
        
        # Action Section
        self.add_section(content, "⚡ CLICK ACTION", detector_id, detector_data, [
            ("Click Type:", "action_type", "left_click"),
            ("Number of Clicks:", "click_count", 1),
        ], combo_fields={"action_type": ["left_click", "right_click", "double_click"]})
        
        # Timing Section
        self.add_timing_section(content, detector_id, detector_data)
        
        # Color preview
        self.add_color_preview(content, detector_data)
    
    def add_section(self, parent, title, detector_id, detector_data, fields, combo_fields=None):
        """Add settings section"""
        if combo_fields is None:
            combo_fields = {}
        
        section = tk.Frame(parent, bg="#1a1f2e")
        section.pack(fill="x", pady=(10, 0))
        
        section_title = tk.Label(
            section,
            text=title,
            font=("Segoe UI", 9, "bold"),
            bg="#1a1f2e",
            fg="#6b7280"
        )
        section_title.pack(anchor="w", pady=(0, 8))
        
        fields_frame = tk.Frame(section, bg="#1a1f2e")
        fields_frame.pack(fill="x", padx=5)
        
        if not hasattr(self, 'field_vars'):
            self.field_vars = {}
        if detector_id not in self.field_vars:
            self.field_vars[detector_id] = {}
        
        for label, key, default in fields:
            field_row = tk.Frame(fields_frame, bg="#1a1f2e")
            field_row.pack(fill="x", pady=(0, 8))
            
            lbl = tk.Label(
                field_row,
                text=label,
                font=("Segoe UI", 9),
                bg="#1a1f2e",
                fg="#a0a8b8",
                width=15,
                anchor="w"
            )
            lbl.pack(side="left")
            
            if key in combo_fields:
                var = tk.StringVar(value=detector_data.get(key, default))
                combo = ttk.Combobox(
                    field_row,
                    textvariable=var,
                    values=combo_fields[key],
                    state="readonly",
                    width=20
                )
                combo.pack(side="left", fill="x", expand=True, padx=(10, 0))
                self.field_vars[detector_id][key] = var
            else:
                var = tk.StringVar(value=str(detector_data.get(key, default)))
                entry = tk.Entry(
                    field_row,
                    textvariable=var,
                    font=("Segoe UI", 9),
                    bg="#252d42",
                    fg="#ffffff",
                    relief="flat",
                    bd=0,
                    width=22
                )
                entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
                self.field_vars[detector_id][key] = var
    
    def add_timing_section(self, parent, detector_id, detector_data):
        """Add timing configuration"""
        section = tk.Frame(parent, bg="#1a1f2e")
        section.pack(fill="x", pady=(10, 0))
        
        section_title = tk.Label(
            section,
            text="⏱️ TIMING SETTINGS",
            font=("Segoe UI", 9, "bold"),
            bg="#1a1f2e",
            fg="#6b7280"
        )
        section_title.pack(anchor="w", pady=(0, 8))
        
        if not hasattr(self, 'field_vars'):
            self.field_vars = {}
        if detector_id not in self.field_vars:
            self.field_vars[detector_id] = {}
        
        # Reaction Delay
        reaction_frame = tk.Frame(section, bg="#1a1f2e")
        reaction_frame.pack(fill="x", padx=5, pady=(0, 8))
        
        tk.Label(
            reaction_frame,
            text="Reaction Delay:",
            font=("Segoe UI", 9),
            bg="#1a1f2e",
            fg="#a0a8b8",
            width=15,
            anchor="w"
        ).pack(side="left")
        
        reaction_sec_var = tk.StringVar(value=str(detector_data.get("reaction_delay_sec", 0)))
        tk.Entry(
            reaction_frame,
            textvariable=reaction_sec_var,
            font=("Segoe UI", 9),
            bg="#252d42",
            fg="#ffffff",
            relief="flat",
            bd=0,
            width=5
        ).pack(side="left", padx=(10, 3))
        
        tk.Label(
            reaction_frame,
            text="sec",
            font=("Segoe UI", 8),
            bg="#1a1f2e",
            fg="#6b7280"
        ).pack(side="left", padx=(0, 10))
        
        reaction_ms_var = tk.StringVar(value=str(detector_data.get("reaction_delay_ms", 100)))
        tk.Entry(
            reaction_frame,
            textvariable=reaction_ms_var,
            font=("Segoe UI", 9),
            bg="#252d42",
            fg="#ffffff",
            relief="flat",
            bd=0,
            width=5
        ).pack(side="left", padx=(0, 3))
        
        tk.Label(
            reaction_frame,
            text="ms",
            font=("Segoe UI", 8),
            bg="#1a1f2e",
            fg="#6b7280"
        ).pack(side="left")
        
        self.field_vars[detector_id]["reaction_delay_sec"] = reaction_sec_var
        self.field_vars[detector_id]["reaction_delay_ms"] = reaction_ms_var
        
        # Click Interval
        interval_frame = tk.Frame(section, bg="#1a1f2e")
        interval_frame.pack(fill="x", padx=5, pady=(0, 8))
        
        tk.Label(
            interval_frame,
            text="Click Interval:",
            font=("Segoe UI", 9),
            bg="#1a1f2e",
            fg="#a0a8b8",
            width=15,
            anchor="w"
        ).pack(side="left")
        
        interval_sec_var = tk.StringVar(value=str(detector_data.get("click_interval_sec", 0)))
        tk.Entry(
            interval_frame,
            textvariable=interval_sec_var,
            font=("Segoe UI", 9),
            bg="#252d42",
            fg="#ffffff",
            relief="flat",
            bd=0,
            width=5
        ).pack(side="left", padx=(10, 3))
        
        tk.Label(
            interval_frame,
            text="sec",
            font=("Segoe UI", 8),
            bg="#1a1f2e",
            fg="#6b7280"
        ).pack(side="left", padx=(0, 10))
        
        interval_ms_var = tk.StringVar(value=str(detector_data.get("click_interval_ms", 500)))
        tk.Entry(
            interval_frame,
            textvariable=interval_ms_var,
            font=("Segoe UI", 9),
            bg="#252d42",
            fg="#ffffff",
            relief="flat",
            bd=0,
            width=5
        ).pack(side="left", padx=(0, 3))
        
        tk.Label(
            interval_frame,
            text="ms",
            font=("Segoe UI", 8),
            bg="#1a1f2e",
            fg="#6b7280"
        ).pack(side="left")
        
        self.field_vars[detector_id]["click_interval_sec"] = interval_sec_var
        self.field_vars[detector_id]["click_interval_ms"] = interval_ms_var
        
        # Cooldown
        cooldown_frame = tk.Frame(section, bg="#1a1f2e")
        cooldown_frame.pack(fill="x", padx=5)
        
        tk.Label(
            cooldown_frame,
            text="Cooldown:",
            font=("Segoe UI", 9),
            bg="#1a1f2e",
            fg="#a0a8b8",
            width=15,
            anchor="w"
        ).pack(side="left")
        
        cooldown_var = tk.StringVar(value=str(detector_data.get("cooldown", 3.0)))
        tk.Entry(
            cooldown_frame,
            textvariable=cooldown_var,
            font=("Segoe UI", 9),
            bg="#252d42",
            fg="#ffffff",
            relief="flat",
            bd=0,
            width=10
        ).pack(side="left", padx=(10, 3))
        
        tk.Label(
            cooldown_frame,
            text="seconds",
            font=("Segoe UI", 8),
            bg="#1a1f2e",
            fg="#6b7280"
        ).pack(side="left")
        
        self.field_vars[detector_id]["cooldown"] = cooldown_var
    
    def add_color_preview(self, parent, detector_data):
        """Add color preview box"""
        preview = tk.Frame(parent, bg="#1a1f2e")
        preview.pack(fill="x", pady=(10, 0))
        
        try:
            r = int(detector_data.get("r", 50))
            g = int(detector_data.get("g", 200))
            b = int(detector_data.get("b", 100))
            color_hex = f"#{r:02x}{g:02x}{b:02x}"
        except:
            color_hex = "#00ff88"
            r = g = b = 0
        
        color_box = tk.Frame(
            preview,
            bg=color_hex,
            height=50,
            highlightthickness=2,
            highlightbackground="#2d3748"
        )
        color_box.pack(fill="x", pady=(0, 8), padx=5)
        color_box.pack_propagate(False)
        
        # RGB display
        rgb_label = tk.Label(
            preview,
            text=f"🎨 RGB({r}, {g}, {b}) {color_hex}",
            font=("Segoe UI", 8),
            bg="#1a1f2e",
            fg="#6b7280",
            padx=5
        )
        rgb_label.pack(anchor="w")

