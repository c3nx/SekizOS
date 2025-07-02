#!/usr/bin/env python3
"""
Windows Agent for Claude Code
Provides Windows control capabilities to Claude Code running in WSL
Version: 2.0
"""

import os
import sys
import json
import base64
import subprocess
import socket
import threading
import time
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
        'version': '2.0',
        'pid': os.getpid(),
        'uptime': time.time()
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

def run_server():
    """Run the Flask server"""
    print("=" * 50)
    print("Windows Agent for Claude Code v2.0")
    print("=" * 50)
    print(f"Starting on {HOST}:{PORT}")
    print(f"API Token: {API_TOKEN}")
    print(f"Listening on ALL interfaces for WSL access")
    print("=" * 50)
    
    # Write agent info for WSL
    write_agent_info()
    
    # Start Flask server
    app.run(host=HOST, port=PORT, debug=False)

if __name__ == '__main__':
    run_server()