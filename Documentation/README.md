# SekizOS - Advanced AI Assistant Toolkit

A comprehensive Windows automation and visual AI toolkit designed for Claude Code integration, featuring ShowUI vision model, intelligent app management, and cross-platform control capabilities.

## 🌟 Key Features

- **🤖 Visual AI** - ShowUI integration for understanding and interacting with UI elements
- **🎮 Smart App Management** - Secure application launcher with whitelist control
- **🖥️ Windows Automation** - Full Windows control from WSL/Linux
- **🔤 ASCII Monitoring** - Lightweight visual verification tools
- **🔒 Security First** - Process-based approach avoiding UI injection

## 🚀 Quick Start

### Prerequisites

- Windows 11 (tested on IoT Enterprise LTSC)
- Python 3.10+
- NVIDIA GPU with 8GB+ VRAM (for ShowUI)
- Windows Agent installed and running

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/SekizOS.git
cd SekizOS

# 2. Install Windows Agent (on Windows side)
cd windows-agent-tool/windows-installer
Run install.bat as Administrator

# 3. Setup Python environment (on WSL/Linux)
python -m venv showui_env
source showui_env/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install ShowUI (optional, for visual AI)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate pillow gradio
```

## 🎯 Core Components

### 1. App Launcher - Intelligent Application Management

```bash
# List available apps
./app_launcher.py list

# Launch applications
./app_launcher.py launch steam
./app_launcher.py launch steam:downloads
./app_launcher.py launch discord

# Close applications
./app_launcher.py close steam
```

Configure allowed apps in `allowed_apps.json`:
```json
{
  "steam": {
    "name": "Steam",
    "launch_methods": [
      {"type": "uri", "command": "steam://"},
      {"type": "path", "command": "C:\\Program Files (x86)\\Steam\\Steam.exe"}
    ]
  }
}
```

### 2. ShowUI CLI - Visual AI Interface

```bash
# Find UI elements
./showui_cli.py -q "Find download button" -i screenshot.png

# Click on elements
./showui_cli.py -q "Click pause button" -c

# Analyze specific areas
./showui_cli.py -a downloads -i steam.png
```

### 3. Windows Control - Automation API

```python
from windows_control import WindowsControl

win = WindowsControl()

# Screenshot
win.screenshot("desktop.png")

# Launch apps via PowerShell
win.powershell('Start-Process "steam://open/downloads"')

# Mouse/Keyboard control
win.click(500, 300)
win.type("Hello World")
win.key("enter")
```

### 4. ASCII Tools - Lightweight Monitoring

```bash
# Quick ASCII conversion
python asciipng/ascii_quick.py screenshot.png -w 100

# Monitor screen changes
python asciipng/ascii_monitor.py -i 2.0

# Compare states
python asciipng/ascii_diff.py before.png after.png
```

## 🔧 Configuration

### ShowUI Setup

Create `showui_config.json`:
```json
{
  "model_path": "showlab/ShowUI-2B",
  "device": "cuda",
  "max_workers": 2,
  "timeout": 30
}
```

### Windows Agent

The agent runs on `http://localhost:8765` with bearer token authentication. Configuration is automatic via `.claude_agent_info` file.

## 🛠️ Troubleshooting

### Common Issues

1. **ShowUI Token Mismatch Error**
   ```
   Solution: Use AutoProcessor with correct pixel constraints
   See CLAUDE.md for detailed fix
   ```

2. **Windows UI Commands Not Working**
   ```
   Solution: Use PowerShell Start-Process instead of UI simulation
   Example: win.powershell('Start-Process "app://"')
   ```

3. **GPU Memory Issues**
   ```
   Solution: Use bfloat16 precision and device_map="cuda"
   ```

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive development guide
- **[SHOWUI_STATUS.md](SHOWUI_STATUS.md)** - ShowUI implementation details
- **[ASCII_TOOLS.md](asciipng/ASCII_TOOLS.md)** - ASCII tool documentation

## 🏗️ Project Structure

```
SekizOS/
├── Core Systems
│   ├── windows_control.py      # Windows automation API
│   ├── app_launcher.py         # Smart app management
│   └── showui_cli.py          # Visual AI CLI
├── Tools
│   ├── asciipng/              # ASCII conversion tools
│   │   ├── ascii_quick.py     # Quick converter
│   │   ├── ascii_monitor.py   # Change monitor
│   │   └── ascii_ui_comprehensive.py
│   └── windows-agent-tool/    # Windows agent
├── Configuration
│   ├── allowed_apps.json      # App whitelist
│   └── showui_config.json     # ShowUI settings
└── Documentation
    ├── README.md              # This file
    ├── CLAUDE.md              # Development guide
    └── *.md                   # Component docs
```

## 🔒 Security Features

- **Application Whitelist** - Only pre-approved apps can be launched
- **Process Isolation** - Each app runs in its own process
- **No UI Injection** - Uses native Windows APIs, not input simulation
- **Token Authentication** - Secure communication with Windows Agent

## 🚦 Usage Examples

### Gaming Automation
```bash
# Open Steam downloads
./app_launcher.py launch steam:downloads

# Find and click update button
./showui_cli.py -q "Find update button" -c

# Monitor download progress
python asciipng/ascii_monitor.py -i 1.0
```

### Window Management
```python
# Bring window to front
win.powershell('''
$proc = Get-Process steam
[Win32]::SetForegroundWindow($proc.MainWindowHandle)
''')
```

### Visual Verification
```bash
# Take screenshot and convert to ASCII
win screenshot current.png
python asciipng/ascii_quick.py current.png -w 120
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

See [CLAUDE.md](CLAUDE.md) for development guidelines.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [ShowUI](https://github.com/showlab/ShowUI) - Visual AI model
- [Qwen2-VL](https://github.com/QwenLM/Qwen2-VL) - Base vision model
- Claude Code - Development environment

---

**Built with ❤️ for AI-assisted development**