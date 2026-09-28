"""
Dual Pixel Detection with Configurable Left Click
- First pixel detector: Bobber detection (right-click)
- Second pixel detector: Custom action (left-click multiple times with interval)
"""
import tkinter as tk
from tkinter import ttk, messagebox

class DualPixelDetectionUI:
    """UI for dual pixel detection"""
    
    COLORS = {
        "bg_main": "#0a0e1a",
        "bg_card": "#1a1f2e",
        "bg_input": "#252d42",
        "accent_green": "#00d98e",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b8c8",
        "text_tertiary": "#7a8494",
        "border": "#2d3748",
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("GamerMacro Pro - Dual Pixel Detection")
        self.root.geometry("1600x1000")
        self.root.config(bg=self.COLORS["bg_main"])
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dual pixel detection UI"""
        main_frame = tk.Frame(self.root, bg=self.COLORS["bg_main"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="Dual Pixel Detection System",
                        font=("SF Pro Display", 24, "bold"),
                        bg=self.COLORS["bg_main"], fg=self.COLORS["accent_green"])
        title.pack(pady=(0, 30))
        
        # Main container with two columns
        container = tk.Frame(main_frame, bg=self.COLORS["bg_main"])
        container.pack(fill="both", expand=True)
        
        # Left side - Pixel Detector 1
        self.create_detector_section(container, 
            "Pixel Detector 1 - BOBBER",
            "Fishing (Right Click)",
            side="left",
            detector_id=1)
        
        # Right side - Pixel Detector 2
        self.create_detector_section(container,
            "Pixel Detector 2 - CUSTOM",
            "Action (Left Click)",
            side="right",
            detector_id=2)
    
    def create_detector_section(self, parent, title, subtitle, side, detector_id):
        """Create a detector section"""
        detector_frame = tk.Frame(parent, bg=self.COLORS["bg_main"])
        if side == "left":
            detector_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        else:
            detector_frame.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        # Title
        title_label = tk.Label(detector_frame, text=title,
                              font=("SF Pro Display", 16, "bold"),
                              bg=self.COLORS["bg_main"],
                              fg=self.COLORS["accent_green"])
        title_label.pack(pady=(0, 5))
        
        subtitle_label = tk.Label(detector_frame, text=subtitle,
                                 font=("SF Pro Display", 11),
                                 bg=self.COLORS["bg_main"],
                                 fg=self.COLORS["text_secondary"])
        subtitle_label.pack(pady=(0, 20))
        
        # Card frame
        card = tk.Frame(detector_frame, bg=self.COLORS["bg_card"],
                       highlightthickness=1, highlightbackground=self.COLORS["border"])
        card.pack(fill="both", expand=True)
        
        content = tk.Frame(card, bg=self.COLORS["bg_card"])
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Pixel Position
        self.create_section_title(content, "PIXEL POSITION")
        pos_frame = tk.Frame(content, bg=self.COLORS["bg_card"])
        pos_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(pos_frame, text="X:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        x_var = tk.IntVar(value=640)
        tk.Spinbox(pos_frame, from_=0, to=2560, textvariable=x_var,
                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                  relief="flat", bd=0, width=8).pack(side="left", padx=(0, 20))
        
        tk.Label(pos_frame, text="Y:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        y_var = tk.IntVar(value=360)
        tk.Spinbox(pos_frame, from_=0, to=1440, textvariable=y_var,
                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                  relief="flat", bd=0, width=8).pack(side="left")
        
        # RGB Colors
        self.create_section_title(content, "COLOR DETECTION")
        rgb_data = {}
        for label, key, default in [("Red (R)", "r", 50), ("Green (G)", "g", 200), ("Blue (B)", "b", 100)]:
            row = tk.Frame(content, bg=self.COLORS["bg_card"])
            row.pack(fill="x", pady=(0, 10))
            
            tk.Label(row, text=f"{label}:", bg=self.COLORS["bg_card"],
                    fg=self.COLORS["text_secondary"], width=8).pack(side="left")
            
            var = tk.IntVar(value=default)
            rgb_data[key] = var
            
            scale = tk.Scale(row, from_=0, to=255, orient="horizontal",
                           variable=var, bg=self.COLORS["bg_input"],
                           fg=self.COLORS["accent_green"], relief="flat", bd=0)
            scale.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            value_lbl = tk.Label(row, text=str(default), bg=self.COLORS["bg_card"],
                                fg=self.COLORS["accent_green"], width=4)
            value_lbl.pack(side="left")
            var.trace("w", lambda *args, lbl=value_lbl, v=var: lbl.config(text=str(v.get())))
        
        # Tolerance
        self.create_section_title(content, "TOLERANCE")
        tol_frame = tk.Frame(content, bg=self.COLORS["bg_card"])
        tol_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(tol_frame, text="±", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"]).pack(side="left", padx=(0, 10))
        tol_var = tk.IntVar(value=25)
        tol_scale = tk.Scale(tol_frame, from_=0, to=255, orient="horizontal",
                           variable=tol_var, bg=self.COLORS["bg_input"],
                           fg=self.COLORS["accent_green"], relief="flat", bd=0)
        tol_scale.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tol_lbl = tk.Label(tol_frame, text="25", bg=self.COLORS["bg_card"],
                          fg=self.COLORS["accent_green"], width=4)
        tol_lbl.pack(side="left")
        tol_var.trace("w", lambda *args: tol_lbl.config(text=str(tol_var.get())))
        
        # Actions
        if detector_id == 1:
            self.create_detector1_section(content)
        else:
            self.create_detector2_section(content)
    
    def create_section_title(self, parent, text):
        """Create section title"""
        title = tk.Label(parent, text=text, font=("SF Pro Display", 9, "bold"),
                        bg=self.COLORS["bg_card"], fg=self.COLORS["accent_green"])
        title.pack(anchor="w", pady=(15, 10))
    
    def create_detector1_section(self, parent):
        """Detector 1: Bobber (Right Click)"""
        self.create_section_title(parent, "ACTION - RIGHT CLICK (BOBBER)")
        
        info = tk.Label(parent,
                       text="Fishing Bobber Detection\n- Right-click to catch fish\n- Natural reaction delay",
                       bg=self.COLORS["bg_card"], fg=self.COLORS["text_secondary"],
                       justify="left", font=("SF Pro Display", 10))
        info.pack(pady=10)
        
        delay_frame = tk.Frame(parent, bg=self.COLORS["bg_card"])
        delay_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(delay_frame, text="Reaction Delay (ms):", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 10))
        
        delay_var = tk.IntVar(value=150)
        tk.Spinbox(delay_frame, from_=0, to=5000, textvariable=delay_var,
                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                  relief="flat", bd=0, width=10, font=("SF Pro Display", 10)).pack(side="left")
    
    def create_detector2_section(self, parent):
        """Detector 2: Custom (Left Click with Interval)"""
        self.create_section_title(parent, "ACTION - LEFT CLICK (CONFIGURABLE)")
        
        # Number of clicks
        clicks_frame = tk.Frame(parent, bg=self.COLORS["bg_card"])
        clicks_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(clicks_frame, text="Number of Clicks:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 10)).pack(side="left", padx=(0, 10))
        
        clicks_var = tk.IntVar(value=1)
        tk.Spinbox(clicks_frame, from_=1, to=50, textvariable=clicks_var,
                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                  relief="flat", bd=0, width=5, font=("SF Pro Display", 11)).pack(side="left", padx=(0, 30))
        
        # Click interval
        interval_frame = tk.Frame(parent, bg=self.COLORS["bg_card"])
        interval_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(interval_frame, text="Interval Between Clicks:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 10)).pack(side="left", padx=(0, 10))
        
        # Seconds
        sec_frame = tk.Frame(interval_frame, bg=self.COLORS["bg_card"])
        sec_frame.pack(side="left", padx=(0, 15))
        
        tk.Label(sec_frame, text="Sec:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_tertiary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 5))
        
        sec_var = tk.IntVar(value=0)
        tk.Spinbox(sec_frame, from_=0, to=60, textvariable=sec_var,
                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                  relief="flat", bd=0, width=4, font=("SF Pro Display", 10)).pack(side="left")
        
        # Milliseconds
        ms_frame = tk.Frame(interval_frame, bg=self.COLORS["bg_card"])
        ms_frame.pack(side="left")
        
        tk.Label(ms_frame, text="Ms:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_tertiary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 5))
        
        ms_var = tk.IntVar(value=500)
        tk.Spinbox(ms_frame, from_=0, to=999, textvariable=ms_var,
                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                  relief="flat", bd=0, width=6, font=("SF Pro Display", 10)).pack(side="left")
        
        # Total display
        total_frame = tk.Frame(parent, bg=self.COLORS["bg_card"])
        total_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(total_frame, text="Total Interval:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 10)).pack(side="left", padx=(0, 10))
        
        total_lbl = tk.Label(total_frame, text="0.500s (500ms)", bg=self.COLORS["bg_card"],
                            fg=self.COLORS["accent_green"], font=("SF Pro Display", 10, "bold"))
        total_lbl.pack(side="left")
        
        def update_total(*args):
            total_ms = sec_var.get() * 1000 + ms_var.get()
            total_lbl.config(text=f"{total_ms/1000:.3f}s ({total_ms}ms)")
        
        sec_var.trace("w", update_total)
        ms_var.trace("w", update_total)
        
        # Description
        desc = tk.Label(parent,
                       text="Custom Action:\n- Detect pixel, left-click X times\n- Set interval between clicks\n- Perfect for clicking buttons, harvesting",
                       bg=self.COLORS["bg_card"], fg=self.COLORS["text_secondary"],
                       justify="left", font=("SF Pro Display", 10))
        desc.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = DualPixelDetectionUI(root)
    root.mainloop()
