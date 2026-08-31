
import pvporcupine
import pyaudio
import struct
import os
import threading
from dotenv import load_dotenv
load_dotenv()

ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")
KEYWORD_PATH = os.path.join(os.path.dirname(__file__), "HEY-Mito_en_mac_v3_0_0.ppn")


def detect_wake_word(callback):
       
    porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[KEYWORD_PATH],
            sensitivities=[0.6]
        )

    audio = pyaudio.PyAudio()
    stream = audio.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
        )

  
    while True:
            audio_data = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, audio_data)
            result = porcupine.process(pcm)
            if result >= 0:
                print("[HEY Mito] Wake word detected!")
                callback()
        


