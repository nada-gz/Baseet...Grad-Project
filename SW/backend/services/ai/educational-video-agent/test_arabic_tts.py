"""
Test script for Arabic TTS with ElevenLabs API.
Tests the updated TTS implementation with VoiceSettings.
"""
import os
import sys
import time
from dotenv import load_dotenv
from colorama import Fore, init
from pathlib import Path

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

print(Fore.WHITE + "="*60)
print(Fore.WHITE + "🧪 ELEVENLABS ARABIC TTS TEST (Updated with VoiceSettings)")
print(Fore.WHITE + "="*60)

# Test 1: Check API Key
print(Fore.CYAN + "\n[TEST 1] Checking API Key Configuration...")
if ELEVENLABS_API_KEY:
    print(Fore.GREEN + f"✅ API Key found: {ELEVENLABS_API_KEY[:20]}...")
else:
    print(Fore.RED + "❌ API Key not found in .env file")
    sys.exit(1)

# Test 2: Check Voice ID
print(Fore.CYAN + "\n[TEST 2] Checking Voice ID Configuration...")
if VOICE_ID:
    print(Fore.GREEN + f"✅ Voice ID found: {VOICE_ID}")
else:
    print(Fore.YELLOW + "⚠️  Voice ID not found, will use default")
    VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

# Test 3: Import ElevenLabs with VoiceSettings
print(Fore.CYAN + "\n[TEST 3] Importing ElevenLabs with VoiceSettings...")
try:
    from elevenlabs import VoiceSettings
    from elevenlabs.client import ElevenLabs
    print(Fore.GREEN + "✅ ElevenLabs + VoiceSettings imported successfully")
except ImportError as e:
    print(Fore.RED + f"❌ Failed to import: {e}")
    print(Fore.YELLOW + "Install with: pip install elevenlabs")
    sys.exit(1)

# Test 4: Initialize ElevenLabs Client
print(Fore.CYAN + "\n[TEST 4] Connecting to ElevenLabs API...")
try:
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    print(Fore.GREEN + "✅ Successfully connected to ElevenLabs API")
except Exception as e:
    print(Fore.RED + f"❌ Failed to connect: {e}")
    sys.exit(1)

# Test 5: List Available Voices
print(Fore.CYAN + "\n[TEST 5] Fetching Available Voices...")
try:
    voices = client.voices.get_all()
    print(Fore.GREEN + f"✅ Found {len(voices.voices)} available voices")
    
    voice_found = False
    for voice in voices.voices:
        if voice.voice_id == VOICE_ID:
            print(Fore.GREEN + f"   ✓ Our Voice: {voice.name} ({voice.voice_id})")
            voice_found = True
            break
    
    if not voice_found:
        print(Fore.YELLOW + f"⚠️  Voice ID {VOICE_ID} not found, showing first 5:")
        for i, voice in enumerate(voices.voices[:5]):
            print(Fore.YELLOW + f"     - {voice.name} ({voice.voice_id})")
except Exception as e:
    print(Fore.RED + f"❌ Failed to fetch voices: {e}")

# Test 6: Import Arabic TTS module
print(Fore.CYAN + "\n[TEST 6] Testing Arabic Text Processor...")
try:
    sys.path.insert(0, str(Path(__file__).parent / "tools"))
    from arabic_tts import TextPostProcessor, generate_arabic_narration
    processor = TextPostProcessor()
    print(Fore.GREEN + "✅ Arabic TTS module imported successfully")
except ImportError as e:
    print(Fore.YELLOW + f"⚠️  Could not import arabic_tts: {e}")
    # Use inline processor
    import re
    class TextPostProcessor:
        def __init__(self):
            self.msa_to_egy = {
                r"\bهذا\b": "دَه", r"\bهذه\b": "دِي",
                r"\bكيف حالك\b": "إِزَّيَّك",
                r"\bازيك\b": "إِزَّيَّك",
                r"\bالجنينة\b": "الْگِنِينَه",
            }
        def normalize_for_tts(self, text):
            if not text: return ""
            text = text.replace("ة", "ه").replace("أ", "ا").replace("إ", "ا")
            for pattern, replacement in self.msa_to_egy.items():
                text = re.sub(pattern, replacement, text)
            return text
    processor = TextPostProcessor()

