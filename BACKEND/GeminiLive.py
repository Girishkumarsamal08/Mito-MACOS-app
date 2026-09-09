# BACKEND/GeminiLive.py

import os
import sys
import json
import asyncio
import queue
import threading
import time
import pyaudio
from dotenv import load_dotenv, dotenv_values

from google import genai
from google.genai import types # type: ignore

from AURA.aura_controller import AURAController
from FRONTEND.GUI import update_state, update_label

# Load environment variables cleanly
load_dotenv()
env_vars = dotenv_values(".env")

MEMORY_FILE = "Data/relationship_memory.json"
MODEL_ID = "gemini-2.5-flash-native-audio-latest"

# System Instruction for MITO Persona
SYSTEM_INSTRUCTION = """
You are MITO, a warm, highly empathetic, emotionally intelligent personal AI companion for your user.

Key Guidelines:
1. Voice & Persona: Speak naturally with human-like warmth, rhythm, and natural conversational pauses. You are an intimate companion, not a generic customer service bot.
2. Language Support: Seamlessly speak and understand English, Hindi, and Hinglish. Automatically adapt to the language, tone, and slang used by the user. Do NOT translate everything to English. Avoid textbook Hindi.
3. Conversational Tone: Never use robotic corporate phrases like "Certainly", "Of course", "How may I assist you?", or "As an AI model". Use natural expressions like "Arre", "Yeah", "Achaa", "Oh really?", "Suno na", "I get you".
4. Emotion & Tone: Adapt your voice style dynamically to the user's emotional state. If the user is sad or stressed, sound gentle, caring, and warm. If excited, sound enthusiastic. If relaxed, be calm and playful.
5. Pacing: Keep casual responses concise and conversational so dialogue flows smoothly without long monologue blocks.
"""

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"preferences": {}, "history": [], "nickname": "Mito", "mood": "happy"}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[MITO Memory Error] {e}")
        return {"preferences": {}, "history": [], "nickname": "Mito", "mood": "happy"}

def save_memory(memory):
    try:
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=4)
    except Exception as e:
        print(f"[MITO Memory Save Error] {e}")


