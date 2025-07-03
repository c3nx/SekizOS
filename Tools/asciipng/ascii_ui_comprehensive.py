#!/usr/bin/env python3
"""
Comprehensive ASCII UI Pattern Detector
Combines arrow detection, button detection, progress bars, and more
"""

import re
import numpy as np
from typing import List, Tuple, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum

class UIElementType(Enum):
    ARROW_DOWN = "arrow_down"
    ARROW_UP = "arrow_up"
    ARROW_LEFT = "arrow_left"
    ARROW_RIGHT = "arrow_right"
    BUTTON = "button"
    PROGRESS_BAR = "progress_bar"
    CHECKBOX = "checkbox"
    RADIO_BUTTON = "radio_button"
    TEXT_INPUT = "text_input"
    MENU_ITEM = "menu_item"
    PAUSE_BUTTON = "pause_button"
    PLAY_BUTTON = "play_button"
    STOP_BUTTON = "stop_button"

@dataclass
class UIElement:
    type: UIElementType
    row: int
    col: int
    width: int
    height: int
    confidence: float
    text: str = ""
    replacement: str = ""
    metadata: Dict = None

class ComprehensiveUIDetector:
    def __init__(self):
        # Character sets
        self.dark_chars = set('█▓▒')
        self.medium_chars = set('▒░')
        self.light_chars = set('░ ')
        self.border_chars = set('│─┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬')
        
        # UI element patterns
        self.patterns = self._initialize_patterns()
        
        # Regex patterns for single-line elements
        self.regex_patterns = {
            UIElementType.PROGRESS_BAR: [
                (r'[█▓]{2,}[░▒ ]{2,}', lambda m: self._format_progress_bar(m.group())),
                (r'\[=[=>]+[-\s]*\]', lambda m: self._format_progress_bar(m.group())),
                (r'\d+%.*[█▓]{2,}', lambda m: self._format_progress_bar(m.group())),
            ],
            UIElementType.BUTTON: [
                (r'\[[\w\s]+\]', lambda m: m.group()),
                (r'[▓█]{3,}[\w\s]+[▓█]{3,}', lambda m: f'[{m.group().strip("▓█ ")}]'),
            ],
            UIElementType.TEXT_INPUT: [
                (r'[│┃][\s\w]*[│┃]', lambda m: f'[{m.group().strip("│┃ ")}]'),
                (r'___+', lambda m: '[___]'),
            ],
            UIElementType.CHECKBOX: [
                (r'\[[ xX]\]', lambda m: '☑' if m.group()[1] in 'xX' else '☐'),
                (r'[▓█] ', lambda m: '☑'),
                (r'[░ ] ', lambda m: '☐'),
            ],
        }
        
    def _initialize_patterns(self) -> Dict[UIElementType, List[Tuple[List[str], float]]]:
        """Initialize multi-line patterns for UI elements"""
        return {
            UIElementType.ARROW_DOWN: [
                # Small arrows
                ([' █ ', '███'], 0.9),
                ([' ▓ ', '▓▓▓'], 0.9),
                ([' █ ', ' █ ', '███'], 0.95),
                # Medium arrows
                (['  █  ', ' ███ ', '█████'], 0.95),
                (['  ▓  ', ' ▓▓▓ ', '▓▓▓▓▓'], 0.95),
                (['  █  ', '  █  ', ' ███ ', '█████'], 0.98),
                # Large arrows
                (['   █   ', '  ███  ', ' █████ ', '███████'], 0.95),
            ],
            UIElementType.ARROW_UP: [
                (['███', ' █ '], 0.9),
                (['▓▓▓', ' ▓ '], 0.9),
                (['█████', ' ███ ', '  █  '], 0.95),
            ],
            UIElementType.ARROW_RIGHT: [
                (['█ ', '██', '██', '█ '], 0.9),
                (['█  ', '██ ', '███', '██ ', '█  '], 0.95),
            ],
            UIElementType.ARROW_LEFT: [
                ([' █', '██', '██', ' █'], 0.9),
                (['  █', ' ██', '███', ' ██', '  █'], 0.95),
            ],
            UIElementType.PAUSE_BUTTON: [
                (['█ █', '█ █', '█ █'], 0.9),
                (['▓ ▓', '▓ ▓', '▓ ▓'], 0.9),
                (['██ ██', '██ ██', '██ ██'], 0.95),
            ],
            UIElementType.PLAY_BUTTON: [
                (['█  ', '██ ', '███', '██ ', '█  '], 0.9),
                (['▓  ', '▓▓ ', '▓▓▓', '▓▓ ', '▓  '], 0.9),
            ],
            UIElementType.STOP_BUTTON: [
                (['███', '███', '███'], 0.9),
                (['▓▓▓', '▓▓▓', '▓▓▓'], 0.9),
            ],
        }
    
    def _format_progress_bar(self, text: str) -> str:
        """Format a progress bar with standard representation"""
        # Count filled vs empty
        filled = sum(1 for c in text if c in '█▓=')
        total = len(text.strip('[]% '))
        
        if total > 0:
            percent = int((filled / total) * 100)
            bar_width = 10
            filled_width = int((percent / 100) * bar_width)
            return f'[{"█" * filled_width}{"_" * (bar_width - filled_width)}] {percent}%'
        
        return '[____] 0%'
    
    def _extract_region(self, lines: List[str], row: int, col: int, height: int, width: int) -> Optional[List[str]]:
        """Extract a region from ASCII art"""
        if row + height > len(lines):
            return None
            
        region = []
        for i in range(height):
            if row + i >= len(lines):
                return None
            line = lines[row + i]
            if col + width > len(line):
                # Pad with spaces if line is too short
                padded = line[col:] + ' ' * (width - (len(line) - col))
                region.append(padded[:width])
            else:
                region.append(line[col:col + width])
                
        return region
    
    def _calculate_similarity(self, region: List[str], pattern: List[str]) -> float:
        """Calculate similarity between region and pattern"""
        if len(region) != len(pattern):
            return 0.0
            
        total_score = 0.0
        total_chars = 0
        
        for r_line, p_line in zip(region, pattern):
            if len(r_line) != len(p_line):
                return 0.0
                
            for r_char, p_char in zip(r_line, p_line):
                total_chars += 1
                
                if r_char == p_char:
                    total_score += 1.0
                elif r_char in self.dark_chars and p_char in self.dark_chars:
                    total_score += 0.8
                elif r_char in self.light_chars and p_char in self.light_chars:
                    total_score += 0.7
                    
        return total_score / total_chars if total_chars > 0 else 0.0
    
    def _detect_multi_line_patterns(self, lines: List[str]) -> List[UIElement]:
        """Detect multi-line UI patterns"""
        detected = []
        
        for ui_type, patterns in self.patterns.items():
            for pattern, base_confidence in patterns:
                pattern_height = len(pattern)
                pattern_width = len(pattern[0])
                
                for row in range(len(lines) - pattern_height + 1):
                    max_col = len(lines[row]) - pattern_width + 1 if lines[row] else 0
                    
                    for col in range(max(0, max_col)):
                        region = self._extract_region(lines, row, col, pattern_height, pattern_width)
                        
                        if region:
                            similarity = self._calculate_similarity(region, pattern)
                            confidence = similarity * base_confidence
                            
                            if confidence >= 0.7:
                                # Choose appropriate symbol
                                symbol = self._get_symbol_for_type(ui_type)
                                
                                detected.append(UIElement(
                                    type=ui_type,
                                    row=row,
                                    col=col,
                                    width=pattern_width,
                                    height=pattern_height,
                                    confidence=confidence,
                                    replacement=symbol
                                ))
                                
        return detected
    
    def _detect_single_line_patterns(self, lines: List[str]) -> List[UIElement]:
        """Detect single-line UI patterns using regex"""
        detected = []
        
        for row, line in enumerate(lines):
            for ui_type, patterns in self.regex_patterns.items():
                for regex, formatter in patterns:
                    for match in re.finditer(regex, line):
                        replacement = formatter(match) if callable(formatter) else formatter
                        
                        detected.append(UIElement(
                            type=ui_type,
                            row=row,
                            col=match.start(),
                            width=len(match.group()),
                            height=1,
                            confidence=0.9,
                            text=match.group(),
                            replacement=replacement
                        ))
                        
        return detected
    
    def _get_symbol_for_type(self, ui_type: UIElementType) -> str:
        """Get appropriate symbol for UI element type"""
        symbols = {
            UIElementType.ARROW_DOWN: '⬇',
            UIElementType.ARROW_UP: '⬆',
            UIElementType.ARROW_LEFT: '⬅',
            UIElementType.ARROW_RIGHT: '➡',
            UIElementType.PAUSE_BUTTON: '⏸',
            UIElementType.PLAY_BUTTON: '▶',
            UIElementType.STOP_BUTTON: '⏹',
            UIElementType.CHECKBOX: '☐',
            UIElementType.RADIO_BUTTON: '○',
        }
        return symbols.get(ui_type, '?')
    
    def detect_ui_elements(self, ascii_art: str) -> List[UIElement]:
        """Detect all UI elements in ASCII art"""
        lines = ascii_art.split('\n')
        
        # Detect both multi-line and single-line patterns
        multi_line = self._detect_multi_line_patterns(lines)
        single_line = self._detect_single_line_patterns(lines)
        
        # Combine and sort by position
        all_elements = multi_line + single_line
        all_elements.sort(key=lambda x: (x.row, x.col))
        
        # Remove overlapping detections (keep highest confidence)
        filtered = []
        occupied = set()
        
        for elem in sorted(all_elements, key=lambda x: -x.confidence):
            # Check if this region overlaps with any already detected
            overlap = False
            for r in range(elem.row, elem.row + elem.height):
                for c in range(elem.col, elem.col + elem.width):
                    if (r, c) in occupied:
                        overlap = True
                        break
                if overlap:
                    break
                    
            if not overlap:
                filtered.append(elem)
                # Mark region as occupied
                for r in range(elem.row, elem.row + elem.height):
                    for c in range(elem.col, elem.col + elem.width):
                        occupied.add((r, c))
                        
        return filtered
    
    def apply_replacements(self, ascii_art: str, elements: List[UIElement]) -> str:
        """Apply UI element replacements to ASCII art"""
        lines = ascii_art.split('\n')
        
        # Sort by position (reverse to avoid index issues)
        elements.sort(key=lambda x: (x.row, x.col), reverse=True)
        
        for elem in elements:
            if elem.replacement:
                if elem.height == 1:
                    # Single line replacement
                    if elem.row < len(lines):
                        line = lines[elem.row]
                        before = line[:elem.col] if elem.col < len(line) else line
                        after = line[elem.col + elem.width:] if elem.col + elem.width < len(line) else ""
                        lines[elem.row] = before + elem.replacement + after
                else:
                    # Multi-line replacement - put symbol in center
                    center_row = elem.row + elem.height // 2
                    if center_row < len(lines):
                        line = lines[center_row]
                        # Center the symbol
                        replacement = elem.replacement.center(elem.width)
                        before = line[:elem.col] if elem.col < len(line) else line
                        after = line[elem.col + elem.width:] if elem.col + elem.width < len(line) else ""
                        lines[center_row] = before + replacement + after
                        
                        # Clear other rows
                        for r in range(elem.row, elem.row + elem.height):
                            if r != center_row and r < len(lines):
                                line = lines[r]
                                cleared = ' ' * elem.width
                                before = line[:elem.col] if elem.col < len(line) else line
                                after = line[elem.col + elem.width:] if elem.col + elem.width < len(line) else ""
                                lines[r] = before + cleared + after
                                
        return '\n'.join(lines)
    
    def analyze_ascii(self, ascii_art: str, apply_replacements: bool = True) -> Dict:
        """Comprehensive analysis of ASCII art"""
        elements = self.detect_ui_elements(ascii_art)
        
        result = {
            'original': ascii_art,
            'elements': elements,
            'element_count': len(elements),
            'element_types': {}
        }
        
        # Count by type
        for elem in elements:
            type_name = elem.type.value
            if type_name not in result['element_types']:
                result['element_types'][type_name] = 0
            result['element_types'][type_name] += 1
        
        # Apply replacements if requested
        if apply_replacements:
            result['annotated'] = self.apply_replacements(ascii_art, elements)
        
        # Create summary
        summary = []
        for elem in elements[:10]:  # First 10 elements
            summary.append(f"[{elem.row+1}:{elem.col+1}] {elem.type.value} "
                          f"(conf: {elem.confidence:.0%})")
            
        result['summary'] = summary
        
        return result

def main():
    """Test the comprehensive UI detector"""
    import sys
    from ascii_converter_enhanced import convert_to_ascii_enhanced
    
    if len(sys.argv) < 2:
        print("Usage: ascii_ui_comprehensive.py <image_path> [width]")
        sys.exit(1)
        
    image_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    # Convert to ASCII
    ascii_art = convert_to_ascii_enhanced(image_path, width)
    
    # Analyze
    detector = ComprehensiveUIDetector()
    result = detector.analyze_ascii(ascii_art, apply_replacements=True)
    
    print("=== Original ASCII ===")
    print(result['original'][:500] + "..." if len(result['original']) > 500 else result['original'])
    
    print(f"\n=== Detected {result['element_count']} UI Elements ===")
    print("Element types:")
    for elem_type, count in result['element_types'].items():
        print(f"  {elem_type}: {count}")
    
    print("\nFirst 10 elements:")
    for line in result['summary']:
        print(f"  {line}")
    
    if 'annotated' in result:
        print("\n=== With UI Replacements ===")
        print(result['annotated'][:500] + "..." if len(result['annotated']) > 500 else result['annotated'])

if __name__ == "__main__":
    main()