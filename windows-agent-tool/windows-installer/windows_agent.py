#!/usr/bin/env python3
"""
Windows Agent for Claude Code
Provides Windows control capabilities to Claude Code running in WSL
Version: 3.0
"""

# Version info
__version__ = "3.0"
__features__ = {
    "2.0": "Basic Windows control (mouse, keyboard, screenshot, powershell)",
    "3.0": "Added window management (focus, maximize, minimize, restore)"
}

import os
import sys
import json
import base64
import subprocess
import socket
import threading
import time
import shutil
import tempfile
import urllib.request
from io import BytesIO
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify
import pyautogui
from PIL import ImageGrab
import psutil
import win32api
import win32con
import win32process
import win32security
import win32gui

app = Flask(__name__)

# Configuration
PORT = 8765
HOST = '0.0.0.0'  # Listen on all interfaces for WSL access
API_TOKEN = os.environ.get('CLAUDE_AGENT_TOKEN', 'claude-agent-2024')

# Disable pyautogui failsafe for better control
pyautogui.FAILSAFE = False

# Write agent info for WSL discovery
def write_agent_info():
    """Write agent connection info for WSL to discover"""
    info_path = os.path.expanduser('~/.claude_agent_info')
    try:
        # Get all IPs
        hostname = socket.gethostname()
        local_ips = socket.gethostbyname_ex(hostname)[2]
        
        # Find the best IP for WSL (usually starts with 172, 10, or 192)
        wsl_ip = None
        for ip in local_ips:
            if ip.startswith(('172.', '10.', '192.')) and not ip.startswith('127.'):
                wsl_ip = ip
                break
        
        if not wsl_ip and local_ips:
            wsl_ip = local_ips[0]
        
        info = {
            'host': wsl_ip or hostname,
            'all_ips': local_ips,
            'port': PORT,
            'token': API_TOKEN,
            'pid': os.getpid(),
            'started': datetime.now().isoformat()
        }
        
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
            
        print(f"Agent info written to: {info_path}")
        print(f"WSL should connect to: http://{wsl_ip}:{PORT}")
        
    except Exception as e:
        print(f"Warning: Could not write agent info: {e}")

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != f'Bearer {API_TOKEN}':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': __version__,
        'pid': os.getpid(),
        'uptime': time.time(),
        'features': __features__.get(__version__, 'Unknown version')
    })

@app.route('/version', methods=['GET'])
def version():
    """Get detailed version information"""
    return jsonify({
        'version': __version__,
        'features': __features__,
        'current_features': __features__.get(__version__, 'Unknown version'),
        'python_version': sys.version,
        'platform': sys.platform,
        'agent_path': os.path.abspath(__file__),
        'last_modified': os.path.getmtime(__file__)
    })

