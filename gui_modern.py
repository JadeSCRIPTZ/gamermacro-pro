"""
GamerMacro Pro - Modern GUI Upgrade
Premium dark theme with green/black/gray colors
Smooth animations, transparency, profile saving
"""
import tkinter as tk
from tkinter import ttk
import json
import os
from pathlib import Path
from datetime import datetime

class ModernGUI:
    """Modern GUI theme with premium colors"""
    
    # Color Palette - Premium Dark Theme
    COLORS = {
        "bg_primary": "#0a0e1a",      # Deep black
        "bg_secondary": "#141820",    # Dark gray
        "bg_tertiary": "#1a1f2e",     # Slightly lighter
        "accent_green": "#00d98e",    # Bright neon green
        "accent_green_dark": "#00a86b", # Dark green
        "text_primary": "#ffffff",    # White text
        "text_secondary": "#a0a8b8",  # Light gray text
        "text_tertiary": "#6b7280",   # Medium gray text
        "border": "#2d3748",          # Dark border
        "success": "#10b981",         # Green success
        "warning": "#f59e0b",         # Orange warning
        "error": "#ef4444",           # Red error
        "hover": "#1f2937",           # Hover state
    }
    
    # Font settings
    FONTS = {
        "title": ("Segoe UI", 14, "bold"),
        "heading": ("Segoe UI", 11, "bold"),
        "normal": ("Segoe UI", 10),
        "small": ("Segoe UI", 9),
    }

class ProfileManager:
    """Manage fishing profiles"""
    
    def __init__(self):
        self.profiles_dir = Path.home() / ".gamermacro" / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.current_profile = "default"
        self.profiles = self.load_profiles()
    
    def load_profiles(self):
        """Load all saved profiles"""
        profiles = {}
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profiles[profile_file.stem] = json.load(f)
            except:
                pass
        
        # Ensure default profile exists
        if "default" not in profiles:
            profiles["default"] = self.get_default_profile()
        
        return profiles
    
    def get_default_profile(self):
        """Get default profile template"""
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
                "cooldown": 3,
                "timeout": 30,
                "pixelwait": 0.1,
                "natural_mode": False,
                "auto_recast": False,
            }
        }
    
    def save_profile(self, profile_name, settings):
        """Save a profile"""
        profile = {
            "name": profile_name,
            "created": self.profiles.get(profile_name, {}).get("created", datetime.now().isoformat()),
            "last_modified": datetime.now().isoformat(),
            "settings": settings
        }
        
        profile_file = self.profiles_dir / f"{profile_name}.json"
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2)
        
        self.profiles[profile_name] = profile
        return True
    
    def delete_profile(self, profile_name):
        """Delete a profile"""
        if profile_name == "default":
            return False  # Can't delete default
        
        profile_file = self.profiles_dir / f"{profile_name}.json"
        if profile_file.exists():
            profile_file.unlink()
        
        if profile_name in self.profiles:
            del self.profiles[profile_name]
        
        return True
    
    def get_profile_names(self):
        """Get list of profile names"""
        return list(self.profiles.keys())
    
    def get_profile(self, profile_name):
        """Get profile settings"""
        return self.profiles.get(profile_name, self.get_default_profile())


