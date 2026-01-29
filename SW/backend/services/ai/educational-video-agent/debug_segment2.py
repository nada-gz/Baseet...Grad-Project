"""
Debug script to isolate and diagnose Segment 2 rendering failure.
This will help us see the FULL error message from Manim.
"""
import asyncio
import json
from pathlib import Path
from llm import QwenClient, generate_code
from tools.manim_executor import execute_manim_code

async def debug_segment2():
    print("=" * 70)
    print("🔍 DEBUGGING SEGMENT 2: Sunlight - The Power Source")
    print("=" * 70)
    
    # Recreate the prompt that would have been used for Segment 2
    segment = {
        "segment_id": 2,
        "title": "Sunlight: The Power Source",
        "concept": "Sunlight provides energy for photosynthesis",
        "visual_type": "text",  # Segment 2 didn't search for an image
        "script": "The sun is like a giant battery in the sky! Its light travels to Earth and gives plants the energy they need to make food. Without sunlight, photosynthesis cannot happen."
    }
    
    prompt = f"""Generate a Manim scene for: {segment['title']}
Concept: {segment['concept']}
Visual type: {segment['visual_type']}

The narration says: "{segment['script']}"

Requirements:
- Create clear, educational animations
- Use self.wait(2-3) between major elements
- Match visuals to what the narration describes
- Keep text in English, clean and readable
- Use colors to highlight important elements"""
    
    print("\n📝 Generating Manim code...")
    qwen_client = QwenClient()
    
    try:
        code = await generate_code(qwen_client, prompt)
        print("\n✅ Code generated successfully")
        print("\n" + "=" * 70)
        print("GENERATED CODE:")
        print("=" * 70)
        print(code)
        print("=" * 70)
        
        # Save the code for inspection
        code_file = Path("debug_segment2_code.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"\n💾 Code saved to: {code_file}")
        
        # Extract scene name
        import re
        match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', code)
        scene_name = match.group(1) if match else "Scene"
        print(f"\n🎬 Scene class: {scene_name}")
        
        # Try to render it
        print("\n🎥 Attempting to render...")
        output_dir = str(Path("debug_outputs").absolute())
        Path(output_dir).mkdir(exist_ok=True)
        
        result = execute_manim_code(code, scene_name, output_dir)
        
        print("\n" + "=" * 70)
        print("MANIM EXECUTION RESULT:")
        print("=" * 70)
        print(f"Status: {result['status']}")
        
        if result['status'] == 'success':
            print(f"✅ Video: {result['video_path']}")
        else:
            print(f"\n❌ FULL ERROR MESSAGE:")
            print("-" * 70)
            print(result.get('error', 'No error message'))
            print("-" * 70)
            
            # Save error for analysis
            with open("debug_segment2_error.txt", "w", encoding="utf-8") as f:
                f.write(result.get('error', 'No error message'))
            print(f"\n💾 Error saved to: debug_segment2_error.txt")
        
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_segment2())
