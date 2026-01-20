import os
import json
import time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import torch
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from colorama import Fore, init

init(autoreset=True)

# --- CONFIGURATION ---
STT_MODEL_ID = "IbrahimAmin/egyptian-arabic-wav2vec2-xlsr-53"
SHARED_FILE = "shared_data.json"
RECORD_SECONDS = 5  # Duration to listen automatically
SAMPLE_RATE = 16000

class EgyptianEar:
    """
    Class responsible for capturing audio and converting it to text (STT).
    """
    def __init__(self):
        print(Fore.YELLOW + "👂 Loading STT Model (Wav2Vec2)...")
        try:
            self.processor = Wav2Vec2Processor.from_pretrained(STT_MODEL_ID)
            self.model = Wav2Vec2ForCTC.from_pretrained(STT_MODEL_ID)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            print(Fore.GREEN + f"✅ STT Ready on: {self.device}")
        except Exception as e:
            print(Fore.RED + f"❌ Error loading STT: {e}")

    def listen(self, filename="temp_in.wav"):
        """
        Records audio automatically for RECORD_SECONDS without user interaction.
        """
        print(Fore.CYAN + f"\n🎤 Auto-Listening for {RECORD_SECONDS} seconds...")
        
        try:
            # Record audio automatically (Non-blocking start, but we wait for it to finish)
            # This replaces the manual 'input()' calls
            recording = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
            
            # Show a simple countdown or wait
            for i in range(RECORD_SECONDS, 0, -1):
                print(Fore.RED + f"🔴 Recording... {i}")
                time.sleep(1)
            
            sd.wait()  # Ensure recording is complete
            print(Fore.GREEN + "⏹️ Recording finished. Processing...")

            # Save file
            write(filename, SAMPLE_RATE, recording)
            
            # Check if there is actual audio (simple volume check)
            volume_norm = np.linalg.norm(recording) * 10
            if volume_norm < 1:
                print(Fore.YELLOW + "⚠️ Audio too quiet, might be silence.")
                return ""

            # Transcribe
            speech, _ = librosa.load(filename, sr=SAMPLE_RATE)
            inputs = self.processor(speech, sampling_rate=SAMPLE_RATE, return_tensors="pt", padding=True)
            
            with torch.no_grad():
                logits = self.model(inputs.input_values.to(self.device)).logits
            
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]
            
            return transcription

        except Exception as e:
            print(Fore.RED + f"❌ Recorder/Transcription Error: {e}")
            return ""

class JsonWriter:
    """
    Helper class to write data to a JSON file securely.
    """
    @staticmethod
    def save_transcription(text):
        data = {
            "raw_text": text,
            "timestamp": time.time(),
            "status": "new"
        }
        try:
            with open(SHARED_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(Fore.GREEN + f"💾 Saved to JSON: {text}")
        except Exception as e:
            print(Fore.RED + f"❌ Error writing JSON: {e}")

def main():
    # Only for testing this module standalone
    print(Fore.WHITE + "="*50)
    print(Fore.WHITE + "🚀 MODULE 1: STT LISTENER (AUTO MODE)")
    print(Fore.WHITE + "="*50)
    
    ear = EgyptianEar()
    
    while True:
        try:
            text = ear.listen()
            if text.strip():
                print(Fore.WHITE + f"📝 Recognized: {text}")
                JsonWriter.save_transcription(text)
            else:
                print(Fore.YELLOW + "⚠️ No speech recognized.")
                
            print(Fore.BLUE + "Waiting 2 seconds before next cycle...\n")
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n👋 Exiting Listener.")
            break

if __name__ == "__main__":
    main()