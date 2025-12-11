import serial
import time
import struct

# --- CONFIG ---
SERIAL_PORT = '/dev/ttyUSB0'  # Check with: ls /dev/ttyUSB*
BAUD_RATE = 921600
SAMPLE_RATE = 16000
DURATION = 5  # Seconds to record
OUTPUT_FILE = "raw_mic_input.pcm"

print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE}...")

try:
    # Open Serial Port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    # Clear buffer to remove old junk
    ser.reset_input_buffer()

    print(f"Recording for {DURATION} seconds... Speak now!")

    # Calculate bytes to read: SampleRate * Seconds * 2 bytes/sample
    total_bytes = SAMPLE_RATE * DURATION * 2

    # Read exact amount of data
    data = ser.read(total_bytes)

    print("Recording finished.")

    # Save to file
    with open(OUTPUT_FILE, "wb") as f:
        f.write(data)

    print(f"Saved {len(data)} bytes to {OUTPUT_FILE}")
    print("Run the ffmpeg command below to play it.")

except serial.SerialException as e:
    print(f"Error: {e}")
    print("Hint: Make sure CLion Serial Monitor is CLOSED.")
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()