#!/usr/bin/env python3
"""
Enhanced ASCII Converter with custom settings
Based on the provided settings for better readability
"""

import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2

def enhance_image(image, brightness=2.0, contrast=0.95, sharpness=9):
    """Apply enhancements based on provided settings"""
    # Brightness (200% = 2.0)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)
    
    # Contrast (95% = 0.95)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)
    
    # Sharpness
    for _ in range(int(sharpness)):
        image = image.filter(ImageFilter.SHARPEN)
    
    return image

def apply_threshold(image, threshold=128):
    """Apply thresholding"""
    img_array = np.array(image)
    img_array = np.where(img_array > threshold, 255, img_array)
    return Image.fromarray(img_array)

def edge_detection(image, strength=1):
    """Simple edge detection"""
    if strength > 0:
        img_array = np.array(image)
        edges = cv2.Canny(img_array, 100, 200)
        # Blend edges with original
        result = cv2.addWeighted(img_array, 0.7, edges, 0.3 * strength, 0)
        return Image.fromarray(result)
    return image

def convert_to_ascii_enhanced(image_path, width=141, settings=None):
    """
    Convert image to ASCII with enhanced settings
    
    Default settings based on provided configuration:
    - Characters: 141 width
    - Brightness: 200% (2.0)
    - Contrast: 95% (0.95)
    - Sharpness: 9
    - Threshold: 128
    - Invert: 100% (True)
    """
    if settings is None:
        settings = {
            'brightness': 2.0,
            'contrast': 0.95,
            'sharpness': 9,
            'threshold': 128,
            'invert': True,
            'edge_detection': 1,
            'chars': "█▓▒░ "  # Dense to light
        }
    
    try:
        # Open and convert to grayscale
        image = Image.open(image_path).convert('L')
        
        # Apply enhancements
        image = enhance_image(image, 
                            settings.get('brightness', 2.0),
                            settings.get('contrast', 0.95),
                            settings.get('sharpness', 9))
        
        # Apply threshold
        if settings.get('threshold', 128) > 0:
            image = apply_threshold(image, settings['threshold'])
        
        # Invert if needed
        if settings.get('invert', True):
            image = Image.eval(image, lambda x: 255 - x)
        
        # Calculate height to maintain aspect ratio
        orig_width, orig_height = image.size
        aspect_ratio = orig_height / orig_width
        height = int(aspect_ratio * width * 0.55)
        
        # Resize
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Convert to ASCII
        pixels = np.array(image)
        chars = settings.get('chars', "█▓▒░ ")
        
        # Better normalization
        pixels = pixels.astype(float)
        min_val = pixels.min()
        max_val = pixels.max()
        
        if max_val > min_val:
            normalized = (pixels - min_val) / (max_val - min_val)
        else:
            normalized = np.zeros_like(pixels)
        
        # Map to characters
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
        print("Usage: ascii_converter_enhanced.py <image_path> [width]")
        print("Uses optimized settings for better readability")
        sys.exit(1)
    
    image_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 141
    
    ascii_art = convert_to_ascii_enhanced(image_path, width)
    print(ascii_art)

if __name__ == "__main__":
    main()