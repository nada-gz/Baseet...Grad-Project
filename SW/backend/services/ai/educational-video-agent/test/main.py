import asyncio
import re
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from agents.manim_generator import manim_coder
from agents.code_fixer import code_fixer
from tools.manim_executor import execute_manim_code

load_dotenv()

def extract_scene_name(code: str) -> str:
    """Extract scene class name from Manim code."""
    match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', code)
    return match.group(1) if match else "HelloWorld"

async def fix_code(code: str, error: str) -> str:
    """Use code_fixer agent to fix broken code."""
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="app", user_id="fixer", session_id="fixer_session")
    runner = Runner(agent=code_fixer, app_name="app", session_service=session_service)
    
    fixed_code = None
    async for event in runner.run_async(
        user_id="fixer", session_id="fixer_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=f"Fix this code:\n{code}\n\nError: {error[:200]}")]
        )
    ):
        if event.is_final_response() and event.content:
            fixed_code = event.content.parts[0].text
    return fixed_code

async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="app", user_id="user1", session_id="session1")
    runner = Runner(agent=manim_coder, app_name="app", session_service=session_service)
    
    response_code = None
    async for event in runner.run_async(
        user_id="user1", session_id="session1",
        new_message=genai_types.Content(
            role="user", parts=[genai_types.Part.from_text(text="Generate a Manim scene with an equation x^2 + y^2 = r^2 animated")]
        )
    ):
        if event.is_final_response() and event.content:
            response_code = event.content.parts[0].text
            print("Generated Code:\n", response_code)
    
    if response_code:
        code = response_code
        scene_name = extract_scene_name(code)
        
        for attempt in range(3):
            print(f"\nAttempt {attempt + 1}/3...")
            result = execute_manim_code(code, scene_name)
            
            if result["status"] == "success":
                print(f"✓ Success! Video: {result['video_path']}")
                return
            
            if attempt < 2:
                print(f"Error: {result['error'][:80]}... Fixing...")
                fixed = await fix_code(code, result['error'])
                if fixed:
                    code = fixed
                    scene_name = extract_scene_name(code)
        
        print(f"✗ Failed after retries")

if __name__ == "__main__":
    asyncio.run(main())
