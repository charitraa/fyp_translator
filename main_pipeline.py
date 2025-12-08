# main_pipeline.py
from urllib import response
import serial
import time
import os
import subprocess
import keyboard  # pip install keyboard  (needs sudo on Linux)
import requests
from pydub import AudioSegment

# ========================= CONFIG =========================
SERIAL_PORT = '/dev/ttyUSB0'      # Change if needed
BAUD_RATE = 921600
RECORD_DURATION = 5               # seconds
ESP_SAMPLE_RATE = 9500 
SAMPLE_RATE = 16000           # Your DAC code uses ~9.5 kHz
API_URL = "http://127.0.0.1:8000/translate/speech/"   # Your Django endpoint
# =========================================================

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
ser.reset_input_buffer()
ser.reset_output_buffer()

def record_from_esp32(duration=5, filename="recorded.pcm"):
    print(f"\nRecording {duration} seconds (16 kHz)... Speak now!")
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    time.sleep(0.05)
    total_bytes = SAMPLE_RATE * duration * 2
    data = b""

    while len(data) < total_bytes:
        chunk = ser.read(total_bytes - len(data))
        if not chunk:
            break
        data += chunk

    # Save whatever we got
    with open(filename, "wb") as f:
        f.write(data)

    actual_sec = len(data) / (16000 * 2)
    print(f"Recorded {len(data)} bytes ({actual_sec:.2f}s) → {filename}")

def convert_for_dac(input_wav="recorded.wav", output_raw="to_speaker_u8.raw"):
    # 16kHz 16-bit → 9.5kHz 8-bit unsigned (exactly what your Arduino code expects)
    cmd = [
        'ffmpeg', '-y',
        '-f', 's16le', '-ar', '16000', '-ac', '1',
        '-i', input_wav,
        '-ar', str(ESP_SAMPLE_RATE), '-ac', '1', '-f', 'u8',
        '-filter:a', 'volume=15',   # LM386 needs big boost
        output_raw
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Converted for ESP32 DAC → {output_raw}")

def send_to_api_and_get_mp3(wav_file):
    print("Sending to translation API...")
    files = {'audio': ('audio.wav', open(wav_file, 'rb'), 'audio/wav')}
    response = requests.post(API_URL, files=files, timeout=60)
    print(response)
    if response.status_code != 200:
        print("API error:", response.text)
        return None

    data = response.json()
    print(data)
    if data.get("error"):
        print('speak clearly!')
        print("API returned error:", data["error"])
        return None
    mp3_url = "http://127.0.0.1:8000" + data['audio_url']   # adjust if domain different
    print("Recognized :", data['recognized_text'])
    print("Translation:", data['translation'])

    # Download the returned MP3
    mp3_path = "translated.mp3"
    with open(mp3_path, "wb") as f:
        f.write(requests.get(mp3_url).content)
    print("Downloaded translated audio → translated.mp3")
    return mp3_path

def stream_raw_to_esp32(raw_file="to_speaker_u8.raw"):
    if not os.path.exists(raw_file):
        print("RAW file not found!")
        return

    with open(raw_file, 'rb') as f:
        audio_bytes = f.read()

    print(f"Playing {len(audio_bytes)} samples on speaker (~{len(audio_bytes)/ESP_SAMPLE_RATE:.1f}s)...")
    dt = 1.0 / ESP_SAMPLE_RATE
    start = time.time()

    for i, byte in enumerate(audio_bytes):
        ser.write(bytes([byte]))
        # Precise timing
        next_time = start + (i + 1) * dt
        sleep_time = next_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

    print("Playback finished.\n")

def main_loop():
    print("Nepali ↔ English Real-time Translator with ESP32 + LM386")
    print("Press ENTER to start recording (5 sec), or Ctrl+C to exit\n")

    while True:
        try:
            input("Press ENTER to record... ")
        except KeyboardInterrupt:
            print("\nBye!")
            break
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.05)
        # 1. Record from ESP32
        record_from_esp32(RECORD_DURATION, "recorded.pcm")

        # 2. Convert 16kHz 16-bit → 16kHz WAV (for API)
        subprocess.run([
            'ffmpeg', '-y',
            '-f', 's16le', '-ar', '9500', '-ac', '1',
            '-i', 'recorded.pcm', '-filter:a', 'volume=10', 'recorded.wav'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        

        # 3. Send to your Django API → get translated MP3
        mp3_path = send_to_api_and_get_mp3("recorded.wav")
        print(mp3_path)
        if not mp3_path:
            continue

        # 4. Convert translated MP3 → 9.5kHz 8-bit raw (for your DAC code)
        # pydub way (cleaner)
        sound = AudioSegment.from_file(mp3_path)
        sound = sound.set_frame_rate(ESP_SAMPLE_RATE).set_channels(1).set_sample_width(1)  # 8-bit
        sound = sound.apply_gain(+18)  # LM386 is weak
        sound.export("to_speaker_u8.raw", format="u8")

        # Alternative pure ffmpeg (same result)
        # convert_for_dac(mp3_path, "to_speaker_u8.raw")

        # 5. Stream to speaker
        stream_raw_to_esp32("to_speaker_u8.raw")

    ser.close()

if __name__ == "__main__":
    main_loop()