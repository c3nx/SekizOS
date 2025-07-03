#!/usr/bin/env python3
"""
Specialized Arrow Detector for ASCII Art
Focuses on detecting arrow patterns in download buttons
"""

def detect_download_arrow(ascii_art):
    """
    Detect download arrow pattern in ASCII art
    Looking for patterns like:
    - Central vertical line getting wider (arrow shaft)
    - Widening at bottom (arrow head)
    """
    lines = ascii_art.split('\n')
    
    # Look for arrow-like patterns
    for i in range(len(lines) - 3):
        # Simple pattern matching for download arrow
        # Check if lines get progressively wider (arrow head)
        if i + 2 < len(lines):
            line1 = lines[i].strip()
            line2 = lines[i + 1].strip()
            line3 = lines[i + 2].strip()
            
            # Count dark pixels (█▓▒) in each line
            dark1 = sum(1 for c in line1 if c in '█▓▒')
            dark2 = sum(1 for c in line2 if c in '█▓▒')
            dark3 = sum(1 for c in line3 if c in '█▓▒')
            
            # Arrow pattern: line gets wider as we go down
            if dark1 > 0 and dark2 > dark1 and dark3 > dark2:
                # Check for symmetry (arrow should be centered)
                if len(line2) > 0:
                    center = len(line2) // 2
                    left = line2[:center]
                    right = line2[center:]
                    
                    # Rough symmetry check
                    if len(left) > 0 and len(right) > 0:
                        return True, i, "Download arrow detected"
    
    return False, -1, "No arrow found"

def annotate_with_arrows(ascii_art):
    """Replace detected arrow patterns with arrow symbol"""
    lines = ascii_art.split('\n')
    
    # Detect arrow
    found, row, message = detect_download_arrow(ascii_art)
    
    if found and row >= 0:
        # Find the center of the arrow
        if row + 2 < len(lines):
            # Replace middle of arrow area with down arrow symbol
            arrow_line = lines[row + 1]
            center = len(arrow_line) // 2
            
            # Insert arrow symbol
            if center > 0:
                new_line = arrow_line[:center-1] + '⬇' + arrow_line[center+1:]
                lines[row + 1] = new_line
                
                # Clear surrounding lines for clarity
                if row < len(lines):
                    lines[row] = ' ' * len(lines[row])
                if row + 2 < len(lines):
                    lines[row + 2] = ' ' * len(lines[row + 2])
    
    return '\n'.join(lines), found, message

def main():
    import sys
    from ascii_converter_enhanced import convert_to_ascii_enhanced
    
    if len(sys.argv) < 2:
        print("Usage: ascii_arrow_detector.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Convert with different sizes
    for width in [15, 20, 30]:
        print(f"\n=== Width: {width} ===")
        ascii_art = convert_to_ascii_enhanced(image_path, width)
        
        # Original
        print("Original:")
        print(ascii_art)
        
        # With arrow detection
        annotated, found, message = annotate_with_arrows(ascii_art)
        print(f"\n{message}")
        
        if found:
            print("With arrow symbol:")
            print(annotated)

if __name__ == "__main__":
    main()