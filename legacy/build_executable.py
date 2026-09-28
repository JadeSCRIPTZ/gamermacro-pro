"""
Build GamerMacro Pro as standalone Windows executable
"""
import os
import sys
from pathlib import Path

def create_spec_file():
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
a = Analysis(['gamermacro.py'],
    pathex=[],
    binaries=[],
    datas=[('gamermacro_modern_upgrade.py', '.'), ('gui_modern.py', '.')],
    hiddenimports=['tkinter', 'pynput', 'pyautogui'],
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
    name='GamerMacro Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='gamermacro.ico' if os.path.exists('gamermacro.ico') else None,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='GamerMacro Pro')
'''
    with open('GamerMacro-Pro.spec', 'w') as f:
        f.write(spec_content)
    print("OK: spec file")

def create_build_batch():
    script = r"""@echo off
echo Building GamerMacro Pro...
pip install pyinstaller pillow pynput pyautogui -q
pyinstaller GamerMacro-Pro.spec -y
echo.
echo Build complete! Check dist\ folder
pause
"""
    with open('build.bat', 'w') as f:
        f.write(script)
    print("OK: build.bat")

def create_build_sh():
    script = '''#!/bin/bash
echo "Building GamerMacro Pro..."
pip3 install pyinstaller pillow pynput pyautogui
pyinstaller GamerMacro-Pro.spec -y
echo ""
echo "Build complete! Check dist/ folder"
'''
    with open('build.sh', 'w') as f:
        f.write(script)
    os.chmod('build.sh', 0o755)
    print("OK: build.sh")

def create_nsis():
    script = r"""
Name "GamerMacro Pro v6.1"
OutFile "GamerMacro-Pro-Setup.exe"
InstallDir "$PROGRAMFILES\GamerMacro Pro"
RequestExecutionLevel admin

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\GamerMacro Pro\*.*"
  CreateDirectory "$SMPROGRAMS\GamerMacro Pro"
  CreateShortCut "$SMPROGRAMS\GamerMacro Pro\GamerMacro Pro.lnk" "$INSTDIR\GamerMacro Pro.exe"
  CreateShortCut "$DESKTOP\GamerMacro Pro.lnk" "$INSTDIR\GamerMacro Pro.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  RMDir /r "$SMPROGRAMS\GamerMacro Pro"
  Delete "$DESKTOP\GamerMacro Pro.lnk"
  RMDir /r "$INSTDIR"
SectionEnd
"""
    with open('installer.nsi', 'w') as f:
        f.write(script)
    print("OK: installer.nsi")

def create_guide():
    guide = """# GamerMacro Pro - Build Guide

## Build Executable

### Windows
1. Double-click: `build.bat`
2. Wait for completion
3. Check: `dist/GamerMacro Pro/GamerMacro Pro.exe`

### Linux/macOS
bash build.sh

## Create Installer (Windows)

1. Download NSIS: https://nsis.sourceforge.io/
2. Run: makensis installer.nsi
3. Result: GamerMacro-Pro-Setup.exe

## Features
- Standalone executable
- No Python installation needed
- Professional installer
- Start menu shortcuts
- Modern green theme GUI
- Profile management
- Auto-save

## Distribution
- Run directly on Windows 10/11
- Professional installer included
- ~150MB executable
- ~100MB installer

## GitHub
https://github.com/JadeSCRIPTZ/gamermacro-pro
"""
    with open('BUILD_GUIDE.md', 'w') as f:
        f.write(guide)
    print("OK: BUILD_GUIDE.md")

if __name__ == "__main__":
    print("Creating build files...")
    create_spec_file()
    create_build_batch()
    create_build_sh()
    create_nsis()
    create_guide()
    print("\nDone! Run: build.bat (Windows) or ./build.sh (Linux/macOS)")
