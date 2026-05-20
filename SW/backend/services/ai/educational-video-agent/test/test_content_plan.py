"""Test content planner without async complexity"""
import os
import json
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = Client(api_key=api_key)

print("Testing content planner generation...\n")

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents="""You are an educational content planner. Given a topic, create a structured learning plan with 3-4 segments. For each segment output:
- segment_id: number (1, 2, 3, 4)
- title: short title
- concept: what to explain
- visual_type: one of (text, equation, diagram)
- script: 2-3 sentence narration

Output as valid JSON array. Example:
[
  {
    "segment_id": 1,
    "title": "Introduction",
    "concept": "What is a derivative",
    "visual_type": "text",
    "script": "A derivative measures how a function changes."
  }
]

Plan a lesson about: Python basics

Return ONLY valid JSON array, no markdown code blocks, no explanations."""
    )
    
    print("✓ Response received:")
    print(response.text[:500])
    
    # Try to parse as JSON
    try:
        data = json.loads(response.text)
        print(f"\n✓ Valid JSON with {len(data)} segments")
        for seg in data:
            print(f"  [{seg.get('segment_id')}] {seg.get('title')}")
    except json.JSONDecodeError as e:
        print(f"\n✗ JSON parse error: {e}")
        print(f"Response text: {response.text}")
        
except Exception as e:
    print(f"✗ Error: {e}")
