import os
import random
import asyncio
import subprocess
import pygame
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
Assistantvoice = env_vars.get("AssistantVoice") or "en-US-AriaNeural"

def _notify_bridge(text: str):
    try:
        from BACKEND.BridgeServer import broadcast_state
        broadcast_state("Speaking", text)
    except Exception:
        pass

async def TextToAudioFile(text: str) -> str:
    file_path = "Data/speech.mp3"
    os.makedirs("Data", exist_ok=True)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    from gtts import gTTS
    tts = gTTS(text=text, lang="en")
    tts.save(file_path)
    return file_path

import re

def remove_emojis(text: str) -> str:
    if not text:
        return ""
    emoji_pattern = re.compile(r'[\U00010000-\U0010FFFF\u2600-\u26FF\u2700-\u27BF]', flags=re.UNICODE)
    cleaned = emoji_pattern.sub('', text)
    return ' '.join(cleaned.split())

def TTS(Text: str, func_or_mood=None):
    Text = remove_emojis(Text)
    if not Text or sum(1 for c in Text if c.isalnum()) < 2:
        print(f"[MITO TTS] Ignored non-speech text: {repr(Text)}")
        return False

    print(f"[MITO Speech] Speaking: {Text}")

    # 1. macOS Native Speech Synthesis (Instantaneous < 5ms start, 100% synchronized with Speaking.mp4 video)
    try:
        # Trigger Speaking state update and voice output at the exact same instant
        _notify_bridge(Text)
        voice = "Samantha"
        res = subprocess.run(["say", "-v", voice, Text], capture_output=True)
        if res.returncode != 0:
            res = subprocess.run(["say", Text], capture_output=True)
        if res.returncode == 0:
            return True
    except Exception as e:
        print(f"[MITO TTS macOS say Error] {e}")

    # 2. Fallback: gTTS (Pre-generate audio file first, then trigger Speaking video state + afplay together)
    try:
        file_path = asyncio.run(TextToAudioFile(Text))
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            _notify_bridge(Text)
            res = subprocess.run(["afplay", file_path], capture_output=True)
            if res.returncode == 0:
                return True
    except Exception as e:
        print(f"[MITO TTS gTTS Warning] {e}")

    return False

def TextToSpeech(Text, func_or_mood=None):
    if not Text or not str(Text).strip():
        return False
    Text = str(Text).strip()
    return TTS(Text, func_or_mood)

if __name__ == "__main__":
    while True:
        txt = input("Enter text: ")
        TextToSpeech(txt)