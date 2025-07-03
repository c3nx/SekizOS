#!/usr/bin/env python3
"""
Quick ASCII Screenshot Tool
Simple wrapper for taking screenshots and converting to ASCII with UI detection
"""

import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path for windows_control
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from windows_control import WindowsControl
from ascii_converter_enhanced import convert_to_ascii_enhanced
from ascii_ui_comprehensive import ComprehensiveUIDetector

def take_screenshot(filename=None):
    """Take a screenshot using Windows Agent"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ascii_screenshot_{timestamp}.png"
    
    win = WindowsControl()
    win.screenshot(filename)
    return filename

def convert_and_detect(image_path, width=100, detect_ui=True, save_output=False):
    """Convert image to ASCII and optionally detect UI elements"""
    
    # Convert to ASCII with enhanced settings
    ascii_art = convert_to_ascii_enhanced(image_path, width)
    
    if detect_ui:
        # Detect UI elements
        detector = ComprehensiveUIDetector()
        result = detector.analyze_ascii(ascii_art, apply_replacements=True)
        
        # Use annotated version
        output = result['annotated']
        
        # Print summary
        print(f"\n=== Detected {result['element_count']} UI Elements ===")
        for elem_type, count in result['element_types'].items():
            if count > 0:
                print(f"  {elem_type}: {count}")
    else:
        output = ascii_art
    
    # Save if requested
    if save_output:
        output_file = image_path.replace('.png', '_ascii.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\nSaved to: {output_file}")
    
    return output

def main():
    parser = argparse.ArgumentParser(description='Quick ASCII Screenshot Tool')
    parser.add_argument('image', nargs='?', help='Image path (if not provided, takes screenshot)')
    parser.add_argument('-w', '--width', type=int, default=100, help='ASCII width (default: 100)')
    parser.add_argument('-n', '--no-ui', action='store_true', help='Disable UI detection')
    parser.add_argument('-s', '--save', action='store_true', help='Save ASCII output to file')
    parser.add_argument('-q', '--quick', action='store_true', help='Quick mode (width=80, no UI)')
    
    args = parser.parse_args()
    
    # Quick mode overrides
    if args.quick:
        args.width = 80
        args.no_ui = True
    
    try:
        # Get image path
        if args.image:
            image_path = args.image
        else:
            print("Taking screenshot...")
            image_path = take_screenshot()
            print(f"Screenshot saved: {image_path}")
        
        # Convert and display
        print(f"\nConverting to ASCII (width={args.width})...")
        ascii_output = convert_and_detect(
            image_path, 
            width=args.width, 
            detect_ui=not args.no_ui,
            save_output=args.save
        )
        
        print("\n=== ASCII Output ===")
        print(ascii_output)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()