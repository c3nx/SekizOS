# Windows Agent Tool

A Windows control agent system that enables Claude Code to fully control Windows from WSL.

## 🚀 Features

- 📸 Screenshot capture
- 🖱️ Mouse control (movement, clicks)
- ⌨️ Keyboard control (text input, key combinations)
- 💻 PowerShell command execution
- 📊 Process management
- 📁 File operations
- 🔄 WSL-Windows integration

## 📦 Installation

### On Windows:
1. Copy the `windows-agent-tool/windows-installer` folder to Windows
2. Run `install.bat` as **administrator**
3. The agent will start automatically

### On WSL:
```bash
# Install the tool
cp windows-agent-tool/win ~/.local/bin/
chmod +x ~/.local/bin/win

# Add aliases
cat windows-agent-tool/windows_aliases.sh >> ~/.windows_aliases
echo "source ~/.windows_aliases" >> ~/.bashrc
source ~/.bashrc
```

## 🎯 Usage

### Command Line:
```bash
# Screenshot
win screenshot
win screenshot desktop.png

# Mouse control
win click 500 300
win move 100 200

# Keyboard
win type "Hello World"
win key enter
win key ctrl+c

# PowerShell
win ps "Get-Date"
win ps "dir C:\\"

# Process management
win processes
win kill 1234
```

### Python:
```python
from windows_control import WindowsControl

win = WindowsControl()
win.screenshot("screen.png")
win.click(500, 300)
win.type("Test")
win.powershell("notepad")
```

## 🔧 Claude Code Integration

Create a `CLAUDE.md` in your project:
```markdown
## Windows Agent Tool
- `win screenshot` - Take screenshot
- `win click <x> <y>` - Click at coordinates
- `win type "text"` - Type text
- `win ps "command"` - Run PowerShell
```

## 📁 File Structure

```
windows-agent-tool/
├── windows-installer/    # Windows installation files
│   ├── windows_agent.py  # Main agent (Flask server)
│   ├── install.bat      # Installation script
│   └── ...
├── windows_control.py   # Python control library
├── win                  # CLI command
└── windows_aliases.sh   # Bash aliases
```

## 🛡️ Security

- Only accessible from localhost and WSL subnets
- Bearer token authentication
- Port: 8765

## 📝 License

MIT License

---
Created for Claude Code integration 🤖