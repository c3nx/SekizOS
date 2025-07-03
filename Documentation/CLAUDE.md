# SekizOS - Claude Code Development Guide

## 🎯 Project Overview

SekizOS is an advanced AI assistant toolkit that combines Windows automation, visual AI capabilities, and intelligent app management. It's designed to work seamlessly with Claude Code for enhanced development workflows.

## 🏗️ Architecture

```
SekizOS/
├── Core Components
│   ├── windows_control.py     # Windows Agent interface
│   ├── app_launcher.py        # Smart app management
│   └── showui_cli.py          # Visual AI interface
├── Tools
│   ├── asciipng/              # ASCII art conversion tools
│   └── windows-agent-tool/    # Windows automation
└── Services
    └── showui_service.py      # ShowUI vision model service
```

## 🚀 Quick Start

### Prerequisites

- Windows 11 (tested on IoT Enterprise LTSC Build 26100)
- Python 3.10+
- NVIDIA GPU with 8GB+ VRAM (for ShowUI)
- Windows Agent installed and running

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/SekizOS.git
cd SekizOS

# Create virtual environment
python -m venv showui_env
source showui_env/bin/activate  # On Windows: showui_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install ShowUI components
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate pillow gradio
```

## 🔧 ShowUI Setup & Troubleshooting

### Common Issues We Solved

#### 1. Token Mismatch Error
**Problem**: "Image features and image tokens do not match: tokens: 1, features 2304"

**Solution**: Use AutoProcessor with correct pixel constraints
```python
# ❌ Wrong way
processor = Qwen2VLImageProcessor()

# ✅ Correct way
processor = AutoProcessor.from_pretrained(
    "showlab/ShowUI-2B",
    min_pixels=256*28*28,
    max_pixels=1344*28*28
)
```

#### 2. Model Loading Issues
**Problem**: Model fails to load or runs out of memory

**Solution**: Use device_map and torch_dtype
```python
model = Qwen2VLForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="cuda"
)
```

#### 3. Windows UI Automation Failures
**Problem**: Windows key, Start menu, and UI interactions don't work

**Root Cause**: Windows 11 UIPI (User Interface Privilege Isolation) blocks simulated inputs

**Solution**: Use process-based approach instead of UI simulation
```python
# ❌ Doesn't work
win.key('win')  # Blocked by Windows security

# ✅ Works
win.powershell('Start-Process "steam://open/downloads"')
```

### ShowUI Service Configuration

Create `showui_config.json`:
```json
{
  "model_path": "showlab/ShowUI-2B",
  "device": "cuda",
  "max_workers": 2,
  "timeout": 30,
  "cache_dir": "./model_cache"
}
```

## 📱 App Management System

### Allowed Apps Configuration

Edit `allowed_apps.json` to control which apps can be launched:

```json
{
  "steam": {
    "name": "Steam",
    "launch_methods": [
      {"type": "uri", "command": "steam://"},
      {"type": "path", "command": "C:\\Program Files (x86)\\Steam\\Steam.exe"}
    ],
    "pages": {
      "library": "steam://open/library",
      "downloads": "steam://open/downloads"
    }
  }
}
```

### Usage Examples

```bash
# List available apps
./app_launcher.py list

# Launch an app
./app_launcher.py launch steam
./app_launcher.py launch steam:downloads

# Close an app
./app_launcher.py close steam
```

## 🖼️ Visual AI with ShowUI

### Basic Usage

```bash
# Take screenshot and analyze
./showui_cli.py -q "Find download button"

# Click on found element
./showui_cli.py -q "Click pause button" -c

# Analyze specific image
./showui_cli.py -i screenshot.png -q "Find all buttons"
```

### Advanced Features

```python
from showui_cli import ShowUIClient

client = ShowUIClient()
result = client.process_request(
    query="Find download progress bars",
    image_path="steam_downloads.png"
)

if result['found']:
    x, y = result['click_point']
    # Perform action at coordinates
