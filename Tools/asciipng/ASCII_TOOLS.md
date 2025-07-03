# ASCII Screenshot Tools

Lightweight tools for converting screenshots to ASCII art with UI element detection.

## Tools Overview

### Core Converters
- **ascii_converter.py** - Basic ASCII converter (minimal, fast)
- **ascii_converter_enhanced.py** - Enhanced converter with your custom settings
  - Brightness: 200%, Contrast: 95%, Sharpness: 9
  - Threshold: 128, Inverted colors
  - Character set: █▓▒░ (dense to light)

### UI Detection Tools
- **ascii_arrow_detector.py** - Specialized arrow detection (⬇⬆⬅➡)
- **ascii_arrow_advanced.py** - Advanced arrow detection with size/confidence
- **ascii_pattern_replacer.py** - Basic pattern detection and replacement
- **ascii_ui_detector.py** - Advanced UI element detection
- **ascii_ui_comprehensive.py** - Complete UI detection system
  - Arrows, buttons, progress bars, checkboxes
  - Pause/play/stop buttons (⏸▶⏹)
  - Text inputs, menus

### Utility Tools
- **ascii_diff.py** - Compare two ASCII outputs, highlight changes
- **ascii_screenshot.py** - Quick screenshot to ASCII conversion
- **ascii_quick.py** - All-in-one tool with command line options
- **ascii_monitor.py** - Continuous screen monitoring with change detection

## Quick Usage

### Take ASCII Screenshot
```bash
# Quick screenshot with UI detection
./ascii_quick.py

# Specific image with custom width
./ascii_quick.py image.png -w 120

# Quick mode (width=80, no UI detection)
./ascii_quick.py -q

# Save output to file
./ascii_quick.py -s
```

### Monitor Screen Changes
```bash
# Monitor with 2 second interval
./ascii_monitor.py

# Custom settings
./ascii_monitor.py -w 100 -i 1.0

# Monitor for 60 seconds
./ascii_monitor.py -d 60

# Compare two saved states
./ascii_monitor.py -c state1.txt state2.txt
```

### Direct Conversion
```bash
# Basic conversion
python ascii_converter.py image.png

# Enhanced with your settings
python ascii_converter_enhanced.py image.png

# With arrow detection
python ascii_arrow_advanced.py image.png

# Full UI detection
python ascii_ui_comprehensive.py image.png 120
```

## Features

### Character Mapping
- Dense to light: █▓▒░ (space)
- Optimized for terminal display
- Aspect ratio correction (height = width * 0.55)

### UI Element Detection
- **Arrows**: Down (⬇), Up (⬆), Left (⬅), Right (➡)
- **Media**: Play (▶), Pause (⏸), Stop (⏹)
- **Progress**: [████____] with percentage
- **Buttons**: [Button Text]
- **Checkboxes**: ☐ (empty), ☑ (checked)

### Performance
- Lightweight alternative to ShowUI
- Fast processing for quick visual checks
- No heavy analysis, just conversion
- Perfect for rapid screen state detection

## Integration with Windows Agent

All tools integrate with Windows Agent for screenshot capture:
```python
from windows_control import WindowsControl
win = WindowsControl()
win.screenshot("screen.png")
```

## Custom Settings

Your preferred settings are built into enhanced converter:
- Brightness: 2.0 (200%)
- Contrast: 0.95 (95%)
- Sharpness: 9
- Threshold: 128
- Invert: True
- Edge Detection: 1

These make Steam UI and other interfaces more readable in ASCII.