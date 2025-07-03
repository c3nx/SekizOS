#!/usr/bin/env python3
"""
Minimal ASCII Converter
Just converts images to ASCII art, nothing more
"""

import sys
from PIL import Image
import numpy as np

def convert_to_ascii(image_path, width=100, contrast=1.0, chars=None):
    """
    Convert image to ASCII art
    
    Args:
        image_path: Path to image file
        width: Width of ASCII output (default: 100)
        contrast: Contrast adjustment (default: 1.0)
        chars: ASCII characters to use (default: dense to light)
    
    Returns:
        ASCII art as string
    """
    # Default character set from dense to light
    if chars is None:
        chars = "█▓▒░ "
    
    try:
        # Open and convert to grayscale
        image = Image.open(image_path).convert('L')
        
        # Calculate height to maintain aspect ratio
        orig_width, orig_height = image.size
        aspect_ratio = orig_height / orig_width
        height = int(aspect_ratio * width * 0.55)  # 0.55 for terminal character aspect
        
        # Resize image
        image = image.resize((width, height))
        
        # Apply contrast if needed
        if contrast != 1.0:
            pixels = np.array(image)
            pixels = np.clip((pixels - 128) * contrast + 128, 0, 255)
            image = Image.fromarray(pixels.astype(np.uint8))
        
        # Convert pixels to ASCII
        pixels = np.array(image)
        
        # Normalize to character index
        normalized = (pixels - pixels.min()) / (pixels.max() - pixels.min())
        indices = (normalized * (len(chars) - 1)).astype(int)
        
        # Create ASCII art
        ascii_art = []
        for row in indices:
            ascii_art.append(''.join(chars[i] for i in row))
        
        return '\n'.join(ascii_art)
        
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: ascii_converter.py <image_path> [width] [contrast]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    contrast = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    
    ascii_art = convert_to_ascii(image_path, width, contrast)
    print(ascii_art)

if __name__ == "__main__":
    main()