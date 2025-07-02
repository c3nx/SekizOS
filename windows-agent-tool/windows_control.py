#!/usr/bin/env python3
"""
Windows Control Tool for Claude Code
Simplified interface to Windows Agent
"""

import os
import sys
import json
import base64
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

Examples:
  win screenshot
  win click 500 300
  win type "Hello World"
  win key enter
  win ps "Get-Date"
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
            
        else:
            print(f"Unknown command: {cmd}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()