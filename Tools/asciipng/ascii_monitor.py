#!/usr/bin/env python3
"""
ASCII Screen Monitor
Continuously monitors screen changes using ASCII conversion
"""

import sys
import os
import time
import argparse
from datetime import datetime
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from windows_control import WindowsControl
from ascii_converter_enhanced import convert_to_ascii_enhanced
from ascii_ui_comprehensive import ComprehensiveUIDetector
from ascii_diff import compute_ascii_diff, highlight_differences

class ASCIIMonitor:
    def __init__(self, width=80, interval=2.0, detect_ui=True):
        self.width = width
        self.interval = interval
        self.detect_ui = detect_ui
        self.win = WindowsControl()
        self.detector = ComprehensiveUIDetector() if detect_ui else None
        self.previous_ascii = None
        self.previous_elements = {}
        
    def take_ascii_screenshot(self) -> Tuple[str, dict]:
        """Take screenshot and convert to ASCII"""
        # Take screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/monitor_{timestamp}.png"
        
        try:
            self.win.screenshot(filename)
            
            # Convert to ASCII
            ascii_art = convert_to_ascii_enhanced(filename, self.width)
            
            # Detect UI elements if enabled
            elements = {}
            if self.detect_ui:
                result = self.detector.analyze_ascii(ascii_art, apply_replacements=True)
                ascii_art = result['annotated']
                elements = result['element_types']
            
            # Clean up temp file
            os.remove(filename)
            
            return ascii_art, elements
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None, {}
    
    def print_changes(self, current_ascii: str, current_elements: dict):
        """Print changes from previous state"""
        if self.previous_ascii is None:
            print("\n=== Initial State ===")
            print(current_ascii)
            if current_elements:
                print("\nUI Elements:")
                for elem_type, count in current_elements.items():
                    if count > 0:
                        print(f"  {elem_type}: {count}")
        else:
            # Compute diff
            diff_result = compute_ascii_diff(self.previous_ascii, current_ascii)
            
            if diff_result['changes'] > 0:
                print(f"\n=== Changes Detected ({datetime.now().strftime('%H:%M:%S')}) ===")
                print(f"Changed characters: {diff_result['changes']} ({diff_result['change_percentage']:.1f}%)")
                
                # Show highlighted diff (first 20 lines)
                highlighted = highlight_differences(self.previous_ascii, current_ascii)
                lines = highlighted.split('\n')[:20]
                for line in lines:
                    print(line)
                
                # Show UI element changes
                if self.previous_elements or current_elements:
                    print("\nUI Element Changes:")
                    all_types = set(self.previous_elements.keys()) | set(current_elements.keys())
                    for elem_type in sorted(all_types):
                        prev_count = self.previous_elements.get(elem_type, 0)
                        curr_count = current_elements.get(elem_type, 0)
                        if prev_count != curr_count:
                            change = curr_count - prev_count
                            sign = "+" if change > 0 else ""
                            print(f"  {elem_type}: {prev_count} -> {curr_count} ({sign}{change})")
            else:
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] No changes detected", end='', flush=True)
    
    def monitor(self, duration=None):
        """Monitor screen for specified duration (None = infinite)"""
        print(f"Starting ASCII monitor (width={self.width}, interval={self.interval}s)")
        print("Press Ctrl+C to stop")
        
        start_time = time.time()
        
        try:
            while True:
                # Check duration
                if duration and (time.time() - start_time) > duration:
                    break
                
                # Take screenshot and convert
                current_ascii, current_elements = self.take_ascii_screenshot()
                
                if current_ascii:
                    # Print changes
                    self.print_changes(current_ascii, current_elements)
                    
                    # Update previous state
                    self.previous_ascii = current_ascii
                    self.previous_elements = current_elements
                
                # Wait for next interval
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped")
    
    def compare_states(self, file1: str, file2: str):
        """Compare two saved ASCII states"""
        try:
            with open(file1, 'r', encoding='utf-8') as f:
                ascii1 = f.read()
            with open(file2, 'r', encoding='utf-8') as f:
                ascii2 = f.read()
            
            # Compute diff
            diff_result = compute_ascii_diff(ascii1, ascii2)
            
            print(f"\n=== Comparison: {os.path.basename(file1)} vs {os.path.basename(file2)} ===")
            print(f"Changed characters: {diff_result['changes']} ({diff_result['change_percentage']:.1f}%)")
            
            # Show regions with most changes
            if diff_result['changed_regions']:
                print("\nMost changed regions:")
                for i, (row, col, size) in enumerate(diff_result['changed_regions'][:5]):
                    print(f"  {i+1}. Row {row}-{row+size}, Col {col}")
            
            # Show highlighted diff
            print("\n=== Visual Diff (first 30 lines) ===")
            highlighted = highlight_differences(ascii1, ascii2)
            lines = highlighted.split('\n')[:30]
            for line in lines:
                print(line)
                
        except Exception as e:
            print(f"Error comparing files: {e}")

def main():
    parser = argparse.ArgumentParser(description='ASCII Screen Monitor')
    parser.add_argument('-w', '--width', type=int, default=80, help='ASCII width (default: 80)')
    parser.add_argument('-i', '--interval', type=float, default=2.0, help='Check interval in seconds (default: 2.0)')
    parser.add_argument('-d', '--duration', type=float, help='Monitor duration in seconds (default: infinite)')
    parser.add_argument('-n', '--no-ui', action='store_true', help='Disable UI detection')
    parser.add_argument('-c', '--compare', nargs=2, metavar=('FILE1', 'FILE2'), help='Compare two ASCII files')
    
    args = parser.parse_args()
    
    if args.compare:
        # Compare mode
        monitor = ASCIIMonitor(width=args.width, detect_ui=not args.no_ui)
        monitor.compare_states(args.compare[0], args.compare[1])
    else:
        # Monitor mode
        monitor = ASCIIMonitor(
            width=args.width,
            interval=args.interval,
            detect_ui=not args.no_ui
        )
        monitor.monitor(duration=args.duration)

if __name__ == "__main__":
    main()