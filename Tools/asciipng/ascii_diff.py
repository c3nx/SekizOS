#!/usr/bin/env python3
"""
ASCII Diff Tool
Compares two ASCII outputs to find differences
"""

import sys
import difflib
from ascii_converter import convert_to_ascii

def ascii_diff(ascii1, ascii2):
    """
    Compare two ASCII arts and highlight differences
    
    Returns:
        Dictionary with diff information
    """
    lines1 = ascii1.split('\n')
    lines2 = ascii2.split('\n')
    
    # Find differences
    differ = difflib.unified_diff(lines1, lines2, lineterm='')
    diff_lines = list(differ)
    
    # Count changed lines
    added = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
    removed = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
    
    # Find changed regions
    changed_regions = []
    for i, (line1, line2) in enumerate(zip(lines1, lines2)):
        if line1 != line2:
            # Find character-level differences
            for j, (c1, c2) in enumerate(zip(line1, line2)):
                if c1 != c2:
                    changed_regions.append({
                        'line': i,
                        'col': j,
                        'old': c1,
                        'new': c2
                    })
    
    return {
        'total_lines': len(lines1),
        'changed_lines': added + removed,
        'added_lines': added,
        'removed_lines': removed,
        'changed_regions': changed_regions[:10],  # First 10 changes
        'has_changes': len(diff_lines) > 0
    }

def compare_images(image1_path, image2_path, width=100):
    """Compare two images by converting to ASCII"""
    ascii1 = convert_to_ascii(image1_path, width)
    ascii2 = convert_to_ascii(image2_path, width)
    
    return ascii_diff(ascii1, ascii2)

def main():
    """CLI interface"""
    if len(sys.argv) < 3:
        print("Usage: ascii_diff.py <image1> <image2> [width]")
        sys.exit(1)
    
    image1 = sys.argv[1]
    image2 = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    result = compare_images(image1, image2, width)
    
    print(f"Total lines: {result['total_lines']}")
    print(f"Changed lines: {result['changed_lines']}")
    print(f"Has changes: {result['has_changes']}")
    
    if result['changed_regions']:
        print("\nFirst changes detected:")
        for change in result['changed_regions'][:5]:
            print(f"  Line {change['line']}, Col {change['col']}: '{change['old']}' → '{change['new']}'")

if __name__ == "__main__":
    main()