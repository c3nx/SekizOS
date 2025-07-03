# ShowUI Command Line Interface (CLI)

A powerful command-line tool for UI element detection using the ShowUI vision model.

## Installation

```bash
# Make sure ShowUI service is running
source showui_env/bin/activate
python showui_service.py &

# The CLI is ready to use
python3 showui_cli.py --help
```

## Usage Examples

### Basic Query
Find a specific UI element:
```bash
python3 showui_cli.py -q "find pause button"
python3 showui_cli.py -q "find download button"
```

### Multiple Queries
Search for multiple elements at once:
```bash
python3 showui_cli.py -q "find pause button" -q "find download progress" -q "find game titles"
```

### Click Mode
Find and click an element automatically:
```bash
python3 showui_cli.py -c "click on download button"
python3 showui_cli.py -c "click pause button"
```

### Analysis Mode
Run comprehensive UI analysis:
```bash
# General UI analysis
python3 showui_cli.py --analyze

# Steam downloads page analysis
python3 showui_cli.py --analyze downloads

# Steam library analysis
python3 showui_cli.py --analyze library
```

### Save Results
Save results to JSON file:
```bash
python3 showui_cli.py -q "find all buttons" -o results.json
```

### Save Marked Screenshot
Save screenshot with detected elements marked:
```bash
python3 showui_cli.py -q "find buttons" -q "find text" -s marked_screenshot.png
```

### JSON Output
Get results in JSON format:
```bash
python3 showui_cli.py -q "find buttons" --json
```

### Analyze Specific Image
Analyze a saved image instead of taking screenshot:
```bash
python3 showui_cli.py -i screenshot.png -q "find buttons"
```

## Command Options

| Option | Description |
|--------|-------------|
| `-q, --query` | Query to send to ShowUI (can be used multiple times) |
| `-c, --click` | Find and click an element |
| `-a, --analyze` | Run comprehensive UI analysis (general/downloads/library) |
| `-i, --image` | Path to image file to analyze |
| `-s, --save-marks` | Save screenshot with detected elements marked |
| `-o, --output` | Save results to JSON file |
| `--json` | Output results as JSON |
| `--show-response` | Show full model response |
| `--url` | ShowUI service URL (default: http://localhost:8766/vision/analyze) |

## Features

- 🎯 **Element Detection**: Find buttons, text, navigation elements, etc.
- 🖱️ **Auto-Click**: Automatically click on found elements
- 📊 **Comprehensive Analysis**: Analyze entire UI with predefined queries
- 🎨 **Visual Marking**: Save screenshots with detected elements marked
- 📁 **Multiple Formats**: Output as text or JSON
- 🖼️ **Flexible Input**: Use live screenshots or analyze saved images
- 🌈 **Colored Output**: Easy-to-read terminal output with colors

## Analysis Modes

### General Analysis
Searches for:
- All buttons
- Clickable elements
- Text elements
- Navigation elements
- Input fields
- Images or icons

### Downloads Analysis
Searches for:
- Download progress
- Pause/resume buttons
- Download speed
- Time remaining
- Game titles
- Install buttons

### Library Analysis
Searches for:
- Game titles
- Play buttons
- Download buttons
- Game cover images
- Categories/filters
- Search bar

## Tips

1. **Be Specific**: Use descriptive queries like "find blue download button" instead of just "find button"
2. **Multiple Queries**: Combine queries to find multiple elements in one command
3. **Save Results**: Use `-o` to save results for later analysis
4. **Visual Debugging**: Use `-s` to save marked screenshots to see what ShowUI detected
5. **Performance**: Analysis mode queries multiple elements but takes longer

## Troubleshooting

- **"Windows control not available"**: Make sure Windows Agent is running
- **"ShowUI service not responding"**: Check if ShowUI service is running on port 8766
- **"Element not found"**: Try different query phrases or use analysis mode
- **Slow response**: ShowUI inference takes 0.5-10 seconds depending on query complexity

## Examples for Common Tasks

### Start a Steam Download
```bash
# Navigate to downloads
python3 showui_cli.py -c "click on View menu"
python3 showui_cli.py -c "click on Downloads"

# Find and click install button
python3 showui_cli.py -c "click on install button"
```

### Monitor Download Progress
```bash
# Check download status
python3 showui_cli.py -q "find download progress" -q "find time remaining" -q "find download speed"

# Pause download
python3 showui_cli.py -c "click pause button"
```

### Analyze Current Screen
```bash
# Full analysis with marked screenshot
python3 showui_cli.py --analyze -s current_ui_analysis.png -o analysis_results.json
```