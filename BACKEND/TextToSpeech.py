import os
import random
import asyncio
import subprocess
import re
import requests
import edge_tts
from dotenv import dotenv_values, load_dotenv

load_dotenv()

def get_openai_key():
    env_vars = dotenv_values(".env")
    return os.getenv("OPENAI_API_KEY") or env_vars.get("OPENAI_API_KEY") or ""

def get_assistant_voice():
    env_vars = dotenv_values(".env")
    return env_vars.get("AssistantVoice") or env_vars.get("Voice") or "maple"

# HD Neural Voice configuration for human-like emotional expressiveness & Maple voice quality
NEURAL_VOICE_HINDI = "hi-IN-SwaraNeural"    # Warm, conversational, human female voice
NEURAL_VOICE_ENGLISH = "en-US-AvaNeural"    # High-fluency warm female voice matching ChatGPT Maple timbre

def _notify_bridge(text: str):
    try:
        from BACKEND.BridgeServer import broadcast_state
        broadcast_state("Speaking", text)
    except Exception:
        pass

def is_hindi_text(text: str) -> bool:
    """Check if text contains Devanagari or Hindi words."""
    if re.search(r'[\u0900-\u097F]', text):
        return True
    
    hindi_keywords = {
        "magar", "aapko", "jab", "zaroorat", "padegi", "aap", "kaise", "kya", "hai", 
        "hain", "ho", "kar", "rahe", "rahi", "main", "thik", "hu", "mera", "meri", 
        "mujhe", "tum", "samajh", "namaste", "dhanyawad", "shukriya", "batao", "suno", 
        "ha", "nahi", "accha", "acha", "bhai", "ji", "karo", "kaha", "kab", "kaun", 
        "kyun", "kyon", "kuch", "sab", "apna", "apni"
    }
    words = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
    matches = words.intersection(hindi_keywords)
    return len(matches) >= 1

def remove_emojis(text: str) -> str:
    if not text:
        return ""
    emoji_pattern = re.compile(r'[\U00010000-\U0010FFFF\u2600-\u26FF\u2700-\u27BF]', flags=re.UNICODE)
    cleaned = emoji_pattern.sub('', text)
    return ' '.join(cleaned.split())

def play_audio_file(file_path: str) -> bool:
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            from FRONTEND.GUI import update_state, update_label
            update_state("Speaking")
            update_label("Speaking...")
            res = subprocess.run(["afplay", file_path], capture_output=True, timeout=30)
            update_state("Idle")
            update_label("Hey MITO")
            return res.returncode == 0
        except subprocess.TimeoutExpired:
            print("[MITO TTS] Audio playback finished or timed out.")
            try:
                from FRONTEND.GUI import update_state, update_label
                update_state("Idle")
                update_label("Hey MITO")
            except Exception:
                pass
            return True
        except Exception as e:
            print(f"[MITO TTS Playback Error] {e}")
            try:
                from FRONTEND.GUI import update_state, update_label
                update_state("Idle")
                update_label("Hey MITO")
            except Exception:
                pass
    return False

# ---------- 1. Free HD Neural Expressive Voice Engine (ChatGPT Realtime Quality) ----------
async def generate_neural_expressive_audio(text: str) -> str:
    file_path = "Data/speech.mp3"
    os.makedirs("Data", exist_ok=True)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    # Pick HD Neural Voice identity
    voice = NEURAL_VOICE_HINDI if is_hindi_text(text) else NEURAL_VOICE_ENGLISH
    
    # Generate speech with dynamic pitch & rate for human emotional warmth
    communicate = edge_tts.Communicate(text, voice, pitch="+2Hz", rate="+0%")
    await communicate.save(file_path)
    return file_path

def free_neural_human_voice_tts(text: str) -> bool:
    """HD Neural voice with human emotion, natural pitch, and breathing — 100% Free."""
    try:
        print(f"[MITO Speech] (HD Neural Expressive Voice) Speaking: {text}")
        file_path = asyncio.run(generate_neural_expressive_audio(text))
        _notify_bridge(text)
        return play_audio_file(file_path)
    except Exception as e:
        print(f"[MITO TTS Neural Engine Error] {e}")
        return False

# ---------- 2. OpenAI ChatGPT Voice Engine ("maple") ----------
def openai_tts(text: str, voice: str = "maple") -> bool:
    key = get_openai_key()
    if not key or not key.strip() or not key.startswith("sk-"):
        return False
    try:
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {key.strip()}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "tts-1",
            "input": text,
            "voice": voice,
            "response_format": "mp3"
        }
        print(f"[MITO TTS OpenAI] Speaking ChatGPT Voice ('{voice}'): {text[:50]}...")
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        if res.status_code == 200:
            file_path = "Data/speech.mp3"
            os.makedirs("Data", exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(res.content)
            _notify_bridge(text)
            return play_audio_file(file_path)
    except Exception as e:
        print(f"[MITO TTS OpenAI Error] {e}")
    return False

# ---------- 3. Unified gTTS Fallback Engine ----------
def gtts_fallback_tts(text: str) -> bool:
    try:
        from gtts import gTTS
        file_path = "Data/speech.mp3"
        os.makedirs("Data", exist_ok=True)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        lang = "hi" if is_hindi_text(text) else "en"
        print(f"[MITO Speech] (gTTS Fallback) Speaking: {text}")
        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)
        _notify_bridge(text)
        return play_audio_file(file_path)
    except Exception as e:
        print(f"[MITO TTS gTTS Error] {e}")
        return False

# ---------- Main TTS Dispatcher ----------
def TTS(Text: str, func_or_mood=None):
    Text = remove_emojis(Text)
    if not Text or sum(1 for c in Text if c.isalnum()) < 2:
        print(f"[MITO TTS] Ignored non-speech text: {repr(Text)}")
        return False

    # 1. OpenAI ChatGPT Voice ("maple") if OpenAI API key is set
    voice_name = get_assistant_voice()
    if openai_tts(Text, voice=voice_name):
        return True

    # 2. HD Neural Expressive Human Emotion Engine (100% FREE, ChatGPT Realtime Quality Maple-style)
    if free_neural_human_voice_tts(Text):
        return True

    # 3. gTTS Fallback
    return gtts_fallback_tts(Text)

def TextToSpeech(Text, func_or_mood=None):
    if not Text or not str(Text).strip():
        return False
    Text = str(Text).strip()
    return TTS(Text, func_or_mood)

if __name__ == "__main__":
    while True:
        txt = input("Enter text: ")
        TextToSpeech(txt)