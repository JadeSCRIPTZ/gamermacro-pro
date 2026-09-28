"""
Winter Panel - Complete Detector 2 UI in expandable sidebar section
All Detector 2 controls in one collapsible Winter section
"""
import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab
import threading

class WinterPanel:
    """Complete Winter panel with all Detector 2 controls"""
    
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
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.picking = False
        self.selected_color = None
        self.selected_pos = None
        
        # Create main frame
        self.frame = tk.Frame(parent, bg=self.COLORS["bg_main"])
        
        # Create content
        self.create_ui()
    
    def create_ui(self):
        """Create complete Winter UI"""
        # Header with toggle
        header = tk.Frame(self.frame, bg=self.COLORS["bg_main"])
        header.pack(fill="x", padx=10, pady=(10, 0))
        
        tk.Label(header, text="❄️ WINTER - DETECTOR 2", 
                font=("SF Pro Display", 11, "bold"),
                bg=self.COLORS["bg_main"], 
                fg=self.COLORS["accent_green"]).pack(anchor="w")
        
        # Main card
        card = tk.Frame(self.frame, bg=self.COLORS["bg_card"],
                       highlightthickness=1, 
                       highlightbackground=self.COLORS["border"])
        card.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        content = tk.Frame(card, bg=self.COLORS["bg_card"])
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # ─── PIXEL PICKER SECTION ─────────────────────────────
        self.create_section(content, "🎯 PIXEL PICKER", self.create_picker_section)
        
        # ─── POSITION SECTION ─────────────────────────────────
        self.create_section(content, "📍 POSITION", self.create_position_section)
        
        # ─── COLOR SECTION ────────────────────────────────────
        self.create_section(content, "🎨 COLOR", self.create_color_section)
        
        # ─── TOLERANCE SECTION ────────────────────────────────
        self.create_section(content, "⚙️ TOLERANCE", self.create_tolerance_section)
        
        # ─── CLICK SETTINGS SECTION ───────────────────────────
        self.create_section(content, "🖱️ CLICKS", self.create_clicks_section)
        
        # ─── INTERVAL SECTION ─────────────────────────────────
        self.create_section(content, "⏱️ INTERVAL", self.create_interval_section)
        
        # ─── ENABLE SECTION ───────────────────────────────────
        self.create_section(content, "✅ CONTROL", self.create_control_section)
    
    def create_section(self, parent, title, create_func):
        """Create a collapsible section"""
        sec_title = tk.Label(parent, text=title,
                            font=("SF Pro Display", 9, "bold"),
                            bg=self.COLORS["bg_card"],
                            fg=self.COLORS["accent_green"])
        sec_title.pack(anchor="w", pady=(10, 8))
        
        sec_content = tk.Frame(parent, bg=self.COLORS["bg_card"])
        sec_content.pack(fill="x", pady=(0, 10))
        
        create_func(sec_content)
    
    def create_picker_section(self, parent):
        """Pixel picker section"""
        btn = tk.Button(parent, text="🎯 SELECT PIXEL FROM SCREEN",
                       command=self.start_picker,
                       font=("SF Pro Display", 10, "bold"),
                       bg=self.COLORS["accent_green"],
                       fg=self.COLORS["bg_main"],
                       relief="flat", bd=0, padx=20, pady=8,
                       cursor="hand2",
                       activebackground="#00c97a",
                       activeforeground=self.COLORS["bg_main"],
                       highlightthickness=0)
        btn.pack(fill="x", pady=(0, 8))
        
        # Status
        self.picker_status = tk.Label(parent, text="Ready to pick...",
                                     font=("SF Pro Display", 8),
                                     bg=self.COLORS["bg_card"],
                                     fg=self.COLORS["text_tertiary"])
        self.picker_status.pack(anchor="w")
    
    def create_position_section(self, parent):
        """Position X, Y section"""
        pos_frame = tk.Frame(parent, bg=self.COLORS["bg_card"])
        pos_frame.pack(fill="x")
        
        # X
        x_frame = tk.Frame(pos_frame, bg=self.COLORS["bg_card"])
        x_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(x_frame, text="X:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 8))
        
        self.x_var = tk.IntVar(value=640)
        self.x_entry = tk.Spinbox(x_frame, from_=0, to=3840, textvariable=self.x_var,
                                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                                  relief="flat", bd=0, width=10, font=("SF Pro Display", 10))
        self.x_entry.pack(side="left", fill="x", expand=True)
        
        # Y
        y_frame = tk.Frame(pos_frame, bg=self.COLORS["bg_card"])
        y_frame.pack(fill="x")
        
        tk.Label(y_frame, text="Y:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 8))
        
        self.y_var = tk.IntVar(value=360)
        self.y_entry = tk.Spinbox(y_frame, from_=0, to=2160, textvariable=self.y_var,
                                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                                  relief="flat", bd=0, width=10, font=("SF Pro Display", 10))
        self.y_entry.pack(side="left", fill="x", expand=True)
    
    def create_color_section(self, parent):
        """RGB Color section"""
        # R, G, B in row
        rgb_frame = tk.Frame(parent, bg=self.COLORS["bg_card"])
        rgb_frame.pack(fill="x")
        
        # R
        r_frame = tk.Frame(rgb_frame, bg=self.COLORS["bg_card"])
        r_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Label(r_frame, text="R:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 5))
        
        self.r_var = tk.IntVar(value=150)
        self.r_entry = tk.Spinbox(r_frame, from_=0, to=255, textvariable=self.r_var,
                                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                                  relief="flat", bd=0, width=6, font=("SF Pro Display", 10))
        self.r_entry.pack(side="left", fill="x", expand=True)
        
        # G
        g_frame = tk.Frame(rgb_frame, bg=self.COLORS["bg_card"])
        g_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Label(g_frame, text="G:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 5))
        
        self.g_var = tk.IntVar(value=150)
        self.g_entry = tk.Spinbox(g_frame, from_=0, to=255, textvariable=self.g_var,
                                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                                  relief="flat", bd=0, width=6, font=("SF Pro Display", 10))
        self.g_entry.pack(side="left", fill="x", expand=True)
        
        # B
        b_frame = tk.Frame(rgb_frame, bg=self.COLORS["bg_card"])
        b_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(b_frame, text="B:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 5))
        
        self.b_var = tk.IntVar(value=150)
        self.b_entry = tk.Spinbox(b_frame, from_=0, to=255, textvariable=self.b_var,
                                  bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                                  relief="flat", bd=0, width=6, font=("SF Pro Display", 10))
        self.b_entry.pack(side="left", fill="x", expand=True)
        
        # Color preview
        self.color_preview = tk.Frame(parent, bg="#ffffff", height=30,
                                     highlightthickness=1,
                                     highlightbackground=self.COLORS["border"])
        self.color_preview.pack(fill="x", pady=(8, 0))
        self.color_preview.pack_propagate(False)
    
    def create_tolerance_section(self, parent):
        """Tolerance section"""
        tol_frame = tk.Frame(parent, bg=self.COLORS["bg_card"])
        tol_frame.pack(fill="x")
        
        tk.Label(tol_frame, text="Tolerance ±:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 8))
        
        self.tol_var = tk.IntVar(value=25)
        self.tol_entry = tk.Spinbox(tol_frame, from_=0, to=255, textvariable=self.tol_var,
                                    bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                                    relief="flat", bd=0, width=10, font=("SF Pro Display", 10))
        self.tol_entry.pack(side="left", fill="x", expand=True)
    
    def create_clicks_section(self, parent):
        """Click count section"""
        clicks_frame = tk.Frame(parent, bg=self.COLORS["bg_card"])
        clicks_frame.pack(fill="x")
        
        tk.Label(clicks_frame, text="Number of Clicks:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 8))
        
        self.clicks_var = tk.IntVar(value=1)
        self.clicks_entry = tk.Spinbox(clicks_frame, from_=1, to=50, textvariable=self.clicks_var,
                                       bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                                       relief="flat", bd=0, width=10, font=("SF Pro Display", 10))
        self.clicks_entry.pack(side="left", fill="x", expand=True)
    
    def create_interval_section(self, parent):
        """Interval section"""
        # Seconds
        sec_frame = tk.Frame(parent, bg=self.COLORS["bg_card"])
        sec_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(sec_frame, text="Seconds:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 8))
        
        self.sec_var = tk.IntVar(value=0)
        self.sec_entry = tk.Spinbox(sec_frame, from_=0, to=60, textvariable=self.sec_var,
                                    bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                                    relief="flat", bd=0, width=10, font=("SF Pro Display", 10))
        self.sec_entry.pack(side="left", fill="x", expand=True)
        
        # Milliseconds
        ms_frame = tk.Frame(parent, bg=self.COLORS["bg_card"])
        ms_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(ms_frame, text="Milliseconds:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 9)).pack(side="left", padx=(0, 8))
        
        self.ms_var = tk.IntVar(value=500)
        self.ms_entry = tk.Spinbox(ms_frame, from_=0, to=999, textvariable=self.ms_var,
                                   bg=self.COLORS["bg_input"], fg=self.COLORS["text_primary"],
                                   relief="flat", bd=0, width=10, font=("SF Pro Display", 10))
        self.ms_entry.pack(side="left", fill="x", expand=True)
        
        # Total
        self.total_lbl = tk.Label(parent, text="Total: 0.500s (500ms)",
                                 font=("SF Pro Display", 9, "bold"),
                                 bg=self.COLORS["bg_card"],
                                 fg=self.COLORS["accent_green"])
        self.total_lbl.pack(anchor="w", pady=(0, 0))
        
        def update_total(*args):
            total_ms = self.sec_var.get() * 1000 + self.ms_var.get()
            self.total_lbl.config(text=f"Total: {total_ms/1000:.3f}s ({total_ms}ms)")
        
        self.sec_var.trace("w", update_total)
        self.ms_var.trace("w", update_total)
    
    def create_control_section(self, parent):
        """Enable/Disable control"""
        self.enabled_var = tk.BooleanVar(value=False)
        tk.Checkbutton(parent,
            text="Enable Winter (Detector 2)",
            variable=self.enabled_var,
            font=("SF Pro Display", 10),
            bg=self.COLORS["bg_card"],
            fg=self.COLORS["text_primary"],
            selectcolor=self.COLORS["bg_input"],
            activebackground=self.COLORS["bg_card"],
            activeforeground=self.COLORS["text_primary"],
            highlightthickness=0).pack(anchor="w")
        
        self.status_lbl = tk.Label(parent, text="Status: Dezactivat",
                                  font=("SF Pro Display", 8),
                                  bg=self.COLORS["bg_card"],
                                  fg=self.COLORS["text_tertiary"])
        self.status_lbl.pack(anchor="w", pady=(4, 0))
    
    def start_picker(self):
        """Start pixel picking"""
        messagebox.showinfo("Pixel Picker",
            "Click anywhere on screen to pick color\n\n"
            "Position and color will auto-fill!")
        
        def pick():
            self.picking = True
            import pyautogui
            
            try:
                import time
                time.sleep(0.5)  # Delay to let user position
                
                x, y = pyautogui.position()
                img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
                pixel = img.getpixel((0, 0))
                
                if len(pixel) >= 3:
                    r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
                    
                    # Auto-fill all fields
                    self.x_var.set(x)
                    self.y_var.set(y)
                    self.r_var.set(r)
                    self.g_var.set(g)
                    self.b_var.set(b)
                    
                    # Update preview
                    hex_color = f'#{r:02x}{g:02x}{b:02x}'
                    self.color_preview.config(bg=hex_color)
                    
                    self.picker_status.config(
                        text=f"✓ Picked: X={x}, Y={y}, RGB({r},{g},{b})",
                        fg=self.COLORS["accent_green"])
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")
            finally:
                self.picking = False
        
        # Run in thread
        threading.Thread(target=pick, daemon=True).start()
    
    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)
    
    def get_values(self):
        """Get all values"""
        return {
            "x": self.x_var.get(),
            "y": self.y_var.get(),
            "r": self.r_var.get(),
            "g": self.g_var.get(),
            "b": self.b_var.get(),
            "tolerance": self.tol_var.get(),
            "clicks": self.clicks_var.get(),
            "interval_sec": self.sec_var.get(),
            "interval_ms": self.ms_var.get(),
            "enabled": self.enabled_var.get()
        }


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Winter Panel")
    root.geometry("500x900")
    root.config(bg="#0a0e1a")
    
    panel = WinterPanel(root)
    panel.pack(fill="both", expand=True)
    
    def show_values():
        print(panel.get_values())
    
    tk.Button(root, text="Get Values", command=show_values,
             bg="#00d98e", fg="#0a0e1a").pack(pady=20)
    
    root.mainloop()

