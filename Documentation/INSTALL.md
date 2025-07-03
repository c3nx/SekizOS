# SekizOS Detailed Installation Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Windows Agent Installation](#windows-agent-installation)
3. [SekizOS Core Installation](#sekizos-core-installation)
4. [ShowUI Setup (Optional)](#showui-setup-optional)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Windows 11 (any edition)
- **Python**: 3.10 or higher
- **RAM**: 8GB
- **Storage**: 10GB free space
- **Network**: Local network access

### Recommended Requirements (for ShowUI)
- **GPU**: NVIDIA GPU with 8GB+ VRAM
- **CUDA**: 11.8 or 12.1
- **RAM**: 16GB+
- **Storage**: 20GB free space

## 🪟 Windows Agent Installation

### Step 1: Download Windows Agent

```powershell
# In Windows (not WSL)
cd C:\
git clone https://github.com/yourusername/SekizOS.git
cd SekizOS\windows-agent-tool\windows-installer
```

### Step 2: Install Windows Agent

1. Right-click on `install.bat`
2. Select "Run as administrator"
3. Follow the prompts
4. The agent will start automatically

### Step 3: Verify Installation

```powershell
# Check if agent is running
curl http://localhost:8765/status

# Expected output:
# {"status": "running", "version": "3.0"}
```

### Step 4: Configure Firewall (if needed)

```powershell
# Allow WSL connections
New-NetFirewallRule -DisplayName "Claude Agent" -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow
```

## 🐧 SekizOS Core Installation

### Step 1: Clone Repository in WSL

```bash
# In WSL/Linux
cd ~
git clone https://github.com/yourusername/SekizOS.git
cd SekizOS
```

### Step 2: Create Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv showui_env
source showui_env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Core Dependencies

```bash
# Install basic requirements
pip install -r requirements.txt

# Make scripts executable
chmod +x app_launcher.py
chmod +x showui_cli.py
chmod +x windows_control.py
```

### Step 4: Configure Windows Control

```bash
# Test Windows Agent connection
python3 -c "from windows_control import WindowsControl; win = WindowsControl(); print('✓ Connected to Windows Agent')"
```

If connection fails, check:
1. Windows Agent is running
2. `.claude_agent_info` file exists in Windows user directory
3. WSL can access Windows directories

## 🤖 ShowUI Setup (Optional)

### Step 1: Check GPU Availability

```bash
# Check NVIDIA GPU
nvidia-smi

# Check CUDA version
nvcc --version
```

### Step 2: Install PyTorch

```bash
# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CPU only (not recommended)
pip install torch torchvision
```

### Step 3: Install ShowUI Dependencies

```bash
# Install ShowUI requirements
pip install -r requirements-showui.txt

# Download model (this will take time)
python3 -c "from transformers import AutoModel; AutoModel.from_pretrained('showlab/ShowUI-2B')"
```

### Step 4: Configure ShowUI

Create `showui_config.json`:
```json
{
  "model_path": "showlab/ShowUI-2B",
  "device": "cuda",
  "torch_dtype": "bfloat16",
  "max_workers": 2,
  "timeout": 30,
  "cache_dir": "./model_cache"
}
```

### Step 5: Test ShowUI

```bash
# Test model loading
python3 -c "
from showui_service import ShowUIService
service = ShowUIService()
print('✓ ShowUI loaded successfully')
"
```

## ✅ Verification

### 1. Test App Launcher

```bash
# List available apps
./app_launcher.py list

# Test calculator launch
./app_launcher.py launch calculator
```

### 2. Test Windows Control

```bash
# Take a screenshot
python3 -c "
from windows_control import WindowsControl
win = WindowsControl()
win.screenshot('test.png')
print('✓ Screenshot saved')
"
```

### 3. Test ShowUI (if installed)

```bash
# Test visual detection
./showui_cli.py -i test.png -q "Find any buttons" -o result.png
```

### 4. Test ASCII Tools

```bash
# Convert screenshot to ASCII
python3 asciipng/ascii_quick.py test.png -w 80
```

## 🔧 Troubleshooting

### Windows Agent Issues

**Problem**: Connection refused error
```bash
# Solution 1: Check if agent is running
tasklist | findstr python

# Solution 2: Restart agent
cd C:\path\to\windows-installer
python windows_agent.py

# Solution 3: Check firewall
netsh advfirewall firewall show rule name="Claude Agent"
```

**Problem**: Token authentication failed
```bash
# Solution: Regenerate token
# In Windows:
del %USERPROFILE%\.claude_agent_info
# Restart agent
```

### ShowUI Issues

**Problem**: CUDA out of memory
```python
# Solution: Use smaller batch size or CPU
{
  "device": "cpu",  # or
  "torch_dtype": "float16"  # uses less memory
}
```

**Problem**: Token mismatch error
```python
# Solution: Use correct processor initialization
from transformers import AutoProcessor

processor = AutoProcessor.from_pretrained(
    "showlab/ShowUI-2B",
    min_pixels=256*28*28,
    max_pixels=1344*28*28
)
```

### WSL Issues

**Problem**: Can't access Windows files
```bash
# Solution: Mount Windows drive
sudo mkdir -p /mnt/c
sudo mount -t drvfs C: /mnt/c
```

### General Issues

**Problem**: Permission denied
```bash
# Solution: Make files executable
chmod +x *.py
chmod +x asciipng/*.py
```

**Problem**: Module not found
```bash
# Solution: Check virtual environment
which python  # Should show showui_env path
pip list  # Check installed packages
```

## 📚 Next Steps

1. Read [CLAUDE.md](CLAUDE.md) for development guide
2. Configure [allowed_apps.json](allowed_apps.json) for your apps
3. Try the examples in README.md
4. Join our Discord for support

## 🆘 Getting Help

- Check existing issues on GitHub
- Read the troubleshooting section
- Ask in Discord community
- Create a new issue with:
  - System info (OS, Python version, GPU)
  - Error messages
  - Steps to reproduce

---

**Happy coding with SekizOS! 🚀**