```

## 🔤 ASCII Art Tools

Quick visual verification without heavy processing:

```bash
# Convert screenshot to ASCII
python asciipng/ascii_quick.py

# Monitor screen changes
python asciipng/ascii_monitor.py -i 2.0

# Compare two states
python asciipng/ascii_monitor.py -c before.txt after.txt
```

## 🛠️ Development Workflow

### 1. Windows Automation
```python
from windows_control import WindowsControl

win = WindowsControl()

# Take screenshot
win.screenshot("current.png")

# Run PowerShell command
result = win.powershell('Get-Process | Select-Object Name')

# Click at coordinates
win.click(100, 200)

# Type text
win.type("Hello World")
```

### 2. Process Management
```python
# Launch app with URI
win.powershell('Start-Process "steam://open/downloads"')

# Bring window to front
win.powershell('''
$proc = Get-Process steam
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@
[Win32]::SetForegroundWindow($proc.MainWindowHandle)
''')
```

### 3. Visual Detection Pipeline
```python
# 1. Take screenshot
win.screenshot("game_list.png")

# 2. Find UI elements
./showui_cli.py -i game_list.png -q "Find update button" -o result.png

# 3. Verify with ASCII (lightweight check)
python asciipng/ascii_quick.py game_list.png -w 100

# 4. Perform action
win.click(found_x, found_y)
```

## 🐛 Debugging Tips

### 1. Check Windows Agent Connection
```python
# Verify agent is running
curl http://192.168.0.15:8765/status

# Test from Python
from windows_control import WindowsControl
win = WindowsControl()  # Should not raise error
```

### 2. ShowUI Model Loading
```python
# Check GPU memory
nvidia-smi

# Test model loading
python -c "from showui_service import test_model; test_model()"
```

### 3. App Launch Issues
```bash
# Test URI support
./app_launcher.py launch calculator  # Should open Calculator

# Check process
Get-Process | Where-Object {$_.MainWindowTitle -ne ""}
```

## 🔒 Security Considerations

1. **App Whitelist**: Only apps in `allowed_apps.json` can be launched
2. **No UI Injection**: Uses native Windows APIs, not input simulation
3. **Process Isolation**: Each app runs in its own process
4. **Token Security**: Windows Agent uses bearer token authentication

## 📊 Performance Optimization

### ShowUI Optimization
- Use `torch.bfloat16` for reduced memory usage
- Implement result caching for repeated queries
- Run as background service to avoid reload overhead

### ASCII Tools
- Lightweight alternative to ShowUI for quick checks
- Use `-q` flag for minimal processing
- Adjust width parameter based on needs

## 🤝 Contributing

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black .
```

### Code Style
- Follow PEP 8
- Use type hints where applicable
- Add docstrings to all functions
- Keep functions focused and small

### Testing New Apps
1. Add app to `allowed_apps.json`
2. Test all launch methods
3. Document any special requirements
4. Add integration test

## 📚 Resources

- [ShowUI Paper](https://arxiv.org/abs/2411.17465)
- [Windows UI Automation](https://docs.microsoft.com/en-us/windows/win32/winauto/windows-automation-api-overview)
- [PowerShell Process Management](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/)

## 🆘 Common Commands Reference

```bash
# App Management
./app_launcher.py list
./app_launcher.py launch steam:downloads
./app_launcher.py close steam

# Visual AI
./showui_cli.py -q "Find button" -i screen.png
./showui_cli.py -a downloads -i screen.png

# ASCII Monitoring
python asciipng/ascii_quick.py -w 100
python asciipng/ascii_monitor.py -i 1.0

# Windows Control
python -c "from windows_control import WindowsControl; win = WindowsControl(); win.screenshot('test.png')"
```

## 🎯 Next Steps

1. Explore the ShowUI CLI for visual automation
2. Customize `allowed_apps.json` for your workflow
3. Try ASCII tools for lightweight monitoring
4. Build your own automation scripts using the provided APIs

---

**Remember**: This toolkit prioritizes security and reliability over UI simulation. Always use process-based approaches when possible.