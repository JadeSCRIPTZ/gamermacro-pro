"""
GamerMacro Pro - Modern GUI Upgrade Module
Integrates modern styling, profile management, and smooth animations
"""
import json
import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class ModernTheme:
    """Premium dark theme with green/black/gray colors"""
    
    COLORS = {
        # Primary backgrounds
        "bg_primary": "#0a0e1a",        # Deep black
        "bg_secondary": "#141820",      # Dark gray
        "bg_tertiary": "#1a1f2e",       # Medium dark gray
        
        # Accents - Green theme
        "accent_green": "#00d98e",      # Bright neon green
        "accent_green_light": "#1fdf64", # Light green
        "accent_green_dark": "#00a86b", # Dark green
        
        # Text colors
        "text_primary": "#ffffff",      # White
        "text_secondary": "#a0a8b8",    # Light gray
        "text_tertiary": "#6b7280",     # Medium gray
        
        # UI elements
        "border": "#2d3748",            # Dark border
        "border_accent": "#00d98e30",   # Green border with transparency
        "hover": "#1f2937",             # Hover state
        "hover_accent": "#00d98e20",    # Hover with green tint
        
        # Status colors
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
    }
    
    FONTS = {
        "title": ("Segoe UI", 16, "bold"),
        "heading": ("Segoe UI", 12, "bold"),
        "subheading": ("Segoe UI", 10, "bold"),
        "normal": ("Segoe UI", 10),
        "small": ("Segoe UI", 9),
        "tiny": ("Segoe UI", 8),
    }


class ProfileManager:
    """Manage fishing profiles with auto-save"""
    
    def __init__(self):
        self.profiles_dir = Path.home() / ".gamermacro" / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.profiles_dir / "profiles.json"
        self.profiles = {}
        self.current_profile = "default"
        self.load_all_profiles()
    
    def load_all_profiles(self):
        """Load all profiles from disk"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.profiles = data.get("profiles", {})
                    self.current_profile = data.get("current_profile", "default")
            except:
                self._create_default_profile()
        else:
            self._create_default_profile()
    
    def _create_default_profile(self):
        """Create default profile"""
        self.profiles = {
            "default": {
                "name": "Default",
                "created": datetime.now().isoformat(),
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
        }
        self.current_profile = "default"
        self.save_all_profiles()
    
    def save_all_profiles(self):
        """Save all profiles to disk"""
        try:
            data = {
                "profiles": self.profiles,
                "current_profile": self.current_profile,
                "last_saved": datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving profiles: {e}")
            return False
    
    def create_profile(self, name, base_settings):
        """Create new profile"""
        self.profiles[name] = {
            "name": name,
            "created": datetime.now().isoformat(),
            "settings": base_settings
        }
        self.save_all_profiles()
        return True
    
    def delete_profile(self, name):
        """Delete profile"""
        if name == "default":
            return False  # Can't delete default
        
        if name in self.profiles:
            del self.profiles[name]
            self.save_all_profiles()
            return True
        return False
    
    def set_current_profile(self, name):
        """Set active profile"""
        if name in self.profiles:
            self.current_profile = name
            self.save_all_profiles()
            return True
        return False
    
    def get_current_settings(self):
        """Get current profile settings"""
        profile = self.profiles.get(self.current_profile)
        return profile["settings"] if profile else {}
    
    def update_current_settings(self, settings):
        """Update current profile settings"""
        if self.current_profile in self.profiles:
            self.profiles[self.current_profile]["settings"] = settings
            self.save_all_profiles()
            return True
        return False


class ModernComponents:
    """Modern GUI components"""
    
    @staticmethod
    def create_button(parent, text, command, width=25, height=2, color="accent_green"):
        """Create modern button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=ModernTheme.FONTS["normal"],
            bg=ModernTheme.COLORS[color],
            fg=ModernTheme.COLORS["text_primary"],
            activebackground=ModernTheme.COLORS["accent_green_dark"],
            activeforeground=ModernTheme.COLORS["text_primary"],
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            highlightthickness=0,
            width=width,
            height=height,
        )
        
        # Hover effect
        def on_enter(e):
            btn.config(bg=ModernTheme.COLORS["accent_green_dark"])
        
        def on_leave(e):
            btn.config(bg=ModernTheme.COLORS[color])
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    @staticmethod
    def create_card(parent, title="", has_border=True):
        """Create modern card"""
        frame = tk.Frame(
            parent,
            bg=ModernTheme.COLORS["bg_secondary"],
            highlightthickness=1 if has_border else 0,
            highlightbackground=ModernTheme.COLORS["border"],
        )
        
        if title:
            title_frame = tk.Frame(frame, bg=ModernTheme.COLORS["bg_secondary"])
            title_frame.pack(fill="x", padx=15, pady=(15, 10))
            
            title_label = tk.Label(
                title_frame,
                text=title,
                font=ModernTheme.FONTS["subheading"],
                bg=ModernTheme.COLORS["bg_secondary"],
                fg=ModernTheme.COLORS["accent_green"],
            )
            title_label.pack(anchor="w")
        
        content = tk.Frame(frame, bg=ModernTheme.COLORS["bg_secondary"])
        content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        return frame, content
    
    @staticmethod
    def create_label_value(parent, label, value=""):
        """Create label with value display"""
        frame = tk.Frame(parent, bg=ModernTheme.COLORS["bg_secondary"])
        
        label_widget = tk.Label(
            frame,
            text=label,
            font=ModernTheme.FONTS["small"],
            bg=ModernTheme.COLORS["bg_secondary"],
            fg=ModernTheme.COLORS["text_secondary"],
        )
        label_widget.pack(anchor="w", pady=(0, 5))
        
        value_widget = tk.Label(
            frame,
            text=value,
            font=ModernTheme.FONTS["normal"],
            bg=ModernTheme.COLORS["bg_tertiary"],
            fg=ModernTheme.COLORS["accent_green"],
            padx=10,
            pady=8,
            relief="flat",
            bd=0,
        )
        value_widget.pack(fill="x")
        
        return frame, value_widget
    
    @staticmethod
    def create_profile_selector(parent, profiles, current, on_change):
        """Create profile selector with modern styling"""
        frame = tk.Frame(parent, bg=ModernTheme.COLORS["bg_secondary"])
        
        tk.Label(
            frame,
            text="Profil Activ:",
            font=ModernTheme.FONTS["small"],
            bg=ModernTheme.COLORS["bg_secondary"],
            fg=ModernTheme.COLORS["text_secondary"],
        ).pack(anchor="w", pady=(0, 5))
        
        var = tk.StringVar(value=current)
        
        combo = ttk.Combobox(
            frame,
            textvariable=var,
            values=profiles,
            state="readonly",
            width=30,
        )
        combo.pack(fill="x")
        
        # Style combobox
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'TCombobox',
            background=ModernTheme.COLORS["bg_tertiary"],
            foreground=ModernTheme.COLORS["text_primary"],
            fieldbackground=ModernTheme.COLORS["bg_tertiary"],
            borderwidth=1,
        )
        
        def on_select(event=None):
            on_change(var.get())
        
        combo.bind('<<ComboboxSelected>>', on_select)
        
        return frame, var


# Initialize profile manager as global
PROFILE_MANAGER = None

def init_profile_manager():
    """Initialize profile manager"""
    global PROFILE_MANAGER
    PROFILE_MANAGER = ProfileManager()
    return PROFILE_MANAGER

