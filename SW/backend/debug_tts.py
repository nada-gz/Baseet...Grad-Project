import os
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

print(f"🔹 Loaded Configuration:")
print(f"   API_KEY: {API_KEY[:4]}...{API_KEY[-4:] if API_KEY else 'None'}")
print(f"   VOICE_ID: {VOICE_ID}")

if not API_KEY or not VOICE_ID:
    print("❌ Critical: Missing API Key or Voice ID.")
    exit(1)

print("\n🔹 Testing TTS API...")
url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": API_KEY
}
data = {
    "text": "Hello, this is a test.",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
}

try:
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Success! Received audio ({len(response.content)} bytes).")
        print("   The Voice ID and API Key are working correctly.")
        print("   👉 If the app still fails, restart the server.")
    else:
        print(f"❌ Failed with Status Code: {response.status_code}")
        print(f"   Error Message: {response.text}")
        if response.status_code == 402:
            print("   ⚠️ This confirms the Voice ID requires payment or the Free Tier limit is reached.")

except Exception as e:
    print(f"❌ Exception: {e}")
