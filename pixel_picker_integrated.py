"""
Integrated Pixel Picker - Communicates with GamerMacro via IPC
"""
import tkinter as tk
from tkinter import messagebox
import pyautogui
from PIL import ImageGrab
import threading
import json
from pathlib import Path
import time

class IntegratedPixelPicker:
    """Pixel picker that integrates with GamerMacro"""
    
    def __init__(self):
        self.ipc_file = Path.home() / ".gamermacro" / "pixel_picker.json"
        self.ipc_file.parent.mkdir(parents=True, exist_ok=True)
    
    def capture_and_save(self, x, y):
        """Capture pixel and save to IPC file"""
        try:
            img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
            pixel = img.getpixel((0, 0))
            
            if len(pixel) >= 3:
                r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
                
                # Save to IPC file
                data = {
                    "timestamp": time.time(),
                    "x": x,
                    "y": y,
                    "r": r,
                    "g": g,
                    "b": b,
                    "hex": f"#{r:02x}{g:02x}{b:02x}"
                }
                
                with open(self.ipc_file, 'w') as f:
                    json.dump(data, f)
                
                return x, y, r, g, b
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def start_picker(self):
        """Start picker mode"""
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showinfo("Pixel Picker", 
            "🎯 Click on any pixel to capture its color!\n\n"
            "Position will be saved: X, Y\n"
            "Color will be saved: R, G, B")
        
        def on_click(event):
            x, y = event.x_root, event.y_root
            result = self.capture_and_save(x, y)
            
            if result:
                x, y, r, g, b = result
                messagebox.showinfo("Captured!",
                    f"✅ Pixel Captured!\n\n"
                    f"Position: X={x}, Y={y}\n"
                    f"Color: R={r}, G={g}, B={b}\n\n"
                    f"Auto-filled in GamerMacro!")
                root.destroy()
        
        root.bind('<Button-1>', on_click)
        root.mainloop()


if __name__ == "__main__":
    picker = IntegratedPixelPicker()
    picker.start_picker()