class ModernGuiComponents:
    """Modern GUI components with smooth styling"""
    
    @staticmethod
    def create_rounded_button(parent, text, command, width=20, color="accent_green"):
        """Create a modern rounded button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=ModernGUI.FONTS["normal"],
            bg=ModernGUI.COLORS[color],
            fg=ModernGUI.COLORS["text_primary"],
            activebackground=ModernGUI.COLORS["accent_green_dark"],
            activeforeground=ModernGUI.COLORS["text_primary"],
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            highlightthickness=0,
        )
        
        # Smooth hover effect
        def on_enter(e):
            btn.config(bg=ModernGUI.COLORS["accent_green_dark"])
        
        def on_leave(e):
            btn.config(bg=ModernGUI.COLORS[color])
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    @staticmethod
    def create_card(parent, title="", bg_color="bg_secondary"):
        """Create a modern card with title"""
        frame = tk.Frame(
            parent,
            bg=ModernGUI.COLORS[bg_color],
            highlightthickness=1,
            highlightbackground=ModernGUI.COLORS["border"],
        )
        
        if title:
            title_label = tk.Label(
                frame,
                text=title,
                font=ModernGUI.FONTS["heading"],
                bg=ModernGUI.COLORS[bg_color],
                fg=ModernGUI.COLORS["accent_green"],
                padx=15,
                pady=10,
            )
            title_label.pack(fill="x")
            
            separator = tk.Frame(
                frame,
                height=1,
                bg=ModernGUI.COLORS["border"],
            )
            separator.pack(fill="x")
        
        return frame
    
    @staticmethod
    def create_checkbox(parent, text, variable=None):
        """Create modern checkbox"""
        if variable is None:
            variable = tk.BooleanVar()
        
        checkbox = tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            font=ModernGUI.FONTS["normal"],
            bg=ModernGUI.COLORS["bg_secondary"],
            fg=ModernGUI.COLORS["text_primary"],
            activebackground=ModernGUI.COLORS["bg_tertiary"],
            activeforeground=ModernGUI.COLORS["accent_green"],
            selectcolor=ModernGUI.COLORS["bg_tertiary"],
            highlightthickness=0,
            bd=0,
        )
        
        return checkbox, variable
    
    @staticmethod
    def create_spinbox(parent, from_val=0, to_val=100, default=50):
        """Create modern spinbox"""
        var = tk.IntVar(value=default)
        spinbox = tk.Spinbutton(
            parent,
            from_=from_val,
            to=to_val,
            textvariable=var,
            font=ModernGUI.FONTS["normal"],
            bg=ModernGUI.COLORS["bg_tertiary"],
            fg=ModernGUI.COLORS["text_primary"],
            activebackground=ModernGUI.COLORS["accent_green"],
            activeforeground=ModernGUI.COLORS["bg_primary"],
            buttonbackground=ModernGUI.COLORS["accent_green"],
            buttoncursor="hand2",
            highlightthickness=0,
            bd=1,
            relief="flat",
            width=10,
        )
        
        return spinbox, var
    
    @staticmethod
    def create_label_input(parent, label_text, default_value=""):
        """Create label with input field"""
        frame = tk.Frame(parent, bg=ModernGUI.COLORS["bg_secondary"])
        
        label = tk.Label(
            frame,
            text=label_text,
            font=ModernGUI.FONTS["small"],
            bg=ModernGUI.COLORS["bg_secondary"],
            fg=ModernGUI.COLORS["text_secondary"],
        )
        label.pack(anchor="w", padx=5)
        
        var = tk.StringVar(value=default_value)
        entry = tk.Entry(
            frame,
            textvariable=var,
            font=ModernGUI.FONTS["normal"],
            bg=ModernGUI.COLORS["bg_tertiary"],
            fg=ModernGUI.COLORS["text_primary"],
            insertbackground=ModernGUI.COLORS["accent_green"],
            highlightthickness=1,
            highlightbackground=ModernGUI.COLORS["border"],
            highlightcolor=ModernGUI.COLORS["accent_green"],
            bd=0,
            relief="flat",
            padx=10,
            pady=6,
        )
        entry.pack(fill="x", padx=5, pady=(5, 10))
        
        return frame, var


# Example usage in main app
if __name__ == "__main__":
    root = tk.Tk()
    root.title("GamerMacro Pro - Modern GUI")
    root.geometry("600x700")
    root.config(bg=ModernGUI.COLORS["bg_primary"])
    
    # Test modern components
    profile_mgr = ProfileManager()
    
    # Main frame
    main_frame = tk.Frame(root, bg=ModernGUI.COLORS["bg_primary"])
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Title
    title = tk.Label(
        main_frame,
        text="GamerMacro Pro",
        font=("Segoe UI", 20, "bold"),
        bg=ModernGUI.COLORS["bg_primary"],
        fg=ModernGUI.COLORS["accent_green"],
    )
    title.pack(pady=(0, 20))
    
    # Test card with modern components
    card = ModernGuiComponents.create_card(main_frame, "Setari Profil")
    card.pack(fill="x", padx=0, pady=(0, 15))
    
    card_content = tk.Frame(card, bg=ModernGUI.COLORS["bg_secondary"])
    card_content.pack(fill="both", padx=15, pady=15)
    
    # Profile selection
    profile_frame = tk.Frame(card_content, bg=ModernGUI.COLORS["bg_secondary"])
    profile_frame.pack(fill="x", pady=(0, 15))
    
    tk.Label(
        profile_frame,
        text="Selectati Profil:",
        font=ModernGUI.FONTS["small"],
        bg=ModernGUI.COLORS["bg_secondary"],
        fg=ModernGUI.COLORS["text_secondary"],
    ).pack(anchor="w")
    
    profile_names = profile_mgr.get_profile_names()
    profile_var = tk.StringVar(value=profile_names[0])
    
    profile_combo = ttk.Combobox(
        profile_frame,
        textvariable=profile_var,
        values=profile_names,
        state="readonly",
    )
    profile_combo.pack(fill="x", pady=(5, 0))
    
    # Test button
    btn = ModernGuiComponents.create_rounded_button(
        card_content,
        "Salveaza Profil",
        lambda: print("Profile saved!")
    )
    btn.pack(fill="x", pady=(10, 0))
    
    root.mainloop()

