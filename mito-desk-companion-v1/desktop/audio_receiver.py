#!/usr/bin/env python3
"""
MITO Desk Companion — Wi-Fi Audio Streaming Receiver (Mac-Side)
==============================================================
Receives raw 16 kHz 16-bit PCM audio from the INMP441 microphone stream
over UDP or WebSocket, and provides a clean queue interface for SpeechRecognition
and Gemini Live.
"""

import socket
import struct
import wave
import time
import os

UDP_IP = "0.0.0.0"
UDP_PORT = 12345
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit PCM

def record_test_audio(output_wav="mito_bench_mic_test.wav", duration_sec=5):
    """
    Listens for UDP audio packets from ESP32 for duration_sec and writes to a WAV file.
    Use this to verify the sound quality of the INMP441 microphone over Wi-Fi.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(2.0)

    print(f"[AUDIO RECEIVER] Listening for ESP32 microphone stream on UDP port {UDP_PORT}...")
    print(f"[AUDIO RECEIVER] Recording {duration_sec} seconds of audio into '{output_wav}'...")

    frames = []
    start_time = time.time()

    try:
        while time.time() - start_time < duration_sec:
            try:
                data, addr = sock.recvfrom(2048)
                frames.append(data)
            except socket.timeout:
                pass
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()

    if frames:
        total_bytes = sum(len(f) for f in frames)
        print(f"[AUDIO RECEIVER] Captured {total_bytes} bytes of audio. Saving to {output_wav}...")
        with wave.open(output_wav, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b"".join(frames))
        print(f"[AUDIO RECEIVER] Success! Test file saved: {os.path.abspath(output_wav)}")
    else:
        print("[AUDIO RECEIVER] No audio packets received. Ensure ESP32 is transmitting to this Mac's IP.")

if __name__ == "__main__":
    record_test_audio()
