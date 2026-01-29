import os
import re
import subprocess
import tempfile
import glob
from pathlib import Path


def sanitize_code_for_manim(code: str) -> str:
    """
    Sanitize code to fix encoding issues on Windows.
    Replace problematic Unicode characters with ASCII equivalents.
    
    Args:
        code: Python code containing Manim Scene definition
        
    Returns:
        Sanitized code
    """
    # Replace subscript numbers with regular numbers in chemical formulas
    # CO₂ -> CO2, H₂O -> H2O, O₂ -> O2, etc.
    replacements = {
        '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
        '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
        # Superscripts
        '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
        '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
        # Other problematic Unicode
        '→': '->',
        '←': '<-',
        '↔': '<->',
        '≈': '~=',
        '≠': '!=',
        '≥': '>=',
        '≤': '<=',
        '±': '+/-',
        '×': '*',
        '÷': '/',
        '°': 'deg',
        'α': 'alpha',
        'β': 'beta',
        'γ': 'gamma',
        'δ': 'delta',
        'θ': 'theta',
        'π': 'pi',
        'Σ': 'Sum',
        'λ': 'lambda',
    }
    
    for old, new in replacements.items():
        code = code.replace(old, new)
    
    return code


def execute_manim_code(code: str, scene_name: str, output_dir: str = None) -> str:
    """
    Saves code to temp file, runs manim command, returns path to generated video.
    
    Args:
        code: Python code containing Manim Scene definition
        scene_name: Name of the Scene class to render
        output_dir: Output directory for the video file (absolute path recommended)
        
    Returns:
        Path to generated video file or error message
    """
    try:
        # to fix formatting issues from code generation
        # Strip markdown code blocks if present
        code = re.sub(r"```python\n", "", code)
        code = re.sub(r"```\n?", "", code)
        code = code.strip()
        
        # Sanitize code to fix encoding issues
        code = sanitize_code_for_manim(code)
        
        # Use temp directory if no output specified
        if output_dir is None:
            output_dir = "outputs/videos"
        
        # Ensure output directory is absolute
        output_dir = str(Path(output_dir).absolute())
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create temp file with the code using UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(code)
            temp_file_path = tmp_file.name
        
        # Set environment variable to skip SoX check and use UTF-8
        env = os.environ.copy()
        env["MANIM_SKIP_AUDIO_DEPS"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONLEGACYWINDOWSSTDIO"] = "0"  # Use UTF-8 for Windows pipes
        env["LANG"] = "C.UTF-8"  # Force UTF-8 locale
        env["LC_ALL"] = "C.UTF-8"
        
        # Run manim command
        cmd = [
            "manim",
            "-ql",
            "--media_dir",
            output_dir,
            "--disable_caching",
            temp_file_path,
            scene_name
        ]
        
        # Run with explicit UTF-8 encoding, ignoring problematic characters
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            return {"status": "error", "video_path": None, "error": error_msg or "Unknown error occurred"}
        
        # Search for the video file in manim's output structure
        # Manim creates: output_dir/videos/partial_movie_files/480p15/SceneName.mp4
        video_pattern = os.path.join(output_dir, "**", f"{scene_name}.mp4")
        found_files = glob.glob(video_pattern, recursive=True)
        
        if found_files:
            return {"status": "success", "video_path": found_files[0], "error": None}
        else:
            return {"status": "error", "video_path": None, "error": f"Video file not found in {output_dir}"}
    
    except Exception as e:
        return {"status": "error", "video_path": None, "error": str(e)}
