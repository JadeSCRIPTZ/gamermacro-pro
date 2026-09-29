@echo off
echo Building GamerMacro Pro (Nebula UI)...
pip install -r requirements-dev.txt -q
pyinstaller --noconfirm --onefile --windowed --name "GamerMacroPro" --add-data "ui;ui" app.py
echo.
echo Build complete! Check dist\ folder for GamerMacroPro.exe
pause
