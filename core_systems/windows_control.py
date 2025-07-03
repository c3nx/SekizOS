#!/usr/bin/env python3
"""
Windows Control Tool for Claude Code
Simplified interface to Windows Agent
"""

import os
import sys
import json
import base64
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

class WindowsControl:
    def __init__(self):
        """Initialize Windows Control with agent info"""
        self.agent_info = self._load_agent_info()
        if self.agent_info:
            self.base_url = f"http://{self.agent_info['host']}:{self.agent_info['port']}"
            self.headers = {"Authorization": f"Bearer {self.agent_info['token']}"}
        else:
            raise Exception("Windows Agent not found! Please install and run the agent first.")
    
    def _load_agent_info(self) -> Optional[Dict]:
        """Load agent connection info"""
        info_paths = [
            "/mnt/c/Users/Uptake/.claude_agent_info",
            Path.home() / ".claude_agent_info",
            "/mnt/c/Users/" + os.environ.get('USER', '') + "/.claude_agent_info"
        ]
        
        for path in info_paths:
            try:
                with open(path) as f:
                    return json.load(f)
            except:
                continue
        return None
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the agent"""
        url = f"{self.base_url}{endpoint}"
        kwargs['headers'] = self.headers
        kwargs['timeout'] = kwargs.get('timeout', 30)
        
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return {"success": False, "error": str(e)}
    
    def screenshot(self, save_path: Optional[str] = None) -> str:
        """Take screenshot and optionally save to file"""
        result = self._request("POST", "/screenshot", json={})
        
        if result.get('success') and save_path:
            img_data = base64.b64decode(result['image'])
            with open(save_path, 'wb') as f:
                f.write(img_data)
            print(f"Screenshot saved: {save_path}")
            return save_path
        
        return result.get('image', '')
    
    def click(self, x: int, y: int, button: str = "left"):
        """Click at coordinates"""
        result = self._request("POST", "/mouse/click", 
                             json={"x": x, "y": y, "button": button})
        if result.get('success'):
            print(f"Clicked at ({x}, {y})")
        return result
    
    def move(self, x: int, y: int):
        """Move mouse to coordinates"""
        result = self._request("POST", "/mouse/move", 
                             json={"x": x, "y": y})
        if result.get('success'):
            print(f"Moved to ({x}, {y})")
        return result
    
    def type(self, text: str):
        """Type text"""
        result = self._request("POST", "/keyboard/type", 
                             json={"text": text})
        if result.get('success'):
            print(f"Typed: {text[:50]}...")
        return result
    
    def key(self, keys: str | List[str]):
        """Press key(s)"""
        result = self._request("POST", "/keyboard/key", 
                             json={"keys": keys})
        if result.get('success'):
            print(f"Pressed: {keys}")
        return result
    
    def powershell(self, command: str) -> str:
        """Run PowerShell command"""
        result = self._request("POST", "/powershell", 
                             json={"command": command})
        if result.get('success'):
            return result.get('stdout', '')
        return result.get('error', 'Command failed')
    
    def processes(self) -> List[Dict]:
        """List processes"""
        result = self._request("GET", "/process/list")
        return result.get('processes', [])
    
    def kill(self, pid: int):
        """Kill process"""
        result = self._request("POST", "/process/kill", 
                             json={"pid": pid})
        if result.get('success'):
            print(f"Killed process {pid}")
        return result
    
    def read_file(self, path: str) -> str:
        """Read Windows file"""
        result = self._request("POST", "/file/read", 
                             json={"path": path})
        return result.get('content', '')
    
    def write_file(self, path: str, content: str):
        """Write Windows file"""
        result = self._request("POST", "/file/write", 
                             json={"path": path, "content": content})
        if result.get('success'):
            print(f"Wrote to: {path}")
        return result
    
    def list_windows(self) -> List[Dict]:
        """List all visible windows"""
        result = self._request("GET", "/window/list")
        return result.get('windows', [])
    
    def focus_window(self, title: Optional[str] = None, pid: Optional[int] = None):
        """Bring window to foreground"""
        data = {}
        if title:
            data['title'] = title
        if pid:
            data['pid'] = pid
        
        result = self._request("POST", "/window/focus", json=data)
        if result.get('success'):
            print(f"Focused: {result.get('title', 'window')}")
        return result
    
    def maximize_window(self, title: Optional[str] = None, pid: Optional[int] = None):
        """Maximize window"""
        data = {}
        if title:
            data['title'] = title
        if pid:
            data['pid'] = pid
        
        result = self._request("POST", "/window/maximize", json=data)
        if result.get('success'):
            print(f"Maximized: {result.get('title', 'window')}")
        return result
    
    def minimize_window(self, title: Optional[str] = None, pid: Optional[int] = None):
        """Minimize window"""
        data = {}
        if title:
            data['title'] = title
        if pid:
            data['pid'] = pid
        
        result = self._request("POST", "/window/minimize", json=data)
        if result.get('success'):
            print(f"Minimized: {result.get('title', 'window')}")
        return result
    
    def restore_window(self, title: Optional[str] = None, pid: Optional[int] = None):
        """Restore window to normal size"""
        data = {}
        if title:
            data['title'] = title
        if pid:
            data['pid'] = pid
        
        result = self._request("POST", "/window/restore", json=data)
        if result.get('success'):
            print(f"Restored: {result.get('title', 'window')}")
        return result
    
    def window_state(self, title: Optional[str] = None, pid: Optional[int] = None) -> Dict:
        """Get window state"""
        data = {}
        if title:
            data['title'] = title
        if pid:
            data['pid'] = pid
        
        result = self._request("POST", "/window/state", json=data)
        return result
    
    def version(self) -> Dict:
        """Get version information"""
        result = self._request("GET", "/version")
        if result.get('success', True):  # Version endpoint doesn't have success field
            print(f"Windows Agent v{result.get('version', 'Unknown')}")
            print(f"Features: {result.get('current_features', 'Unknown')}")
        return result
    
    def update_check(self) -> Dict:
        """Check for updates"""
        result = self._request("GET", "/update/check")
        if result.get('success'):
            current = result.get('current_version')
            latest = result.get('latest_version')
            if result.get('update_available'):
                print(f"Update available: v{current} → v{latest}")
            else:
                print(f"Up to date (v{current})")
        return result
    
    def update_download(self, url: Optional[str] = None) -> Dict:
        """Download update"""
        data = {}
        if url:
            data['url'] = url
        result = self._request("POST", "/update/download", json=data)
        if result.get('success'):
            print("Update downloaded successfully")
        return result
    
    def update_apply(self) -> Dict:
        """Apply update and restart"""
        result = self._request("POST", "/update/apply", json={})
        if result.get('success'):
            print("Update applied. Agent will restart...")
        return result
    
    def update_status(self) -> Dict:
        """Get update status"""
        result = self._request("GET", "/update/status")
        return result

# CLI Interface
def main():
    if len(sys.argv) < 2:
        print("""Windows Control - Usage:
        
