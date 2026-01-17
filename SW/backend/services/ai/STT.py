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
        print(Fore.CYAN + "\n🎤 Press [Enter] to start recording...")
        input()
        print(Fore.RED + "🔴 Listening... (Press [Enter] to stop)")
        
        recording = []
        def callback(indata, frames, time, status):
            recording.append(indata.copy())
            
        with sd.InputStream(samplerate=16000, channels=1, callback=callback):
            input() 
            
        if not recording: return ""
        
        full_rec = np.concatenate(recording, axis=0)
        write(filename, 16000, full_rec)
        
        try:
            speech, _ = librosa.load(filename, sr=16000)
            inputs = self.processor(speech, sampling_rate=16000, return_tensors="pt", padding=True)
            with torch.no_grad():
                logits = self.model(inputs.input_values.to(self.device)).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]
            return transcription
        except Exception as e:
            print(Fore.RED + f"❌ Transcription Error: {e}")
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
            "status": "new"  # Flag to tell the other script there is new data
        }
        try:
            with open(SHARED_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(Fore.GREEN + f"💾 Saved to JSON: {text}")
        except Exception as e:
            print(Fore.RED + f"❌ Error writing JSON: {e}")

def main():
    print(Fore.WHITE + "="*50)
    print(Fore.WHITE + "🚀 MODULE 1: STT LISTENER & WRITER")
    print(Fore.WHITE + "="*50)
    
    ear = EgyptianEar()
    
    while True:
        try:
            # 1. Listen
            text = ear.listen()
            
            if text.strip():
                print(Fore.WHITE + f"📝 Recognized: {text}")
                # 2. Save to JSON
                JsonWriter.save_transcription(text)
            else:
                print(Fore.YELLOW + "⚠️ No speech detected.")
                
        except KeyboardInterrupt:
            print("\n👋 Exiting Listener.")
            break

if __name__ == "__main__":
    main()