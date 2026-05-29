import asyncio
import json
import re
import sys
from pathlib import Path

# Add parent directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from agents.content_planner import content_planner

load_dotenv()

async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="app", user_id="tester", session_id="test_session")
    runner = Runner(agent=content_planner, app_name="app", session_service=session_service)
    
    async for event in runner.run_async(
        user_id="tester", session_id="test_session",
        new_message=genai_types.Content(
            role="user", parts=[genai_types.Part.from_text(text="Plan a lesson about neural networks")]
        )
    ):
        if event.is_final_response() and event.content:
            response = event.content.parts[0].text
            print("Raw Response:")
            print(response)
            
            # Strip markdown code blocks
            response = re.sub(r"```json\n?", "", response)
            response = re.sub(r"```\n?", "", response)
            response = response.strip()
            
            try:
                plan = json.loads(response)
                print("\n✓ Parsed JSON Plan:")
                print(json.dumps(plan, indent=2))
            except json.JSONDecodeError as e:
                print(f"\n✗ Failed to parse JSON: {e}")

if __name__ == "__main__":
    asyncio.run(main())
