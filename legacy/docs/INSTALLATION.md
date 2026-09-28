# GamerMacro Pro - Complete Installation Guide

## For End Users (Just Want to Use It)

### Windows
1. Download: `GamerMacro-Pro-Setup.exe` from Releases
2. Run installer
3. Follow prompts
4. App appears in Start Menu & Desktop
5. Double-click to launch

### macOS/Linux
1. Download: `GamerMacro-Pro` from Releases
2. Make executable: `chmod +x GamerMacro-Pro`
3. Run: `./GamerMacro-Pro`

## For Developers (Want to Build From Source)

### Requirements
- Python 3.8+
- Windows 10/11 (for executable)
- 500MB free disk space

### Build Steps

#### Windows
```batch
# 1. Clone repository
git clone https://github.com/JadeSCRIPTZ/gamermacro-pro.git
cd gamermacro-pro

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Build executable
build.bat

# 4. Find in dist/GamerMacro Pro/
```

#### Linux/macOS
```bash
# 1. Clone
git clone https://github.com/JadeSCRIPTZ/gamermacro-pro.git
cd gamermacro-pro

# 2. Install
pip3 install -r requirements-dev.txt

# 3. Build
./build.sh

# 4. Find in dist/GamerMacro Pro/
```

### Creating Windows Installer

1. Install NSIS: https://nsis.sourceforge.io/
2. Run: `makensis installer.nsi`
3. Get: `GamerMacro-Pro-Setup.exe`

## First Run

1. Open app
2. Go to: SETARI tab
3. Click: "Salveaza Profil"
4. Settings saved automatically
5. Next time, just load profile

## Profile Management

- **Create**: Click "+ Profil Nou"
- **Load**: Select from dropdown, click "Incarca Profil"
- **Save**: Click "Salveaza Profil" after changes
- **Profiles stored in**: `~/.gamermacro/profiles/`

## Features

✅ Modern green/black/gray theme
✅ Smooth animations & transitions
✅ Profile save/load
✅ Auto-recast option
✅ Natural mode
✅ Full pixel detection
✅ Timeout recalibration
✅ Real-time statistics
✅ Activity logging

## Troubleshooting

### "App won't start"
- Windows: Make sure antivirus allows it
- macOS: Right-click → Open
- Linux: Check permissions: `chmod +x GamerMacro-Pro`

### "Profiles not saving"
- Check folder: `~/.gamermacro/profiles/`
- Make sure folder has write permissions
- Try: `chmod 777 ~/.gamermacro`

### "Settings not loading"
- Click "Incarca Profil" button
- Select profile from dropdown first

## Support

GitHub Issues: https://github.com/JadeSCRIPTZ/gamermacro-pro/issues
