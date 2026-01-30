"""Test ElevenLabs TTS generation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.tts_generator import generate_audio

# Create output directory if it doesn't exist
output_dir = Path(__file__).parent.parent / "outputs" / "audio"
output_dir.mkdir(parents=True, exist_ok=True)

# Test text
test_text = "Hello, this is a test of ElevenLabs text to speech."
output_path = str(output_dir / "test.mp3")

# Generate audio
result = generate_audio(test_text, output_path)

# Print result
print(f"Success: {result['success']}")
print(f"Audio Path: {result['audio_path']}")
print(f"Error: {result['error']}")

if result['success']:
    print(f"✓ Audio generated successfully at {output_path}")
