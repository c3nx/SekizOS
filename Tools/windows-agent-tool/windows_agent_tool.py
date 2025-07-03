#!/usr/bin/env python3
"""
Windows Agent Tool for Claude Code
This tool enables Claude to control Windows directly
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List

class WindowsAgentTool:
    """Windows Agent integration for Claude Code"""
    
    def __init__(self):
        self.agent_info = self._load_agent_info()
        if not self.agent_info:
            raise Exception("Windows Agent not found. Please install from C:\\Users\\Uptake\\WindowsAgent")
        
        self.base_url = f"http://{self.agent_info['host']}:{self.agent_info['port']}"
        self.headers = {"Authorization": f"Bearer {self.agent_info['token']}"}
    
    def _load_agent_info(self) -> Optional[Dict]:
        """Load Windows Agent connection info"""
        paths = [
            "/mnt/c/Users/Uptake/.claude_agent_info",
            "/mnt/c/Users/uptake/.claude_agent_info",
            Path.home() / ".claude_agent_info"
        ]
        
        for path in paths:
            try:
                with open(path) as f:
                    return json.load(f)
            except:
                continue
        return None
    
    def screenshot(self) -> Dict[str, Any]:
        """Take a screenshot of Windows desktop"""
        response = requests.post(
            f"{self.base_url}/screenshot",
            headers=self.headers,
            timeout=30
        )
        return response.json()
    
    def mouse_click(self, x: int, y: int, button: str = "left") -> Dict[str, Any]:
        """Click mouse at specified coordinates"""
        response = requests.post(
            f"{self.base_url}/mouse/click",
            headers=self.headers,
            json={"x": x, "y": y, "button": button}
        )
        return response.json()
    
    def mouse_move(self, x: int, y: int) -> Dict[str, Any]:
        """Move mouse to specified coordinates"""
        response = requests.post(
            f"{self.base_url}/mouse/move",
            headers=self.headers,
            json={"x": x, "y": y}
        )
        return response.json()
    
    def type_text(self, text: str) -> Dict[str, Any]:
        """Type text using keyboard"""
        response = requests.post(
            f"{self.base_url}/keyboard/type",
            headers=self.headers,
            json={"text": text}
        )
        return response.json()
    
    def press_key(self, keys: str | List[str]) -> Dict[str, Any]:
        """Press key or key combination"""
        response = requests.post(
            f"{self.base_url}/keyboard/key",
            headers=self.headers,
            json={"keys": keys}
        )
        return response.json()
    
    def powershell(self, command: str) -> Dict[str, Any]:
        """Execute PowerShell command"""
        response = requests.post(
            f"{self.base_url}/powershell",
            headers=self.headers,
            json={"command": command}
        )
        return response.json()
    
    def list_processes(self) -> Dict[str, Any]:
        """List running Windows processes"""
        response = requests.get(
            f"{self.base_url}/process/list",
            headers=self.headers
        )
        return response.json()
    
    def kill_process(self, pid: int) -> Dict[str, Any]:
        """Kill a Windows process by PID"""
        response = requests.post(
            f"{self.base_url}/process/kill",
            headers=self.headers,
            json={"pid": pid}
        )
        return response.json()
    
    def read_file(self, path: str) -> Dict[str, Any]:
        """Read a file from Windows filesystem"""
        response = requests.post(
            f"{self.base_url}/file/read",
            headers=self.headers,
            json={"path": path}
        )
        return response.json()
    
    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to a file in Windows filesystem"""
        response = requests.post(
            f"{self.base_url}/file/write",
            headers=self.headers,
            json={"path": path, "content": content}
        )
        return response.json()

# Make tool available globally
windows_agent = WindowsAgentTool()