#!/usr/bin/env python3
"""
ShowUI Command Line Tool
A simple CLI for interacting with ShowUI vision model
"""

import argparse
import sys
import json
import time
import base64
import requests
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Try to import windows_control if available
try:
    from windows_control import WindowsControl
    HAS_WINDOWS_CONTROL = True
except ImportError:
    HAS_WINDOWS_CONTROL = False
    print("Warning: windows_control not found. Limited functionality.")

# ANSI color codes for pretty output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str = Colors.RESET, bold: bool = False):
    """Print colored text to terminal"""
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.RESET}")
    else:
        print(f"{color}{text}{Colors.RESET}")

def get_screenshot() -> Optional[str]:
    """Get screenshot from Windows Agent"""
    if not HAS_WINDOWS_CONTROL:
        return None
    
    try:
        win = WindowsControl()
        win.screenshot("_temp_screenshot.png")
        
        with open("_temp_screenshot.png", "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        # Clean up temp file
        Path("_temp_screenshot.png").unlink(missing_ok=True)
        return image_data
    except Exception as e:
        print_colored(f"Error getting screenshot: {e}", Colors.RED)
        return None

def load_image(image_path: str) -> Optional[str]:
    """Load and encode image from file"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        print_colored(f"Error loading image: {e}", Colors.RED)
        return None

def query_showui(image_data: str, query: str, showui_url: str = "http://localhost:8766/vision/analyze") -> Dict[str, Any]:
    """Send query to ShowUI service"""
    try:
        response = requests.post(showui_url, json={
            "image": image_data,
            "query": query
        }, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def format_result(query: str, result: Dict[str, Any], show_response: bool = False) -> None:
    """Format and print query result"""
    print(f"\n{Colors.BOLD}Query:{Colors.RESET} {query}")
    
    if not result.get('success'):
        print_colored(f"  ✗ Error: {result.get('error', 'Unknown error')}", Colors.RED)
        return
    
    if result.get('found'):
        coords = result.get('coordinates', {})
        x, y = coords.get('x', 0), coords.get('y', 0)
        print_colored(f"  ✓ Found at: ({x}, {y})", Colors.GREEN)
        
        # Show inference time if available
        if 'inference_time' in result:
            print(f"  ⏱  Time: {result['inference_time']:.2f}s")
    else:
        print_colored("  ✗ Not found", Colors.YELLOW)
    
    if show_response and 'response' in result:
        print(f"  📝 Response: {result['response'][:100]}...")

def click_element(image_data: str, query: str, showui_url: str = "http://localhost:8766/vision/analyze") -> bool:
    """Find and click an element"""
    if not HAS_WINDOWS_CONTROL:
        print_colored("Error: Windows control not available for clicking", Colors.RED)
        return False
    
    result = query_showui(image_data, query, showui_url)
    
    if result.get('success') and result.get('found'):
        coords = result.get('coordinates', {})
        x, y = coords.get('x', 0), coords.get('y', 0)
        
        print_colored(f"Found element at ({x}, {y})", Colors.GREEN)
        print(f"Clicking...")
        
        try:
            win = WindowsControl()
            win.click(x, y)
            print_colored("✓ Clicked successfully!", Colors.GREEN, bold=True)
            return True
        except Exception as e:
            print_colored(f"✗ Click failed: {e}", Colors.RED)
            return False
    else:
        print_colored("✗ Element not found", Colors.YELLOW)
        return False

def analyze_ui(image_data: str, analysis_type: str = "general") -> List[Dict[str, Any]]:
    """Run comprehensive UI analysis"""
    queries = {
        "general": [
            "find all buttons",
            "find all clickable elements",
            "find all text elements",
            "find navigation elements",
            "find input fields",
            "find images or icons"
        ],
        "downloads": [
            "find download progress",
            "find pause or resume buttons",
            "find download speed",
            "find time remaining",
            "find game titles",
            "find install buttons"
        ],
        "library": [
            "find game titles",
            "find play buttons",
            "find download buttons",
            "find game cover images",
            "find categories or filters",
            "find search bar"
        ]
    }
    
    selected_queries = queries.get(analysis_type, queries["general"])
    results = []
    
    print_colored(f"\n=== Running {analysis_type.upper()} Analysis ===", Colors.CYAN, bold=True)
    
    for query in selected_queries:
        result = query_showui(image_data, query)
        format_result(query, result)
        
        if result.get('success'):
            results.append({
                'query': query,
                'found': result.get('found', False),
                'coordinates': result.get('coordinates', {}) if result.get('found') else None
            })
        
        time.sleep(0.5)  # Don't overwhelm the service
    
    # Summary
    found_count = sum(1 for r in results if r['found'])
    print_colored(f"\n=== Summary: {found_count}/{len(results)} elements found ===", Colors.CYAN, bold=True)
    
    return results

def save_marked_screenshot(image_data: str, results: List[Dict[str, Any]], output_path: str):
    """Save screenshot with detected elements marked"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        
        # Decode image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        draw = ImageDraw.Draw(image)
        
        # Try to load font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), 
            (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
        
        # Draw detected elements
        for i, result in enumerate(results):
            if result['found'] and result['coordinates']:
                x = result['coordinates']['x']
                y = result['coordinates']['y']
                color = colors[i % len(colors)]
                
                # Draw crosshair
                draw.line([(x-20, y), (x+20, y)], fill=color, width=3)
                draw.line([(x, y-20), (x, y+20)], fill=color, width=3)
                
                # Draw circle
                draw.ellipse([(x-15, y-15), (x+15, y+15)], outline=color, width=3)
                
                # Add label
                label = f"{i+1}: {result['query'][:20]}..."
                draw.text((x+25, y-10), label, fill=color, font=font)
        
        image.save(output_path)
        print_colored(f"✓ Marked screenshot saved to: {output_path}", Colors.GREEN)
        
    except Exception as e:
        print_colored(f"Error saving marked screenshot: {e}", Colors.RED)

def main():
    parser = argparse.ArgumentParser(
        description='ShowUI Command Line Tool - UI element detection using AI vision',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  showui -q "find pause button"                    # Find UI element
  showui -c "click on download button"             # Find and click element
  showui -q "find buttons" -q "find text"          # Multiple queries
  showui --analyze                                 # Run comprehensive analysis
  showui -q "find buttons" -s marked.png           # Save marked screenshot
  showui -q "find buttons" --json                  # Output as JSON
  showui -i screenshot.png -q "find buttons"       # Analyze specific image
        """
    )
    
    parser.add_argument('-q', '--query', action='append', 
                        help='Query to send to ShowUI (can be used multiple times)')
    parser.add_argument('-c', '--click', 
                        help='Find and click an element')
    parser.add_argument('-a', '--analyze', nargs='?', const='general',
                        choices=['general', 'downloads', 'library'],
                        help='Run comprehensive UI analysis')
    parser.add_argument('-i', '--image', 
                        help='Path to image file to analyze (uses screenshot if not provided)')
    parser.add_argument('-s', '--save-marks', 
                        help='Save screenshot with detected elements marked')
    parser.add_argument('-o', '--output', 
                        help='Save results to JSON file')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    parser.add_argument('--show-response', action='store_true',
                        help='Show full model response')
    parser.add_argument('--url', default='http://localhost:8766/vision/analyze',
                        help='ShowUI service URL')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.query, args.click, args.analyze]):
        parser.print_help()
        sys.exit(1)
    
    # Get image data
    if args.image:
        image_data = load_image(args.image)
        if not image_data:
            sys.exit(1)
    else:
        print("Taking screenshot...")
        image_data = get_screenshot()
        if not image_data:
            print_colored("Error: Could not get screenshot", Colors.RED)
            sys.exit(1)
    
    results = []
    
    # Handle click mode
    if args.click:
        success = click_element(image_data, args.click, args.url)
        sys.exit(0 if success else 1)
    
    # Handle analysis mode
    if args.analyze:
        results = analyze_ui(image_data, args.analyze)
    
    # Handle queries
    if args.query:
        for query in args.query:
            result = query_showui(image_data, query, args.url)
            format_result(query, result, args.show_response)
            
            if result.get('success'):
                results.append({
                    'query': query,
                    'found': result.get('found', False),
                    'coordinates': result.get('coordinates', {}) if result.get('found') else None,
                    'response': result.get('response', '') if args.show_response else None
                })
    
    # Save marked screenshot if requested
    if args.save_marks and results:
        save_marked_screenshot(image_data, results, args.save_marks)
    
    # Output results
    if args.json or args.output:
        output_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print_colored(f"\n✓ Results saved to: {args.output}", Colors.GREEN)
        else:
            print(json.dumps(output_data, indent=2))

if __name__ == "__main__":
    main()