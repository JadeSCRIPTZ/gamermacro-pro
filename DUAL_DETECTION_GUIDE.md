# GamerMacro Pro v6.2+ - Dual Pixel Detection System

## 🔍 Dual Pixel Detection Features

### Detector 1: Bobber Detection (Right-Click)
Default detector for fishing automation
- Detects bobber movement
- Performs RIGHT-CLICK actions
- Default: 2 clicks per detection
- Fully customizable

### Detector 2: Custom Detection (Left-Click)
Additional detector for custom automation
- Detects any pixel color
- Performs LEFT-CLICK actions (or right/double)
- Customizable click count
- Independent timing

## ⚙️ Configuration

### Pixel Detection Settings
Each detector independently configures:

**Pixel Coordinates:**
- X Position (horizontal - 0 to 1920)
- Y Position (vertical - 0 to 1080)

**Color Detection:**
- Red (R): 0-255
- Green (G): 0-255
- Blue (B): 0-255
- Tolerance: ±0-50 (color matching threshold)

### Click Action Settings

**Click Type (Choose one):**
- `left_click` - Left mouse button
- `right_click` - Right mouse button
- `double_click` - Double left-click

**Number of Clicks:**
- Set how many times to click per detection
- Range: 1-10 clicks
- Example: Bobber = 2 clicks, Custom = 1 click

### ⏱️ Timing Configuration

Each detector has independent timing:

**Reaction Delay:**
- Delay before performing action after detection
- Format: Seconds + Milliseconds
- Example: 0 sec + 100 ms = 100ms total
- Use for human-like timing

**Click Interval:**
- Time between multiple clicks
- Format: Seconds + Milliseconds
- Example: 0 sec + 500 ms = 500ms between clicks
- Only applies when click_count > 1

**Cooldown:**
- Waiting time after action completes
- Format: Seconds (decimal)
- Example: 3.0 seconds
- Prevents rapid re-triggering

## 📋 Example Configurations

### Hypixel Fishing (Detector 1)
```
Name: 🎣 Bobber Detection
Enabled: Yes

Pixel Color:
  X: 640, Y: 360
  RGB: (50, 200, 100) - Green bobber
  Tolerance: 25

Action:
  Type: right_click
  Clicks: 2

Timing:
  Reaction: 0s + 100ms
  Interval: 0s + 500ms
  Cooldown: 3.0s
```

### Custom Mining (Detector 2)
```
Name: ⚡ Custom Detection
Enabled: Yes

Pixel Color:
  X: 800, Y: 400
  RGB: (255, 150, 50) - Orange ore
  Tolerance: 15

Action:
  Type: left_click
  Clicks: 1

Timing:
  Reaction: 0s + 50ms
  Interval: 0s + 300ms
  Cooldown: 1.0s
```

## 🎮 Usage Scenarios

### Dual Automation
Run both detectors simultaneously:
1. Detector 1 (Bobber) → Right-click to catch
2. Detector 2 (Custom) → Left-click for other action
3. Each detector independent timing

### Sequential Detection
Use if/then logic:
1. Detect Bobber (Detector 1) → Catch fish
2. After cooldown → Detect next bobber
3. Detector 2 on standby

### Color Sensitivity
Adjust tolerance for lighting conditions:
- High tolerance (30+): Works in different lighting
- Low tolerance (5-15): Precise color matching
- Test in your game environment

## 💾 Profile Saving

Each profile saves:
- Both detector configurations
- All pixel settings
- All action settings
- All timing settings

Switch profiles instantly - both detectors update!

## 🎯 Tips & Tricks

**Finding Pixel Coordinates:**
1. Know your screen resolution (usually 1920x1080)
2. Bobber typically center: (960, 540)
3. Use color picker tool to find RGB values
4. Adjust tolerance if detection fails

**Reaction Delay:**
- Fishing: 50-150ms (human-like)
- Mining: 20-50ms (faster)
- Crafting: 100-200ms (deliberate)

**Click Interval:**
- Reel animation: 400-600ms
- Double-click: 200-300ms
- Rapid clicks: 100-200ms

**Cooldown:**
- Between actions: 1-3 seconds
- Prevent spam detection: 0.5-1.0 seconds
- Long recovery: 5+ seconds

## 🔧 Advanced

### Custom Color Detection
1. Screenshot your screen
2. Use eyedropper tool to get RGB
3. Test with tolerance 10-25
4. Adjust tolerance up if unreliable

### Multiple Macros
Create profiles for different games:
- Profile "Hypixel Fishing" - Bobber only
- Profile "Mining" - Ore detection
- Profile "Clicking" - Button clicking
- Switch instantly between profiles

### Disable Detectors
- Detector 1 disabled = Normal fishing mode
- Detector 2 disabled = Default behavior
- Both disabled = Idle (nothing triggers)

## 📊 Performance Tips

- **CPU Usage**: Pixel detection ~5-10% per detector
- **Accuracy**: Better in consistent lighting
- **Stability**: Test timing settings before long sessions
- **Reliability**: Log file tracks all detections

## ⚡ Troubleshooting

**Detection not working:**
- Check pixel coordinates are correct
- Verify RGB values match detected color
- Increase tolerance value
- Test detection in different lighting

**Wrong clicks being sent:**
- Verify click type (left/right/double)
- Check click count setting
- Confirm mouse is in game window

**Timing issues:**
- Increase reaction delay if too fast
- Increase interval between clicks
- Adjust cooldown for game response time

---

**GamerMacro Pro - Professional Dual Pixel Detection** 🎮
