"""
Pixel Picker Tool - Click on screen to select pixel color
For Detector 2 configuration
"""
import tkinter as tk
from tkinter import messagebox
import pyautogui
from PIL import ImageGrab, Image, ImageDraw, ImageTk
import threading

class PixelPicker:
    """Screen pixel color picker"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.picking = False
        self.selected_color = None
        self.selected_pos = None
    
    def start_picking(self):
        """Start picking mode"""
        self.picking = True
        self.show_crosshair()
    
    def show_crosshair(self):
        """Show crosshair and listen for clicks"""
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        messagebox.showinfo("Pixel Picker", 
            "Click on screen to pick color...\n\n"
            "The crosshair will help you position.\n"
            "Position: X, Y\n"
            "Color: R, G, B")
        
        # Create transparent overlay
        def on_click(event):
            x, y = event.x_root, event.y_root
            self.capture_pixel(x, y, root)
        
        root.bind('<Button-1>', on_click)
        root.mainloop()
    
    def capture_pixel(self, x, y, root):
        """Capture pixel color at position"""
        try:
            # Get pixel color
            img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
            pixel = img.getpixel((0, 0))
            
            if len(pixel) >= 3:
                r, g, b = pixel[0], pixel[1], pixel[2]
                self.selected_color = (r, g, b)
                self.selected_pos = (x, y)
                
                if self.callback:
                    self.callback(x, y, r, g, b)
                
                messagebox.showinfo("Picked",
                    f"Position: X={x}, Y={y}\n"
                    f"Color: R={r}, G={g}, B={b}")
                
                self.picking = False
                root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture: {e}")
            root.destroy()
    
    def get_selected(self):
        """Get selected color and position"""
        return self.selected_pos, self.selected_color


def start_picker_app():
    """Standalone pixel picker window"""
    root = tk.Tk()
    root.title("Pixel Picker")
    root.geometry("400x300")
    root.config(bg="#0a0e1a")
    
    # Title
    title = tk.Label(root, text="Pixel Color Picker",
                    font=("SF Pro Display", 16, "bold"),
                    bg="#0a0e1a", fg="#00d98e")
    title.pack(pady=20)
    
    # Info
    info = tk.Label(root,
        text="Click button below to pick a pixel color from screen\n\n"
             "Move cursor to desired location\n"
             "Click to capture color\n\n"
             "Returns: Position (X, Y) and Color (R, G, B)",
        bg="#0a0e1a", fg="#b0b8c8",
        justify="left", font=("SF Pro Display", 10))
    info.pack(padx=20, pady=20)
    
    # Results
    results_frame = tk.Frame(root, bg="#1a1f2e", highlightthickness=1,
                            highlightbackground="#2d3748")
    results_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    pos_label = tk.Label(results_frame, text="Position: --",
                        bg="#1a1f2e", fg="#b0b8c8", font=("SF Pro Display", 10))
    pos_label.pack(pady=10)
    
    color_label = tk.Label(results_frame, text="Color: --",
                          bg="#1a1f2e", fg="#b0b8c8", font=("SF Pro Display", 10))
    color_label.pack(pady=10)
    
    color_preview = tk.Frame(results_frame, bg="#ffffff", width=100, height=50)
    color_preview.pack(pady=10)
    
    # Pick button
    def on_pick():
        def callback(x, y, r, g, b):
            pos_label.config(text=f"Position: X={x}, Y={y}")
            color_label.config(text=f"Color: R={r}, G={g}, B={b}")
            color_preview.config(bg=f'#{r:02x}{g:02x}{b:02x}')
        
        picker = PixelPicker(callback=callback)
        # Run in thread so UI doesn't freeze
        threading.Thread(target=picker.show_crosshair, daemon=True).start()
    
    pick_btn = tk.Button(root, text="Pick Color from Screen",
                        command=on_pick,
                        font=("SF Pro Display", 11),
                        bg="#00d98e", fg="#0a0e1a",
                        relief="flat", bd=0, padx=15, pady=10,
                        cursor="hand2")
    pick_btn.pack(pady=20)
    
    root.mainloop()


if __name__ == "__main__":
    start_picker_app()

