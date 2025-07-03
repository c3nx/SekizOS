#!/usr/bin/env python3
"""
Advanced Arrow Pattern Detector for ASCII Art
Detects various arrow patterns with improved accuracy
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

@dataclass
class ArrowPattern:
    """Represents an arrow pattern detection result"""
    type: str  # down, up, left, right
    row: int
    col: int
    confidence: float
    size: str  # small, medium, large
    symbol: str

class AdvancedArrowDetector:
    def __init__(self):
        # Define arrow patterns with variations
        self.arrow_patterns = {
            'down': {
                'symbol': '⬇',
                'patterns': {
                    'small': [
                        # Basic patterns
                        ([' █ ', '███'], 0.9),
                        ([' ▓ ', '▓▓▓'], 0.9),
                        ([' ▒ ', '▒▒▒'], 0.8),
                        # With shaft
                        ([' █ ', ' █ ', '███'], 0.95),
                        ([' ▓ ', ' ▓ ', '▓▓▓'], 0.95),
                        # Hollow patterns
                        ([' ▓ ', '▓ ▓', '▓▓▓'], 0.85),
                    ],
                    'medium': [
                        # Standard medium arrows
                        (['  █  ', ' ███ ', '█████'], 0.95),
                        (['  ▓  ', ' ▓▓▓ ', '▓▓▓▓▓'], 0.95),
                        (['  ▒  ', ' ▒▒▒ ', '▒▒▒▒▒'], 0.9),
                        # With longer shaft
                        (['  █  ', '  █  ', ' ███ ', '█████'], 0.98),
                        (['  ▓  ', '  ▓  ', ' ▓▓▓ ', '▓▓▓▓▓'], 0.98),
                        # Thick shaft
                        ([' ███ ', ' ███ ', '█████', '█████'], 0.9),
                    ],
                    'large': [
                        # Large arrows
                        (['   █   ', '  ███  ', ' █████ ', '███████'], 0.95),
                        (['   ▓   ', '  ▓▓▓  ', ' ▓▓▓▓▓ ', '▓▓▓▓▓▓▓'], 0.95),
                        # Extra large
                        (['    █    ', '   ███   ', '  █████  ', ' ███████ ', '█████████'], 0.95),
                    ]
                }
            },
            'up': {
                'symbol': '⬆',
                'patterns': {
                    'small': [
                        (['███', ' █ '], 0.9),
                        (['▓▓▓', ' ▓ '], 0.9),
                        (['███', ' █ ', ' █ '], 0.95),
                    ],
                    'medium': [
                        (['█████', ' ███ ', '  █  '], 0.95),
                        (['▓▓▓▓▓', ' ▓▓▓ ', '  ▓  '], 0.95),
                    ],
                    'large': [
                        (['███████', ' █████ ', '  ███  ', '   █   '], 0.95),
                    ]
                }
            },
            'right': {
                'symbol': '➡',
                'patterns': {
                    'small': [
                        (['█ ', '██', '██', '█ '], 0.9),
                        (['▓ ', '▓▓', '▓▓', '▓ '], 0.9),
                    ],
                    'medium': [
                        (['█  ', '██ ', '███', '██ ', '█  '], 0.95),
                    ]
                }
            },
            'left': {
                'symbol': '⬅',
                'patterns': {
                    'small': [
                        ([' █', '██', '██', ' █'], 0.9),
                        ([' ▓', '▓▓', '▓▓', ' ▓'], 0.9),
                    ],
                    'medium': [
                        (['  █', ' ██', '███', ' ██', '  █'], 0.95),
                    ]
                }
            }
        }
        
        # Character sets for detection
        self.dark_chars = set('█▓▒')
        self.light_chars = set('░ ')
        
    def _extract_region(self, lines: List[str], row: int, col: int, height: int, width: int) -> Optional[List[str]]:
        """Extract a region from ASCII art lines"""
        if row + height > len(lines):
            return None
            
        region = []
        for i in range(height):
            line = lines[row + i]
            if col + width > len(line):
                return None
            region.append(line[col:col + width])
            
        return region
    
    def _calculate_pattern_match(self, region: List[str], pattern: List[str]) -> float:
        """Calculate how well a region matches a pattern"""
        if len(region) != len(pattern):
            return 0.0
            
        total_score = 0.0
        total_chars = 0
        
        for r_line, p_line in zip(region, pattern):
            if len(r_line) != len(p_line):
                return 0.0
                
            for r_char, p_char in zip(r_line, p_line):
                total_chars += 1
                
                # Exact match
                if r_char == p_char:
                    total_score += 1.0
                # Dark character match (█▓▒ are somewhat interchangeable)
                elif r_char in self.dark_chars and p_char in self.dark_chars:
                    total_score += 0.8
                # Light character match
                elif r_char in self.light_chars and p_char in self.light_chars:
                    total_score += 0.7
                # Mismatch between dark and light
                else:
                    total_score += 0.0
                    
        return total_score / total_chars if total_chars > 0 else 0.0
    
    def _check_arrow_context(self, lines: List[str], row: int, col: int, arrow_type: str) -> float:
        """Check surrounding context to improve arrow detection confidence"""
        context_score = 1.0
        
        # Check for button-like borders around arrow
        if row > 0 and row < len(lines) - 1:
            above = lines[row - 1]
            below = lines[row + 1]
            
            # Check for horizontal borders
            if col > 0 and col < len(above) - 1:
                if above[col-1:col+2] in ['───', '━━━', '═══']:
                    context_score *= 1.1
                if below[col-1:col+2] in ['───', '━━━', '═══']:
                    context_score *= 1.1
                    
        # Check for download-related text nearby
        search_radius = 3
        for i in range(max(0, row - search_radius), min(len(lines), row + search_radius + 1)):
            line_lower = lines[i].lower()
            if any(word in line_lower for word in ['download', 'pause', 'resume', 'update']):
                context_score *= 1.2
                break
                
        return min(context_score, 1.5)  # Cap at 1.5
    
    def detect_arrows(self, ascii_art: str) -> List[ArrowPattern]:
        """Detect all arrow patterns in ASCII art"""
        lines = ascii_art.split('\n')
        detected = []
        
        # Track already detected regions to avoid duplicates
        detected_regions = set()
        
        for arrow_type, arrow_config in self.arrow_patterns.items():
            symbol = arrow_config['symbol']
            
            for size, size_patterns in arrow_config['patterns'].items():
                for pattern, base_confidence in size_patterns:
                    pattern_height = len(pattern)
                    pattern_width = len(pattern[0])
                    
                    # Scan through the ASCII art
                    for row in range(len(lines) - pattern_height + 1):
                        for col in range(max(0, len(lines[row]) - pattern_width + 1)):
                            # Skip if region already detected
                            region_key = (row, col, row + pattern_height, col + pattern_width)
                            if region_key in detected_regions:
                                continue
                                
                            region = self._extract_region(lines, row, col, pattern_height, pattern_width)
                            if region is None:
                                continue
                                
                            # Calculate pattern match
                            match_score = self._calculate_pattern_match(region, pattern)
                            
                            # Apply context bonus
                            context_multiplier = self._check_arrow_context(lines, row, col, arrow_type)
                            final_confidence = match_score * base_confidence * context_multiplier
                            
                            # Detection threshold
                            if final_confidence >= 0.7:
                                detected.append(ArrowPattern(
                                    type=arrow_type,
                                    row=row,
                                    col=col,
                                    confidence=min(final_confidence, 1.0),
                                    size=size,
                                    symbol=symbol
                                ))
                                detected_regions.add(region_key)
                                
        # Sort by confidence and position
        detected.sort(key=lambda x: (-x.confidence, x.row, x.col))
        
        return detected
    
    def annotate_ascii(self, ascii_art: str, show_replacements: bool = True) -> Tuple[str, List[str]]:
        """Annotate ASCII art with detected arrows"""
        lines = ascii_art.split('\n')
        arrows = self.detect_arrows(ascii_art)
        annotations = []
        
        if show_replacements and arrows:
            # Apply replacements (highest confidence first)
            for arrow in arrows:
                # Get pattern info
                patterns = self.arrow_patterns[arrow.type]['patterns'][arrow.size]
                
                # Find the pattern that was matched
                pattern_height = 0
                for pattern, _ in patterns:
                    if arrow.row + len(pattern) <= len(lines):
                        pattern_height = len(pattern)
                        pattern_width = len(pattern[0])
                        break
                        
                if pattern_height > 0:
                    # Replace middle of arrow with symbol
                    middle_row = arrow.row + pattern_height // 2
                    if middle_row < len(lines):
                        line = lines[middle_row]
                        # Center the arrow symbol
                        replacement = arrow.symbol.center(pattern_width)
                        if arrow.col + pattern_width <= len(line):
                            lines[middle_row] = (
                                line[:arrow.col] + 
                                replacement + 
                                line[arrow.col + pattern_width:]
                            )
                            
                        # Clear other rows of the pattern
                        for offset in range(pattern_height):
                            if offset != pattern_height // 2:
                                row_idx = arrow.row + offset
                                if row_idx < len(lines) and arrow.col + pattern_width <= len(lines[row_idx]):
                                    line = lines[row_idx]
                                    cleared = ' ' * pattern_width
                                    lines[row_idx] = (
                                        line[:arrow.col] + 
                                        cleared + 
                                        line[arrow.col + pattern_width:]
                                    )
        
        # Create annotations
        for arrow in arrows:
            ann = (f"[{arrow.row+1}:{arrow.col+1}] {arrow.type.title()} Arrow "
                   f"({arrow.size}, confidence: {arrow.confidence:.0%})")
            annotations.append(ann)
            
        return '\n'.join(lines), annotations

def main():
    """Test the advanced arrow detector"""
    import sys
    from ascii_converter_enhanced import convert_to_ascii_enhanced
    
    if len(sys.argv) < 2:
        print("Usage: ascii_arrow_advanced.py <image_path> [width]")
        sys.exit(1)
        
    image_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    
    detector = AdvancedArrowDetector()
    
    # Convert to ASCII
    ascii_art = convert_to_ascii_enhanced(image_path, width)
    
    print("=== Original ASCII ===")
    print(ascii_art)
    
    # Detect arrows
    arrows = detector.detect_arrows(ascii_art)
    
    print(f"\n=== Detected {len(arrows)} Arrows ===")
    for arrow in arrows[:5]:  # Show first 5
        print(f"{arrow.type} arrow at [{arrow.row+1}:{arrow.col+1}], "
              f"size: {arrow.size}, confidence: {arrow.confidence:.0%}")
    
    # Show with replacements
    annotated, annotations = detector.annotate_ascii(ascii_art, show_replacements=True)
    
    print("\n=== With Arrow Symbols ===")
    print(annotated)

if __name__ == "__main__":
    main()