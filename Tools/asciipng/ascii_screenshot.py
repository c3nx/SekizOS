#!/usr/bin/env python3
"""
Quick ASCII screenshot tool
Takes a screenshot and converts it to ASCII art
"""

import sys
import os
from windows_control import WindowsControl
from asciipng.ascii_converter import convert_to_ascii

def ascii_screenshot(width=100, save_original=False):
    """
    Take a screenshot and convert to ASCII
    
    Args:
        width: ASCII width (default: 100)
        save_original: Keep the original PNG file (default: False)
    
    Returns:
        ASCII art string
    """
    try:
        # Initialize Windows control
        win = WindowsControl()
        
        # Take screenshot
        temp_file = "temp_ascii_screenshot.png"
        win.screenshot(temp_file)
        
        # Convert to ASCII
        ascii_art = convert_to_ascii(temp_file, width)
        
        # Clean up unless requested to save
        if not save_original and os.path.exists(temp_file):
            os.remove(temp_file)
        
        return ascii_art
        
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """CLI usage"""
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    save = "--save" in sys.argv
    
    print("Taking screenshot and converting to ASCII...")
    ascii_art = ascii_screenshot(width, save)
    print(ascii_art)

if __name__ == "__main__":
    main()