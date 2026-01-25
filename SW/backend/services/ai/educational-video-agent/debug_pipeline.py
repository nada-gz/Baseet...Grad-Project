"""Debug script to test each pipeline step independently."""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from llm import QwenClient, plan_lesson, generate_code, fix_code
from tools.manim_executor import execute_manim_code
from tools.tts_generator import generate_audio
import re

load_dotenv()

def extract_scene_name(code: str) -> str:
    match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', code)
    return match.group(1) if match else "Scene"

async def test_step1_lesson_planning():
    """Test: Can we generate a lesson plan?"""
    print("\n" + "="*60)
    print("STEP 1: Testing Lesson Planning (qwen-flash)")
    print("="*60)
    
    try:
        client = QwenClient()
        segments = await plan_lesson(client, "simple math addition")
        print(f"✓ SUCCESS: Generated {len(segments)} segments")
        print(f"\nFirst segment:")
        print(f"  ID: {segments[0].get('segment_id')}")
        print(f"  Title: {segments[0].get('title')}")
        print(f"  Concept: {segments[0].get('concept')}")
        print(f"  Visual Type: {segments[0].get('visual_type')}")
        print(f"  Script: {segments[0].get('script')[:100]}...")
        return segments[0]  # Return first segment for next tests
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return None

async def test_step2_code_generation(segment):
    """Test: Can we generate Manim code?"""
    print("\n" + "="*60)
    print("STEP 2: Testing Code Generation (qwen3-coder-flash)")
    print("="*60)
    
    if not segment:
        print("⊘ SKIPPED: No segment from step 1")
        return None
    
    try:
        client = QwenClient()
        prompt = f"Generate simple Manim scene showing: {segment.get('concept')}. Keep it very basic."
        code = await generate_code(client, prompt)
        
        print(f"✓ SUCCESS: Generated {len(code)} characters of code")
        print("\nGenerated code:")
        print("-" * 60)
        print(code[:500])
        if len(code) > 500:
            print(f"\n... (truncated, total {len(code)} chars)")
        print("-" * 60)
        return code
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_step3_manim_execution(code):
    """Test: Can we execute the Manim code?"""
    print("\n" + "="*60)
    print("STEP 3: Testing Manim Execution")
    print("="*60)
    
    if not code:
        print("⊘ SKIPPED: No code from step 2")
        return None
    
    try:
        # Clean code
        code = re.sub(r"```python\n?|```\n?", "", code).strip()
        scene_name = extract_scene_name(code)
        print(f"Scene name: {scene_name}")
        
        result = execute_manim_code(code, scene_name)
        
        if result["status"] == "success":
            print(f"✓ SUCCESS: Video created at {result['video_path']}")
            return result["video_path"]
        else:
            print(f"✗ FAILED:")
            print("-" * 60)
            print(result['error'])  # Print full error
            print("-" * 60)
            return None
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        print("-" * 60)
        traceback.print_exc()
        print("-" * 60)
        return None

def test_step4_audio_generation():
    """Test: Can we generate audio?"""
    print("\n" + "="*60)
    print("STEP 4: Testing Audio Generation (ElevenLabs)")
    print("="*60)
    
    try:
        Path("outputs/audio").mkdir(parents=True, exist_ok=True)
        audio_path = "outputs/audio/test_audio.mp3"
        
        result = generate_audio("This is a test of the audio system.", audio_path)
        
        if result["success"]:
            print(f"✓ SUCCESS: Audio created at {result['audio_path']}")
            return result["audio_path"]
        else:
            print(f"✗ FAILED: {result['error']}")
            return None
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("\n🔍 DEBUGGING EDUCATIONAL VIDEO PIPELINE")
    print("Testing each component independently...\n")
    
    # Test each step
    segment = await test_step1_lesson_planning()
    code = await test_step2_code_generation(segment)
    video = test_step3_manim_execution(code)
    audio = test_step4_audio_generation()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Step 1 (Lesson Planning):   {'✓ PASS' if segment else '✗ FAIL'}")
    print(f"Step 2 (Code Generation):    {'✓ PASS' if code else '✗ FAIL'}")
    print(f"Step 3 (Manim Execution):    {'✓ PASS' if video else '✗ FAIL'}")
    print(f"Step 4 (Audio Generation):   {'✓ PASS' if audio else '✗ FAIL'}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
