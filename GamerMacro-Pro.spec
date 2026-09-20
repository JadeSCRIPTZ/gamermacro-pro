# -*- mode: python ; coding: utf-8 -*-
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