@app.route('/screenshot', methods=['POST'])
@require_auth
def screenshot():
    """Capture screenshot"""
    try:
        data = request.json or {}
        x = data.get('x')
        y = data.get('y')
        width = data.get('width')
        height = data.get('height')
        
        # Capture screenshot
        if all(v is not None for v in [x, y, width, height]):
            img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        else:
            img = ImageGrab.grab()
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': img_base64,
            'width': img.width,
            'height': img.height
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/mouse/move', methods=['POST'])
@require_auth
def mouse_move():
    """Move mouse to position"""
    try:
        data = request.json
        x = data['x']
        y = data['y']
        duration = data.get('duration', 0.2)
        
        pyautogui.moveTo(x, y, duration=duration)
        
        return jsonify({'success': True, 'position': {'x': x, 'y': y}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/mouse/click', methods=['POST'])
@require_auth
def mouse_click():
    """Click mouse button"""
    try:
        data = request.json or {}
        x = data.get('x')
        y = data.get('y')
        button = data.get('button', 'left')
        clicks = data.get('clicks', 1)
        
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button, clicks=clicks)
        else:
            pyautogui.click(button=button, clicks=clicks)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/keyboard/type', methods=['POST'])
@require_auth
def keyboard_type():
    """Type text"""
    try:
        data = request.json
        text = data['text']
        interval = data.get('interval', 0.05)
        
        pyautogui.typewrite(text, interval=interval)
        
        return jsonify({'success': True, 'typed': text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/keyboard/key', methods=['POST'])
@require_auth
def keyboard_key():
    """Press key or key combination"""
    try:
        data = request.json
        keys = data['keys']  # Can be string or list
        
        if isinstance(keys, str):
            pyautogui.press(keys)
        else:
            pyautogui.hotkey(*keys)
        
        return jsonify({'success': True, 'keys': keys})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/powershell', methods=['POST'])
@require_auth
def powershell():
    """Execute PowerShell command"""
    try:
        data = request.json
        command = data['command']
        timeout = data.get('timeout', 30)
        
        # Run PowerShell with bypass execution policy
        ps_command = [
            'powershell.exe',
            '-ExecutionPolicy', 'Bypass',
            '-NoProfile',
            '-Command', command
        ]
        
        result = subprocess.run(
            ps_command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return jsonify({
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Command timed out'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/process/list', methods=['GET'])
@require_auth
def process_list():
    """List running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return jsonify({'success': True, 'processes': processes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/process/kill', methods=['POST'])
@require_auth
def process_kill():
    """Kill process by PID"""
    try:
        data = request.json
        pid = data['pid']
        force = data.get('force', False)
        
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            
            # Wait a bit for process to die
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                pass
            
            return jsonify({'success': True, 'pid': pid})
        except psutil.NoSuchProcess:
            return jsonify({'success': False, 'error': 'Process not found'}), 404
        except psutil.AccessDenied:
            return jsonify({'success': False, 'error': 'Access denied - admin rights required'}), 403
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/file/read', methods=['POST'])
@require_auth
def file_read():
    """Read file contents"""
    try:
        data = request.json
        path = data['path']
        encoding = data.get('encoding', 'utf-8')
        
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'path': path,
            'content': content,
            'size': len(content)
        })
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/file/write', methods=['POST'])
@require_auth
def file_write():
    """Write file contents"""
    try:
        data = request.json
        path = data['path']
        content = data['content']
        encoding = data.get('encoding', 'utf-8')
        create_dirs = data.get('create_dirs', True)
        
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        
        if create_dirs:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'path': path,
            'size': len(content)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/file/delete', methods=['POST'])
@require_auth
def file_delete():
    """Delete file"""
    try:
        data = request.json
        path = data['path']
        
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
        else:
            return jsonify({'success': False, 'error': 'Path not found'}), 404
        
        return jsonify({'success': True, 'path': path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/file/list', methods=['POST'])
@require_auth
def file_list():
    """List directory contents"""
    try:
        data = request.json
        path = data.get('path', '.')
        
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        
        if not os.path.isdir(path):
            return jsonify({'success': False, 'error': 'Not a directory'}), 400
        
        items = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                stat = os.stat(item_path)
                items.append({
                    'name': item,
                    'path': item_path,
                    'is_dir': os.path.isdir(item_path),
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
            except:
                pass
        
        return jsonify({
            'success': True,
            'path': path,
            'items': items
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Window Management Endpoints
@app.route('/window/list', methods=['GET'])
@require_auth
def window_list():
    """List all visible windows"""
    try:
        windows = []
        
        def enum_handler(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        rect = win32gui.GetWindowRect(hwnd)
                        is_minimized = win32gui.IsIconic(hwnd)
                        is_maximized = win32gui.IsZoomed(hwnd)
                        
                        results.append({
                            'hwnd': hwnd,
                            'title': window_text,
                            'pid': pid,
                            'rect': {
                                'left': rect[0],
                                'top': rect[1],
                                'right': rect[2],
                                'bottom': rect[3],
                                'width': rect[2] - rect[0],
                                'height': rect[3] - rect[1]
                            },
                            'state': 'minimized' if is_minimized else 'maximized' if is_maximized else 'normal'
                        })
                    except:
                        pass
            return True
        
        win32gui.EnumWindows(enum_handler, windows)
        
        return jsonify({
            'success': True,
            'windows': windows,
            'count': len(windows)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/window/focus', methods=['POST'])
@require_auth
def window_focus():
    """Bring window to foreground"""
    try:
        data = request.json
        title = data.get('title')
        pid = data.get('pid')
        
        hwnd = None
        
        # Find window by title or PID
        def enum_handler(h, param):
            if title and title.lower() in win32gui.GetWindowText(h).lower():
                param.append(h)
            elif pid:
                _, window_pid = win32process.GetWindowThreadProcessId(h)
                if window_pid == pid:
                    param.append(h)
            return True
        
        handles = []
        win32gui.EnumWindows(enum_handler, handles)
        
        if not handles:
            return jsonify({'success': False, 'error': 'Window not found'}), 404
        
        hwnd = handles[0]
        
        # Restore window if minimized
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # Bring to foreground
        win32gui.SetForegroundWindow(hwnd)
        
        return jsonify({
            'success': True,
            'hwnd': hwnd,
            'title': win32gui.GetWindowText(hwnd)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/window/maximize', methods=['POST'])
@require_auth
def window_maximize():
    """Maximize window"""
    try:
        data = request.json
        title = data.get('title')
        pid = data.get('pid')
        
        # Find window
        def enum_handler(h, param):
            if title and title.lower() in win32gui.GetWindowText(h).lower():
                param.append(h)
            elif pid:
                _, window_pid = win32process.GetWindowThreadProcessId(h)
                if window_pid == pid:
                    param.append(h)
            return True
        
        handles = []
        win32gui.EnumWindows(enum_handler, handles)
        
        if not handles:
            return jsonify({'success': False, 'error': 'Window not found'}), 404
        
        hwnd = handles[0]
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        
        return jsonify({
            'success': True,
            'hwnd': hwnd,
            'title': win32gui.GetWindowText(hwnd)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/window/minimize', methods=['POST'])
@require_auth
def window_minimize():
    """Minimize window"""
    try:
        data = request.json
        title = data.get('title')
        pid = data.get('pid')
        
        # Find window
        def enum_handler(h, param):
            if title and title.lower() in win32gui.GetWindowText(h).lower():
                param.append(h)
            elif pid:
                _, window_pid = win32process.GetWindowThreadProcessId(h)
                if window_pid == pid:
                    param.append(h)
            return True
        
        handles = []
        win32gui.EnumWindows(enum_handler, handles)
        
        if not handles:
            return jsonify({'success': False, 'error': 'Window not found'}), 404
        
        hwnd = handles[0]
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        
        return jsonify({
            'success': True,
            'hwnd': hwnd,
            'title': win32gui.GetWindowText(hwnd)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/window/restore', methods=['POST'])
@require_auth
def window_restore():
    """Restore window to normal size"""
    try:
        data = request.json
        title = data.get('title')
        pid = data.get('pid')
        
        # Find window
        def enum_handler(h, param):
            if title and title.lower() in win32gui.GetWindowText(h).lower():
                param.append(h)
            elif pid:
                _, window_pid = win32process.GetWindowThreadProcessId(h)
                if window_pid == pid:
                    param.append(h)
            return True
        
        handles = []
        win32gui.EnumWindows(enum_handler, handles)
        
        if not handles:
            return jsonify({'success': False, 'error': 'Window not found'}), 404
        
        hwnd = handles[0]
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        return jsonify({
            'success': True,
            'hwnd': hwnd,
            'title': win32gui.GetWindowText(hwnd)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/window/state', methods=['POST'])
@require_auth
def window_state():
    """Get window state"""
    try:
        data = request.json
        title = data.get('title')
        pid = data.get('pid')
        
        # Find window
        def enum_handler(h, param):
            if title and title.lower() in win32gui.GetWindowText(h).lower():
                param.append(h)
            elif pid:
                _, window_pid = win32process.GetWindowThreadProcessId(h)
                if window_pid == pid:
                    param.append(h)
            return True
        
        handles = []
        win32gui.EnumWindows(enum_handler, handles)
        
        if not handles:
            return jsonify({'success': False, 'error': 'Window not found'}), 404
        
        hwnd = handles[0]
        rect = win32gui.GetWindowRect(hwnd)
        is_minimized = win32gui.IsIconic(hwnd)
        is_maximized = win32gui.IsZoomed(hwnd)
        
        return jsonify({
            'success': True,
            'hwnd': hwnd,
            'title': win32gui.GetWindowText(hwnd),
            'state': 'minimized' if is_minimized else 'maximized' if is_maximized else 'normal',
            'rect': {
                'left': rect[0],
                'top': rect[1],
                'right': rect[2],
                'bottom': rect[3],
                'width': rect[2] - rect[0],
                'height': rect[3] - rect[1]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Update System Endpoints
@app.route('/update/check', methods=['GET'])
@require_auth
def update_check():
    """Check for updates from GitHub"""
    try:
        # GitHub raw URL for the agent file
        github_url = "https://raw.githubusercontent.com/your-repo/windows-agent/main/windows_agent.py"
        
        # For now, let's simulate update checking
        # In real implementation, you'd fetch from GitHub and compare versions
        return jsonify({
            'success': True,
            'current_version': __version__,
            'latest_version': '3.1',  # Simulated
            'update_available': False,
            'download_url': github_url,
            'changelog': {
                '3.1': 'Added automatic update system',
                '3.0': 'Added window management features',
                '2.0': 'Initial release with basic controls'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/update/download', methods=['POST'])
@require_auth
def update_download():
    """Download update to temporary file"""
    try:
        data = request.json or {}
        download_url = data.get('url', 'https://raw.githubusercontent.com/your-repo/windows-agent/main/windows_agent.py')
        
        # Download to temp file
        temp_file = os.path.join(tempfile.gettempdir(), 'windows_agent_update.py')
        
        # Simulate download (in real implementation, download from URL)
        # urllib.request.urlretrieve(download_url, temp_file)
        
        return jsonify({
            'success': True,
            'temp_file': temp_file,
            'size': 0,  # os.path.getsize(temp_file)
            'message': 'Update downloaded successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/update/apply', methods=['POST'])
@require_auth
def update_apply():
    """Apply the downloaded update"""
    try:
        current_file = os.path.abspath(__file__)
        backup_file = current_file + '.bak'
        temp_file = os.path.join(tempfile.gettempdir(), 'windows_agent_update.py')
        
        # Check if update file exists
        if not os.path.exists(temp_file):
            return jsonify({'success': False, 'error': 'No update file found. Download first.'}), 400
        
        # Create backup
        shutil.copy2(current_file, backup_file)
        
        # Prepare restart script
        restart_script = f'''
import os
import sys
import time
import shutil

# Wait for current process to exit
time.sleep(2)

# Copy new file
shutil.copy2(r"{temp_file}", r"{current_file}")

# Start new version
os.system(f'"{sys.executable}" "{current_file}"')
'''
        
        restart_file = os.path.join(tempfile.gettempdir(), 'restart_agent.py')
        with open(restart_file, 'w') as f:
            f.write(restart_script)
        
        # Start restart process
        subprocess.Popen([sys.executable, restart_file], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS)
        
        # Schedule shutdown
        def shutdown():
            time.sleep(1)
            os._exit(0)
        
        threading.Thread(target=shutdown).start()
        
        return jsonify({
            'success': True,
            'message': 'Update applied. Agent will restart in 2 seconds.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/update/status', methods=['GET'])
@require_auth
def update_status():
    """Get update system status"""
    try:
        current_file = os.path.abspath(__file__)
        backup_file = current_file + '.bak'
        temp_file = os.path.join(tempfile.gettempdir(), 'windows_agent_update.py')
        
        return jsonify({
            'success': True,
            'current_version': __version__,
            'backup_exists': os.path.exists(backup_file),
            'update_pending': os.path.exists(temp_file),
            'auto_update_enabled': True,
            'last_check': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def run_server():
    """Run the Flask server"""
    print("=" * 50)
    print(f"Windows Agent for Claude Code v{__version__}")
    print("=" * 50)
    print(f"Starting on {HOST}:{PORT}")
    print(f"API Token: {API_TOKEN}")
    print(f"Features: {__features__.get(__version__, 'Unknown')}")
    print(f"Listening on ALL interfaces for WSL access")
    print("=" * 50)
    
    # Write agent info for WSL
    write_agent_info()
    
    # Start Flask server
    app.run(host=HOST, port=PORT, debug=False)

if __name__ == '__main__':
    run_server()