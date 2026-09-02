import os
import io
import speech_recognition as sr
import numpy as np
import mtranslate as mt
from dotenv import dotenv_values
from groq import Groq

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Lazy-loaded local whisper model for offline fallback
_local_whisper_model = None

def get_local_whisper():
    global _local_whisper_model
    if _local_whisper_model is None:
        import whisper
        print("[MITO STT] Loading local Whisper fallback model...")
        _local_whisper_model = whisper.load_model("base")
    return _local_whisper_model

def QueryModifier(Query):
    if not Query or not Query.strip():
        return ""
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["what", "where", "when", "who", "why", "whose", "which", "how", "whom", "can you", "what's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def _notify_bridge(state: str, text: str):
    try:
        from BACKEND.BridgeServer import broadcast_state
        broadcast_state(state, text)
    except Exception:
        pass

# Global recognizer instance to preserve energy threshold
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.6
recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 300

def SpeechRecognition():
    try:
        with sr.Microphone() as source:
            print("[MITO STT] Listening for speech...")
            _notify_bridge("listening", "Listening...")
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=12
            )

        print("[MITO STT] Transcribing audio...")
        _notify_bridge("thinking", "Transcribing...")

        query = ""

        # 1. Try Groq Whisper API (Ultra-fast, ~100ms response time)
        if GroqAPIKey:
            try:
                client = Groq(api_key=GroqAPIKey)
                wav_data = audio.get_wav_data(convert_rate=16000, convert_width=2)
                buffer = io.BytesIO(wav_data)
                buffer.name = "audio.wav"

                transcription = client.audio.transcriptions.create(
                    file=buffer,
                    model="whisper-large-v3-turbo",
                    prompt="MITO assistant, Hinglish and English conversation."
                )
                query = transcription.text.strip()
            except Exception as groq_err:
                print(f"[MITO STT Groq Warning] {groq_err}")

        # 2. Fallback to local Whisper
        if not query:
            try:
                model = get_local_whisper()
                audio_np = np.frombuffer(
                    audio.get_raw_data(convert_rate=16000, convert_width=2),
                    np.int16
                ).astype(np.float32) / 32768.0
                result = model.transcribe(audio_np, fp16=False)
                query = result.get("text", "").strip()
            except Exception as local_err:
                print(f"[MITO STT Local Whisper Error] {local_err}")

        if not query:
            print("[MITO STT] No words recognized.")
            return ""

        print(f"[MITO STT] User said: {query}")
        _notify_bridge("thinking", f"User: {query}")

        if InputLanguage and ("en" in InputLanguage.lower()):
            return QueryModifier(query)
        else:
            return QueryModifier(UniversalTranslator(query))

    except sr.WaitTimeoutError:
        print("[MITO STT] Listening timeout (no speech detected).")
        return ""

    except sr.UnknownValueError:
        print("[MITO STT] Audio unintelligible.")
        return ""

    except Exception as e:
        print(f"[MITO STT Error] {e}")
        return ""

 