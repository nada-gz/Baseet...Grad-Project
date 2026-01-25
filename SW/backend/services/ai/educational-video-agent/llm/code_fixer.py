"""Code fixing agent."""
from .client import QwenClient


SYSTEM_PROMPT = """You are a Manim code debugger. Given Manim code and an error message, analyze the error, identify the issue, and fix the code. Ensure the corrected code is complete and executable.

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
