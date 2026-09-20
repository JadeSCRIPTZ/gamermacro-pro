@echo off
echo Building GamerMacro Pro...
pip install pyinstaller pillow pynput pyautogui -q
pyinstaller GamerMacro-Pro.spec -y
echo.
echo Build complete! Check dist\ folder
pause
