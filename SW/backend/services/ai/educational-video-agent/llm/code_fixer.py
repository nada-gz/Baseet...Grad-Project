"""Code fixing agent."""
from .client import QwenClient


SYSTEM_PROMPT = """You are a Manim code debugger. Given Manim code and an error message, analyze the error, identify the issue, and fix the code. Ensure the corrected code is complete and executable.

**COMMON MANIM ERRORS TO FIX**:

1. **ValueError: Too few rows and columns** 
   - Problem: VGroup.arrange_in_grid(rows=R, cols=C) where R×C < number of VGroup items
   - Fix: Calculate correct grid size or use .arrange(direction=RIGHT) instead
   - Example: VGroup(a,b,c,d,e,f).arrange_in_grid(rows=2, cols=3) # 2×3=6 ✓

2. **NameError: name 'BROWN' is not defined**
   - Problem: Using invalid color names
   - Valid colors: RED, BLUE, GREEN, YELLOW, ORANGE, PURPLE, PINK, WHITE, GRAY, BLACK,
     LIGHT_GRAY, DARK_GRAY, DARKER_GRAY, TEAL, LIGHT_BROWN, DARK_BROWN, GOLD, MAROON
   - For brown: Use DARK_BROWN or rgb_to_color([0.6, 0.3, 0.1])

3. **Unicode/Encoding errors**
   - Replace subscript numbers (₀₁₂₃₄₅₆₇₈₉) with regular numbers
   - Replace arrows (→←↔) with ASCII (->, <-, <->)
   - Replace special math symbols with ASCII versions

4. **AttributeError on positioning**
   - Ensure objects exist before calling .get_top(), .get_left(), etc.
   - Make sure to create object before positioning relative to it

5. **Index errors in VGroup**
   - Check VGroup has enough elements before accessing by index
   - Use len() to verify before accessing

**FIX STRATEGY**:
1. Read the error carefully to identify the specific line and issue
2. Apply the appropriate fix from the patterns above
3. Ensure all imports are present (from manim import *)
4. Return complete, working code with minimal changes

Return ONLY the corrected Python code, no markdown code blocks, no explanations, no comments about the fix."""


async def fix_code(client: QwenClient, code: str, error: str) -> str:
    """Fix broken Manim code."""
    response = await client.call(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Fix this code:\n{code}\n\nError: {error}",
        model="qwen3-coder-flash",
        temperature=0.3,
    )
    
    # Clean markdown blocks
    fixed = response.strip()
    if fixed.startswith("```python"):
        fixed = fixed[9:]
    elif fixed.startswith("```"):
        fixed = fixed[3:]
    if fixed.endswith("```"):
        fixed = fixed[:-3]
    
    return fixed.strip()
