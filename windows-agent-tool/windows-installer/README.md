# Windows Agent for Claude Code v2.0

A Windows agent system that provides full control capabilities for Claude Code running in WSL.

## 🚀 Quick Installation

### **On Windows:**

1. Run `install.bat` as **administrator**
   - Right-click → "Run as administrator"
   - All steps will complete automatically

2. The agent will start automatically when installation is complete

## 📋 Features

- 📸 **Screenshot**: Full screen or specific area capture
- 🖱️ **Mouse Control**: Movement, clicks, dragging
- ⌨️ **Keyboard Control**: Text input, shortcuts
- 💻 **PowerShell**: Execute Windows commands
- 📊 **Process Management**: List/terminate processes
- 📁 **File Operations**: Read, write, delete files
- 🔄 **Auto Start**: Starts automatically with Windows

## 🔧 Usage

### **From WSL/Claude Code:**

```python
import requests
import json

# Read agent info
with open('/mnt/c/Users/[Username]/.claude_agent_info') as f:
    info = json.load(f)

# Connect
url = f"http://{info['host']}:{info['port']}"
headers = {'Authorization': f"Bearer {info['token']}"}

# Take screenshot
response = requests.post(f"{url}/screenshot", headers=headers)
screenshot = response.json()['image']  # Base64 encoded
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/screenshot` | POST | Capture screenshot |
| `/mouse/move` | POST | Move mouse |
| `/mouse/click` | POST | Click mouse |
| `/keyboard/type` | POST | Type text |
| `/keyboard/key` | POST | Press key |
| `/powershell` | POST | Run PowerShell command |
| `/process/list` | GET | List processes |
| `/process/kill` | POST | Kill process |
| `/file/read` | POST | Read file |
| `/file/write` | POST | Write file |
| `/file/delete` | POST | Delete file |

## 🛡️ Security

- Only accessible from localhost
- Bearer token authentication
- Firewall rules configured automatically

## ❌ Uninstall

Run `uninstall.bat` as administrator in Windows

## 🔍 Troubleshooting

1. **Agent not starting**: Ensure Python 3.8+ is installed (`python --version`)
2. **WSL can't connect**: Check Windows Firewall for port 8765
3. **PowerShell errors**: Check execution policy

## 📊 Technical Details

- **Port**: 8765
- **Host**: 0.0.0.0 (all interfaces)
- **Token**: claude-agent-2024
- **Python**: 3.8+
- **Dependencies**: Flask, pyautogui, Pillow, psutil, pywin32

---
Version: 2.0 | Port: 8765