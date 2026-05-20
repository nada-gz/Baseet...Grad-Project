"""
Simple code validator to catch common Manim errors before rendering.
"""
import re
from typing import Dict, List


VALID_MANIM_COLORS = {
    'RED', 'BLUE', 'GREEN', 'YELLOW', 'ORANGE', 'PURPLE', 'PINK', 
    'WHITE', 'GRAY', 'GREY', 'BLACK', 'LIGHT_GRAY', 'LIGHT_GREY',
    'DARK_GRAY', 'DARK_GREY', 'DARKER_GRAY', 'DARKER_GREY',
    'LIGHT_BROWN', 'DARK_BROWN', 'GOLD', 'MAROON', 'TEAL'
}


def validate_manim_code(code: str) -> Dict[str, any]:
    """
    Validates Manim code for common errors.
    
    Returns:
        dict with:
            - valid: bool
            - warnings: list of warning messages
            - errors: list of error messages
    """
    warnings = []
    errors = []
    
    # 1. Check for invalid colors
    color_pattern = r'color\s*=\s*([A-Z_]+)'
    for match in re.finditer(color_pattern, code):
        color = match.group(1)
        if color not in VALID_MANIM_COLORS and not color.startswith('rgb_to_color'):
            errors.append(f"Invalid color '{color}' - use {', '.join(sorted(VALID_MANIM_COLORS)[:5])}... or rgb_to_color()")
    
    # 2. Check for VGroup grid sizing issues
    # Pattern: VGroup(...).arrange_in_grid(rows=X, cols=Y)
    vgroup_pattern = r'VGroup\((.*?)\)\.arrange_in_grid\(.*?rows\s*=\s*(\d+).*?cols\s*=\s*(\d+)'
    for match in re.finditer(vgroup_pattern, code, re.DOTALL):
        items_str = match.group(1)
        rows = int(match.group(2))
        cols = int(match.group(3))
        
        # Count items (rough estimate by counting commas)
        item_count = items_str.count(',') + 1 if items_str.strip() else 0
        grid_size = rows * cols
        
        if item_count > grid_size:
            warnings.append(
                f"VGroup grid sizing issue: {item_count} items in grid of {rows}×{cols}={grid_size}. "
                f"Consider rows={rows}, cols={item_count // rows + (1 if item_count % rows else 0)}"
            )
    
    # 3. Check for unicode characters (common encoding issues)
    unicode_patterns = [
        (r'[₀₁₂₃₄₅₆₇₈₉]', 'subscript numbers'),
        (r'[⁰¹²³⁴⁵⁶⁷⁸⁹]', 'superscript numbers'),
        (r'[→←↔]', 'arrow symbols'),
        (r'[≈≠≥≤±×÷°]', 'math symbols'),
    ]
    
    for pattern, name in unicode_patterns:
        if re.search(pattern, code):
            warnings.append(f"Unicode {name} detected - may cause encoding issues on Windows")
    
    # 4. Check for missing import
    if 'from manim import' not in code and 'import manim' not in code:
        errors.append("Missing 'from manim import *' statement")
    
    # 5. Check for Scene class
    if not re.search(r'class\s+\w+\s*\(\s*Scene\s*\)', code):
        errors.append("No Scene class found - must inherit from Scene")
    
    return {
        'valid': len(errors) == 0,
        'warnings': warnings,
        'errors': errors
    }


def get_validation_summary(validation: Dict) -> str:
    """Get a human-readable summary of validation results."""
    if validation['valid']:
        if validation['warnings']:
            return f"⚠️  {len(validation['warnings'])} warnings: " + "; ".join(validation['warnings'][:2])
        return "✅ Code validation passed"
    else:
        return f"❌ {len(validation['errors'])} errors: " + "; ".join(validation['errors'][:2])


if __name__ == "__main__":
    # Test with problematic code
    test_code = """
from manim import *

class Test(Scene):
    def construct(self):
        items = VGroup(a, b, c, d, e, f)
        items.arrange_in_grid(rows=1, cols=3)
        
        line = Line(color=BROWN)
        self.play(Create(line))
"""
    
    result = validate_manim_code(test_code)
    print(f"Valid: {result['valid']}")
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")
    print(f"\nSummary: {get_validation_summary(result)}")
