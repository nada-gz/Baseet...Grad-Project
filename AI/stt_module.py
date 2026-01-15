import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import librosa
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import time

class EgyptianSTT:
    def __init__(self):
        self.model_name = "IbrahimAmin/egyptian-arabic-wav2vec2-xlsr-53"
        print(f"⏳ Loading model: {self.model_name}...")
        self.processor = Wav2Vec2Processor.from_pretrained(self.model_name)
        self.model = Wav2Vec2ForCTC.from_pretrained(self.model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"✅ Model loaded successfully on: {self.device}")

    def transcribe(self, audio_path):
        start_time = time.time()
        # Load and resample audio
        speech, _ = librosa.load(audio_path, sr=16000)
        inputs = self.processor(speech, sampling_rate=16000, return_tensors="pt", padding=True)
        
        with torch.no_grad():
            logits = self.model(inputs.input_values.to(self.device)).logits
        
        predicted_ids = torch.argmax(logits, dim=-1)
        result = self.processor.batch_decode(predicted_ids)[0]
        
        end_time = time.time()
        print(f"⏱️ Processing Time: {end_time - start_time:.2f} seconds")
        return result

# Initialize the engine once
stt_engine = EgyptianSTT()

def fast_test():
    fs = 44100
    temp_file = "fast_test.wav"
    
    input("\n🎤 Press [Enter] to start recording...")
    print("🔴 Recording... speak now.")
    
    recording = []
    # Recording stream
    with sd.InputStream(samplerate=fs, channels=1, callback=lambda i,f,t,s: recording.append(i.copy())):
        input("⏹️ Press [Enter] to stop recording...")
    
    if recording:
        full_rec = np.concatenate(recording, axis=0)
        write(temp_file, fs, full_rec)
        
        print("⏳ Transcribing audio...")
        transcription = stt_engine.transcribe(temp_file)
        
        # Output result in Arabic as requested
        print(f"📝 Transcription (Arabic): {transcription}")
        
        if not transcription.strip():
            print("⚠️ Warning: No speech detected.")
        else:
            print("✅ Process completed.")

if __name__ == "__main__":
    print("--- Egyptian STT Module Test ---")
    try:
        while True:
            fast_test()
            print("-" * 40)
    except KeyboardInterrupt:
        print("\n👋 Testing stopped by user.")