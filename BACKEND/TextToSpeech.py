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

def TTS(Text: str, func_or_mood=None):
    print(f"[MITO Speech] Speaking: {Text}")
    _notify_bridge(Text)

    # 1. Try gTTS -> afplay / pygame
    try:
        file_path = asyncio.run(TextToAudioFile(Text))
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            res = subprocess.run(["afplay", file_path], capture_output=True)
            if res.returncode == 0:
                return True

            # Fallback to pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if callable(func_or_mood) and func_or_mood() == False:
                    break
                pygame.time.Clock().tick(10)
            return True
    except Exception as e:
        print(f"[MITO TTS gTTS Warning] {e}")

    # 2. Fallback to macOS native 'say' command (Offline, instantaneous, ultra-reliable)
    try:
        print("[MITO TTS] Using macOS native speech synthesis...")
        # Prefer a female macOS voice if available (e.g. Samantha, Karen, Victoria, Ava)
        voice = "Samantha"
        res = subprocess.run(["say", "-v", voice, Text], capture_output=True)
        if res.returncode != 0:
            res = subprocess.run(["say", Text], capture_output=True)
        if res.returncode == 0:
            return True
    except Exception as e:
        print(f"[MITO TTS macOS say Error] {e}")

    # 3. Fallback to pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(Text)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"[MITO TTS pyttsx3 Error] {e}")

    return False

def TextToSpeech(Text, func_or_mood=None):
    if not Text or not str(Text).strip():
        return False
    Text = str(Text).strip()
    Data = Text.split(".")
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir."
    ]
    if len(Data) > 4 and len(Text) >= 250:
        short_text = " ".join(Text.split(".")[0:1]) + ". " + random.choice(responses)
        return TTS(short_text, func_or_mood)
    else:
        return TTS(Text, func_or_mood)

if __name__ == "__main__":
    while True:
        txt = input("Enter text: ")
        TextToSpeech(txt)