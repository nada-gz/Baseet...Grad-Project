"""Test if Gemini API key works"""
import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("✗ GEMINI_API_KEY not found in .env")
    exit(1)

print(f"✓ API Key loaded: {api_key[:20]}...")

try:
    client = Client(api_key=api_key)
    print("✓ Client created")
    
    # Try a simple request
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents="Say 'Hello' in one word."
    )
    
    print(f"✓ API Response: {response.text}")
    print("\n✅ API Key works!")
    
except Exception as e:
    print(f"✗ API Error: {str(e)}")
    print(f"✗ Error type: {type(e).__name__}")
