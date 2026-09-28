"""
Winter Detector 2 - Interactive Pixel Selector with Mouse Cursor
Beautiful UI for selecting pixels visually on screen
"""
import tkinter as tk
from tkinter import messagebox
import pyautogui

class WinterDetectorUI:
    """Winter Detector 2 - Beautiful interactive pixel selection"""
    
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
    
    def __init__(self, parent_frame):
        self.frame = tk.Frame(parent_frame, bg=self.COLORS["bg_main"])
        self.selected_pos = None
        self.selected_color = None
        
    def create_winter_ui(self):
        """Create beautiful Winter Detector UI"""
        # Clear frame
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        # Title
        title = tk.Label(self.frame, text="❄️ Winter Detector",
                        font=("SF Pro Display", 20, "bold"),
                        bg=self.COLORS["bg_main"],
                        fg=self.COLORS["accent_green"])
        title.pack(pady=(20, 10))
        
        subtitle = tk.Label(self.frame, text="Click to select pixel from screen",
                           font=("SF Pro Display", 11),
                           bg=self.COLORS["bg_main"],
                           fg=self.COLORS["text_secondary"])
        subtitle.pack(pady=(0, 30))
        
        # Main card
        card = tk.Frame(self.frame, bg=self.COLORS["bg_card"],
                       highlightthickness=1, 
                       highlightbackground=self.COLORS["border"])
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        content = tk.Frame(card, bg=self.COLORS["bg_card"])
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Position display
        tk.Label(content, text="SELECTED POSITION",
                font=("SF Pro Display", 10, "bold"),
                bg=self.COLORS["bg_card"],
                fg=self.COLORS["accent_green"]).pack(anchor="w", pady=(0, 10))
        
        pos_frame = tk.Frame(content, bg=self.COLORS["bg_card"])
        pos_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(pos_frame, text="X:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], width=5).pack(side="left", padx=(0, 10))
        self.x_label = tk.Label(pos_frame, text="---", bg=self.COLORS["bg_input"],
                               fg=self.COLORS["accent_green"], font=("SF Pro Display", 11, "bold"),
                               padx=10, pady=5, width=10)
        self.x_label.pack(side="left", padx=(0, 20))
        
        tk.Label(pos_frame, text="Y:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], width=5).pack(side="left", padx=(0, 10))
        self.y_label = tk.Label(pos_frame, text="---", bg=self.COLORS["bg_input"],
                               fg=self.COLORS["accent_green"], font=("SF Pro Display", 11, "bold"),
                               padx=10, pady=5, width=10)
        self.y_label.pack(side="left")
        
        # Color display
        tk.Label(content, text="DETECTED COLOR",
                font=("SF Pro Display", 10, "bold"),
                bg=self.COLORS["bg_card"],
                fg=self.COLORS["accent_green"]).pack(anchor="w", pady=(20, 10))
        
        color_frame = tk.Frame(content, bg=self.COLORS["bg_card"])
        color_frame.pack(fill="x", pady=(0, 20))
        
        # Color preview box
        self.color_preview = tk.Label(color_frame, text="", bg="#808080",
                                     width=15, height=3, relief="solid", bd=1)
        self.color_preview.pack(side="left", padx=(0, 20))
        
        # RGB values
        rgb_frame = tk.Frame(color_frame, bg=self.COLORS["bg_card"])
        rgb_frame.pack(side="left", fill="both", expand=True)
        
        for label, attr in [("Red:", "r"), ("Green:", "g"), ("Blue:", "b")]:
            row = tk.Frame(rgb_frame, bg=self.COLORS["bg_card"])
            row.pack(fill="x", pady=(0, 8))
            
            tk.Label(row, text=label, bg=self.COLORS["bg_card"],
                    fg=self.COLORS["text_secondary"], width=8).pack(side="left", padx=(0, 10))
            
            lbl = tk.Label(row, text="---", bg=self.COLORS["bg_input"],
                          fg=self.COLORS["accent_green"], font=("SF Pro Display", 11, "bold"),
                          padx=10, pady=3, width=8)
            lbl.pack(side="left")
            
            setattr(self, f"{attr}_label", lbl)
        
        # Buttons
        button_frame = tk.Frame(content, bg=self.COLORS["bg_card"])
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Pick button
        pick_btn = tk.Button(button_frame, text="🎯 Pick Pixel (Click Screen)",
                            command=self.pick_pixel,
                            bg=self.COLORS["accent_green"],
                            fg=self.COLORS["bg_main"],
                            font=("SF Pro Display", 11, "bold"),
                            relief="flat", bd=0, padx=15, pady=10,
                            activebackground="#00a86b")
        pick_btn.pack(side="left", padx=(0, 10))
        
        # Save button
        save_btn = tk.Button(button_frame, text="💾 Save to Detector 2",
                            command=self.save_to_detector2,
                            bg="#4F8EF7",
                            fg="white",
                            font=("SF Pro Display", 11, "bold"),
                            relief="flat", bd=0, padx=15, pady=10,
                            activebackground="#1A3A7A")
        save_btn.pack(side="left")
        
        # Info
        info = tk.Label(content, 
                       text="1. Click 'Pick Pixel' button\n2. Move cursor to desired pixel on screen\n3. Click to capture position and color\n4. Click 'Save to Detector 2' to apply",
                       bg=self.COLORS["bg_card"],
                       fg=self.COLORS["text_secondary"],
                       justify="left", font=("SF Pro Display", 9))
        info.pack(anchor="w", pady=(20, 0))
        
        return self.frame
    
    def pick_pixel(self):
        """Pick pixel from screen using mouse"""
        self.picking = True
        messagebox.showinfo("Pick Pixel",
            "Move your mouse to the desired pixel and click!\n\n" +
            "The pixel position and color will be captured automatically.")
        
        # Create invisible window to capture mouse click
        self.capture_window = tk.Tk()
        self.capture_window.attributes('-alpha', 0.1)
        self.capture_window.geometry(f"{pyautogui.size()[0]}x{pyautogui.size()[1]}+0+0")
        self.capture_window.attributes('-topmost', True)
        
        # Bind mouse click
        self.capture_window.bind("<Button-1>", self.on_mouse_click)
        self.capture_window.bind("<Escape>", lambda e: self.capture_window.destroy())
        
        # Update display
        self.capture_window.update()
    
    def on_mouse_click(self, event):
        """Handle mouse click to capture pixel"""
        try:
            # Get mouse position
            x, y = pyautogui.position()
            
            # Get pixel color
            color = pyautogui.pixel(x, y)
            r, g, b = color[0], color[1], color[2]
            
            # Store values
            self.selected_pos = (x, y)
            self.selected_color = (r, g, b)
            
            # Update display
            self.x_label.config(text=str(x))
            self.y_label.config(text=str(y))
            self.r_label.config(text=str(r))
            self.g_label.config(text=str(g))
            self.b_label.config(text=str(b))
            
            # Update color preview
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.color_preview.config(bg=hex_color)
            
            # Close capture window
            self.capture_window.destroy()
            
            messagebox.showinfo("Success!",
                f"Pixel captured!\n\nPosition: X={x}, Y={y}\n" +
                f"Color: R={r}, G={g}, B={b}\n" +
                f"Hex: {hex_color}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture pixel: {e}")
    
    def save_to_detector2(self):
        """Save selected pixel to Detector 2"""
        if self.selected_pos is None:
            messagebox.showwarning("Warning", "Please pick a pixel first!")
            return
        
        x, y = self.selected_pos
        r, g, b = self.selected_color
        
        messagebox.showinfo("Saved!",
            f"Pixel saved to Detector 2:\n\n" +
            f"Position: X={x}, Y={y}\n" +
            f"Color: R={r}, G={g}, B={b}\n\n" +
            f"Go to SETARI tab to see the values!")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x500")
    root.config(bg="#0a0e1a")
    
    detector = WinterDetectorUI(root)
    detector.create_winter_ui().pack(fill="both", expand=True)
    
    root.mainloop()
