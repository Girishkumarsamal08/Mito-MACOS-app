import speech_recognition as sr
import whisper
import numpy as np
import os
import mtranslate as mt
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage")
model = whisper.load_model("base")

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["what", "where", "when", "who", "why", "whose", "which", "how", "whom", "can you", "what's", "how's", "can you"]

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

def SpeechRecognition():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Listening...")

            r.adjust_for_ambient_noise(source, duration=2)

            r.dynamic_energy_threshold = True
            r.energy_threshold = 300
            r.pause_threshold = 1

            audio = r.listen(
                source,
                timeout=15,
                phrase_time_limit=12
            )

        print("Transcribing with Whisper...")

        audio_np = np.frombuffer(
            audio.get_raw_data(convert_rate=16000, convert_width=2),
            np.int16
        ).astype(np.float32) / 32768.0

        result = model.transcribe(audio_np, fp16=False)
        query = result["text"].strip()
        if not query:
            print("[MITO] Empty transcription.")
            return ""

        print(f"User said: {query}")

        if InputLanguage and (InputLanguage.lower() == "en" or "en" in InputLanguage.lower()):
            return QueryModifier(query)
        else:
            return QueryModifier(UniversalTranslator(query))

    except sr.WaitTimeoutError:
        print("Timeout — no speech detected.")
        return ""

    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""

    except Exception as e:
        print(f"SpeechRecognition Error: {e}")
        return ""
 