Commands:
  screenshot [path]     Take screenshot (optionally save to path)
  click <x> <y>        Click at coordinates
  move <x> <y>         Move mouse to coordinates
  type <text>          Type text
  key <key>            Press key (e.g., 'enter', 'ctrl+c')
  ps <command>         Run PowerShell command
  processes            List running processes
  kill <pid>           Kill process by PID
  read <path>          Read file from Windows
  write <path> <text>  Write text to Windows file
  
Window Management:
  windows              List all visible windows
  focus <title>        Bring window to foreground
  maximize <title>     Maximize window
  minimize <title>     Minimize window
  restore <title>      Restore window to normal size
  window <title>       Combined: focus and maximize window

Version & Updates:
  version              Show agent version and features
  update check         Check for updates
  update download      Download available update
  update apply         Apply update and restart agent
  update status        Show update system status

Examples:
  win screenshot
  win click 500 300
  win type "Hello World"
  win key enter
  win ps "Get-Date"
  win windows
  win focus "Steam"
  win maximize "Steam"
  win window "Steam"    # Focus and maximize
  win version
  win update check
""")
        return
    
    try:
        win = WindowsControl()
        cmd = sys.argv[1].lower()
        
        if cmd == "screenshot":
            path = sys.argv[2] if len(sys.argv) > 2 else None
            win.screenshot(path)
            
        elif cmd == "click":
            if len(sys.argv) < 4:
                print("Usage: win click <x> <y>")
                return
            win.click(int(sys.argv[2]), int(sys.argv[3]))
            
        elif cmd == "move":
            if len(sys.argv) < 4:
                print("Usage: win move <x> <y>")
                return
            win.move(int(sys.argv[2]), int(sys.argv[3]))
            
        elif cmd == "type":
            if len(sys.argv) < 3:
                print("Usage: win type <text>")
                return
            text = ' '.join(sys.argv[2:])
            win.type(text)
            
        elif cmd == "key":
            if len(sys.argv) < 3:
                print("Usage: win key <key>")
                return
            keys = sys.argv[2]
            if '+' in keys:
                keys = keys.split('+')
            win.key(keys)
            
        elif cmd == "ps" or cmd == "powershell":
            if len(sys.argv) < 3:
                print("Usage: win ps <command>")
                return
            cmd = ' '.join(sys.argv[2:])
            output = win.powershell(cmd)
            print(output)
            
        elif cmd == "processes":
            procs = win.processes()
            for p in procs[:20]:  # Show first 20
                print(f"{p['pid']:8} {p['name']}")
                
        elif cmd == "kill":
            if len(sys.argv) < 3:
                print("Usage: win kill <pid>")
                return
            win.kill(int(sys.argv[2]))
            
        elif cmd == "read":
            if len(sys.argv) < 3:
                print("Usage: win read <path>")
                return
            content = win.read_file(sys.argv[2])
            print(content)
            
        elif cmd == "write":
            if len(sys.argv) < 4:
                print("Usage: win write <path> <content>")
                return
            path = sys.argv[2]
            content = ' '.join(sys.argv[3:])
            win.write_file(path, content)
            
        elif cmd == "windows":
            windows = win.list_windows()
            for w in windows[:20]:  # Show first 20
                state = w['state']
                print(f"{w['pid']:8} [{state:10}] {w['title']}")
                
        elif cmd == "focus":
            if len(sys.argv) < 3:
                print("Usage: win focus <title>")
                return
            title = ' '.join(sys.argv[2:])
            win.focus_window(title=title)
            
        elif cmd == "maximize":
            if len(sys.argv) < 3:
                print("Usage: win maximize <title>")
                return
            title = ' '.join(sys.argv[2:])
            win.maximize_window(title=title)
            
        elif cmd == "minimize":
            if len(sys.argv) < 3:
                print("Usage: win minimize <title>")
                return
            title = ' '.join(sys.argv[2:])
            win.minimize_window(title=title)
            
        elif cmd == "restore":
            if len(sys.argv) < 3:
                print("Usage: win restore <title>")
                return
            title = ' '.join(sys.argv[2:])
            win.restore_window(title=title)
            
        elif cmd == "window":
            # Combined focus and maximize
            if len(sys.argv) < 3:
                print("Usage: win window <title>")
                return
            title = ' '.join(sys.argv[2:])
            win.focus_window(title=title)
            time.sleep(0.2)  # Small delay to ensure window is focused
            win.maximize_window(title=title)
            
        elif cmd == "version":
            win.version()
            
        elif cmd == "update":
            if len(sys.argv) < 3:
                print("Usage: win update <check|download|apply|status>")
                return
            
            subcmd = sys.argv[2].lower()
            if subcmd == "check":
                win.update_check()
            elif subcmd == "download":
                win.update_download()
            elif subcmd == "apply":
                win.update_apply()
            elif subcmd == "status":
                status = win.update_status()
                if status.get('success', True):
                    print(f"Version: {status.get('current_version')}")
                    print(f"Backup exists: {status.get('backup_exists')}")
                    print(f"Update pending: {status.get('update_pending')}")
            else:
                print(f"Unknown update command: {subcmd}")
            
        else:
            print(f"Unknown command: {cmd}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()