#!/bin/bash
echo "Building GamerMacro Pro..."
pip3 install pyinstaller pillow pynput pyautogui
pyinstaller GamerMacro-Pro.spec -y
echo ""
echo "Build complete! Check dist/ folder"
