#!/usr/bin/env python3
"""
App Launcher for Windows Control
Uses allowed_apps.json to launch applications safely
"""

import json
import os
from pathlib import Path
from windows_control import WindowsControl

class AppLauncher:
    def __init__(self):
        self.win = WindowsControl()
        self.apps_config = self._load_config()
        
    def _load_config(self):
        """Load allowed apps configuration"""
        config_path = Path(__file__).parent / "allowed_apps.json"
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def list_apps(self):
        """List all available apps"""
        print("Available applications:")
        for app_id, app_info in self.apps_config.items():
            print(f"  - {app_id}: {app_info['name']}")
            if 'pages' in app_info:
                for page_id, _ in app_info['pages'].items():
                    print(f"      • {app_id}:{page_id}")
    
    def launch(self, app_name, page=None):
        """Launch an application"""
        # Parse app:page format
        if ':' in app_name and page is None:
            app_name, page = app_name.split(':', 1)
        
        if app_name not in self.apps_config:
            print(f"Error: '{app_name}' not found in allowed apps")
            self.list_apps()
            return False
        
        app_info = self.apps_config[app_name]
        
        # If specific page requested
        if page and 'pages' in app_info:
            if page in app_info['pages']:
                command = app_info['pages'][page]
                print(f"Opening {app_info['name']} - {page} page...")
                result = self.win.powershell(f'Start-Process "{command}"')
                return True
            else:
                print(f"Error: Page '{page}' not found for {app_name}")
                return False
        
        # Try launch methods in order
        for method in app_info['launch_methods']:
            try:
                command = method['command']
                print(f"Trying {method['type']} method: {command}")
                
                if method['type'] in ['uri', 'path', 'system']:
                    result = self.win.powershell(f'Start-Process "{command}"')
                    print(f"Launched {app_info['name']} successfully")
                    return True
                    
            except Exception as e:
                print(f"Method failed: {e}")
                continue
        
        print(f"Failed to launch {app_name}")
        return False
    
    def close(self, app_name):
        """Close an application"""
        if app_name not in self.apps_config:
            print(f"Error: '{app_name}' not found")
            return False
        
        # Common process names
        process_map = {
            'steam': 'Steam',
            'epic': 'EpicGamesLauncher',
            'battlenet': 'Battle.net',
            'discord': 'Discord',
            'spotify': 'Spotify',
            'chrome': 'chrome',
            'notepad': 'notepad'
        }
        
        if app_name in process_map:
            process_name = process_map[app_name]
            result = self.win.powershell(f'Stop-Process -Name "{process_name}" -Force -ErrorAction SilentlyContinue')
            print(f"Closed {app_name}")
            return True
        
        return False

def main():
    """CLI interface"""
    import sys
    
    launcher = AppLauncher()
    
    if len(sys.argv) < 2:
        print("Usage: app_launcher.py <command> [args]")
        print("Commands:")
        print("  list              - List available apps")
        print("  launch <app>      - Launch an app")
        print("  launch <app:page> - Launch app with specific page")
        print("  close <app>       - Close an app")
        print("\nExamples:")
        print("  app_launcher.py launch steam")
        print("  app_launcher.py launch steam:downloads")
        print("  app_launcher.py close steam")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        launcher.list_apps()
    elif command == "launch" and len(sys.argv) > 2:
        launcher.launch(sys.argv[2])
    elif command == "close" and len(sys.argv) > 2:
        launcher.close(sys.argv[2])
    else:
        print("Invalid command")

if __name__ == "__main__":
    main()