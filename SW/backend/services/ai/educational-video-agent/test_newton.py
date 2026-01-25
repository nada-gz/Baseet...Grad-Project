"""Test updated code generator with Newton's Laws."""
import asyncio
from dotenv import load_dotenv
from llm import QwenClient, generate_code
from tools.manim_executor import execute_manim_code
import re

load_dotenv()


async def test_newton_laws():
    print("=" * 70)
    print("Testing Code Generator: Newton's Laws of Motion")
    print("=" * 70)
    
    client = QwenClient()
    
    # Generate code
    print("\n🎬 Generating Manim code...")
    prompt = "Create a visual explanation of Newton's First Law of Motion with the equation and a clear example"
    
    code = await generate_code(client, prompt)
    
    print(f"✓ Generated {len(code)} characters of code\n")
    print("Generated Code:")
    print("-" * 70)
    print(code)
    print("-" * 70)
    
    # Extract scene name
    match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', code)
    scene_name = match.group(1) if match else "Scene"
    
    # Execute
    print(f"\n🎥 Executing scene: {scene_name}")
    result = execute_manim_code(code, scene_name)
    
    if result["status"] == "success":
        print(f"✅ SUCCESS: Video at {result['video_path']}")
        return True
    else:
        print(f"❌ FAILED: {result['error']}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_newton_laws())
    exit(0 if success else 1)
