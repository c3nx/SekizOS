#!/usr/bin/env python3
"""
ASCII Pattern Replacer
Recognizes common UI patterns in ASCII art and replaces them with actual characters
"""

import re
import numpy as np

# Common UI patterns to detect
PATTERNS = {
    # Arrow patterns (multi-line)
    'down_arrow': [
        [' ▓ ', '▓▓▓', ' ▓ '],  # Simple down arrow
        ['░▓░', '▓▓▓', '░▓░'],  # Down arrow with light borders
        [' █ ', '███', ' █ '],  # Bold down arrow
        ['  ▓  ', ' ▓▓▓ ', '▓▓▓▓▓', ' ▓▓▓ ', '  ▓  '],  # Large down arrow
    ],
    'up_arrow': [
        [' ▓ ', '▓▓▓', ' ▓ '],  # Reversed pattern
        ['  ▓  ', ' ▓▓▓ ', '▓▓▓▓▓'],  # Large up arrow
    ],
    'right_arrow': [
        ['▓ ', '▓▓', '▓▓', '▓ '],  # Side arrow
        ['░▓', '▓▓', '░▓'],
    ],
    'left_arrow': [
        [' ▓', '▓▓', '▓▓', ' ▓'],
    ],
    # Button patterns
    'button': [
        ['▓▓▓▓▓', '▓   ▓', '▓▓▓▓▓'],  # Simple button
        ['░▓▓▓░', '▓   ▓', '░▓▓▓░'],  # Button with borders
    ],
    # Progress bar patterns
    'progress': [
        ['█████░░░░░'],  # Progress bar partial
        ['▓▓▓▓▓▒▒▒▒▒'],  # Different style
    ],
}

# Replacement characters
REPLACEMENTS = {
    'down_arrow': '↓',
    'up_arrow': '↑',
    'right_arrow': '→',
    'left_arrow': '←',
    'button': '[■]',
    'progress': '[████____]',
}

def find_pattern_in_ascii(ascii_lines, pattern):
    """Find a pattern in ASCII art lines"""
    pattern_height = len(pattern)
    pattern_width = len(pattern[0])
    matches = []
    
    for i in range(len(ascii_lines) - pattern_height + 1):
        line_segment = ascii_lines[i:i + pattern_height]
        
        for j in range(len(line_segment[0]) - pattern_width + 1):
            # Extract region
            region = []
            for line in line_segment:
                if j + pattern_width <= len(line):
                    region.append(line[j:j + pattern_width])
            
            # Check if matches pattern
            if len(region) == pattern_height:
                match = True
                for pi, pattern_line in enumerate(pattern):
                    if isinstance(pattern_line, list):
                        pattern_str = ''.join(pattern_line)
                    else:
                        pattern_str = pattern_line
                        
                    if pi < len(region) and region[pi] != pattern_str:
                        match = False
                        break
                
                if match:
                    matches.append((i, j))
    
    return matches

def detect_ui_elements(ascii_art):
    """Detect common UI elements in ASCII art"""
    lines = ascii_art.split('\n')
    detected_elements = []
    
    # Look for arrow patterns
    for pattern_name, pattern_list in PATTERNS.items():
        for pattern in pattern_list:
            matches = find_pattern_in_ascii(lines, pattern)
            for row, col in matches:
                detected_elements.append({
                    'type': pattern_name,
                    'row': row,
                    'col': col,
                    'height': len(pattern),
                    'width': len(pattern[0]) if isinstance(pattern[0], list) else len(pattern[0]),
                    'replacement': REPLACEMENTS.get(pattern_name, '?')
                })
    
    # Look for single-line patterns (like progress bars)
    for i, line in enumerate(lines):
        # Detect download/progress indicators
        if re.search(r'[█▓]{3,}[░▒ ]{3,}', line):
            detected_elements.append({
                'type': 'progress_bar',
                'row': i,
                'col': line.find('█') if '█' in line else line.find('▓'),
                'text': 'Progress Bar Detected'
            })
        
        # Detect button-like structures
        if re.search(r'\[.+\]', line) or re.search(r'▓{3,}.*▓{3,}', line):
            detected_elements.append({
                'type': 'button',
                'row': i,
                'col': 0,
                'text': 'Button-like Element'
            })
    
    return detected_elements

def replace_patterns(ascii_art, min_confidence=0.7):
    """Replace detected patterns with actual characters"""
    lines = ascii_art.split('\n')
    modified_lines = lines.copy()
    
    # Detect elements
    elements = detect_ui_elements(ascii_art)
    
    # Sort by position to avoid conflicts
    elements.sort(key=lambda x: (x['row'], x.get('col', 0)), reverse=True)
    
    # Replace patterns
    for element in elements:
        if 'replacement' in element:
            row = element['row']
            col = element['col']
            replacement = element['replacement']
            
            # For multi-line patterns, replace middle line
            if element['height'] > 1:
                middle_row = row + element['height'] // 2
                if middle_row < len(modified_lines):
                    line = modified_lines[middle_row]
                    # Replace pattern with character centered
                    new_line = line[:col] + replacement.center(element['width']) + line[col + element['width']:]
                    modified_lines[middle_row] = new_line
            else:
                # Single line replacement
                if row < len(modified_lines):
                    line = modified_lines[row]
                    new_line = line[:col] + replacement + line[col + len(replacement):]
                    modified_lines[row] = new_line
    
    return '\n'.join(modified_lines), elements

def annotate_ascii(ascii_art):
    """Add annotations for detected UI elements"""
    lines = ascii_art.split('\n')
    elements = detect_ui_elements(ascii_art)
    
    annotations = []
    for element in elements:
        annotation = f"Line {element['row']+1}: {element['type'].replace('_', ' ').title()}"
        if 'text' in element:
            annotation += f" - {element['text']}"
        annotations.append(annotation)
    
    return ascii_art, annotations

def main():
    """Test the pattern replacer"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: ascii_pattern_replacer.py <image_path>")
        print("Detects and replaces UI patterns in ASCII art")
        sys.exit(1)
    
    # First convert to ASCII
    from ascii_converter_enhanced import convert_to_ascii_enhanced
    
    image_path = sys.argv[1]
    ascii_art = convert_to_ascii_enhanced(image_path)
    
    print("=== Original ASCII ===")
    print(ascii_art[:500] + "..." if len(ascii_art) > 500 else ascii_art)
    
    print("\n=== Pattern Detection ===")
    _, annotations = annotate_ascii(ascii_art)
    for ann in annotations[:10]:  # Show first 10
        print(ann)
    
    print("\n=== With Replacements ===")
    replaced, elements = replace_patterns(ascii_art)
    print(replaced[:500] + "..." if len(replaced) > 500 else replaced)
    
    print(f"\nTotal elements detected: {len(elements)}")

if __name__ == "__main__":
    main()