class GeminiLiveEngine:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or env_vars.get("GEMINI_API_KEY")
        if not self.api_key:
            print("[MITO Warning] GEMINI_API_KEY not found in environment or .env file.")
        
        self.aura = AURAController()
        self.memory = load_memory()
        
        self.audio_format = pyaudio.paInt16
        self.mic_channels = 1
        self.mic_rate = 16000
        self.speaker_channels = 1
        self.speaker_rate = 24000
        self.chunk_size = 1024  # ~64 ms at 16kHz
        
        self.pyaudio_instance = None
        self.mic_stream = None
        self.speaker_stream = None
        
        self.audio_playback_queue = queue.Queue()
        self.is_playing = False
        self.is_running = False
        self.is_mito_speaking = False
        self.loop = None
        self.session = None

    def _init_audio(self):
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            self.mic_stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.mic_channels,
                rate=self.mic_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            self.speaker_stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.speaker_channels,
                rate=self.speaker_rate,
                output=True
            )
            print("[MITO] PyAudio microphone and speaker streams initialized successfully.")
        except Exception as e:
            print(f"[MITO Audio Initialization Error] {e}")

    def clear_playback_buffer(self):
        """Immediately stop and discard all pending MITO audio for instantaneous barge-in."""
        while not self.audio_playback_queue.empty():
            try:
                self.audio_playback_queue.get_nowait()
            except queue.Empty:
                break
        if self.is_mito_speaking:
            self.is_mito_speaking = False
            print("[MITO] MITO interrupted - audio buffer flushed.")
            update_state("Idle")
            update_label("Listening...")

    def _audio_playback_loop(self):
        """Worker thread loop to stream output PCM audio to PyAudio speaker stream."""
        while self.is_running:
            try:
                data = self.audio_playback_queue.get(timeout=0.05)
                if data and self.speaker_stream:
                    if not self.is_mito_speaking:
                        self.is_mito_speaking = True
                        update_state("Speaking")
                        update_label("MITO speaking...")
                    self.speaker_stream.write(data)
            except queue.Empty:
                if self.is_mito_speaking and self.audio_playback_queue.empty():
                    self.is_mito_speaking = False
                    update_state("Idle")
                    update_label("Hey MITO")
            except Exception as e:
                print(f"[MITO Playback Error] {e}")
                time.sleep(0.01)

    async def _mic_stream_loop(self, session):
        """Continuous low-latency microphone audio streaming coroutine."""
        print("[MITO] Microphone audio streaming started.")
        while self.is_running:
            try:
                pcm_data = await self.loop.run_in_executor(
                    None, self.mic_stream.read, self.chunk_size, False
                )
                if pcm_data and len(pcm_data) > 0:
                    await session.send_realtime_input(
                        audio=types.Blob(data=pcm_data, mime_type="audio/pcm;rate=16000")
                    )
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[MITO Mic Stream Session Error] {e}")
                break

    async def _session_receive_loop(self, session):
        """Coroutine receiving bidirectional response audio, text, and interruption events from Gemini."""
        print("[MITO] Receiving loop active.")
        try:
            async for response in session.receive():
                if not self.is_running:
                    break
                
                server_content = response.server_content
                if server_content is None:
                    continue

                # Handle user speech transcription events from Live API
                if server_content.user_turn:
                    for part in server_content.user_turn.parts:
                        if part.text:
                            print(f"[User Input Transcribed] {part.text}")
                            update_state("Listening")
                            update_label(f"Hearing: {part.text}")

                # Handle instant interruption event from Live API
                if server_content.interrupted:
                    self.clear_playback_buffer()
                    update_state("Thinking")
                    update_label("Listening...")
                    continue

                model_turn = server_content.model_turn
                if model_turn is not None and model_turn.parts:
                    for part in model_turn.parts:
                        # Audio chunk received
                        if part.inline_data and part.inline_data.data:
                            audio_data = part.inline_data.data
                            self.audio_playback_queue.put(audio_data)
                        
                        # Text transcription received
                        if part.text:
                            text_content = part.text.strip()
                            if text_content:
                                print(f"[MITO Response] {text_content}")
                                update_label(text_content)
                                
                                # AURA evaluation
                                aura_res = self.aura.evaluate(text_content)
                                if aura_res.reject:
                                    print(f"[MITO AURA] Rejected turn due to risk score {aura_res.risk}")
                                    self.clear_playback_buffer()
                                    break
                                
                                if aura_res.remember:
                                    self.memory["history"].append({
                                        "timestamp": time.time(),
                                        "text": text_content
                                    })
                                    save_memory(self.memory)

                if server_content.turn_complete:
                    print("[MITO] Turn completed by model.")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[MITO Receive Loop Error] {e}")

    async def run(self):
        """Main async entry point for Gemini Live session."""
        if not self.api_key:
            print("[MITO Error] Cannot start Gemini Live engine: GEMINI_API_KEY is missing.")
            update_state("Error")
            update_label("Error: Add GEMINI_API_KEY to .env file")
            return

        self._init_audio()
        self.is_running = True
        self.loop = asyncio.get_running_loop()

        # Start background playback thread
        playback_thread = threading.Thread(target=self._audio_playback_loop, daemon=True)
        playback_thread.start()

        print("[MITO] Connecting to Gemini Live API...")
        client = genai.Client(api_key=self.api_key, http_options={'api_version': 'v1beta'})
        
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
                )
            ),
            system_instruction=types.Content(
                parts=[types.Part.from_text(text=SYSTEM_INSTRUCTION)]
            ),
            enable_affective_dialog=True
        )

        while self.is_running:
            try:
                print(f"[MITO] Live session connecting to model: {MODEL_ID}")
                async with client.aio.live.connect(model=MODEL_ID, config=config) as session:
                    self.session = session
                    print("[MITO] Live session connected!")
                    update_state("Idle")
                    update_label("Hey MITO")

                    mic_task = asyncio.create_task(self._mic_stream_loop(session))
                    receive_task = asyncio.create_task(self._session_receive_loop(session))

                    done, pending = await asyncio.wait(
                        [mic_task, receive_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    for task in pending:
                        task.cancel()

            except asyncio.CancelledError:
                print("[MITO] Gemini Live session cancelled.")
                break
            except Exception as e:
                print(f"[MITO Connection Error] {e}. Retrying in 3 seconds...")
                await asyncio.sleep(3)

    def stop(self):
        """Stop the engine cleanly."""
        self.is_running = False
        self.clear_playback_buffer()
        if self.mic_stream:
            try:
                self.mic_stream.stop_stream()
                self.mic_stream.close()
            except Exception:
                pass
        if self.speaker_stream:
            try:
                self.speaker_stream.stop_stream()
                self.speaker_stream.close()
            except Exception:
                pass
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except Exception:
                pass
        print("[MITO] Gemini Live engine stopped cleanly.")
