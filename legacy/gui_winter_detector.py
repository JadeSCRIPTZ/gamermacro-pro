"""
Winter Tab - Visual Pixel Detector with Cursor Selection
Select pixel colors directly from screen with mouse cursor
"""
import tkinter as tk
from tkinter import messagebox
import pyautogui
from PIL import ImageGrab
import threading

class WinterDetectorUI:
    """Winter tab with visual pixel detection and cursor selection"""
    
    COLORS = {
        "bg_main": "#0a0e1a",
        "bg_card": "#1a1f2e",
        "bg_input": "#252d42",
        "accent_green": "#00d98e",
        "accent_red": "#ef4444",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b8c8",
        "text_tertiary": "#7a8494",
        "border": "#2d3748",
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("GamerMacro Pro - Winter Detector")
        self.root.geometry("1400x900")
        self.root.config(bg=self.COLORS["bg_main"])
        
        self.selected_x = 0
        self.selected_y = 0
        self.selected_r = 0
        self.selected_g = 0
        self.selected_b = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the winter detector UI"""
        main_frame = tk.Frame(self.root, bg=self.COLORS["bg_main"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="Winter - Pixel Detector",
                        font=("SF Pro Display", 24, "bold"),
                        bg=self.COLORS["bg_main"], fg=self.COLORS["accent_green"])
        title.pack(pady=(0, 30))
        
        # Main container
        container = tk.Frame(main_frame, bg=self.COLORS["bg_main"])
        container.pack(fill="both", expand=True)
        
        # Left side - Cursor selector
        self.create_cursor_section(container)
        
        # Right side - Settings
        self.create_settings_section(container)
    
    def create_cursor_section(self, parent):
        """Create cursor selection section"""
        left_frame = tk.Frame(parent, bg=self.COLORS["bg_main"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        # Title
        title = tk.Label(left_frame, text="📍 Select Pixel with Cursor",
                        font=("SF Pro Display", 14, "bold"),
                        bg=self.COLORS["bg_main"], fg=self.COLORS["accent_green"])
        title.pack(pady=(0, 20))
        
        # Instructions
        instructions = tk.Frame(left_frame, bg=self.COLORS["bg_card"],
                               highlightthickness=1, highlightbackground=self.COLORS["border"])
        instructions.pack(fill="x", pady=(0, 20))
        
        instr_text = tk.Label(instructions,
                             text="1. Click 'Start Selection' button\n"
                                  "2. Move cursor to the pixel you want\n"
                                  "3. Press SPACE to capture color\n"
                                  "4. Press ESC to stop selection\n\n"
                                  "The color will be automatically\n"
                                  "captured and saved below!",
                             bg=self.COLORS["bg_card"],
                             fg=self.COLORS["text_secondary"],
                             justify="left",
                             font=("SF Pro Display", 10),
                             padx=20, pady=20)
        instr_text.pack()
        
        # Start button
        self.start_btn = tk.Button(left_frame, text="🎯 Start Selection",
                                  command=self.start_cursor_selection,
                                  font=("SF Pro Display", 12, "bold"),
                                  bg=self.COLORS["accent_green"],
                                  fg=self.COLORS["bg_main"],
                                  activebackground="#00cc6b",
                                  relief="flat", bd=0, padx=20, pady=15,
                                  cursor="hand2", highlightthickness=0)
        self.start_btn.pack(fill="x", pady=(0, 20))
        
        # Stop button
        self.stop_btn = tk.Button(left_frame, text="⛔ Stop Selection",
                                 command=self.stop_cursor_selection,
                                 font=("SF Pro Display", 11),
                                 bg=self.COLORS["accent_red"],
                                 fg=self.COLORS["text_primary"],
                                 activebackground="#cc3333",
                                 relief="flat", bd=0, padx=20, pady=10,
                                 cursor="hand2", highlightthickness=0,
                                 state="disabled")
        self.stop_btn.pack(fill="x", pady=(0, 20))
        
        # Status
        status_card = tk.Frame(left_frame, bg=self.COLORS["bg_card"],
                              highlightthickness=1, highlightbackground=self.COLORS["border"])
        status_card.pack(fill="x")
        
        tk.Label(status_card, text="Status", font=("SF Pro Display", 10, "bold"),
                bg=self.COLORS["bg_card"], fg=self.COLORS["accent_green"],
                padx=15, pady=(15, 10)).pack(anchor="w")
        
        self.status_label = tk.Label(status_card, text="Waiting for selection...",
                                    bg=self.COLORS["bg_card"],
                                    fg=self.COLORS["text_secondary"],
                                    font=("SF Pro Display", 10),
                                    padx=15, pady=(0, 15))
        self.status_label.pack(anchor="w")
    
    def create_settings_section(self, parent):
        """Create settings display section"""
        right_frame = tk.Frame(parent, bg=self.COLORS["bg_main"])
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Title
        title = tk.Label(right_frame, text="⚙️ Detected Values",
                        font=("SF Pro Display", 14, "bold"),
                        bg=self.COLORS["bg_main"], fg=self.COLORS["accent_green"])
        title.pack(pady=(0, 20))
        
        # Position card
        pos_card = tk.Frame(right_frame, bg=self.COLORS["bg_card"],
                           highlightthickness=1, highlightbackground=self.COLORS["border"])
        pos_card.pack(fill="x", pady=(0, 15))
        
        tk.Label(pos_card, text="Position", font=("SF Pro Display", 10, "bold"),
                bg=self.COLORS["bg_card"], fg=self.COLORS["accent_green"],
                padx=15, pady=(15, 10)).pack(anchor="w")
        
        pos_content = tk.Frame(pos_card, bg=self.COLORS["bg_card"])
        pos_content.pack(fill="x", padx=15, pady=(0, 15))
        
        tk.Label(pos_content, text="X:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 10)).pack(side="left", padx=(0, 10))
        self.x_label = tk.Label(pos_content, text="0", bg=self.COLORS["bg_card"],
                               fg=self.COLORS["accent_green"], font=("SF Pro Display", 11, "bold"))
        self.x_label.pack(side="left", padx=(0, 30))
        
        tk.Label(pos_content, text="Y:", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 10)).pack(side="left", padx=(0, 10))
        self.y_label = tk.Label(pos_content, text="0", bg=self.COLORS["bg_card"],
                               fg=self.COLORS["accent_green"], font=("SF Pro Display", 11, "bold"))
        self.y_label.pack(side="left")
        
        # Color card
        color_card = tk.Frame(right_frame, bg=self.COLORS["bg_card"],
                             highlightthickness=1, highlightbackground=self.COLORS["border"])
        color_card.pack(fill="x", pady=(0, 15))
        
        tk.Label(color_card, text="Color (RGB)", font=("SF Pro Display", 10, "bold"),
                bg=self.COLORS["bg_card"], fg=self.COLORS["accent_green"],
                padx=15, pady=(15, 10)).pack(anchor="w")
        
        color_content = tk.Frame(color_card, bg=self.COLORS["bg_card"])
        color_content.pack(fill="x", padx=15, pady=(0, 15))
        
        # Color preview
        self.color_preview = tk.Frame(color_content, bg="#7a7a7a", height=50, width=100)
        self.color_preview.pack(side="left", padx=(0, 20))
        
        # RGB values
        rgb_frame = tk.Frame(color_content, bg=self.COLORS["bg_card"])
        rgb_frame.pack(side="left", fill="x", expand=True)
        
        for label, attr in [("R:", "r"), ("G:", "g"), ("B:", "b")]:
            row = tk.Frame(rgb_frame, bg=self.COLORS["bg_card"])
            row.pack(fill="x", pady=(0, 8))
            
            tk.Label(row, text=label, bg=self.COLORS["bg_card"],
                    fg=self.COLORS["text_secondary"], width=3).pack(side="left")
            
            val_label = tk.Label(row, text="0", bg=self.COLORS["bg_card"],
                                fg=self.COLORS["accent_green"], 
                                font=("SF Pro Display", 10, "bold"), width=4)
            val_label.pack(side="left", padx=(5, 0))
            
            setattr(self, f"{attr}_label", val_label)
        
        # Tolerance card
        tol_card = tk.Frame(right_frame, bg=self.COLORS["bg_card"],
                           highlightthickness=1, highlightbackground=self.COLORS["border"])
        tol_card.pack(fill="x", pady=(0, 15))
        
        tk.Label(tol_card, text="Tolerance", font=("SF Pro Display", 10, "bold"),
                bg=self.COLORS["bg_card"], fg=self.COLORS["accent_green"],
                padx=15, pady=(15, 10)).pack(anchor="w")
        
        tol_content = tk.Frame(tol_card, bg=self.COLORS["bg_card"])
        tol_content.pack(fill="x", padx=15, pady=(0, 15))
        
        tk.Label(tol_content, text="±", bg=self.COLORS["bg_card"],
                fg=self.COLORS["text_secondary"], font=("SF Pro Display", 10)).pack(side="left", padx=(0, 10))
        
        self.tol_var = tk.IntVar(value=25)
        self.tol_scale = tk.Scale(tol_content, from_=0, to=255, orient="horizontal",
                                 variable=self.tol_var, bg=self.COLORS["bg_input"],
                                 fg=self.COLORS["accent_green"], relief="flat", bd=0)
        self.tol_scale.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.tol_label = tk.Label(tol_content, text="25", bg=self.COLORS["bg_card"],
                                 fg=self.COLORS["accent_green"], width=4)
        self.tol_label.pack(side="left")
        self.tol_var.trace("w", lambda *args: self.tol_label.config(text=str(self.tol_var.get())))
        
        # Copy button
        copy_btn = tk.Button(right_frame, text="📋 Copy to Detector 2",
                            command=self.copy_to_detector2,
                            font=("SF Pro Display", 11, "bold"),
                            bg=self.COLORS["accent_green"],
                            fg=self.COLORS["bg_main"],
                            activebackground="#00cc6b",
                            relief="flat", bd=0, padx=15, pady=10,
                            cursor="hand2", highlightthickness=0)
        copy_btn.pack(fill="x", pady=(20, 0))
    
    def start_cursor_selection(self):
        """Start cursor selection mode"""
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Selection active... Press SPACE to capture, ESC to stop",
                                fg=self.COLORS["accent_green"])
        
        # Run selection in separate thread
        thread = threading.Thread(target=self.cursor_selection_loop, daemon=True)
        thread.start()
    
    def stop_cursor_selection(self):
        """Stop cursor selection"""
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Selection stopped", fg=self.COLORS["text_secondary"])
    
    def cursor_selection_loop(self):
        """Loop for cursor selection"""
        from pynput import keyboard
        
        listener = keyboard.Listener(on_press=self.on_key_press)
        listener.start()
        
        def check_listener():
            if listener.is_alive():
                self.root.after(100, check_listener)
            else:
                self.stop_cursor_selection()
        
        check_listener()
    
    def on_key_press(self, key):
        """Handle key press during selection"""
        try:
            if key == keyboard.Key.space:
                self.capture_pixel_at_cursor()
            elif key == keyboard.Key.esc:
                self.stop_cursor_selection()
                return False
        except:
            pass
    
    def capture_pixel_at_cursor(self):
        """Capture pixel color at cursor position"""
        try:
            x, y = pyautogui.position()
            self.selected_x = x
            self.selected_y = y
            
            # Get pixel color
            screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
            pixel = screenshot.getpixel((0, 0))
            
            self.selected_r = pixel[0]
            self.selected_g = pixel[1]
            self.selected_b = pixel[2]
            
            # Update display
            self.root.after(0, self.update_display)
            self.root.after(0, lambda: self.status_label.config(
                text=f"✓ Captured: X={x}, Y={y}, R={self.selected_r}, G={self.selected_g}, B={self.selected_b}",
                fg=self.COLORS["accent_green"]))
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(
                text=f"Error: {str(e)}", fg=self.COLORS["accent_red"]))
    
    def update_display(self):
        """Update display with captured values"""
        self.x_label.config(text=str(self.selected_x))
        self.y_label.config(text=str(self.selected_y))
        
        self.r_label.config(text=str(self.selected_r))
        self.g_label.config(text=str(self.selected_g))
        self.b_label.config(text=str(self.selected_b))
        
        # Update color preview
        hex_color = f"#{self.selected_r:02x}{self.selected_g:02x}{self.selected_b:02x}"
        self.color_preview.config(bg=hex_color)
    
    def copy_to_detector2(self):
        """Copy values to detector 2"""
        messagebox.showinfo("Success",
                          f"Values ready to copy:\n"
                          f"Position: X={self.selected_x}, Y={self.selected_y}\n"
                          f"Color: R={self.selected_r}, G={self.selected_g}, B={self.selected_b}\n"
                          f"Tolerance: ±{self.tol_var.get()}\n\n"
                          f"Open Detector 2 in Settings and paste these values!")


if __name__ == "__main__":
    root = tk.Tk()
    app = WinterDetectorUI(root)
    root.mainloop()