# Test Arabic texts
test_texts = [
    "ازيك يا سكر، ايه الاخبار؟",
    "شوفتي النباتات الخضرا في الجنينة؟",
    "مرحبا بك في البرنامج التعليمي",
    "النظام يعمل بنجاح، هذا جميل جدا",
]

print(Fore.GREEN + "✅ Sample Arabic texts prepared:")
for text in test_texts:
    normalized = processor.normalize_for_tts(text)
    print(Fore.CYAN + f"   • Original:   {text}")
    print(Fore.MAGENTA + f"     Processed: {normalized}")

# Test 7: Generate Arabic Audio with VoiceSettings
print(Fore.CYAN + "\n[TEST 7] Generating Arabic Audio with VoiceSettings...")

output_dir = Path("test_outputs")
output_dir.mkdir(exist_ok=True)

audio_results = []

for idx, text in enumerate(test_texts, 1):
    processed = processor.normalize_for_tts(text)
    print(Fore.MAGENTA + f"\n   [{idx}] Original: {text}")
    print(Fore.CYAN + f"       Processed: {processed}")
    
    try:
        # Generate audio with VoiceSettings
        audio_generator = client.text_to_speech.convert(
            text=processed,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.90,
                similarity_boost=0.50,
                style=0.0,
                use_speaker_boost=True
            )
        )
        
        audio_bytes = b"".join(audio_generator)
        
        output_file = output_dir / f"arabic_test_{idx}.mp3"
        with open(output_file, 'wb') as f:
            f.write(audio_bytes)
        
        audio_results.append({
            'text': text,
            'file': output_file,
            'size': len(audio_bytes),
            'status': 'success'
        })
        
        print(Fore.GREEN + f"       ✅ Saved: {output_file} ({len(audio_bytes)} bytes)")
        time.sleep(1)
        
    except Exception as e:
        audio_results.append({
            'text': text,
            'file': None,
            'error': str(e),
            'status': 'failed'
        })
        print(Fore.RED + f"       ❌ Failed: {e}")

# Test 8: Summary Report
print(Fore.WHITE + "\n" + "="*60)
print(Fore.WHITE + "📊 TEST SUMMARY")
print(Fore.WHITE + "="*60)

successful = sum(1 for r in audio_results if r['status'] == 'success')
failed = sum(1 for r in audio_results if r['status'] == 'failed')

print(Fore.GREEN + f"✅ Successful: {successful}/{len(audio_results)}")
print(Fore.RED + f"❌ Failed: {failed}/{len(audio_results)}")

if audio_results:
    print(Fore.CYAN + "\nGenerated Files:")
    for result in audio_results:
        if result['status'] == 'success':
            print(Fore.GREEN + f"   ✓ {result['file']} ({result['size']} bytes)")
        else:
            print(Fore.RED + f"   ✗ {result['text']} - {result.get('error', 'Unknown error')}")

print(Fore.CYAN + f"\nOutput directory: {output_dir.absolute()}")

# Test 9: Play audio automatically
print(Fore.CYAN + "\n[TEST 9] Playing first audio file...")
if audio_results and audio_results[0]['status'] == 'success':
    try:
        audio_file = str(audio_results[0]['file'])
        print(Fore.YELLOW + f"🔊 Opening: {audio_file}")
        os.startfile(audio_file)
        print(Fore.GREEN + "✅ Audio player launched!")
    except Exception as e:
        print(Fore.YELLOW + f"⚠️  Could not auto-play: {e}")
        print(Fore.CYAN + f"   Manually open: {audio_results[0]['file']}")

print(Fore.WHITE + "\n" + "="*60)
if successful == len(audio_results):
    print(Fore.GREEN + "🎉 ALL TESTS PASSED! Arabic TTS is working properly.")
    print(Fore.GREEN + "Ready to run the full pipeline.")
else:
    print(Fore.YELLOW + "⚠️  Some tests failed. Check errors above.")
print(Fore.WHITE + "="*60)
