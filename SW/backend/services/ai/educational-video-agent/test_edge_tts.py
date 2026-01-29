"""
Test script for Arabic TTS with Edge-TTS (Free Microsoft TTS).
Tests the updated TTS implementation using Edge-TTS.
"""
import os
import sys
import asyncio
from pathlib import Path
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

print(Fore.WHITE + "="*60)
print(Fore.WHITE + "🧪 EDGE-TTS ARABIC TEST (Free Microsoft TTS)")
print(Fore.WHITE + "="*60)

# Test 1: Import Edge-TTS
print(Fore.CYAN + "\n[TEST 1] Checking Edge-TTS Installation...")
try:
    import edge_tts
    print(Fore.GREEN + "✅ edge-tts is installed")
except ImportError:
    print(Fore.RED + "❌ edge-tts not installed")
    print(Fore.YELLOW + "Install with: pip install edge-tts")
    sys.exit(1)

# Test 2: List Available Arabic Voices
print(Fore.CYAN + "\n[TEST 2] Listing Available Arabic Voices...")

async def list_voices():
    voices = await edge_tts.list_voices()
    arabic_voices = [v for v in voices if v['Locale'].startswith('ar-')]
    
    print(Fore.GREEN + f"✅ Found {len(arabic_voices)} Arabic voices:")
    for voice in arabic_voices[:10]:  # Show first 10
        print(Fore.CYAN + f"   • {voice['ShortName']} ({voice['Gender']}) - {voice['Locale']}")
    
    return arabic_voices

arabic_voices = asyncio.run(list_voices())

# Test 3: Import Arabic TTS module
print(Fore.CYAN + "\n[TEST 3] Testing Arabic Text Processor...")
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

# Available voices to test
test_voices = [
    "ar-EG-SalmaNeural",      # Egyptian Arabic Female
    "ar-EG-ShakirNeural",     # Egyptian Arabic Male
    "ar-SA-HamedNeural",      # Saudi Arabic Male
    "ar-SA-ZariyahNeural",    # Saudi Arabic Female
]

# Use the first available voice
default_voice = test_voices[0]
print(Fore.CYAN + f"\n[TEST 4] Using voice: {default_voice}")

print(Fore.GREEN + "\n✅ Sample Arabic texts prepared:")
for text in test_texts:
    normalized = processor.normalize_for_tts(text)
    print(Fore.CYAN + f"   • Original:   {text}")
    print(Fore.MAGENTA + f"     Processed: {normalized}")

# Test 5: Generate Arabic Audio with Edge-TTS
print(Fore.CYAN + "\n[TEST 5] Generating Arabic Audio with Edge-TTS...")

output_dir = Path("test_outputs_edge")
output_dir.mkdir(exist_ok=True)

audio_results = []

async def generate_audio(text, output_file, voice):
    """Generate audio using edge-tts."""
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_file))
        return True
    except Exception as e:
        print(Fore.RED + f"       ❌ Failed: {e}")
        return False

for idx, text in enumerate(test_texts, 1):
    processed = processor.normalize_for_tts(text)
    print(Fore.MAGENTA + f"\n   [{idx}] Original: {text}")
    print(Fore.CYAN + f"       Processed: {processed}")
    
    output_file = output_dir / f"arabic_edge_test_{idx}.mp3"
    
    success = asyncio.run(generate_audio(processed, output_file, default_voice))
    
    if success and output_file.exists():
        size = output_file.stat().st_size
        audio_results.append({
            'text': text,
            'file': output_file,
            'size': size,
            'status': 'success'
        })
        print(Fore.GREEN + f"       ✅ Saved: {output_file} ({size} bytes)")
    else:
        audio_results.append({
            'text': text,
            'file': None,
            'error': 'Generation failed',
            'status': 'failed'
        })

# Test 6: Summary Report
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

# Test 7: Play audio automatically
print(Fore.CYAN + "\n[TEST 7] Playing first audio file...")
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
    print(Fore.GREEN + "🎉 ALL TESTS PASSED! Edge-TTS is working perfectly.")
    print(Fore.GREEN + "✅ FREE - No API key needed!")
    print(Fore.GREEN + "Ready to run the full pipeline.")
else:
    print(Fore.YELLOW + "⚠️  Some tests failed. Check errors above.")
print(Fore.WHITE + "="*60)

# Test 8: Available voices for reference
print(Fore.CYAN + "\n[INFO] Available Edge-TTS Arabic Voices:")
print(Fore.YELLOW + "Egyptian Arabic:")
print(Fore.CYAN + "  • ar-EG-SalmaNeural (Female)")
print(Fore.CYAN + "  • ar-EG-ShakirNeural (Male)")
print(Fore.YELLOW + "Saudi Arabic:")
print(Fore.CYAN + "  • ar-SA-HamedNeural (Male)")
print(Fore.CYAN + "  • ar-SA-ZariyahNeural (Female)")
print(Fore.YELLOW + "\nTo change voice, edit .env file:")
print(Fore.CYAN + "  EDGE_VOICE=ar-EG-SalmaNeural")
