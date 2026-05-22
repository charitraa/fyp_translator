from urllib import response
import serial
import time
import os
import subprocess
import keyboard  
import requests
from pydub import AudioSegment
from pydub.playback import play

# ========================= CONFIG =========================
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 921600
RECORD_DURATION = 3
ESP_SAMPLE_RATE = 9500
SAMPLE_RATE = 16000
API_URL = "http://127.0.0.1:8000/translate/speech/"
# =========================================================

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
ser.reset_input_buffer()
ser.reset_output_buffer()

# =========================================================
# ASK USER FOR MODEL SELECTION
# =========================================================
def select_model():
    print("\nChoose Speech-to-Text Model:")
    print("1 → English")
    print("2 → Nepali")

    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice in ["1", "2"]:
            print(f"Selected Model → {choice}\n")
            return int(choice)
        print("❌ Invalid input. Please enter 1 or 2.")



# =========================================================
# RECORD AUDIO
# =========================================================
def record_from_esp32(duration=3, filename="recorded.pcm"):
    print(f"\nRecording {duration} seconds... Speak now!")
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

    with open(filename, "wb") as f:
        f.write(data)

    actual_sec = len(data) / (16000 * 2)
    print(f"Recorded {len(data)} bytes ({actual_sec:.2f}s) → {filename}")


# =========================================================
# API CALL + SEND MODEL MODE
# =========================================================
def send_to_api_and_get_mp3(wav_file,model_mode):
    print("Sending to translation API...")

    files = {'audio': ('audio.wav', open(wav_file, 'rb'), 'audio/wav')}
    data = {'mode': model_mode}        # <── send user’s model choice

    response = requests.post(API_URL, files=files, data=data, timeout=60)
    print(response)

    if response.status_code != 200:
        print("API error:", response.text)
        return None

    data = response.json()
    print(data)

    if data.get("error"):
        print("Speak clearly!")
        print("API returned error:", data["error"])
        return None

    mp3_url = "http://127.0.0.1:8000" + data['audio_url']
    print("Recognized :", data['recognized_text'])
    print("Translation:", data['translation'])

    # Download translated MP3
    mp3_path = "translated.mp3"
    with open(mp3_path, "wb") as f:
        f.write(requests.get(mp3_url).content)

    print("Downloaded translated audio → translated.mp3")
    return mp3_path


# =========================================================
# STREAM TO ESP32
# =========================================================
def stream_raw_to_esp32(raw_file="to_speaker_u8.raw"):
    if not os.path.exists(raw_file):
        print("RAW file not found!")
        return

    with open(raw_file, 'rb') as f:
        audio_bytes = f.read()

    print(f"Playing {len(audio_bytes)} samples (~{len(audio_bytes)/ESP_SAMPLE_RATE:.1f}s)...")
    dt = 1.0 / ESP_SAMPLE_RATE
    start = time.time()

    for i, byte in enumerate(audio_bytes):
        ser.write(bytes([byte]))
        next_time = start + (i + 1) * dt
        sleep_time = next_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

    print("Playback finished.\n")


# =========================================================
# MAIN LOOP
# =========================================================
def main_loop():
    print("Nepali ↔ English Real-time Translator with ESP32 + LM386")
    print("Press ENTER to start recording (5 sec), or Ctrl+C to exit\n")

    while True:
        try:
            input("Press ENTER to record... ")
        except KeyboardInterrupt:
            print("\nBye!")
            break
        model_mode = select_model()
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.05)

        # 1. Record
        record_from_esp32(RECORD_DURATION, "recorded.pcm")

        # 2. Convert PCM → WAV
        subprocess.run([
            'ffmpeg', '-y',
            '-f', 's16le', '-ar', '9500', '-ac', '1',
            '-i', 'recorded.pcm',
            '-filter:a', 'volume=10',
            'recorded.wav'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 3. Send to API
        mp3_path = send_to_api_and_get_mp3("recorded.wav",model_mode)
        if not mp3_path:
            continue

        sound = AudioSegment.from_file(mp3_path)
        sound = sound.set_frame_rate(16000).set_channels(1)

        print("🔊 Playing translated audio on laptop...")
        play(sound)


        # # 4. Convert translated MP3 → raw
        # sound = AudioSegment.from_file(mp3_path)
        # sound = sound.set_frame_rate(ESP_SAMPLE_RATE).set_channels(1).set_sample_width(1)
        # sound = sound.apply_gain(+18)
        # sound.export("to_speaker_u8.raw", format="u8")

        # # 5. Stream to speaker
        # stream_raw_to_esp32("to_speaker_u8.raw")

    ser.close()


if __name__ == "__main__":
    main_loop()
