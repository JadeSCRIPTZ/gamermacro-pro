# GamerMacro Pro - Dual Pixel Detection System

## Overview

Two independent pixel detectors working simultaneously:
- **Detector 1**: Bobber detection (Right-click for fishing)
- **Detector 2**: Custom action (Left-click with configurable interval)

## Detector 1: Bobber Detection (Right-Click)

### Purpose
Automatic fishing bobber detection and catching.

### Configuration

**Pixel Position:**
- X Coordinate: Screen horizontal position (0-2560)
- Y Coordinate: Screen vertical position (0-1440)

**Color Detection:**
- Red (R): 0-255
- Green (G): 0-255
- Blue (B): 0-255
- Tolerance (±): 0-255

**Action:**
- Right-click on bobber detection
- Reaction delay: 0-5000ms (milliseconds)
- Simulates natural reaction time

### Example Configuration
```
Pixel Position: X=640, Y=360 (center of screen)
Color: R=50, G=200, B=100 (greenish)
Tolerance: ±25
Reaction Delay: 150ms
```

When detector finds pixel matching color (with tolerance),
it waits 150ms then right-clicks to catch fish.

## Detector 2: Custom Action (Left-Click)

### Purpose
Perform custom actions when pixel is detected.
Perfect for:
- Clicking harvest buttons
- Clicking collect rewards
- Clicking open chests
- Any repetitive clicking task

### Configuration

**Pixel Position:**
- X Coordinate: Button/action location
- Y Coordinate: Button/action location

**Color Detection:**
- Red (R): Color component 0-255
- Green (G): Color component 0-255
- Blue (B): Color component 0-255
- Tolerance (±): Color matching tolerance

**Click Configuration:**

1. **Number of Clicks**: 1-50
   - How many times to click
   - Example: 3 clicks to harvest

2. **Interval Between Clicks**: Configurable
   - Seconds: 0-60 seconds
   - Milliseconds: 0-999 milliseconds
   - Total: Displayed in real-time

### Example Configurations

#### Single Click
```
Clicks: 1
Interval: 0s 0ms
Use: Single button click
```

#### Rapid Clicks
```
Clicks: 5
Interval: 0s 100ms (100 milliseconds)
Total: 0.1s between each click
Use: Spam-clicking harvest button
```

#### Timed Clicks
```
Clicks: 3
Interval: 2s 500ms (2.5 seconds)
Total: 2.5s between each click
Use: Clicking with delay between harvests
```

#### Complex Interval
```
Clicks: 10
Interval: 1s 750ms (1.75 seconds)
Total: 1.75s between each click
Use: Automated collection with gaps
```

## How It Works

### Detection Process
1. **Scanner checks pixel at X, Y coordinates**
2. **Compares detected color to configured color**
3. **If within tolerance range, action triggers**

### Tolerance Explained
```
Configured Color: R=100, G=150, B=200
Tolerance: ±25

Pixel detected: R=110, G=155, B=195
- Red: 110 vs 100 ✓ (difference of 10, within 25)
- Green: 155 vs 150 ✓ (difference of 5, within 25)
- Blue: 195 vs 200 ✓ (difference of 5, within 25)
- MATCH! Action triggers

Pixel detected: R=140, G=200, B=200
- Red: 140 vs 100 ✗ (difference of 40, exceeds 25)
- NO MATCH! Action doesn't trigger
```

### Action Execution

**Detector 1 (Right-Click):**
```
Pixel detected with matching color
↓
Wait [Reaction Delay] milliseconds
↓
Right-click mouse button
↓
Loop back to detection
```

**Detector 2 (Left-Click):**
```
Pixel detected with matching color
↓
For i = 1 to [Number of Clicks]:
  - Left-click mouse button
  - Wait [Interval] (Sec + Ms)
↓
Clicks complete
↓
Loop back to detection
```

## Profile Saving

Each profile stores:

### Detector 1
- Position (X, Y)
- Color (R, G, B)
- Tolerance (±)
- Reaction Delay (ms)
- Enabled/Disabled status

### Detector 2
- Position (X, Y)
- Color (R, G, B)
- Tolerance (±)
- Number of Clicks
- Interval (Seconds + Milliseconds)
- Enabled/Disabled status

### Example Profile JSON
```json
{
  "name": "Fishing Farm",
  "detectors": {
    "detector1": {
      "enabled": true,
      "x": 640,
      "y": 360,
      "r": 50,
      "g": 200,
      "b": 100,
      "tolerance": 25,
      "reaction_delay_ms": 150
    },
    "detector2": {
      "enabled": false,
      "x": 800,
      "y": 500,
      "r": 150,
      "g": 150,
      "b": 150,
      "tolerance": 20,
      "num_clicks": 1,
      "interval_sec": 0,
      "interval_ms": 0
    }
  }
}
```

## Best Practices

### Finding Exact Pixel Position
1. Use screen capture tool
2. Measure pixels from top-left (0, 0)
3. Test with high tolerance first (50-100)
4. Gradually reduce tolerance to find exact match

### Color Detection Tips
- Use color picker tool to get exact RGB
- Start with tolerance of 50
- Reduce by 5-10 until stable detection
- Test multiple locations to verify consistency

### Reaction Delay
- Fishing: 100-200ms (natural human reaction)
- Clicking: 0-100ms (instant to human-like)
- Farming: 50-150ms (varies by task)

### Click Interval
- Rapid clicks: 50-200ms
- Normal clicks: 300-500ms
- Spaced clicks: 1-5 seconds
- Auto-complete: 5-10 seconds

## Common Use Cases

### Hypixel Skyblock Fishing
```
Detector 1: Bobber detection
- Position: Center of screen
- Color: Bobber color
- Tolerance: 20-30
- Reaction Delay: 150ms
- Result: Auto-catch fish
```

### Garden Harvesting
```
Detector 2: Harvest button
- Position: Harvest button location
- Color: Button color
- Tolerance: 25
- Clicks: 1
- Interval: 0ms (instant)
- Result: Single-click harvesting
```

### Batch Collection
```
Detector 2: Collect reward button
- Position: Button location
- Color: Button color
- Tolerance: 20
- Clicks: 3 (multiple rewards)
- Interval: 500ms (0.5s between)
- Result: Collect 3 times with 0.5s gaps
```

### Automated Farming
```
Detector 1: Crop detection
- Auto-harvest when crop ready

Detector 2: Plant button
- Auto-plant after harvest
- Clicks: 1
- Interval: 1s (1 second gap)
- Result: Full farm automation
```

## Troubleshooting

### Detector Not Triggering
- Check pixel position (use screenshot)
- Verify color values (use color picker)
- Increase tolerance
- Ensure pixel position is on screen

### False Positives
- Decrease tolerance
- Make sure colors are unique
- Check lighting (shadows affect colors)
- Verify not detecting wrong element

### Click Not Working
- Verify mouse pointer is on screen
- Check click interval isn't too short
- Ensure game window is active
- Try increasing number of retries

## Advanced Timing

### Millisecond Precision
Example intervals:
- 50ms = 0s + 50ms (very rapid)
- 500ms = 0s + 500ms (half second)
- 1500ms = 1s + 500ms (one and half seconds)
- 5000ms = 5s + 0ms (five seconds)

### Real-World Examples
- Single button click: 0ms
- Auto-attack spam: 100-200ms
- Farm planting cycle: 1000-2000ms
- Batch collection: 500-1000ms

---

**GamerMacro Pro - Dual Detection System**
Full automation power in your hands! ⚙️
