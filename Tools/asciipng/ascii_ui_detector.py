#!/usr/bin/env python3
"""
Advanced ASCII UI Element Detector
Detects and annotates UI elements in ASCII art
"""

import re
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict

@dataclass
class UIElement:
    type: str
    row: int
    col: int
    width: int
    height: int
    confidence: float
    text: str = ""
    replacement: str = ""

class ASCIIUIDetector:
    def __init__(self):
        # Define patterns for UI elements
        self.patterns = {
            'download_arrow': {
                'patterns': [
                    # Small down arrow
                    ["  ▓  ", " ▓▓▓ ", "▓▓▓▓▓"],
                    ["  █  ", " ███ ", "█████"],
                    ["  ▒  ", " ▒▒▒ ", "▒▒▒▒▒"],
                    # Medium down arrow  
                    ["   ▓   ", "  ▓▓▓  ", " ▓▓▓▓▓ ", "▓▓▓▓▓▓▓"],
                    ["   █   ", "  ███  ", " █████ ", "███████"],
                ],
                'replacement': '⬇',
                'min_confidence': 0.7
            },
            'play_button': {
                'patterns': [
                    ["▓  ", "▓▓ ", "▓▓▓", "▓▓ ", "▓  "],
                    ["█  ", "██ ", "███", "██ ", "█  "],
                ],
                'replacement': '▶',
                'min_confidence': 0.8
            },
            'pause_button': {
                'patterns': [
                    ["▓▓ ▓▓", "▓▓ ▓▓", "▓▓ ▓▓"],
                    ["██ ██", "██ ██", "██ ██"],
                    ["▓ ▓", "▓ ▓", "▓ ▓"],
                ],
                'replacement': '⏸',
                'min_confidence': 0.8
            },
            'progress_bar': {
                'regex': r'[█▓]{3,}[░▒ ]{2,}',
                'replacement': lambda m: f'[{"█" * (len(m.group())//2)}{"_" * (len(m.group())//2)}]',
                'single_line': True
            },
            'button': {
                'regex': r'[▓█]{3,}\s*\w+\s*[▓█]{3,}',
                'replacement': lambda m: f'[{m.group().strip("▓█ ")}]',
                'single_line': True
            }
        }
    
    def calculate_similarity(self, region: List[str], pattern: List[str]) -> float:
        """Calculate similarity between a region and a pattern"""
        if len(region) != len(pattern):
            return 0.0
        
        total_chars = sum(len(line) for line in pattern)
        matching_chars = 0
        
        for i, (r_line, p_line) in enumerate(zip(region, pattern)):
            if len(r_line) >= len(p_line):
                for j, p_char in enumerate(p_line):
                    if j < len(r_line) and r_line[j] == p_char:
                        matching_chars += 1
        
        return matching_chars / total_chars if total_chars > 0 else 0.0
    
    def extract_region(self, lines: List[str], row: int, col: int, height: int, width: int) -> List[str]:
        """Extract a region from ASCII art"""
        region = []
        for i in range(height):
            if row + i < len(lines):
                line = lines[row + i]
                if col + width <= len(line):
                    region.append(line[col:col + width])
                else:
                    region.append(line[col:] + ' ' * (width - (len(line) - col)))
        return region
    
    def detect_patterns(self, ascii_art: str) -> List[UIElement]:
        """Detect all UI patterns in ASCII art"""
        lines = ascii_art.split('\n')
        detected = []
        
        # Check multi-line patterns
        for element_type, config in self.patterns.items():
            if 'patterns' in config:
                for pattern in config['patterns']:
                    pattern_height = len(pattern)
                    pattern_width = len(pattern[0])
                    
                    for row in range(len(lines) - pattern_height + 1):
                        for col in range(max(0, len(lines[row]) - pattern_width + 1)):
                            region = self.extract_region(lines, row, col, pattern_height, pattern_width)
                            
                            if len(region) == pattern_height:
                                similarity = self.calculate_similarity(region, pattern)
                                
                                if similarity >= config.get('min_confidence', 0.7):
                                    detected.append(UIElement(
                                        type=element_type,
                                        row=row,
                                        col=col,
                                        width=pattern_width,
                                        height=pattern_height,
                                        confidence=similarity,
                                        replacement=config.get('replacement', '?')
                                    ))
        
        # Check single-line patterns with regex
        for i, line in enumerate(lines):
            for element_type, config in self.patterns.items():
                if 'regex' in config and config.get('single_line', False):
                    matches = re.finditer(config['regex'], line)
                    for match in matches:
                        replacement = config['replacement']
                        if callable(replacement):
                            replacement_text = replacement(match)
                        else:
                            replacement_text = replacement
                        
                        detected.append(UIElement(
                            type=element_type,
                            row=i,
                            col=match.start(),
                            width=len(match.group()),
                            height=1,
                            confidence=1.0,
                            text=match.group(),
                            replacement=replacement_text
                        ))
        
        return detected
    
    def annotate_ascii(self, ascii_art: str, show_replacements: bool = True) -> Tuple[str, List[str]]:
        """Annotate ASCII art with detected elements"""
        elements = self.detect_patterns(ascii_art)
        lines = ascii_art.split('\n')
        annotations = []
        
        if show_replacements:
            # Sort by position to avoid conflicts
            elements.sort(key=lambda x: (x.row, x.col), reverse=True)
            
            # Apply replacements
            for elem in elements:
                if elem.replacement:
                    if elem.height == 1:
                        # Single line replacement
                        if elem.row < len(lines):
                            line = lines[elem.row]
                            before = line[:elem.col]
                            after = line[elem.col + elem.width:] if elem.col + elem.width < len(line) else ""
                            lines[elem.row] = before + elem.replacement + after
                    else:
                        # Multi-line pattern - replace with symbol in middle
                        middle_row = elem.row + elem.height // 2
                        if middle_row < len(lines):
                            line = lines[middle_row]
                            # Center the replacement
                            replacement = elem.replacement.center(elem.width)
                            before = line[:elem.col]
                            after = line[elem.col + elem.width:] if elem.col + elem.width < len(line) else ""
                            lines[middle_row] = before + replacement + after
                            
                            # Clear other lines of the pattern
                            for offset in range(elem.height):
                                if offset != elem.height // 2:
                                    row_idx = elem.row + offset
                                    if row_idx < len(lines):
                                        line = lines[row_idx]
                                        cleared = ' ' * elem.width
                                        before = line[:elem.col]
                                        after = line[elem.col + elem.width:] if elem.col + elem.width < len(line) else ""
                                        lines[row_idx] = before + cleared + after
        
        # Create annotations
        for elem in elements:
            ann = f"[{elem.row+1}:{elem.col+1}] {elem.type.replace('_', ' ').title()} (confidence: {elem.confidence:.0%})"
            if elem.text:
                ann += f" - '{elem.text}'"
            annotations.append(ann)
        
        return '\n'.join(lines), annotations

def main():
    """Test the UI detector"""
    import sys
    from ascii_converter_enhanced import convert_to_ascii_enhanced
    
    if len(sys.argv) < 2:
        print("Usage: ascii_ui_detector.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    detector = ASCIIUIDetector()
    
    # Convert to ASCII
    ascii_art = convert_to_ascii_enhanced(image_path, width=80)
    
    print("=== Original ASCII ===")
    print(ascii_art)
    
    # Detect and annotate
    annotated, annotations = detector.annotate_ascii(ascii_art, show_replacements=True)
    
    print("\n=== With UI Elements Replaced ===")
    print(annotated)
    
    print("\n=== Detected Elements ===")
    for ann in annotations[:20]:  # Show first 20
        print(ann)

if __name__ == "__main__":
    main()