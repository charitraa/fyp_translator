import serial
import time
import sys
import os

SERIAL_PORT = '/dev/ttyUSB0'  # Adjust for your system
BAUD_RATE = 921600
FILENAME = 'to_speaker_u8.raw'    # 8-bit unsigned PCM
SAMPLE_RATE = 9500             # Hz

# Open serial
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=None)
time.sleep(1)  # let ESP32 reset
ser.reset_output_buffer()
print(f"Connected to {SERIAL_PORT}")

# Read raw bytes
if not os.path.exists(FILENAME):
    print(f"File not found: {FILENAME}")
    sys.exit(1)

with open(FILENAME, 'rb') as f:
    audio_bytes = f.read()

total_samples = len(audio_bytes)
print(f"Total samples: {total_samples}")

# Time between samples
dt = 1.0 / SAMPLE_RATE  # seconds per sample

# Stream bytes at the correct rate
start_time = time.time()
for i, sample in enumerate(audio_bytes):
    ser.write(bytes([sample]))

    # Calculate next sample time
    next_time = start_time + (i+1)*dt
    now = time.time()
    sleep_time = next_time - now
    if sleep_time > 0:
        time.sleep(sleep_time)

ser.close()
print("\nStreaming done!")