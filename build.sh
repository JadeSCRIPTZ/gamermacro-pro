#!/bin/bash
echo "Building GamerMacro Pro (Nebula UI)..."
pip3 install -r requirements-dev.txt
pyinstaller --noconfirm --onefile --windowed --name "GamerMacroPro" --add-data "ui:ui" app.py
echo ""
echo "Build complete! Check dist/ folder"
