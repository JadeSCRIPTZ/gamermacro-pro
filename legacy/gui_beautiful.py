"""
GamerMacro Pro - Ultra Modern Beautiful GUI
Premium dark theme with gradients, animations, and professional design
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageTk
import io

class BeautifulTheme:
    """Ultra-modern premium theme"""
    
    COLORS = {
        # Primary backgrounds - Deep gradients
        "bg_darkest": "#0a0e1a",        # Deep black
        "bg_dark": "#0f1419",            # Slightly lighter
        "bg_main": "#141820",            # Main dark
        "bg_card": "#1a1f2e",            # Card background
        "bg_input": "#252d42",           # Input background
        "bg_hover": "#1f2937",           # Hover state
        
        # Green accents - Professional
        "green_bright": "#00ff88",       # Bright neon green
        "green_primary": "#00d98e",      # Primary green
        "green_dark": "#00a86b",         # Dark green
        "green_muted": "#1f7a4a",        # Muted green
        
        # Gradients
        "gradient_top": "#1a3a2a",       # Green gradient top
        "gradient_bottom": "#0a0e1a",    # Black gradient bottom
        
        # Text colors
        "text_primary": "#ffffff",       # White
        "text_secondary": "#b0b8c8",     # Light gray
        "text_tertiary": "#7a8494",      # Medium gray
        "text_muted": "#4a5568",         # Muted gray
        
        # Accents
        "border_light": "#2d3748",       # Light border
        "border_accent": "#00ff8844",    # Green border with alpha
        "shadow": "#00000040",           # Shadow
        
        # Status
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
    }
    
    FONTS = {
        "title": ("SF Pro Display", 28, "bold"),
        "heading": ("SF Pro Display", 16, "bold"),
        "subheading": ("SF Pro Display", 12, "bold"),
        "normal": ("SF Pro Display", 11),
        "small": ("SF Pro Display", 10),
        "tiny": ("SF Pro Display", 9),
    }


class ProfileManagerAdvanced:
    """Advanced profile manager with full settings storage"""
    
    def __init__(self):
        self.profiles_dir = Path.home() / ".gamermacro" / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.profiles = {}
        self.current_profile = "Default"
        self.load_profiles()
    
    def get_default_profile(self):
        """Get complete default profile"""
        return {
            "name": "Default",
            "created": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "settings": {
                "x": 100,
                "y": 100,
                "r": 50,
                "g": 200,
                "b": 100,
                "tolerance": 25,
                "delay": 0.5,
                "cooldown": 3.0,
                "timeout": 30,
                "pixelwait": 0.1,
            },
            "modes": {
                "natural_mode": False,
                "auto_recast": False,
            },
            "colors": {
                "theme": "dark",
                "accent_color": "#00d98e",
                "bg_color": "#141820",
                "text_color": "#ffffff",
            },
            "ui_settings": {
                "window_width": 1200,
                "window_height": 800,
                "sidebar_width": 280,
                "font_size": 11,
            }
        }
    
    def load_profiles(self):
        """Load all profiles from disk"""
        try:
            for profile_file in self.profiles_dir.glob("*.json"):
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.profiles[data["name"]] = data
        except:
            pass
        
        if "Default" not in self.profiles:
            self.profiles["Default"] = self.get_default_profile()
            self.save_profile("Default", self.profiles["Default"])
    
    def save_profile(self, name, profile_data):
        """Save profile with all settings"""
        profile_data["name"] = name
        profile_data["last_modified"] = datetime.now().isoformat()
        
        self.profiles[name] = profile_data
        
        profile_file = self.profiles_dir / f"{name}.json"
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def create_profile(self, name, base_profile=None):
        """Create new profile"""
        if base_profile is None:
            base_profile = self.get_default_profile()
        
        new_profile = base_profile.copy()
        new_profile["name"] = name
        new_profile["created"] = datetime.now().isoformat()
        new_profile["last_modified"] = datetime.now().isoformat()
        
        self.save_profile(name, new_profile)
        return True
    
    def delete_profile(self, name):
        """Delete profile"""
        if name == "Default":
            return False
        
        profile_file = self.profiles_dir / f"{name}.json"
        if profile_file.exists():
            profile_file.unlink()
        
        if name in self.profiles:
            del self.profiles[name]
        
        return True
    
    def get_profile_names(self):
        """Get list of profile names"""
        return sorted(self.profiles.keys())


class ModernBeautifulGUI:
    """Ultra-modern beautiful GUI with advanced profile management"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GamerMacro Pro v6.2")
        self.root.geometry("1400x900")
        self.root.config(bg=BeautifulTheme.COLORS["bg_darkest"])
        
        self.profile_mgr = ProfileManagerAdvanced()
        self.current_settings = self.profile_mgr.get_default_profile()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the beautiful UI"""
        # Main container
        main_container = tk.Frame(self.root, bg=BeautifulTheme.COLORS["bg_darkest"])
        main_container.pack(fill="both", expand=True)
        
        # Gradient background
        self.create_gradient_background(main_container)
        
        # Layout: Sidebar + Content
        self.create_sidebar(main_container)
        self.create_main_content(main_container)
    
    def create_gradient_background(self, parent):
        """Create gradient background"""
        gradient = Image.new('RGB', (1, 100))
        pixels = gradient.load()
        
        top_color = tuple(int(BeautifulTheme.COLORS["bg_main"][i:i+2], 16) for i in (1, 3, 5))
        bottom_color = tuple(int(BeautifulTheme.COLORS["bg_darkest"][i:i+2], 16) for i in (1, 3, 5))
        
        for i in range(100):
            ratio = i / 100
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pixels[0, i] = (r, g, b)
        
        gradient = gradient.resize((1400, 900))
        self.bg_image = ImageTk.PhotoImage(gradient)
        
        bg_label = tk.Label(parent, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()
    
    def create_sidebar(self, parent):
        """Create beautiful sidebar"""
        sidebar = tk.Frame(parent, bg=BeautifulTheme.COLORS["bg_main"], 
                          highlightthickness=1, highlightbackground=BeautifulTheme.COLORS["border_light"])
        sidebar.place(x=0, y=0, width=280, relheight=1)
        
        # Logo/Title
        title = tk.Label(sidebar, text="GamerMacro", font=BeautifulTheme.FONTS["heading"],
                        bg=BeautifulTheme.COLORS["bg_main"], fg=BeautifulTheme.COLORS["green_bright"],
                        pady=20)
        title.pack(fill="x")
        
        subtitle = tk.Label(sidebar, text="Pro v6.2", font=BeautifulTheme.FONTS["small"],
                           bg=BeautifulTheme.COLORS["bg_main"], fg=BeautifulTheme.COLORS["text_tertiary"])
        subtitle.pack(fill="x", padx=15)
        
        # Divider
        divider = tk.Frame(sidebar, height=2, bg=BeautifulTheme.COLORS["border_accent"])
        divider.pack(fill="x", padx=15, pady=15)
        
        # Profile Section
        profile_label = tk.Label(sidebar, text="PROFILE", font=BeautifulTheme.FONTS["tiny"],
                                bg=BeautifulTheme.COLORS["bg_main"], 
                                fg=BeautifulTheme.COLORS["text_tertiary"],
                                padx=15, pady=(15, 5))
        profile_label.pack(anchor="w")
        
        # Profile selector with custom style
        self.profile_var = tk.StringVar(value=self.profile_mgr.current_profile)
        profile_combo = ttk.Combobox(sidebar, textvariable=self.profile_var,
                                    values=self.profile_mgr.get_profile_names(),
                                    state="readonly", width=25)
        profile_combo.pack(padx=15, pady=(0, 10), fill="x")
        profile_combo.bind('<<ComboboxSelected>>', self.on_profile_select)
        
        # Action buttons
        btn_load = self.create_sidebar_button(sidebar, "Load Profile", self.load_profile)
        btn_load.pack(fill="x", padx=15, pady=(0, 5))
        
        btn_save = self.create_sidebar_button(sidebar, "Save Profile", self.save_profile)
        btn_save.pack(fill="x", padx=15, pady=(0, 5))
        
        btn_new = self.create_sidebar_button(sidebar, "+ New Profile", self.new_profile)
        btn_new.pack(fill="x", padx=15, pady=(0, 15))
        
        # Divider
        divider2 = tk.Frame(sidebar, height=1, bg=BeautifulTheme.COLORS["border_light"])
        divider2.pack(fill="x", padx=15, pady=10)
        
        # Settings section
        settings_label = tk.Label(sidebar, text="SETTINGS", font=BeautifulTheme.FONTS["tiny"],
                                 bg=BeautifulTheme.COLORS["bg_main"], 
                                 fg=BeautifulTheme.COLORS["text_tertiary"],
                                 padx=15, pady=(0, 5))
        settings_label.pack(anchor="w")
        
        # Tabs
        self.create_sidebar_tab(sidebar, "🎣 Fishing")
        self.create_sidebar_tab(sidebar, "⚙️ Settings")
        self.create_sidebar_tab(sidebar, "📊 Stats")
        self.create_sidebar_tab(sidebar, "📋 Log")
        
        # Status bar at bottom
        status_frame = tk.Frame(sidebar, bg=BeautifulTheme.COLORS["bg_card"])
        status_frame.pack(side="bottom", fill="x", padx=15, pady=15)
        
        status_text = tk.Label(status_frame, text="Ready", 
                              font=BeautifulTheme.FONTS["small"],
                              bg=BeautifulTheme.COLORS["bg_card"],
                              fg=BeautifulTheme.COLORS["green_primary"])
        status_text.pack()
    
    def create_sidebar_button(self, parent, text, command):
        """Create beautiful sidebar button"""
        btn = tk.Button(parent, text=text, command=command,
                       font=BeautifulTheme.FONTS["small"],
                       bg=BeautifulTheme.COLORS["green_primary"],
                       fg=BeautifulTheme.COLORS["bg_darkest"],
                       activebackground=BeautifulTheme.COLORS["green_dark"],
                       activeforeground=BeautifulTheme.COLORS["bg_darkest"],
                       relief="flat", bd=0, padx=12, pady=8,
                       cursor="hand2", highlightthickness=0)
        return btn
    
    def create_sidebar_tab(self, parent, text):
        """Create sidebar navigation tab"""
        tab = tk.Button(parent, text=text,
                       font=BeautifulTheme.FONTS["normal"],
                       bg=BeautifulTheme.COLORS["bg_main"],
                       fg=BeautifulTheme.COLORS["text_secondary"],
                       activebackground=BeautifulTheme.COLORS["bg_card"],
                       activeforeground=BeautifulTheme.COLORS["green_bright"],
                       relief="flat", bd=0, padx=15, pady=10,
                       anchor="w", cursor="hand2", highlightthickness=0)
        tab.pack(fill="x", pady=(0, 2))
    
    def create_main_content(self, parent):
        """Create main content area"""
        content = tk.Frame(parent, bg=BeautifulTheme.COLORS["bg_darkest"])
        content.place(x=280, y=0, relwidth=0.8, relheight=1)
        
        # Header
        header = tk.Frame(content, bg=BeautifulTheme.COLORS["bg_card"], height=80)
        header.pack(fill="x", padx=20, pady=20)
        
        title = tk.Label(header, text="Fishing Automation", 
                        font=BeautifulTheme.FONTS["heading"],
                        bg=BeautifulTheme.COLORS["bg_card"],
                        fg=BeautifulTheme.COLORS["green_bright"])
        title.pack(anchor="w", padx=20, pady=20)
        
        # Cards area
        cards_frame = tk.Frame(content, bg=BeautifulTheme.COLORS["bg_darkest"])
        cards_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Detection card
        self.create_card(cards_frame, "Detection Settings", 0, 0)
        self.create_card(cards_frame, "Timing & Delays", 0, 1)
        self.create_card(cards_frame, "Modes", 1, 0)
        self.create_card(cards_frame, "Colors", 1, 1)
    
    def create_card(self, parent, title, row, col):
        """Create beautiful card"""
        card = tk.Frame(parent, bg=BeautifulTheme.COLORS["bg_card"],
                       highlightthickness=1, highlightbackground=BeautifulTheme.COLORS["border_light"])
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Card title
        card_title = tk.Label(card, text=title, font=BeautifulTheme.FONTS["subheading"],
                             bg=BeautifulTheme.COLORS["bg_card"],
                             fg=BeautifulTheme.COLORS["green_primary"],
                             padx=15, pady=15)
        card_title.pack(fill="x")
        
        # Card content
        content = tk.Frame(card, bg=BeautifulTheme.COLORS["bg_card"])
        content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Add some sample controls
        tk.Label(content, text="Sample content", 
                bg=BeautifulTheme.COLORS["bg_card"],
                fg=BeautifulTheme.COLORS["text_secondary"],
                font=BeautifulTheme.FONTS["small"]).pack()
    
    def on_profile_select(self, event=None):
        """Handle profile selection"""
        profile_name = self.profile_var.get()
        self.current_settings = self.profile_mgr.profiles[profile_name]
    
    def load_profile(self):
        """Load selected profile"""
        profile_name = self.profile_var.get()
        if profile_name in self.profile_mgr.profiles:
            self.current_settings = self.profile_mgr.profiles[profile_name]
            messagebox.showinfo("Success", f"Profile '{profile_name}' loaded!")
    
    def save_profile(self):
        """Save current profile"""
        profile_name = self.profile_var.get()
        self.profile_mgr.save_profile(profile_name, self.current_settings)
        messagebox.showinfo("Success", f"Profile '{profile_name}' saved!")
    
    def new_profile(self):
        """Create new profile"""
        name = simpledialog.askstring("New Profile", "Enter profile name:")
        if name and name not in self.profile_mgr.profiles:
            base = self.profile_mgr.get_default_profile()
            self.profile_mgr.create_profile(name, base)
            self.profile_var.set(name)
            # Update combo box
            messagebox.showinfo("Success", f"Profile '{name}' created!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernBeautifulGUI(root)
    root.mainloop()

